from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Certificate
from django.shortcuts import get_object_or_404

class DeleteCertifiactesView(APIView):
    """View for deleting multiple certificates.
    This view allows users to delete certificates by providing their IDs in the request data.
    It checks if the user has the necessary permissions to delete each certificate based on their team memberships.
    If the user is not authorized to delete a certificate, it returns a 403 Forbidden response.
    If the certificates are successfully deleted, it returns a 204 No Content response. 
    If no certificates are found with the provided IDs, it returns a 404 Not Found response.
    """
    def delete(self,request):
        cert_ids = request.data.get('ids',[])

        if not cert_ids:
            return Response({"error": "No certificates selected"}, status=status.HTTP_400_BAD_REQUEST)
        
        certificates=Certificate.objects.filter(id__in=cert_ids)

        if certificates.exists():
            for cert in certificates:
                if cert.access_teams.exists():
                    if not cert.access_teams.filter(members=request.user).exists():
                        return Response({"error":f"Not Authorized to delete certificate {cert.name}"}, status=status.HTTP_403_FORBIDDEN)
            
            certificates.delete()
            return Response({"message":f"Certificates deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Certificates not found"}, status=status.HTTP_404_NOT_FOUND)