from datetime import timedelta
import uuid
from urllib.parse import urlparse
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .managers import CustomUserManager
from django.utils import timezone

def default_invite_expiry():
    return timezone.now() + timedelta(days=7)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=150, blank=True, null=True, unique=False)

    objects=CustomUserManager()

    def __str__(self):
        return self.email

class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(CustomUser, related_name='teams',blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_company_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"

class Certificate(models.Model):
    name = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)
    subject = models.TextField()
    issuer = models.TextField()
    serial_number = models.CharField(max_length=255)
    not_before = models.DateTimeField()
    not_after = models.DateTimeField()
    is_expired = models.BooleanField(default=False)
    public_key_type = models.CharField(max_length=255, null=True, blank=True)
    public_key_length = models.IntegerField(null=True, blank=True)
    signature_algorithm = models.CharField(max_length=255)
    san = models.JSONField(default=list)
    file = models.ForeignKey('UploadedFile', on_delete=models.CASCADE, null=True, blank=True)
    file_format = models.CharField(max_length=20,default='PEM')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='p_certificate')
    children = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="c_certificate")
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    access_teams = models.ManyToManyField(Team, related_name='certificates', blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True,blank=True)
    cert_hash = models.CharField(max_length=255,unique=True,blank=True,null=True)
    issuer_hash = models.CharField(max_length=255, null=True, blank=True)
    subject_hash = models.CharField(max_length=255, null=True, blank=True)
    certificate_type=models.CharField(
        max_length=20,
        choices=[
            ('RootCA','Root CA'),
            ('IntermediateCA','Intermediate CA'),
            ('Leaf', 'Leaf Certificate'),
        ],
        null=True,
        blank=True
    )
    @property
    def has_private_key(self):
        return getattr(self, 'private_key', None) is not None
    
    def __str__(self):
        return f"{self.name} ({self.subject})"
    
class PrivateKey(models.Model):
    name = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)
    encrypted_key_file = models.FileField(upload_to='keys/')
    created_at = models.DateTimeField(auto_now_add=True)
    certificate = models.OneToOneField('Certificate', on_delete=models.CASCADE, related_name='private_key', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    keysize = models.CharField(max_length=20,default=None, null=True,blank=True)
    file_format = models.CharField(max_length=20,default='PEM')
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    access_teams = models.ManyToManyField(Team, related_name='private_key',blank=True)
    key_hash = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
class UploadedFile(models.Model):
    file = models.FileField(upload_to='certificates/',null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.file.name} by {self.uploaded_by.email}"
    
class Website(models.Model):
    url = models.URLField(max_length=200)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE,related_name="websites",blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.url:
            parsed_url = urlparse(self.url)
            self.domain = parsed_url.netloc
            if self.domain.startswith("www."):
                self.domain = self.domain[4:] 
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.url
    
class InviteToken(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=default_invite_expiry)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return self.expires_at < timezone.now()

    def __str__(self):
        return f"{self.email} - {'used' if self.is_used else 'active'}"

@receiver(post_delete, sender=Certificate)
def delete_cert_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete()


@receiver(post_delete, sender=PrivateKey)
def delete_key_file(sender, instance, **kwargs):
    if instance.encrypted_key_file:
        instance.encrypted_key_file.delete(save=False)


@receiver(post_delete, sender=UploadedFile)
def delete_file_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)