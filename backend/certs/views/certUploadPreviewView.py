from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from cryptography import x509
from certs.utils import parse_uploaded_file, detect_file_format, parse_uploaded_content,extract_common_name
import uuid
import os



class UploadCertFilePreviewView(APIView):
    """View for uploading a certificate file and previewing its contents.
This view handles the parsing of various certificate formats, including PEM, DER, PFX (PKCS12), and others.
It extracts certificate and key information, checks for password requirements, and prepares a session for previewing
the uploaded content.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("file")
        password = request.data.get("password", "")
        
        if not file:
            return Response({"error": "No file provided."}, status=400)
        
        file_format = detect_file_format(file)
        file_name_without_extension = os.path.splitext(file.name)[0] 

        try:
            parsed = parse_uploaded_content(file, password=password)

            if parsed.get("password_required"):
                return Response({
                    "status": "password_required",
                    "message": parsed["error"],
                    "format": "PKCS12",
                    "password_required": True
                }, status=400)
        except Exception as e:
            # PKCS12 password failure — special case
            if file_format == "PKCS12":
                return Response({
                    "status": "password_required",
                    "message": "This file is a PFX archive and requires a password to continue.",
                    "format": "PKCS12",
                    "password_required": True
                }, status=400)
            else:
                return Response({"error": str(e)}, status=400)

        session_key = f"upload_preview:{request.user.id}:{uuid.uuid4()}"
        session_data = {"certs": {}, "key": {}}
        # Build a frontend-friendly preview list
        certs_metadata = []
        for i, cert in enumerate(parsed.get("certs",[])):
            temp_id = f"cert_{uuid.uuid4()}"
            session_data["certs"][temp_id] = cert.public_bytes(encoding=settings.X509_ENCODING).decode("utf-8")
            cert_name = extract_common_name(cert.subject)
            certs_metadata.append({
                "filename": file_name_without_extension,
                "temp_id": temp_id,
                "common_name":cert_name,
                "subject": cert.subject.rfc4514_string(),
                "not_after": cert.not_valid_after_utc,
                "serial": str(cert.serial_number),
            })

        key_info = None
        key = parsed.get("key")
        if key:
            temp_id = f"key_{uuid.uuid4()}"
            session_data["key"][temp_id] = key.private_bytes(
                encoding=settings.X509_ENCODING,
                format=settings.KEY_FORMAT,
                encryption_algorithm=settings.KEY_ENCRYPTION_ALGO
            ).decode("utf-8")

            key_info = {
                "temp_id": temp_id,
                "type": key.__class__.__name__,
                "bit_length": getattr(key, 'key_size', None),
                "filename":file_name_without_extension,
            }
        request.session[session_key] = session_data
        request.session.set_expiry(600)
        request.session.modified = True
        request.session.save()


        return Response({
            "status": "pars ed",
            "format": file_format,
            "session_key": session_key,
            "certificates": certs_metadata,
            "private_key": key_info
        }, status=200)
