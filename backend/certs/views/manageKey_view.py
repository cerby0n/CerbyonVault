from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import PrivateKey
from django.shortcuts import get_object_or_404
from  ..serializers import PrivateKeyUpdateSerializer

class ManageKeyView(APIView):

    """View for managing a specific private key.
    This view allows users to retrieve, update, or delete a private key identified by its primary
    key ID. It checks if the user has the necessary permissions to access or modify the private key based on
    their team memberships.
    - GET: Retrieve the private key details.
    - DELETE: Delete the private key.
    - PATCH: Update the private key with partial data.
    If the user is not authorized to access or modify the private key, it returns a
    403 Forbidden response.
    If the private key is not found, it returns a 404 Not Found response.   
    Only authenticated users can access this view.
    """
    def patch(self, request, key_id):
        private_key = get_object_or_404(PrivateKey, pk=key_id)

        if not private_key:
            return Response({"error": "No key selected"}, status=status.HTTP_400_BAD_REQUEST)

        if private_key.access_teams.exists():
            if not private_key.access_teams.filter(members=request.user).exists():
                return Response({"error": "Not authorized to modify this key"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrivateKeyUpdateSerializer(private_key, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
