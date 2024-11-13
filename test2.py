import requests

request_body = {
    "env": "Staging",
    "purpose": "Auth",
    "specVersion": "0.9.5.1.5",
    "timeout": "300000",
    "captureTime": "2024-09-23T02:52:58Z",
    "domainUri": "https://api.apps-external.uat2.phylsys.gov.ph",
    "transactionId": "1234567890",
    "bio": [
        {
            "type": "Finger",
            "count": "3",
            "bioSubType": [
                "UNKNOWN"
            ],
            "requestedScore": "60",
            "deviceId": "2147000102",
            "deviceSubId": "1",
            "previousHash": ""
        }
    ],
    "customOpts": [
        {
            "name": "name1",
            "value": "value1"
        }
    ]
}

request_uri = "http://127.0.0.1:4501/capture"

response = requests.post(request_uri, json=request_body)

print(response)