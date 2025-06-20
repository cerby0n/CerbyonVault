from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
import hashlib

def hash_certificate(cert: x509.Certificate) -> str:
    """
    Return the SHA-256 hash (hex) of the certificate in DER format.
    """
    der_bytes = cert.public_bytes(serialization.Encoding.DER)
    return hashlib.sha256(der_bytes).hexdigest()


def compute_issuer_hash(cert):
    """
    Return the SHA-256 hash (hex) of the certificate issuer's distinguished name.
    """
    issuer = cert.issuer.rfc4514_string()
    issuer_hash = hashlib.sha256(issuer.encode()).hexdigest()
    return issuer_hash

def compute_subject_hash(cert):
    """
    Return the SHA-256 hash (hex) of the certificate subject's distinguished name.
    """
    subject = cert.subject.rfc4514_string()
    subject_hash = hashlib.sha256(subject.encode()).hexdigest()
    return subject_hash

def calculate_key_hash(private_key):
    """
    Return the SHA-256 hash (hex) of the private key in DER format.
    """
    key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(key_bytes)
    return digest.finalize().hex()