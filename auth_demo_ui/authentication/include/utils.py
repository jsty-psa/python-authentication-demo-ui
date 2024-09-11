from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

import hashlib, binascii

def print_hex_binary(data):
    data = data.encode("utf-8")
    hasher = hashlib.sha256()
    hasher.update(data)
    hasher = hasher.digest()
    
    return binascii.hexlify(hasher).upper().decode('ascii')

def get_current_time():
    t = datetime.now(timezone.utc)
    t = t.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    return t

def get_thumbprint(fname):
    with open(fname, "rb") as cert_file:
        cert_data = cert_file.read()
        
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    thumbprint = cert.fingerprint(hashes.SHA256())
    
    return thumbprint.hex()