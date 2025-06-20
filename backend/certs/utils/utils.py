from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from django.conf import settings
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key

def load_certificate_from_bytes(data: bytes) -> x509.Certificate:
    """
    Tries to load a certificate from bytes. Supports both PEM and DER formats.
    """
    try:
        return x509.load_pem_x509_certificate(data, default_backend())
    except ValueError:
        return x509.load_der_x509_certificate(data, default_backend())
    
def _load_and_decrypt_key(encrypted_data: bytes) -> object:
    """
    Decrypts with your FERNET, then loads a private key object.
    """
    raw = settings.FERNET.decrypt(encrypted_data)

    try:
        # PEM first
        return load_pem_private_key(raw, password=None)
    except ValueError:
        # fall back to DER
        return load_der_private_key(raw, password=None)

    
def extract_common_name(subject):
    """Extracts the common name (CN) from a certificate subject.
    If no common name is found, returns a default value.
    Args:
        subject (x509.Name): The subject of the certificate.
    Returns:
        str: The common name or a default value if not found.
    """
    try:
        return subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    except IndexError:
        return "Unnamed Cert"
    
def walk_certificate_chain(cert_obj, visited=None):
    """
    Recursively walks the .chain of a certificate and returns the full list in order.
    """
    if visited is None:
        visited = set()
    
    chain = []

    for next_cert in cert_obj.chain.all():
        if next_cert.id in visited:
            continue  # avoid circular loops
        visited.add(next_cert.id)
        chain.append(next_cert)
        chain.extend(walk_certificate_chain(next_cert, visited))

    return chain

def build_cert_chain_tree(cert_obj, visited=None):
    """
    Recursively builds a tree-like dictionary of the certificate's trust chain.
    """
    if visited is None:
        visited = set()
    if cert_obj.id in visited:
        return None  # prevent loops
    visited.add(cert_obj.id)

    return {
        "id": cert_obj.id,
        "subject": cert_obj.subject,
        "issuer": cert_obj.issuer,
        "chain": [
            build_cert_chain_tree(child, visited)
            for child in cert_obj.chain.all()
            if child.id not in visited
        ]
    }