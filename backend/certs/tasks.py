from celery import shared_task
from django.utils import timezone
from .models import Certificate

@shared_task
def check_and_update_expired_certificates():
    """Check for expired certificates and mark them as expired if necessary."""
    """This task checks all certificates and marks them as expired if their not_after date is in the past."""
    now = timezone.now()
    # Find certificates that are not marked as expired but should be
    expired_certs = Certificate.objects.filter(not_after__lt=now, is_expired=False)
    count = expired_certs.update(is_expired=True)
    return f"Marked {count} certificates as expired."