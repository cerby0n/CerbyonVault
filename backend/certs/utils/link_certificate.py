from .chain_utils import certificate_relationship


def link_certificates(certificates):
    """
    Given a list of Certificate model instances,
    link them based on subject/issuer hash.
    """
    cert_by_subject = {cert.subject_hash: cert for cert in certificates}

    for cert in certificates:
        if cert.issuer_hash and cert.issuer_hash in cert_by_subject:
            parent_cert = cert_by_subject[cert.issuer_hash]
            certificate_relationship(
                cert_type=cert.certificate_type,
                certificate=cert,
                issuer_hash=cert.issuer_hash,
                subject_hash=cert.subject_hash
            )
            print(f"🔗 Linked {cert.name} → {parent_cert.name}")
        else:
            print(f"🔗 No parent found for {cert.name}")
