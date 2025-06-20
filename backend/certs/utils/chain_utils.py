from typing import List, Dict
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from certs.models import Certificate
from certs.utils.certificate_hashing import hash_certificate
from cryptography.hazmat.primitives import serialization

"""def link_chain_by_hash(certificate: Certificate, chain_objs:List[Certificate])-> None:

    all_certs = [certificate] + chain_objs

    subject_to_hash: Dict[str, str] = {}
    for cert_obj in all_certs:
        # Load X.509 object from file on disk
        data = cert_obj.cert_file.open("rb").read()
        x509_obj = x509.load_pem_x509_certificate(data, default_backend())

        # Compute & persist hash if missing
        new_hash = hash_certificate(x509_obj)
        if cert_obj.cert_hash != new_hash:
            cert_obj.cert_hash = new_hash
            cert_obj.save(update_fields=["cert_hash"])

        subject_to_hash[cert_obj.subject] = new_hash

    # 3. Build hash→Certificate lookup
    hash_to_cert = {cert.cert_hash: cert for cert in all_certs}

    # 4. Clear any existing chain links
    for cert_obj in all_certs:
        cert_obj.chain.clear()

    # 5. Link each cert to its parent
    for cert_obj in all_certs:
        parent_hash = subject_to_hash.get(cert_obj.issuer)
        if parent_hash:
            parent = hash_to_cert.get(parent_hash)
            if parent and parent != cert_obj:
                cert_obj.chain.add(parent)"""

def get_parent_certificate(issuer_hash):
    """Retrieve the parent certificate based on the issuer hash.
    Args:
        issuer_hash (str): The hash of the issuer's subject.
    Returns:       
        Certificate: The parent certificate if found, otherwise None.
    """
    matching_parent = Certificate.objects.filter(subject_hash=issuer_hash).first()
    if matching_parent:
        return matching_parent
    return None

def get_children_item(subject_hash):
    """Retrieve the child certificates based on the subject hash.
    Args:
        subject_hash (str): The hash of the subject's distinguished name.
    Returns:
        List[Certificate]: A list of child certificates if found, otherwise None.
    """
    children = Certificate.objects.filter(issuer_hash=subject_hash, parent__isnull=True)
    if children:
        return children
    return None

def certificate_relationship(cert_type,certificate,issuer_hash,subject_hash):
    """Establish the parent-child relationship between certificates based on their hashes.
    Args:
        cert_type (str): The type of the certificate (e.g., "RootCA", "IntermediateCA", "EndEntity").
        certificate (Certificate): The certificate object to be processed.
        issuer_hash (str): The hash of the issuer's distinguished name.
        subject_hash (str): The hash of the subject's distinguished name.
    """

    if cert_type == "RootCA":
        certificate.parent = None
        certificate.save()
    else:
        parent_cert = get_parent_certificate(issuer_hash)

        if parent_cert:
                certificate.parent = parent_cert
                parent_cert.children.add(certificate)
                parent_cert.save()
        certificate.save()
    
    children = get_children_item(subject_hash)
    if children:
        for child in children:
            if child != certificate:
                child.parent = certificate
                child.save()
                certificate.children.add(child)
        certificate.save()