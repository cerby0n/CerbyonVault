from cryptography import x509
from datetime import datetime, timezone

def get_certificate_info(cert: x509.Certificate) -> dict:
    """
    Parses X.509 certificate and returns metadata in dictionary format.
    """
    info = {}

    info["subject"] = cert.subject.rfc4514_string()
    info["issuer"] = cert.issuer.rfc4514_string()
    info["serial_number"] = cert.serial_number
    info["version"] = cert.version.name
    info["not_before"] = cert.not_valid_before_utc.isoformat()
    info["not_after"] = cert.not_valid_after_utc.isoformat()
    info["is_expired"] = datetime.now(timezone.utc) > cert.not_valid_after_utc
    info["signature_algorithm"] = cert.signature_algorithm_oid._name

    # Public key info
    public_key = cert.public_key()
    if hasattr(public_key, "key_size"):
        key_type = public_key.__class__.__name__
        key_length = public_key.key_size
    elif hasattr(public_key, "curve"):
        key_type = f"EC ({public_key.curve.name})"
        key_length = None
    else:
        key_type = public_key.__class__.__name__
        key_length = None

    info["public_key_type"] = key_type
    info["public_key_length"] = key_length

    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        info["san"] = ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        info["san"] = []

    return info