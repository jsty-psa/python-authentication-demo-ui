from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from django_keygen import KeyGen
from django.shortcuts import redirect
from authlib.jose import JsonWebSignature

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA as RSA_key
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

from cryptography import x509
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding as cpadding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import os, json, base64, rsa, hashlib, requests, binascii, secrets, warnings

warnings.filterwarnings("ignore")

# Create your views here.
def requestOTP(request, pcn):
    os.system('clear')
    datetime_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    base_url = os.environ.get('BASE_URL')
    misp_license_key = os.environ.get('TSP_LICENSE_KEY')
    partner_id = os.environ.get('PARTNER_ID')
    partner_api_key = os.environ.get('API_KEY')
    env = os.environ.get('ENV')
    version = os.environ.get('VERSION')
    # transaction_id = get_random_string(length=32, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    transaction_id = get_random_string(length=10, allowed_chars='0123456789')
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem'
    otp_url = f'{base_url}/idauthentication/v1/otp/{misp_license_key}/{partner_id}/{partner_api_key}'
    
    otp_request = {}
    otp_request_header = {}
    otp_request['id'] = 'philsys.identity.otp'
    otp_request['version'] = version
    otp_request['transactionID'] = transaction_id
    otp_request['requestTime'] = getCurrentTime()
    otp_request['individualId'] = str(pcn)
    otp_request['individualIdType'] = "VID"
    otp_request['otpChannel'] = ['email']
    
    otp_request_header['signature'] = create_signature(json.dumps(otp_request), partner_private_key_location)
    otp_request_header['Authorization'] = getAuthorization()
    otp_request_header['Content-type'] = "application/json"
    
    print(f'OTP Request Header:\n{str(json.dumps(otp_request_header))}\n')
    print(f'OTP Request URL:\n{otp_url}\n')
    
    response = requests.post(otp_url, data=json.dumps(otp_request), headers=otp_request_header, verify=False)
    
    print(f'OTP Response:\n{str(response.json())}\n')
    
    if not response.json()["errors"]:
    
        result = {}
        partner_id = os.environ.get('PARTNER_ID')
        
        partner_private_key = open(f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem').read()
        partner_private_key_bytes = bytes(partner_private_key, "utf-8")
        
        response_session_key_encrypted = base64URLDecode(response.json()["responseSessionKey"])
        response_encrypted = base64URLDecode(response.json()["response"])
        result["response_session_key"] = asymmetric_decrypt(response_session_key_encrypted, partner_private_key_bytes)
        result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
                
        print(f"response_session_key_encrypted: {response_session_key_encrypted}")
        print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}")
        print(f"response_encrypted: {response_encrypted}")
        print(f"response_encrypted length: {len(response_encrypted)}")
        print(f"response_session_key: {result['response_session_key']}")
        print(f"response_session_key length: {len(result['response_session_key'])}")
        print(f"response: {result['response']}\n")

        return JsonResponse(result['response'])
    
    response = json.loads(str(response.json()).replace('[', '').replace(']', '').replace('\'', '"').replace('None', '"None"'))
    return JsonResponse(response)

def requestOTPTest(request):
    
    result = {}
    partner_id = os.environ.get('PARTNER_ID')
    
    partner_private_key = open(f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem').read()
    partner_private_key_bytes = bytes(partner_private_key, "utf-8")

    # Test Data
    response= {}
    response["response"] = "bhebzY_1rdCPVc5dXCW7pxmn4BecC21VPTnGocbY2YKfhXWBXQQKQkhg5cZTLkxD0g29pop_7clU7u7i3rCT2YJD5M0ihTkWcfZtePZwmFCXwPv0WgqU9POCTCLzWfhJkkLXCD8vYHXPh8gG3D-58wrL_04KwvCIbFjCnGvBLe_IvzPV5BY"
    response["responseSessionKey"] = "Qu2AQEl4XPYBmJGKDkmPfBUmZkxOxCNnix0U3eqvBS0JzeZFDoRXnD1br76yEN6RCIq2WrkCtiIAvBXZYj1W1LpQb4j4JTKcrD-A3bMU7AXcHELauVZ6le-iz8mS-CsqoWL_-iXiVQaOjER9eJRfAyoPQb7EqQMkBsh_bLmrl6m-cS8ZSxyFA2zqnVUEoNXchihnBhmDQqjERwu2LZF1Hk_CGseO-H3kl-ROJsPNtdlaiOHa9dKuDYfts3pTd2W5RbNObIszKZ1Fvu9A3MF0vKOPhTh6y_BjAOrNGh7SRB_loSNovO4UMHzWtmazGPy3SQ-CEW-NiezRAjTZtCYZzg"
    response_session_key_encrypted = base64URLDecode(response["responseSessionKey"])
    response_encrypted = base64URLDecode(response['response'])
    
    result["response_session_key"] = asymmetric_decrypt(response_session_key_encrypted, partner_private_key_bytes)
    
    print(f"Session Key:\n{result['response_session_key']}\n")
    print(f"Session Key Length:\n{len(result['response_session_key'])}\n")
    
    result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
    
    print(f"response_session_key_encrypted: {response_session_key_encrypted}")
    print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}")
    print(f"response_encrypted: {response_encrypted}")
    print(f"response_encrypted length: {len(response_encrypted)}")
    print(f"response_session_key: {result['response_session_key']}")
    print(f"response_session_key length: {len(result['response_session_key'])}")
    print(f"response: {result['response']}\n")

    return JsonResponse(result['response'])
    
    
def test(request):
    return render(request, 'authenticate.html')

def authenticate(request):
    os.system('clear')
    http_request_body = {}
    http_request_header = {}
    http_request_body['requestedAuth'] = {}
    http_request_body['request'] = {}
    http_request_body_request = {}

    transaction_id = get_random_string(length=10, allowed_chars='0123456789')
    value = request.GET.dict()
    
    partner_id = os.environ.get('PARTNER_ID')
    IDA_certificate_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-IDAcertificate.cer'
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem'
    base_url = os.environ.get('BASE_URL')
    version = os.environ.get('VERSION')
    auth_url = base_url + '/idauthentication/v1/' + ('kyc/' if value['input_ekyc'] == 'on' else 'auth/') + os.environ.get('TSP_LICENSE_KEY') + '/' + os.environ.get('PARTNER_ID') + '/' + os.environ.get('API_KEY')
    
    datetime_now = getCurrentTime()
    
    value['input_ekyc'] = "on"
    
    http_request_body['id'] = 'philsys.identity.kyc' if value['input_ekyc'] == 'on' else 'philsys.identity.auth'
    http_request_body['version'] = version
    http_request_body['requestTime'] = datetime_now
    http_request_body['env'] = os.environ.get('ENV')
    http_request_body['domainUri'] = base_url
    http_request_body['transactionID'] = transaction_id
    http_request_body['requestedAuth']['otp'] = value['input_otp'] == 'on'
    http_request_body['requestedAuth']['demo'] = value['input_demo'] == 'on'
    http_request_body['requestedAuth']['bio'] = value['input_bio'] == 'on'
    http_request_body['consentObtained'] = True
    http_request_body['individualId'] = value['individual_id']
    http_request_body['individualIdType'] = value['individual_id_type']
    
    http_request_body_request['timestamp'] = datetime_now
    http_request_body_request['otp'] = None
    http_request_body_request['demographics'] = None
    http_request_body_request['biometrics'] = None
    
    if(value['input_otp'] == 'on'):
        http_request_body_request['otp'] = value['input_otp_value']
    if(value['input_demo'] == 'on'):
        http_request_body_request['demographics'] = json.loads(value['input_demo_value'])
    if(value['input_bio'] == 'on'):
        http_request_body_request['biometrics'] = json.loads("load_biometric_value_here")
        
    # request
    authentication_request_request = json.dumps(http_request_body_request)
    authentication_request_request = str(authentication_request_request)
    
    AES_SECRET_KEY = secrets.token_bytes(32)
    
    http_request_body['request'] = symmetric_encrypt(authentication_request_request, AES_SECRET_KEY)
    http_request_body['request'] = base64URLSafeString(http_request_body['request'])
    
    # requestSessionKey
    ida_certificate = open(IDA_certificate_location).read()
    ida_certificate_bytes = bytes(ida_certificate, "utf-8")
    # No need for PYTHON
    # AES_SECRET_KEY_ENCODED = base64.b64encode(AES_SECRET_KEY).decode('utf-8')
    request_session_key = asymmetric_encrypt(AES_SECRET_KEY, ida_certificate_bytes)
    http_request_body['requestSessionKey'] = base64URLSafeString(request_session_key)

    # requestHMAC
    request_HMAC = printHexBinary(authentication_request_request)
    http_request_body['requestHMAC'] = symmetric_encrypt(request_HMAC, AES_SECRET_KEY)
    http_request_body['requestHMAC'] = base64URLSafeString(http_request_body['requestHMAC'])
    
    # thumbprint
    http_request_body['thumbprint'] = get_thumbprint(IDA_certificate_location)

    # signature header
    http_request_header['signature'] = create_signature(json.dumps(http_request_body), partner_private_key_location)
    
    # authorization header
    http_request_header['authorization'] = getAuthorization()
    
    # content-type header
    http_request_header['content-type'] = "application/json"
        
    response = requests.post(auth_url, headers=http_request_header, data=json.dumps(http_request_body), verify=False)
        
    if not response.json()['errors']:
    
        result = {}
        partner_id = os.environ.get('PARTNER_ID')
        
        partner_private_key = open(f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem').read()
        partner_private_key_bytes = bytes(partner_private_key, "utf-8")
        
        response_session_key_encrypted = base64URLDecode(response.json()["responseSessionKey"])
        response_encrypted = base64URLDecode(response.json()["response"])
        result["response_session_key"] = asymmetric_decrypt(response_session_key_encrypted, partner_private_key_bytes)
        result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
        
        print(f"response_session_key_encrypted: {response_session_key_encrypted}")
        print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}")
        print(f"response_encrypted: {response_encrypted}")
        print(f"response_encrypted length: {len(response_encrypted)}")
        print(f"response_session_key: {result['response_session_key']}")
        print(f"response_session_key length: {len(result['response_session_key'])}")
        print(f"response: {result['response']}\n")

        return JsonResponse(result['response'])
    
    response = json.loads(str(response.json()).replace('[', '').replace(']', '').replace('\'', '"').replace('None', '"None"'))
    
    return JsonResponse(response)

def symmetric_encrypt(message, key):
    nonce = secrets.token_bytes(16)
    
    message = message.encode('utf-8')
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    
    return ciphertext + tag + nonce

def finalize_symmetric_encrypt(ciphertext: bytes, tag: bytes, nonce: bytes):
    output = ciphertext
    
    if(tag is not None):
        output = bytearray(len(ciphertext) + len(tag))
        array_copy(ciphertext, 0, output, 0, len(ciphertext))
        array_copy(tag, 0, output, len(ciphertext), len(tag))
    
        ciphertext = output
    
    if(nonce is not None):
        output = bytearray(len(ciphertext) + len(nonce))
        
        array_copy(ciphertext, 0, output, 0, len(ciphertext))
        array_copy(nonce, 0, output, len(ciphertext), len(nonce))
    
    return output
    
def symmetric_decrypt(encrypted_data, key):    
    # The block size for AES in GCM mode is 16 bytes (128 bits)
    block_size = 16
    tag_size = 16

    # Extract the nonce (last 16 bytes of enc_response)
    nonce = encrypted_data[-block_size:]
    
    # Extract the tag
    tag = encrypted_data[:-block_size][-block_size:]
    
    # Extract the encrypted data (everything except the last 16 bytes)
    encrypted_kyc_data = encrypted_data[:-(block_size + tag_size)]
    
    # Create the cipher object and initialize it for decryption
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    # Decrypt the data
    decrypted_data = cipher.decrypt_and_verify(encrypted_kyc_data, tag)
        
    # Assuming the decrypted data is JSON encoded, convert it to a dictionary
    response_map = json.loads(decrypted_data)
    
    return response_map

def asymmetric_encrypt(data: bytes, public_key_pem: bytes) -> bytes:
    # Load the certificate from PEM format
    certificate = x509.load_pem_x509_certificate(public_key_pem, default_backend())
    public_key = certificate.public_key()

    # Encrypt the data
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_data

def asymmetric_decrypt(encrypted_data: bytes, private_key_pem: bytes) -> bytes:
    # Load the private key from PEM format
    private_key = load_pem_private_key(
        private_key_pem,
        password=None,
    )
    
    # Decrypt the data
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return decrypted_data

def get_thumbprint(fname):
    with open(fname, "rb") as cert_file:
        cert_data = cert_file.read()
        
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    thumbprint = cert.fingerprint(hashes.SHA256())
    
    return thumbprint.hex()

def create_signature(request, key_location):
    partner_id = os.environ.get('PARTNER_ID')
    partner_private_key = open(key_location).read()
    signed_certificate = open(f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-signedcertificate.cer').read()
    signed_certificate = signed_certificate.replace("\n", "").replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "")

    jws = JsonWebSignature()
    jwt = jws.serialize_compact({'x5c': [f'{signed_certificate}'],'alg': 'RS256'}, request, partner_private_key).decode()
    jwt = jwt.split(".")
    jwt = f"{jwt[0]}..{jwt[2]}"

    return jwt

def getAuthorization():
    http_authorization = {}
    http_authorization_header = {}
    http_authorization['request'] = {}
    datetime_now = getCurrentTime()
    http_authorization['requestTime'] = datetime_now
    http_authorization['request']['clientId'] = os.environ.get('CLIENT_ID')
    http_authorization['request']['secretKey'] = os.environ.get('SECRET_KEY')
    http_authorization['request']['appId'] = os.environ.get('APP_ID')
    http_autorization_request_body = json.dumps(http_authorization)
    http_authorization_header['content-type'] = 'application/json'

    response = requests.post(os.environ.get('ID_AUTH_MANAGER'), data=http_autorization_request_body, verify=False, headers=http_authorization_header)
    
    return response.headers['authorization']

def getCurrentTime():
    t = datetime.now(timezone.utc)
    t = t.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    return t

def base64URLSafeString(data):
    data = base64.b64encode(data)
    data = data.decode("utf-8")
    data = data.replace('+', '-').replace('/', '_').rstrip('=')
    
    return data

def printHexBinary(data):
    data = data.encode("utf-8")
    hasher = hashlib.sha256()
    hasher.update(data)
    hasher = hasher.digest()
    
    return binascii.hexlify(hasher).upper().decode('ascii')

def base64URLDecode(base64URL):
    base64_string = base64URL.replace("-", "+").replace("_", "/")
    
    padding = len(base64_string) % 4
    
    if padding > 0:
        base64_string += "=" * padding
        
    result = base64.b64decode(base64_string)
    
    return result

def array_copy(src, src_pos, dest, dest_pos, length):
    dest[dest_pos:dest_pos + length] = src[src_pos:src_pos + length]