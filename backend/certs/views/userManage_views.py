from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from certs.models import CustomUser, Team
from certs.serializers import TeamSerializer, UserSerializer,MyTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


class TeamListView(generics.ListAPIView):
    """View for listing all teams.
    This view retrieves all teams from the database and serializes them using the TeamSerializer.   
    The response includes a serialized list of teams.
    Only authenticated admins can access this view.
    """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
class UserListView(generics.ListAPIView):
    """View for listing all users.
    This view retrieves all users from the database and serializes them using the UserSerializer.
    The response includes a serialized list of users.
    Only authenticated admins can access this view.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
class UserInfoView(RetrieveUpdateAPIView):
    """View for retrieving and updating the authenticated user's information.
    This view allows the user to retrieve their own information and update it using the UserSerializer. 
    The user must be authenticated to access this view.
    The response includes the user's serialized data.   
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class MyTokenObtainPairView(TokenObtainPairView):

    serializer_class=MyTokenObtainPairSerializer

        
