from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from certs.serializers import PrivateKeyDetailSerializer
from certs.models import (
    PrivateKey
)

class PrivateKeyListView(APIView):
    """View for listing all private keys accessible to the user.
    This view retrieves all private keys that the user can access based on their team memberships.
    It uses the `PrivateKeyDetailSerializer` to serialize the private keys.
    The response includes a serialized list of private keys.
    Only authenticated users can access this view.
    """
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user_teams = request.user.teams.all()
        privatekey = PrivateKey.objects.filter(
            Q(access_teams__in=user_teams) | Q(access_teams=None)
        ).distinct()
        serializer = PrivateKeyDetailSerializer(privatekey,many=True)
        return Response(serializer.data)
    
class PrivateKeyDetailView(APIView):
    """View for retrieving, updating, or deleting a specific private key.
    This view allows users to perform operations on a private key identified by its primary key (key
    id).
    It checks if the user has the necessary permissions to access or modify the private key based on their
    team memberships.   
    - GET: Retrieve the private key details.
    - DELETE: Delete the private key.
    - PATCH: Update the private key with partial data.
    If the user is not authorized to access or modify the private key, it returns a 403
    Forbidden response.
    If the private key is not found, it returns a 404 Not Found response.
    Only authenticated users can access this view.
    """
    permission_classes=[IsAuthenticated]
    def get(self, request, key_id):
        key = get_object_or_404(PrivateKey,pk=key_id)

        if not key.access_teams.filter(members=request.user).exists():
            return Response({"error": "Not authorized to view this Private Key"}, status=403)
        
        serializer = PrivateKeyDetailSerializer(key)
        return Response(serializer.data)
    
    def delete(self, request, key_id):
        kid = get_object_or_404(PrivateKey, pk= key_id)

        if not kid.access_teams.filter(members=request.user).exists():
            return Response({"error": "Not authorized to delete this Private Key"}, status=403)
        
        kid.delete()
        return Response ({"message" : f"Privat Key {key_id} deleted"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self,request,key_id):
        kid = get_object_or_404(PrivateKey,pk=key_id)

        serializer = PrivateKeyDetailSerializer(kid, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)