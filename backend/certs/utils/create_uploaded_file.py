from django.core.files.base import ContentFile
from certs.models import UploadedFile
import uuid

def create_uploaded_file(content: bytes, user, suffix=".pem") -> UploadedFile:
    """Create an UploadedFile object with the given content and user.
    Args:
        content (bytes): The content of the file to be uploaded.
        user (User): The user who is uploading the file.
        suffix (str, optional): The file extension to use. Defaults to ".pem".  
    Returns:
        UploadedFile: The created UploadedFile object.
    """
    filename = f"{uuid.uuid4()}{suffix}"
    uploaded_file = UploadedFile.objects.create(uploaded_by=user)
    uploaded_file.file.save(filename, ContentFile(content))
    return uploaded_file