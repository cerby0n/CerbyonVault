from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import PrivateKey
from django.shortcuts import get_object_or_404

class DeleteKeysView(APIView):
    """View for deleting multiple private keys.
    This view allows users to delete private keys by providing their IDs in the request data.
    It checks if the user has the necessary permissions to delete each key based on their team memberships.
    If the user is not authorized to delete a key, it returns a 403 Forbidden response
    If the keys are successfully deleted, it returns a 204 No Content response.
    If no keys are found with the provided IDs, it returns a 404 Not Found response
    """
    def delete(self,request):
        keys_ids = request.data.get('ids',[])

        if not keys_ids:
            return Response({"error": "No key selected"}, status=status.HTTP_400_BAD_REQUEST)
        
        private_keys=PrivateKey.objects.filter(id__in=keys_ids)

        if private_keys.exists():
            for key in private_keys:
                if key.access_teams.exists():
                    if not key.access_teams.filter(members=request.user).exists():
                        return Response({"error":f"Not Authorized to delete certificate {key.name}"}, status=status.HTTP_403_FORBIDDEN)
        
            private_keys.delete()
            return Response({"message":f"Key deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Key not found"}, status=status.HTTP_404_NOT_FOUND)