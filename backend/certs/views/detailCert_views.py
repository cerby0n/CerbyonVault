from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from certs.serializers import CertificateSerializer
from certs.models import (
    Certificate
)
from certs.utils import user_can_access_certificate,get_accessible_certificates

class CertificateListView(APIView):
    """View for listing all certificates accessible to the user.
    This view retrieves all certificates that the user can access based on their team memberships.
    It uses the `get_accessible_certificates` utility function to filter the certificates.
    The response includes a serialized list of certificates.
    Only authenticated users can access this view.
    """
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user_teams = request.user.teams.all()
        certs = get_accessible_certificates(request.user)
        serializer = CertificateSerializer(certs,many=True)
        return Response(serializer.data)
    
class CertificateDetailView(APIView):
    """View for retrieving, updating, or deleting a specific certificate.
    This view allows users to perform operations on a certificate identified by its primary key (cert_id).
    It checks if the user has the necessary permissions to access or modify the certificate based on their
    team memberships.
    - GET: Retrieve the certificate details.
    - DELETE: Delete the certificate.
    - PATCH: Update the certificate with partial data.
    If the user is not authorized to access or modify the certificate, it returns a 403
    Forbidden response.
    If the certificate is not found, it returns a 404 Not Found response.
    Only authenticated users can access this view.
    """
    permission_classes=[IsAuthenticated]
    def get(self,request,cert_id):
        cert = get_object_or_404(Certificate,pk=cert_id)

        if not user_can_access_certificate(cert, request.user):
            return Response({"error": "Not authorized to modify this certificate"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CertificateSerializer(cert)
        return Response(serializer.data)
    
    def delete(self,request,cert_id):
        cert = get_object_or_404(Certificate,pk=cert_id)

        if not user_can_access_certificate(cert, request.user):
            return Response({"error": "Not authorized to modify this certificate"}, status=status.HTTP_403_FORBIDDEN)
        
        cert.delete()
        return Response ({"message" : f"Certificate {cert_id} deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self,request,cert_id):
        cert = get_object_or_404(Certificate,pk=cert_id)
        serializer = CertificateSerializer(cert, data=request.data, partial=True)

        if not user_can_access_certificate(cert, request.user):
            return Response({"error": "Not authorized to modify this certificate"}, status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)