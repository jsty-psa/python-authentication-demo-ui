from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from django_keygen import KeyGen
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA as RSA_key
from Crypto.Hash import SHA256
from Crypto.IO import PEM
from django.shortcuts import redirect
from authlib.jose import JsonWebSignature

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography import x509

import os, json, base64, rsa, hashlib, sys, re, requests

# Create your views here.
def requestOTP(request, pcn):
    datetime_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    base_url = os.environ.get('BASE_URL')
    misp_license_key = os.environ.get('TSP_LICENSE_KEY')
    partner_id = os.environ.get('PARTNER_ID')
    partner_api_key = os.environ.get('API_KEY')
    env = os.environ.get('ENV')
    version = os.environ.get('VERSION')
    transaction_id = get_random_string(length=32, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    # transaction_id = get_random_string(length=10, allowed_chars='0123456789')
    # transaction_id = "1234567890"
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}-partner-private-key.pem'
    # partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}-inter-private-key.pem'
    otp_url = f'{base_url}/idauthentication/v1/otp/{misp_license_key}/{partner_id}/{partner_api_key}'
    
    otp_request = {}
    otp_request_header = {}
    otp_request['id'] = 'philsys.identity.otp'
    otp_request['version'] = version
    otp_request['transactionID'] = transaction_id
    # otp_request['requestTime'] = datetime_now
    otp_request['requestTime'] = getCurrentTime()
    # otp_request['env'] = env
    # otp_request['domainUri'] = base_url
    otp_request['individualId'] = str(pcn)
    otp_request['individualIdType'] = "VID"
    otp_request['otpChannel'] = ['email']
    
    otp_request_header['signature'] = create_signature(json.dumps(otp_request), partner_private_key_location)
    otp_request_header['authorization'] = getAuthorization()
    otp_request_header['content-type'] = 'application/json'
    
    print(f'OTP Request Header:\n{str(json.dumps(otp_request_header))}\n')
    print(f'OTP Request URL:\n{otp_url}\n')
    
    # response = requests.post(otp_url, data=str(json.dumps(otp_request)), verify=False, headers=str(json.dumps(otp_request_header)))
    response = requests.post(otp_url, data=otp_request, headers=otp_request_header, verify=False)
    
    print(f'OTP Response:\n{str(response.json())}')
    
    if not response.json()["errors"]:
        partner_id = os.environ.get('PARTNER_ID')
        
        partner_private_key = open(f'./auth_demo_ui/authentication/keys/{partner_id}-partner-private-key.pem').read()
        partner_private_key_bytes = bytes(partner_private_key, "utf-8")
        
        response_session_key_encrypted = base64URLDecode(response.json()["responseSessionKey"])
        response_encrypted = base64URLDecode(response.json()["response"])
        
        print(f"response_session_key_encrypted: {response_session_key_encrypted}")
        print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}")
        
        print(f"response_encrypted: {response_encrypted}")
        print(f"response_encrypted length: {len(response_encrypted)}")
        
        result = {}
        result["response_session_key"] = decrypt_session_key(response_session_key_encrypted, partner_private_key_bytes)
        
        print(f"response_session_key: {result['response_session_key']}")
        print(f"response_session_key length: {len(result['response_session_key'])}")
        
        result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
        
        return JsonResponse(str((result["response"])["maskedEmail"]))
    
    response = str(response.json()["errors"]).replace("[", "").replace("]", "")
    
    return JsonResponse(response, safe = False)
    
def test(request):
    return render(request, 'authenticate.html')
    return redirect("authenticate")

def authenticate(request):
    http_request_body = {}
    http_request_header = {}
    http_request_body['requestedAuth'] = {}
    http_request_body['request'] = {}
    http_request_body_request = {}
    
    # transaction_id = get_random_string(length=32, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    transaction_id = get_random_string(length=32, allowed_chars='0123456789')
    value = request.GET.dict()
    
    secret_key = KeyGen(length=32).gen_secret_key()
    partner_id = os.environ.get('PARTNER_ID')
    IDA_certificate_location = f'./auth_demo_ui/authentication/keys/{partner_id}-IDAcertificate.cer'
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}-partner-private-key.pem'
    base_url = os.environ.get('BASE_URL')
    version = os.environ.get('VERSION')
    
    datetime_now = getCurrentTime()
    
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
    if(value['input_otp'] == 'on'):
        http_request_body_request['otp'] = value['input_otp_value']
    if(value['input_demo'] == 'on'):
        http_request_body_request['demo'] = value['input_demo_value']
    
    # request
    authentication_request_request = json.dumps(http_request_body_request)
    AES_SECRET_KEY = bytes(secret_key, 'utf-8')
    
    http_request_body['request'] = symmetric_encrypt(authentication_request_request, AES_SECRET_KEY)
    http_request_body['request'] = http_request_body['request'].replace("+", "-").replace("/", "-").replace("=","")
    
    # requestSessionKey
    IDA_certificate = RSA_key.import_key(open(IDA_certificate_location).read())
    request_session_key = rsa.encrypt(AES_SECRET_KEY, IDA_certificate)
    http_request_body['requestSessionKey'] = base64.b64encode(request_session_key).decode("utf-8")
    http_request_body['requestSessionKey'] = http_request_body['requestSessionKey'].replace("+", "-").replace("/", "-").replace("=","")


    
    # requestHMAC
    authentication_request_request_sha256 = hashlib.sha256(authentication_request_request.encode()).hexdigest()
    http_request_body['requestHMAC'] = symmetric_encrypt(authentication_request_request_sha256, AES_SECRET_KEY)
    
    # thumbprint
    http_request_body['thumbprint'] = get_fingerprint(IDA_certificate_location)

    # signature header
    http_request_header['signature'] = create_signature(json.dumps(http_request_body), partner_private_key_location)
    
    # authorization header
    http_request_header['authorization'] = getAuthorization()
    
    # content-type header
    http_request_header['content-type'] = "application/json"
    
    auth_headers = json.dumps(http_request_header)
    
    auth_url = base_url + '/idauthentication/v1/' + ('kyc/' if value['input_ekyc'] == 'on' else 'auth/') + os.environ.get('TSP_LICENSE_KEY') + '/' + os.environ.get('PARTNER_ID') + '/' + os.environ.get('API_KEY')
    
    http_request_body = json.dumps(http_request_body)    
    
    response = requests.post(auth_url, headers=http_request_header, data=http_request_body, verify=False)
    
    print(f"Authentication Response: {response.json()}")
    
    return HttpResponse(None)
    
    # return JsonResponse(http_request_body)
    # return HttpResponse(transaction_id)

def symmetric_encrypt(message, key):
    message_padded = pad(message.encode(), 32)
    cipher = AES.new(key, AES.MODE_ECB)
    output = cipher.encrypt(message_padded)
    
    return base64.b64encode(output).decode("utf8")

def symmetric_decrypt(encrypted_data, key):    
    # The block size for AES in GCM mode is 16 bytes (128 bits)
    block_size = 16

    # Extract the nonce (last 16 bytes of enc_response)
    nonce = encrypted_data[-block_size:]
    
    # Extract the encrypted data (everything except the last 16 bytes)
    encrypted_kyc_data = encrypted_data[:-block_size]
    
    # Create the cipher object and initialize it for decryption
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_kyc_data)
    decrypted_data = str(decrypted_data).split("\\")[0].replace("b'", "")
    
    # Assuming the decrypted data is JSON encoded, convert it to a dictionary
    response_map = json.loads(decrypted_data)
    
    return response_map

def get_fingerprint(fname):
    """
    Read an X.509 certificate and return the SHA-256 fingerprint in hex
    """

    with open(fname, "r", encoding="utf-8") as f:
        pem_data = f.read()

    r = re.compile(r"\s*-----BEGIN (.*)-----\s+")
    m = r.match(pem_data)
    marker = m.group(1)

    if marker != "CERTIFICATE":
        print("Error: Expected X.509 Certificate")
        sys.exit(1)

    der = PEM.decode(pem_data)
    h = SHA256.new()
    h.update(der[0])
    fingerprint = h.hexdigest()

    # insert leading zero bytes to make the string 40 digits
    while len(fingerprint) < 40:
        fingerprint = '0' + fingerprint

    return fingerprint

def create_signature(request, key_location):
    partner_id = os.environ.get('PARTNER_ID')
    partner_private_key = open(key_location).read()
    signed_certificate = open(f'./auth_demo_ui/authentication/keys/{partner_id}-signedcertificate.cer').read()
    signed_certificate = signed_certificate.replace("\n", "").replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "")

    print(f"API Request Body:\n{request}\n")

    jws = JsonWebSignature()
    jwt = jws.serialize_compact({'x5u': signed_certificate,'alg': 'RS256'}, request, partner_private_key).decode()
    # jwt = jws.serialize_compact({'alg': 'RS256'}, request, partner_private_key).decode()
    jwt = jwt.split(".")
    jwt = f"{jwt[0]}.. {jwt[2]}"

    # print(f"Signature\n{jwt}")

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

def base64URLDecode(base64URL):
    base64_string = base64URL.replace("-", "+").replace("_", "/")
    
    padding = len(base64_string) % 4
    
    if padding > 0:
        base64_string += "=" * padding
        
    result = base64.b64decode(base64_string)
    
    return result

def decrypt_session_key(encrypted_data: bytes, private_key_pem: bytes) -> bytes:
    # Load the private key from PEM format
    private_key = load_pem_private_key(
        private_key_pem,
        password=None,  # if the key is encrypted with a password, provide it here
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