from django.contrib.auth.models import BaseUserManager

class CustomUserManager (BaseUserManager):
    """Custom user manager for handling user creation and management.
    This manager is used to create user and superuser instances with email as the unique identifier.
    It ensures that email is normalized and required for user creation. 
    It also provides methods to create regular users and superusers with appropriate permissions.
    """
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
    
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)
    