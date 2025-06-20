from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key
from cryptography.hazmat.backends import default_backend
import re

def detect_file_format(uploaded_file):
    """Detect the format of the uploaded file based on its extension."""
    ext = uploaded_file.name.lower().split('.')[-1]
    if ext in ['p12', 'pfx']:
        return "PKCS12"
    elif ext in ['pem']:
        return "PEM"
    elif ext in ['crt', 'cer']:
        return "CRT"
    elif ext in ['key']:
        return "KEY"
    else:
        return "UNKNOWN"
    
def split_pem_sections(pem_data):
    """Split PEM data into its individual sections."""
    pattern = re.compile(r'(-----BEGIN [^-]+-----.*?-----END [^-]+-----)', re.DOTALL)
    blocks = pattern.findall(pem_data.decode())
    return blocks

def parse_uploaded_file(file, password=None):
    """Parse an uploaded file to extract certificate, key, and chain information.
    Args:
        file (UploadedFile): The uploaded file object.
        password (str, optional): Password for encrypted files (if applicable).
    Returns:
        dict: A dictionary containing the parsed certificate, key, chain, format, original filename, and any error messages.
    """
    result = {
        "cert": None,
        "key": None,
        "chain": [],
        "format": detect_file_format(file),
        "original_filename": file.name,
        "error": None
    }

    content = file.read()

    if result["format"] == "PEM":
        blocks = split_pem_sections(content)
        for block in blocks:
            if "PRIVATE KEY" in block and not result["key"]:
                result["key"] = load_pem_private_key(block.encode(), password=None, backend=default_backend())
            elif "CERTIFICATE" in block:
                cert = x509.load_pem_x509_certificate(block.encode(), backend=default_backend())
                if not result["cert"]:
                    result["cert"] = cert
                else:
                    result["chain"].append(cert)

    elif result["format"] == "PKCS12":
        try:
            key, cert, additional_certs = pkcs12.load_key_and_certificates(content, password.encode() if password else None)
            result.update({"cert": cert, "key": key, "chain": additional_certs or []})
        except Exception as e:
            result["error"] = f"PKCS12 parse failed: {str(e)}"

    elif result["format"] == "CRT":
        try:
        # Try PEM first
            result["cert"] = load_pem_x509_certificate(content, backend=default_backend())
        except ValueError:
        # If PEM fails, try DER
            result["cert"] = load_der_x509_certificate(content, backend=default_backend())
    elif result["format"] =="KEY":
        try:
            result["key"] = load_pem_private_key(content, password=None, backend=default_backend())
        except ValueError:
            result["key"] = load_der_private_key(content, password=None, backend=default_backend())

    return result