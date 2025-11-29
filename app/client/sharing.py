import uuid
import requests
import json

from datetime import datetime, timezone

from app.client.engsel import BASE_API_URL, UA
from app.client.encrypt import (
    API_KEY,
    java_like_timestamp,
    get_x_signature_balance_allotment,
    encryptsign_xdata,
    decrypt_xdata,
)

def balance_allotment(
    api_key: str,
    tokens: dict,
    stage_token: str,
    receiver_msisdn: str,
    amount: int,
):
    path = "sharings/api/v8/balance/allotment"
        
    allotment_payload = {
        "access_token": tokens["access_token"],
        "receiver": receiver_msisdn,
        "amount": amount,
        "stage_token": stage_token,
        "lang": "en",
        "is_enterprise": False,
    }
    
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method="POST",
        path=path,
        id_token=tokens["id_token"],
        payload=allotment_payload
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    sig_time_sec = (xtime // 1000)
    x_requested_at = datetime.fromtimestamp(sig_time_sec, tz=timezone.utc).astimezone()
    
    body = encrypted_payload["encrypted_body"]
    
    x_sig = get_x_signature_balance_allotment(
        api_key=api_key,
        path=path,
        access_token=tokens["access_token"],
        msisdn=receiver_msisdn,
        amount=amount,
    )
    
    headers = {
        "host": BASE_API_URL.replace("https://", ""),
        "content-type": "application/json; charset=utf-8",
        "user-agent": UA,
        "x-api-key": API_KEY,
        "authorization": f"Bearer {tokens['id_token']}",
        "x-hv": "v3",
        "x-signature-time": str(sig_time_sec),
        "x-signature": x_sig,
        "x-request-id": str(uuid.uuid4()),
        "x-request-at": java_like_timestamp(x_requested_at),
        "x-version-app": "8.9.0",
    }
    
    url = f"{BASE_API_URL}/{path}"
    print("Sending balance allotment request...")
    
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        if decrypted_body["status"] != "SUCCESS":
            print("Failed")
            print(f"Error: {decrypted_body}")
            return None
        
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text
        