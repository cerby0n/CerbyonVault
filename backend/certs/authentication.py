from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed,TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status


class CookieJWTAutentication(JWTAuthentication):
    """Custom JWT Authentication class that retrieves tokens from cookies.
    If the access token is expired, it attempts to refresh it using the refresh token.
    If both tokens are missing or invalid, it raises an AuthenticationFailed exception.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not access_token and not refresh_token:
            raise AuthenticationFailed("Authentication credentials not provided. Please log in.")

        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
            except AuthenticationFailed as e:

                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        new_access_token = str(refresh.access_token)
                        validated_token = self.get_validated_token(new_access_token)
                        response = Response({"message": "Access token refreshed successfully"}, status=status.HTTP_200_OK)
                        response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite="Strict")
                    except AuthenticationFailed:
                        raise AuthenticationFailed("Invalid refresh token. Please log in again.")
                else:
                    raise AuthenticationFailed("Access token expired and no refresh token provided. Please log in again.")

        try:
            user = self.get_user(validated_token)
            return user, validated_token
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f"Error retrieving user: {str(e)}")