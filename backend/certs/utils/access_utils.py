from certs.models import Certificate, PrivateKey
from django.db.models import Q

def user_can_access_certificate(cert, user):
    """
    Return True if the user can access this certificate (either it's public, or they're in an access team).
    """
    if cert.access_teams.count() == 0:
        return True
    return cert.access_teams.filter(members=user).exists()

def get_accessible_certificates(user):
    """
    Return a queryset of certificates the user can access.
    """
    user_teams = user.teams.all()
    return Certificate.objects.filter(
        Q(access_teams__in=user_teams) | Q(access_teams__isnull=True)
    ).distinct()

def user_can_access_key(key, user):
    """
    Return True if the user can access this key
    (either it's public, or they're in an access team).
    """
    if key.access_teams.count() == 0:
        return True
    return key.access_teams.filter(members=user).exists()

def get_accessible_keys(user):
    """
    Return a queryset of keys the user can access.
    """
    user_teams = user.teams.all()
    return PrivateKey.objects.filter(
        Q(access_teams__in=user_teams) | Q(access_teams__isnull=True)
    ).distinct()