from django.shortcuts import render
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from authentication.include.authorization import get_authorization
from authentication.include.base64 import base64_url_safe_string, base64_url_decode
from authentication.include.crypto import symmetric_encrypt, symmetric_decrypt, asymmetric_encrypt, asymmetric_decrypt
from authentication.include.signature import create_signature
from authentication.include.utils import print_hex_binary, get_current_time, get_thumbprint

import os, json, requests, secrets, warnings

warnings.filterwarnings("ignore")

def test(request):
    return render(request, 'authenticate.html')

def requestOTP(request, pcn):
    print("\n\n\n\n\n")
    
    base_url = os.environ.get('BASE_URL')
    misp_license_key = os.environ.get('TSP_LICENSE_KEY')
    partner_id = os.environ.get('PARTNER_ID')
    partner_api_key = os.environ.get('API_KEY')
    env = os.environ.get('ENV')
    version = os.environ.get('VERSION')
    # transaction_id = get_random_string(length=10, allowed_chars='0123456789')
    transaction_id = "1234567890"
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem'
    otp_url = f'{base_url}/idauthentication/v1/otp/{misp_license_key}/{partner_id}/{partner_api_key}'
    
    otp_request = {}
    otp_request_header = {}
    otp_request['id'] = 'philsys.identity.otp'
    otp_request['version'] = version
    otp_request['transactionID'] = transaction_id
    otp_request['requestTime'] = get_current_time()
    otp_request['individualId'] = str(pcn)
    otp_request['individualIdType'] = "VID"
    otp_request['otpChannel'] = ['email']
    
    otp_request_header['signature'] = create_signature(json.dumps(otp_request), partner_private_key_location)
    otp_request_header['Authorization'] = get_authorization()
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
        
        response_session_key_encrypted = base64_url_decode(response.json()["responseSessionKey"])
        response_encrypted = base64_url_decode(response.json()["response"])
        result["response_session_key"] = asymmetric_decrypt(response_session_key_encrypted, partner_private_key_bytes)
        result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
                
        print(f"response_session_key_encrypted: {response_session_key_encrypted}\n")
        print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}\n")
        print(f"response_encrypted: {response_encrypted}\n")
        print(f"response_encrypted length: {len(response_encrypted)}\n")
        print(f"response_session_key: {result['response_session_key']}\n")
        print(f"response_session_key length: {len(result['response_session_key'])}\n")
        print(f"response: {result['response']}\n")

        return JsonResponse(result['response'])
    
    response = json.loads(str(response.json()).replace('[', '').replace(']', '').replace('\'', '"').replace('None', '"None"'))
    return JsonResponse(response)

def authenticate(request):
    print("\n\n\n\n\n")
    
    http_request_body = {}
    http_request_header = {}
    http_request_body['requestedAuth'] = {}
    http_request_body['request'] = {}
    http_request_body_request = {}

    # transaction_id = request.get("transaction_id", get_random_string(length=10, allowed_chars='0123456789'))
    transaction_id = "1234567890"
    value = request.GET.dict()

    print(f"Value:{value}\n\n")
    print(f"Value:{request.GET}")
    
    partner_id = os.environ.get('PARTNER_ID')
    IDA_certificate_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-IDAcertificate.cer'
    partner_private_key_location = f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem'
    base_url = os.environ.get('BASE_URL')
    version = os.environ.get('VERSION')
    auth_url = base_url + '/idauthentication/v1/' + ('kyc/' if value['input_ekyc'] == 'on' else 'auth/') + os.environ.get('TSP_LICENSE_KEY') + '/' + os.environ.get('PARTNER_ID') + '/' + os.environ.get('API_KEY')
    
    datetime_now = get_current_time()
    
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
    http_request_body['request'] = base64_url_safe_string(http_request_body['request'])
    
    # requestSessionKey
    ida_certificate = open(IDA_certificate_location).read()
    ida_certificate_bytes = bytes(ida_certificate, "utf-8")
    # No need for PYTHON
    # AES_SECRET_KEY_ENCODED = base64.b64encode(AES_SECRET_KEY).decode('utf-8')
    request_session_key = asymmetric_encrypt(AES_SECRET_KEY, ida_certificate_bytes)
    http_request_body['requestSessionKey'] = base64_url_safe_string(request_session_key)

    # requestHMAC
    request_HMAC = print_hex_binary(authentication_request_request)
    http_request_body['requestHMAC'] = symmetric_encrypt(request_HMAC, AES_SECRET_KEY)
    http_request_body['requestHMAC'] = base64_url_safe_string(http_request_body['requestHMAC'])
    
    # thumbprint
    http_request_body['thumbprint'] = get_thumbprint(IDA_certificate_location)

    # signature header
    http_request_header['signature'] = create_signature(json.dumps(http_request_body), partner_private_key_location)
    
    # authorization header
    http_request_header['authorization'] = get_authorization()
    
    # content-type header
    http_request_header['content-type'] = "application/json"
        
    response = requests.post(auth_url, headers=http_request_header, data=json.dumps(http_request_body), verify=False)
    
    print(f'Authentication Request URL:\n{auth_url}\n')
    print(f'Authentication Request Header:\n{http_request_header}\n')
    print(f'Authentication Request Body:\n{http_request_body}\n')
    
    print(f'Authentication Response:\n{response.json()}\n')
    
    if not response.json()["errors"]:
    
        result = {}
        partner_id = os.environ.get('PARTNER_ID')
        
        partner_private_key = open(f'./auth_demo_ui/authentication/keys/{partner_id}/{partner_id}-partner-private-key.pem').read()
        partner_private_key_bytes = bytes(partner_private_key, "utf-8")
        
        response_session_key_encrypted = base64_url_decode(response.json()["responseSessionKey"])
        response_encrypted = base64_url_decode(response.json()["response"])
        result["response_session_key"] = asymmetric_decrypt(response_session_key_encrypted, partner_private_key_bytes)
        result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])
                
        print(f"response_session_key_encrypted: {response_session_key_encrypted}\n")
        print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}\n")
        print(f"response_encrypted: {response_encrypted}\n")
        print(f"response_encrypted length: {len(response_encrypted)}\n")
        print(f"response_session_key: {result['response_session_key']}\n")
        print(f"response_session_key length: {len(result['response_session_key'])}\n")
        print(f"response: {result['response']}\n")

        return JsonResponse(result['response'])
    
    response = json.loads(str(response.json()).replace('[', '').replace(']', '').replace('\'', '"').replace('None', '"None"'))
    
    return JsonResponse(response)