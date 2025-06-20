from certs.models import PrivateKey, UploadedFile
from django.core.files.base import ContentFile
import uuid
from cryptography.hazmat.primitives import serialization
from django.conf import settings
import os
from .certificate_hashing import calculate_key_hash

def create_private_key(key_obj, bit_length ,user, teams, linked_certificate=None, original_name=None, file_format="PEM") -> PrivateKey:
    """Create a PrivateKey object from a cryptography key object.
    Args:
        key_obj (cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivate
        bit_length (int): The bit length of the key.
        user (User): The user who uploaded the key. 
        teams (list): List of Team objects to associate with the key.
        linked_certificate (Certificate, optional): The certificate to link with the key.
        original_name (str, optional): Optional name to override the original filename. 
        file_format (str, optional): The format of the key file (default is "PEM").
    Returns:
        PrivateKey: The created PrivateKey object.  
    """
    # 🔐 Encrypt the key bytes
    encrypted = settings.FERNET.encrypt(
        key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()  # We encrypt later using Fernet
        )
    )

    # 📦 Save as uploaded file
    filename = f"{uuid.uuid4()}_key.enc"
    file_content = ContentFile(encrypted)
    
    key_hash = calculate_key_hash(key_obj)

    # ✅ Create PrivateKey model and save encrypted file
    private_key = PrivateKey.objects.create(
        name=original_name or "Private Key",
        certificate=linked_certificate,
        uploaded_by=user,
        file_format=file_format,
        original_filename=original_name or "key",
        keysize=bit_length,
        key_hash = key_hash,
    )
    private_key.encrypted_key_file.save(filename, file_content)  # Will go to `keys/` folder

    for tid in teams:
        private_key.access_teams.add(tid)

    return private_key
