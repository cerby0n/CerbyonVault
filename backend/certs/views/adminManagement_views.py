# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from certs.models import CustomUser, Team, InviteToken
from certs.serializers import AdminUserCreateSerializer, AdminUserUpdateSerializer, RegistrationSerializer, TeamDetailSerializer, TeamSerializer
from rest_framework import status, generics
from django.shortcuts import get_object_or_404

class CreateUserView(generics.CreateAPIView):
    """View for creating a new user by an admin.
    This view allows admins to create users with specific roles and permissions.
    It uses the AdminUserCreateSerializer to validate and save the user data. 
    Only authenticated admins can access this view.
    """
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserUpdateView(generics.UpdateAPIView):
    """View for updating an existing user by an admin.
    This view allows admins to update user details such as email, first name, last name, and roles.
    It uses the AdminUserUpdateSerializer to validate and save the updated user data.
    Only authenticated admins can access this view.
    """
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "pk"

class SendPasswordResetLinkView(APIView):
    """View for sending a password reset link to a user.
    This view generates a password reset link for a user identified by their primary key (pk).
    It uses Django's default token generator to create a secure token and sends an email with the reset link.
    Only authenticated admins can access this view.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        try:
            send_mail(
                subject="CerbyonVault - Set your password",
                message=f"Click to set your password: {link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"status": "sent"})
        except Exception as e:
            return Response({"status": "manual", "link": link, "error": str(e)})

class DeleteUserView(APIView):
    """View for deleting a user by an admin.
    This view allows admins to delete a user identified by their primary key (pk). 
    It retrieves the user object and deletes it from the database.
    If the user is not found, it returns a 404 error.
    Only authenticated admins can access this view.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateTeamView(generics.CreateAPIView):
    """View for creating a new team by an admin.
    This view allows admins to create teams with a name and members.
    It uses the TeamSerializer to validate and save the team data.
    Only authenticated admins can access this view.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class TeamUpdateMembersView(APIView):
    """View for updating team members by an admin.
    This view allows admins to update the members of an existing team identified by its primary key (
    pk).
    It retrieves the team object, updates its name and members based on the provided user IDs, 
    and saves the changes.
    Only authenticated admins can access this view. 
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        user_ids = request.data.get("user_ids", [])
        users = CustomUser.objects.filter(id__in=user_ids)
        team.name = request.data.get("name", team.name)
        team.members.set(users)
        team.save()
        return Response({"status": "updated"})

class DeleteTeamView(APIView):
    """View for deleting a team by an admin.
    This view allows admins to delete a team identified by its primary key (pk).
    It retrieves the team object and deletes it from the database.
    If the team is not found, it returns a 404 error.
    Only authenticated admins can access this view.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GenerateInviteView(APIView):
    """View for generating an invitation link for a new user.
    This view allows admins to create an invitation token for a user identified by their email.
    It generates a unique token and constructs a registration link that can be sent to the user.
    The link directs the user to a registration page where they can set their password. 
    Only authenticated admins can access this view.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get("email")
        token = InviteToken.objects.create(email=email)
        link = f"{settings.FRONTEND_URL}/register/{token.token}/"
        return Response({"link": link})
    
class RegisterFromInviteView(APIView):
    """View for registering a new user from an invitation link.
    This view allows users to register by providing a valid invitation token.   
    It retrieves the email associated with the token and uses the RegistrationSerializer to validate
    and save the new user data. If the token is valid and not used, the user
    can register successfully. If the token is invalid or expired, it returns an error message.
    """
    def get(self, request, token):
        try:
            invite = InviteToken.objects.get(token=token, is_used=False)
            return Response({"email": invite.email})
        except InviteToken.DoesNotExist:
            return Response({"detail": "Invalid or expired invitation."}, status=400)

    def post(self, request, token):
        serializer = RegistrationSerializer(data={**request.data, "token": token})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"detail": "User registered successfully."})
            except IntegrityError as e:
                if 'email' in str(e):
                    return Response(
                        {"detail": "A user with this email already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {"detail": "Registration failed due to a database error."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TeamDetailView(RetrieveAPIView):
    """View for retrieving details of a specific team.
    This view allows authenticated users to retrieve details of a team identified by its primary key (pk
    ). It uses the TeamDetailSerializer to serialize the team data.
    The view is accessible to all authenticated users, and it returns the team details including its members
    and associated users.
    """
    queryset = Team.objects.all()
    serializer_class = TeamDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"