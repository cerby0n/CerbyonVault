from datetime import datetime

import pytz
from certs.models import Certificate, Team,Website
from certs.utils import (
    extract_common_name,
    hash_certificate,
    compute_issuer_hash,
    compute_subject_hash,
    classify_certificate
)
from cryptography import x509

def create_certificate(cert_obj: x509.Certificate, uploaded_file, teams, user, name_override=None,urls=None) -> Certificate:
    """Create a Certificate object from a cryptography x509.Certificate object.
    Args:
        cert_obj (x509.Certificate): The certificate object to create from.             
        uploaded_file (File): The file object containing the certificate.
        teams (list): List of Team objects to associate with the certificate.
        user (User): The user who uploaded the certificate.
        name_override (str, optional): Optional name to override the common name extraction.
    Returns:
        Certificate: The created Certificate object.
    """
    main_hash = hash_certificate(cert_obj)
    issuer_hash = compute_issuer_hash(cert_obj)
    subject_hash = compute_subject_hash(cert_obj)
    cert_type = classify_certificate(cert_obj)
    hex_serial = format(cert_obj.serial_number, 'x').upper()

    try:
        ext = cert_obj.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san = ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        san = []

    cert_name = name_override or extract_common_name(cert_obj.subject)

    certificate = Certificate.objects.create(
        name=cert_name,
        subject=cert_obj.subject.rfc4514_string(),
        issuer=cert_obj.issuer.rfc4514_string(),
        serial_number=hex_serial,
        not_before=cert_obj.not_valid_before_utc,
        not_after=cert_obj.not_valid_after_utc,
        is_expired=cert_obj.not_valid_after_utc < datetime.now(pytz.utc),
        signature_algorithm=cert_obj.signature_algorithm_oid._name,
        public_key_type=cert_obj.public_key().__class__.__name__,
        public_key_length=getattr(cert_obj.public_key(), 'key_size', None),
        san=san,
        file=uploaded_file,
        file_format="PEM",  # could be passed as param too
        original_filename=uploaded_file.file.name,
        cert_hash=main_hash,
        issuer_hash=issuer_hash,
        subject_hash=subject_hash,
        certificate_type=cert_type[:20],
        uploaded_by=user
    )

    for tid in teams:
        certificate.access_teams.add(tid)

    if urls:
        for url in urls:
            website = Website.objects.create(url=url, certificate=certificate)

    return certificate
