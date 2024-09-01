from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES

import json, base64

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

partner_id = "AP2023100400003"

testing = {}
testing["response"] = "LjsAASV-tKAnGVtIJJEfakp8qYVW83wFAWLQig7logUsCwyAMLwZ5Gq0Wi04dvYNZrt_A2stmDY_3F2dBMe6KyimXzdcTkET_A"
testing["responseSessionKey"] = "AJG0bg9-s7DKr5JN8O-d9czgtbJuOuV_dqDIMLzoEcQ0uAhxxqERnvk7xX7j5lSf7Wp2nsFeu31WFWpkQWRq63Jwj7tyzw5QyRArMWkNkPt10Yi47gLFqAmHJOyDXf84ab9bdrs-s84JfLr36Y1r-mmiCSn08w8S4iB146i-lOypWchjgfUKPRGAa8POojItDjqEnDjVpYE0a0bI2rsTbHxUf0rrECBUKZHE_9UxOZhkGBM-XFRAIvvxbfABsek_HbiKn7ymhhm90TU_EYXiTvXbafl6B81OMPfkk91GMbSBy1jSgQ8974dgBrZ52ywD74DdxmRjsmGnf-9h-7KWsA"
partner_private_key = open(f'{partner_id}-partner-private-key.pem').read()
partner_private_key_bytes = bytes(partner_private_key, "utf-8")

response_session_key_encrypted = base64URLDecode(testing["responseSessionKey"])
response_encrypted = base64URLDecode(testing["response"])

print(f"response_session_key_encrypted: {response_session_key_encrypted}\n")
print(f"response_session_key_encrypted length: {len(response_session_key_encrypted)}\n")

print(f"response_encrypted: {response_encrypted}\n")
print(f"response_encrypted length: {len(response_encrypted)}\n")

result = {}
result["response_session_key"] = decrypt_session_key(response_session_key_encrypted, partner_private_key_bytes)

print(f"response_session_key: {result['response_session_key']}\n")
print(f"response_session_key length: {len(result['response_session_key'])}\n")

result["response"] = symmetric_decrypt(response_encrypted, result["response_session_key"])

print((result["response"])["maskedEmail"])