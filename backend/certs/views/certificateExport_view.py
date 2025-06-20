# views.py
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from cryptography.hazmat.primitives.serialization import Encoding, BestAvailableEncryption, load_pem_private_key, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates

from certs.models import Certificate,PrivateKey
from certs.utils.utils import load_certificate_from_bytes

def read_fieldfile_bytes(field_file):
    """
    Open the FileField, read all bytes, then close it.
    Returns the raw bytes so ASN.1 parsing will see the full certificate/key.
    """
    field_file.open('rb')
    data = field_file.read()
    field_file.close()
    return data


class CertificateExportView(APIView):
    permission_classes = [IsAuthenticated]
    """
    GET /api/certificates/<cert_id>/export/
      ?format={pem|crt|pfx}
      &chain={true|false}
      &key={true|false}
      &password=<pwd_for_pfx>
    """
    def get(self, request, cert_id):
        cert_obj     = get_object_or_404(Certificate, pk=cert_id)
        fmt          = request.query_params.get('fmt', 'pem').lower()
        include_chain= request.query_params.get('chain','false').lower() == 'true'
        include_key  = request.query_params.get('key','false').lower()   == 'true'
        pwd          = request.query_params.get('pwd','')

        # 1️⃣ Validate format/key combos
        if fmt not in {'pem','crt','pfx'}:
            return Response(
                {"detail": f"Unsupported format: {fmt}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if include_key and fmt == 'crt':
            return Response(
                {"detail": "Cannot include private key in CRT format; use PEM or PFX."},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        # 2️⃣ Build the cert chain (leaf → ... → root)
        seen = set()
        chain_objs = []
        node = cert_obj
        while node and node.id not in seen:
            chain_objs.append(node)
            seen.add(node.id)
            node = node.parent

        # if someone ever injected a loop (parent=self or a cycle) we stop here
        if include_chain:
            final_chain = chain_objs
        else:
            final_chain = chain_objs[:1]   # leaf only

        # 3️⃣ Load & serialize certificates
        enc = Encoding.PEM if fmt=='pem' else Encoding.DER
        cert_bytes = b''
        for c in final_chain:
            raw = read_fieldfile_bytes(c.file.file)
            x509 = load_certificate_from_bytes(raw)
            cert_bytes += x509.public_bytes(enc)

        # 4️⃣ Handle private key if requested
        key_bytes = b''
        if include_key:
            # fetch & decrypt the stored key file
            try:
                priv = cert_obj.private_key
            except PrivateKey.DoesNotExist:
                return Response(
                    {"detail": "No private key associated with this certificate."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raw_encrypted = read_fieldfile_bytes(priv.encrypted_key_file)
            raw_decrypted = settings.FERNET.decrypt(raw_encrypted)
            priv_key = load_pem_private_key(raw_decrypted, password=None)
            
            key_bytes = priv_key.private_bytes(
                encoding=Encoding.PEM,
                format=settings.KEY_FORMAT,            
                encryption_algorithm=settings.KEY_ENCRYPTION_ALGO
            )

        # 5️⃣ Build the response blob
        if fmt in {'pem','crt'} and not include_key:
            # cert(±chain) only
            data = cert_bytes
            mime = 'application/x-pem-file' if fmt=='pem' else 'application/pkix-cert'
            ext  = fmt

        elif fmt=='pem' and include_key:
            # PEM cert(+chain) + key in one .pem
            data = cert_bytes + b'\n' + key_bytes
            mime = 'application/x-pem-file'
            ext  = 'pem'

        elif fmt == 'pfx':
            # fmt=='pfx' and include_key==True
            # Note: serialize_key_and_certificates expects the leaf cert as `cert`,
            # and the rest of chain_objs[1:] as `cas`
            leaf = load_certificate_from_bytes(read_fieldfile_bytes(chain_objs[0].file.file))
            if include_chain:
                cas = [
                    load_certificate_from_bytes(read_fieldfile_bytes(c.file.file))
                    for c in chain_objs[1:]
                ]
            else:
                cas = None

            if pwd:
                enc_algo = BestAvailableEncryption(pwd.encode())
            else:
                enc_algo = NoEncryption()

            data = serialize_key_and_certificates(
                name=cert_obj.name.encode(),
                key=priv_key,
                cert=leaf,
                cas=cas,
                encryption_algorithm=enc_algo
            )
            mime = 'application/x-pkcs12'
            ext  = 'pfx'

        # 6️⃣ Return as a file download
        resp = HttpResponse(data, content_type=mime)
        resp['Content-Disposition'] = f'attachment; filename="{cert_obj.name}.{ext}"'
        return resp
    

class CertificateTestView(APIView):
    
    def get(self, request,cert_id):
        cert_obj = get_object_or_404(Certificate, pk=cert_id)

        #fmt = request.query_params.get('format')

        params = request.query_params.get("fmt")
        return Response(
            {params}
        )
    
    