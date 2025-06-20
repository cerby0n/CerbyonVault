from django.conf import settings
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from certs.models import Certificate, PrivateKey, UploadedFile, Team
from certs.utils import (
    create_uploaded_file,
    create_certificate, create_private_key,certificate_relationship
)
import uuid
from django.core.files.base import ContentFile




class ImportCertMetadataView(APIView):
    """View for importing certificate metadata from a session.
    This view allows users to import certificates and private keys that were previously uploaded    
    and stored in the session. It processes the session data, creates certificate and key models,
    and handles any necessary relationships between them.   
    The view expects a session key and the certificate and key data in the request body.
    If the session data is valid, it creates the corresponding models and cleans up the session.    
    If any errors occur during the import process, it returns appropriate error messages.
    """
    permission_classes = [IsAuthenticated]

    def post(self,request):
        session_key = request.data.get("session_key")
        certs_data = request.data.get("certs",[])
        key_data = request.data.get("key")
        print("🛬 Received session_key:", session_key)
        session_data = request.session.get(session_key)
        print("📦 Session data found?", session_data is not None)


        print("Received session_key:", session_key)
        print("Certs from session:", list(session_data["certs"].keys()))
        print("Key from session:", list(session_data["key"].keys()))
        if not session_data:
            return Response({"error": "Invalid or expired session."}, status=400)
        
        cert_models = {}
        for cert_input in certs_data:
            temp_id = cert_input["temp_id"]
            name = cert_input["name"]
            teams = cert_input["teams"]
            urls=cert_input["urls"]

            pem_data = session_data["certs"].get(temp_id)
            if not pem_data:
                continue

            cert_obj = x509.load_pem_x509_certificate(pem_data.encode("utf-8"))
            cert_bytes = cert_obj.public_bytes(encoding=settings.X509_ENCODING)
            uploaded_file = create_uploaded_file(cert_bytes, request.user)
            try:
                cert_model = create_certificate(
                    cert_obj=cert_obj,
                    uploaded_file=uploaded_file,
                    teams=teams,
                    user=request.user,
                    name_override=name,
                    urls=urls

                )
            except IntegrityError:
                return Response(
                    {"error": "This certificate already exist."},status=status.HTTP_400_BAD_REQUEST
                )
            cert_models[temp_id] = cert_model
        for temp_id, cert_model in cert_models.items():
            
                certificate_relationship(
                cert_type=cert_model.certificate_type,
                certificate=cert_model,
                issuer_hash=cert_model.issuer_hash,
                subject_hash=cert_model.subject_hash
            )
            
        if key_data:
            key_pem = session_data["key"].get(key_data["temp_id"])
            key_name = key_data["filename"]
            if key_pem:
                key_obj = serialization.load_pem_private_key(
                    key_pem.encode("utf-8"),
                    password=None
                )
                
                linked_cert_temp_id = key_data.get("linked_cert_temp_id")
                if linked_cert_temp_id:
                    linked_cert = cert_models.get(linked_cert_temp_id)
                else:
                    linked_cert = None
                
                try:
                    create_private_key(
                        key_obj=key_obj,
                        user=request.user,
                        teams=key_data["teams"],
                        linked_certificate=linked_cert,
                        bit_length=key_data["bit_length"],
                        original_name=linked_cert.name if linked_cert else key_name
                    )
                except IntegrityError:
                    return Response(
                        {"error": "This Key already exist."},status=status.HTTP_400_BAD_REQUEST
                    )
                

        # ✅ Clean up session
        del request.session[session_key]
        request.session.modified = True

        return Response({
            "message": "Certificates and key imported successfully.",
            "imported_count": len(cert_models)
        }, status=status.HTTP_201_CREATED)