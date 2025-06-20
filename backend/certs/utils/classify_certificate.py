from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID

def classify_certificate(cert_data):
    """
    Classify the certificate as a Root CA, Intermediate CA, or Leaf Certificate.

    Args:
    - cert_data: The certificate data (PEM bytes or parsed cert object).

    Returns:
    - A string indicating whether the certificate is a 'Root CA', 'Intermediate CA', or 'Leaf Certificate'.
    """
    try:
        # If we have a parsed certificate (as object), use it
        if isinstance(cert_data, x509.Certificate):
            cert = cert_data
        else:
            # Otherwise, if we have raw PEM data, load it as a certificate
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        
        # Check the Basic Constraints to see if it's a CA
        try:
            basic_constraints = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
            is_ca = basic_constraints.value.ca
        except x509.ExtensionNotFound:
            return 'Leaf'  # No basic constraints means it's a leaf cert

        # If the certificate is self-signed, it's a Root CA
        if cert.subject == cert.issuer:
            if is_ca:
                return 'RootCA'
            else:
                return 'Leaf'

        # If it's a CA cert, it's an Intermediate CA
        if is_ca:
            return 'IntermediateCA'

        # Otherwise, it's a Leaf cert
        return 'Leaf'

    except Exception as e:
        return f"Error: {str(e)}"