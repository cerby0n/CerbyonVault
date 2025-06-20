from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import Certificate,Team
from django.shortcuts import get_object_or_404
from  ..serializers import CertificateUpdateSerializer
from certs.utils import user_can_access_certificate

class ManageCertificatesView(APIView):
    """View for managing a specific certificate.
    This view allows users to retrieve, update, or delete a certificate identified by its primary key
    (cert_id). It checks if the user has the necessary permissions to access or modify the certificate based on
    their team memberships.
    - GET: Retrieve the certificate details.
    - DELETE: Delete the certificate.
    - PATCH: Update the certificate with partial data.  
    If the user is not authorized to access or modify the certificate, it returns a 403
    Forbidden response.
    If the certificate is not found, it returns a 404 Not Found response.
    Only authenticated users can access this view.
    """
    def patch(self, request, cert_id):
        cert = get_object_or_404(Certificate, pk=cert_id)

        if not cert:
            return Response({"error": "No certficates selected"}, status=status.HTTP_400_BAD_REQUEST)

        if not user_can_access_certificate(cert, request.user):
            return Response({"error": "Not authorized to modify this certificate"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CertificateUpdateSerializer(cert, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
