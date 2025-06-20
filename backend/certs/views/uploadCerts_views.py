from cryptography import x509
from datetime import datetime
import pytz
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from certs.models import Certificate,UploadedFile
from certs.serializers import UploadFileSerializer, CertificateSerializer,CertificateMetaSerializer
from certs.utils import (
    hash_certificate,
    parse_uploaded_file,
    extract_common_name,
    classify_certificate,
    compute_issuer_hash,
    compute_subject_hash,
    certificate_relationship
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from django.conf import settings
import uuid
from certs.models import (
    Certificate,
    Team,
    PrivateKey, 
)


class MetaDataUploadView(APIView):
    """View for uploading certificate metadata.
    This view handles the upload of certificate metadata, including the file ID, team IDs,
    optional password, and certificate name. It processes the uploaded file, checks ownership,  
    validates team access, and extracts certificate information. If a private key is present,
    it creates a corresponding PrivateKey model. It also handles certificate chains and relationships.
    The view expects a file ID, team IDs, optional password, and certificate name in the request data.  
    If the upload is successful, it returns a success message with the certificate ID and type.
    If any validation fails, it returns appropriate error messages.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CertificateMetaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data['name']
        file_id = serializer.validated_data['file']
        team_ids = serializer.validated_data['teams']
        password = serializer.validated_data.get('password')

        # ✅ Check file ownership
        try:
            uploaded_file_obj = UploadedFile.objects.get(id=file_id,uploaded_by=request.user)
        except UploadedFile.DoesNotExist:
            return Response({"error": "You do not own this file or it doesn't exist"})
        
        uploaded_file = uploaded_file_obj.file

        # ✅ Team access control
        user_team_ids = list(request.user.teams.values_list('id', flat=True))
        for tid in team_ids:
            if tid not in user_team_ids:
                return Response(
                    {"error": f"You cannot assign to teams you don't belong to."},
                    status=403
                )
            
        # ✅ Parse certificate
        parsed = parse_uploaded_file(uploaded_file, password=password)
        if parsed.get("error"):
            return Response({"error": parsed["error"]}, status=400)

        certificate = None

        if parsed["cert"]:

            cert_type = classify_certificate(parsed["cert"])
            main_hash = hash_certificate(parsed["cert"])
            issuer_hash = compute_issuer_hash(parsed["cert"])
            subject_hash = compute_subject_hash(parsed["cert"])
            existing_cert = Certificate.objects.filter(cert_hash=main_hash).first()

            if existing_cert:
                certificate = existing_cert
            else:
                try:
                    ext = parsed["cert"].extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    san = ext.value.get_values_for_type(x509.DNSName)
                except x509.ExtensionNotFound:
                    san = []

                if not name:
                    name=extract_common_name(parsed["cert"].subject)

                filename = f"{uuid.uuid4()}_cert.pem"
                file_content = ContentFile(parsed["cert"].public_bytes(encoding=settings.X509_ENCODING))
                certificate = Certificate.objects.create(
                    name=name,
                    subject=parsed["cert"].subject.rfc4514_string(),
                    issuer=parsed["cert"].issuer.rfc4514_string(),
                    serial_number=str(parsed["cert"].serial_number),
                    not_before=parsed["cert"].not_valid_before_utc,
                    not_after=parsed["cert"].not_valid_after_utc,
                    is_expired=parsed["cert"].not_valid_after_utc < datetime.now(pytz.utc),
                    signature_algorithm=parsed["cert"].signature_algorithm_oid._name,
                    public_key_type=parsed["cert"].public_key().__class__.__name__,
                    public_key_length=getattr(parsed["cert"].public_key(), 'key_size', None),
                    san=san,
                    file=uploaded_file_obj,
                    file_format=parsed["format"],
                    original_filename=parsed["original_filename"],
                    cert_hash=main_hash,
                    issuer_hash=issuer_hash,
                    subject_hash=subject_hash,
                    certificate_type=cert_type[:20],
                )

                print(f"Created certificate: {certificate.name} - {certificate.certificate_type}")
                

                for tid in team_ids:
                    team = Team.objects.get(id=tid)
                    certificate.access_teams.add(team)

            certificate_relationship(
                cert_type=cert_type, 
                certificate=certificate,
                issuer_hash=issuer_hash,
                subject_hash=subject_hash
                )

        # ✅ If private key exists
        if parsed["key"]:
            encrypted = settings.FERNET.encrypt(
                parsed["key"].private_bytes(
                    encoding=settings.X509_ENCODING,
                    format=settings.KEY_FORMAT,
                    encryption_algorithm=settings.KEY_ENCRYPTION_ALGO
                )
            )
            key_filename = f"{uuid.uuid4()}_key.enc"
            key_file = ContentFile(encrypted)

            certificate_id = serializer.validated_data.get('certificate_id')
            if certificate_id:
                try:
                    certificate = Certificate.objects.get(id=certificate_id)
                except Certificate.DoesNotExist:
                    return Response({"error": "Linked certificate not found."}, status=404)
            
            private_key = PrivateKey.objects.create(
                name=name,
                certificate=certificate,
                uploaded_by=request.user,
                file_format=parsed["format"],
                original_filename=parsed["original_filename"]
            )
            private_key.encrypted_key_file.save(key_filename, key_file)

            for tid in team_ids:
                private_key.access_teams.add(Team.objects.get(id=tid))

        # ✅ Chain parsing
        for chain_cert in parsed["chain"]:

            cert_type = classify_certificate(chain_cert)
            cert_hash = hash_certificate(chain_cert)
            issuer_hash = compute_issuer_hash(chain_cert)
            subject_hash = compute_subject_hash(chain_cert)
            chain_cert_obj = Certificate.objects.filter(cert_hash=cert_hash).first()

            if not chain_cert_obj:
                try:
                    ext = chain_cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    san = ext.value.get_values_for_type(x509.DNSName)
                except:
                    san = []

                chain_cert_obj = Certificate.objects.create(
                    name=extract_common_name(chain_cert.subject),
                    subject=chain_cert.subject.rfc4514_string(),
                    issuer=chain_cert.issuer.rfc4514_string(),
                    serial_number=str(chain_cert.serial_number),
                    not_before=chain_cert.not_valid_before_utc,
                    not_after=chain_cert.not_valid_after_utc,
                    is_expired=chain_cert.not_valid_after_utc < datetime.now(pytz.utc),
                    signature_algorithm=chain_cert.signature_algorithm_oid._name,
                    public_key_type=chain_cert.public_key().__class__.__name__,
                    public_key_length=getattr(chain_cert.public_key(), 'key_size', None),
                    file_format="PEM",
                    original_filename=f"chain_{str(chain_cert.serial_number)}.pem",
                    cert_hash=cert_hash,
                    issuer_hash=issuer_hash,
                    subject_hash=subject_hash,
                    certificate_type=cert_type[:20], 
                )

                for tid in team_ids:
                    chain_cert_obj.access_teams.add(Team.objects.get(id=tid))

                chain_filename = f"{uuid.uuid4()}_chain_cert.pem"
                cert_file = ContentFile(chain_cert.public_bytes(encoding=settings.X509_ENCODING))
                uploaded_chain_file = UploadedFile.objects.create(
                    uploaded_by=request.user,
                )
                uploaded_chain_file.file.save(chain_filename, cert_file)
                chain_cert_obj.file = uploaded_chain_file
                chain_cert_obj.uploaded_by = request.user
                print(f"Chain cert: {chain_cert_obj.name} - {chain_cert_obj.certificate_type}")
                chain_cert_obj.save()

            certificate_relationship(
                cert_type=cert_type,
                certificate=chain_cert_obj,
                issuer_hash=issuer_hash,
                subject_hash=subject_hash,
            )

        #link_chain_by_hash(certificate,chain_objs)
        print("Main:", parsed["cert"].subject)
        print("Chain:", [c.subject for c in parsed["chain"]])
        return Response({
            "message": "File uploaded and handled successfully.",
            "certificate_id": certificate.id if certificate else None,
            "certificate_type": certificate.certificate_type if certificate else None,
        }, status=status.HTTP_201_CREATED)
    

class FileUploadView(generics.CreateAPIView):
    """View for uploading files.
    This view allows authenticated users to upload files. The uploaded files are stored in the UploadedFile 
    model, which includes fields for the file itself, the user who uploaded it, and the timestamp of the upload.
    The view uses the UploadFileSerializer to validate and save the uploaded file data. 
    The uploaded file is associated with the user who uploaded it.
    """ 
    queryset = UploadedFile.objects.all()
    serializer_class = UploadFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)