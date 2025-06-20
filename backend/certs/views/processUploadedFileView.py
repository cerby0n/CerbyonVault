from cryptography import x509
from rest_framework.permissions import IsAuthenticated
from certs.models import UploadedFile
from certs.serializers import UploadedFileProcessSerializer
from certs.utils import (
    parse_uploaded_content,
    create_uploaded_file,
    create_certificate,
    create_private_key,
    link_certificates
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class ProcessUploadedFileView(APIView):
    """View for processing an uploaded file to extract certificates and keys.
    This view handles the parsing of uploaded files, validates ownership and team access,
    and creates corresponding certificate and private key models.
    It expects a file ID, team IDs, and optional password and name override in the request data.
    If the file is successfully processed, it returns a success message with the count of certificates
    and whether a key was found. If any validation fails, it returns appropriate error messages.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadedFileProcessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_id = serializer.validated_data["file_id"]
        team_ids = serializer.validated_data["teams"]
        password = serializer.validated_data.get("password", None)
        name_override = serializer.validated_data.get("name", "").strip()

        # ✅ Validate uploaded file ownership
        try:
            uploaded_file_obj = UploadedFile.objects.get(id=file_id, uploaded_by=request.user)
        except UploadedFile.DoesNotExist:
            return Response({"error": "You do not own this file or it does not exist."}, status=403)

        # ✅ Validate team access
        user_team_ids = list(request.user.teams.values_list('id', flat=True))
        invalid_teams = [tid for tid in team_ids if tid not in user_team_ids]
        if invalid_teams:
            return Response({"error": f"You don't belong to these teams: {invalid_teams}"}, status=403)

        # ✅ STEP 2: Run the parser!
        
        parsed = parse_uploaded_content(uploaded_file_obj.file, password=password)

        cert_objs = parsed.get("certs",[])
        cert_models = []

        for i, cert in enumerate(cert_objs):
            cert_bytes = cert.public_bytes(encoding=settings.X509_ENCODING)
            uploaded_cert_file = create_uploaded_file(
                content=cert_bytes,
                user=request.user,
                suffix=".pem"
            )

            cert_model = create_certificate(
                cert_obj=cert,
                uploaded_file=uploaded_cert_file,
                teams=team_ids,
                user=request.user,
                name_override=name_override if i == 0 else None
            )

            cert_models.append(cert_model)

        # 🔗 Link certificate chain (leaf → root)
        link_certificates(cert_models)

        # 🔐 If key present, link it to the first (leaf) certificate
        if parsed.get("key"):
            create_private_key(
                key_obj=parsed["key"],
                user=request.user,
                teams=team_ids,
                linked_certificate=cert_models[0] if cert_models else None,
                original_name=parsed.get("original_filename")
            )

        return Response({
            "message": "Certificates and key saved successfully",
            "cert_count": len(cert_models),
            "has_key": bool(parsed.get("key")),
            "linked_to": cert_models[0].id if cert_models else None
        }, status=201)