import traceback
from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12, load_pem_private_key,load_der_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
import base64
import re

def detect_file_format(uploaded_file): 
    """Detect the format of the uploaded file based on its extension.
    Args:
        uploaded_file (UploadedFile): The uploaded file object.
    Returns:
        str: The format of the file (e.g., "PKCS12", "PEM", "CRT", "KEY", or "UNKNOWN").
    """
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
    """Split PEM data into its individual sections.
    Args:
        pem_data (bytes): The PEM data to split.
    Returns:
        list: A list of PEM blocks found in the data.
    """
    pattern = re.compile(r'(-----BEGIN [^-]+-----.*?-----END [^-]+-----)', re.DOTALL)
    blocks = pattern.findall(pem_data.decode())
    return blocks

def parse_uploaded_content(file, password=None):
    """Parse an uploaded file to extract certificate, key, and chain information.
    Args:
        file (UploadedFile): The uploaded file object.
        password (str, optional): Password for encrypted files (if applicable).
    Returns:
        dict: A dictionary containing the parsed certificate, key, chain, format, original filename, error messages, and password requirement status.
    """
    result = {
        "certs": [],
        "key": None,
        "format": detect_file_format(file),
        "original_filename": file.name,
        "error": None,
        "password_required": False
    }

    content = file.read()
    primary_cert = None
    chain = []

    try:
        if result["format"] == "PEM":
            blocks = split_pem_sections(content)
            for i, block in enumerate(blocks):
                print(f"\n🔎 Block #{i+1} PREVIEW:\n{block[:60]}...")
                if "PRIVATE KEY" in block and not result["key"]:
                    try:
                        result["key"] = load_pem_private_key(
                            block.encode(),
                            password=password.encode() if password else None,
                            backend=default_backend()
                        )
                    except Exception:
                        continue  # Not a key
                elif "CERTIFICATE" in block:
                    try:
                        cert = x509.load_pem_x509_certificate(block.encode(), backend=default_backend())
                        if not primary_cert:
                            primary_cert = cert
                        else:
                            chain.append(cert)
                    except Exception:
                        continue

        elif result["format"] == "PKCS12":
            try:
                key, cert, additional_certs = pkcs12.load_key_and_certificates(
                    content, password.encode() if password else None, backend=default_backend()
                )
                result["key"] = key
                if cert:
                    primary_cert = cert
                if additional_certs:
                    chain.extend(additional_certs)
            except ValueError as e:
                error_message = str(e).lower()
                if "invalid password" in error_message or "mac verify failure" in error_message:
                    result["error"] = "Password required or incorrect"
                    result["password_required"] = True
                else:
                    result["error"] = f"PKCS12 parse failed: {str(e)}"

        elif result["format"] == "CRT":
            try:
                primary_cert = load_pem_x509_certificate(content, backend=default_backend())
            except ValueError:
                primary_cert = load_der_x509_certificate(content, backend=default_backend())

        elif result["format"] == "KEY":
            try:
                result["key"] = load_pem_private_key(content, password=None, backend=default_backend())
            except ValueError:
                result["key"] = load_der_private_key(content, password=None, backend=default_backend())

    except Exception as e:
        result["error"] = f"Unhandled parse error: {str(e)}"
    # Final certs cleanup
    if primary_cert:
        result["certs"].append(primary_cert)
    result["certs"].extend(chain)

    return result