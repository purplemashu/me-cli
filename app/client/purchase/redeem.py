import os
import json
import uuid
import requests

from datetime import datetime, timezone

from app.client.engsel import BASE_API_URL, UA
from app.client.encrypt import (
    API_KEY,
    build_encrypted_field,
    decrypt_xdata,
    encryptsign_xdata,
    get_x_signature_loyalty,
    java_like_timestamp,
    get_x_signature_bounty,
    get_x_signature_bounty_allotment,
)

BASE_API_URL = os.getenv("BASE_API_URL")
AX_FP = os.getenv("AX_FP")
UA = os.getenv("UA")

def settlement_bounty(
    api_key: str,
    tokens: dict,
    token_confirmation: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
    item_name: str = "",
):
    # Settlement request
    path = "api/v8/personalization/bounties-exchange"
    settlement_payload = {
        "total_discount": 0,
        "is_enterprise": False,
        "payment_token": "",
        "token_payment": "",
        "activated_autobuy_code": "",
        "cc_payment_type": "",
        "is_myxl_wallet": False,
        "pin": "",
        "ewallet_promo_id": "",
        "members": [],
        "total_fee": 0,
        "fingerprint": "",
        "autobuy_threshold_setting": {
            "label": "",
            "type": "",
            "value": 0
        },
        "is_use_point": False,
        "lang": "en",
        "payment_method": "BALANCE",
        "timestamp": ts_to_sign,
        "points_gained": 0,
        "can_trigger_rating": False,
        "akrab_members": [],
        "akrab_parent_alias": "",
        "referral_unique_code": "",
        "coupon": "",
        "payment_for": "REDEEM_VOUCHER",
        "with_upsell": False,
        "topup_number": "",
        "stage_token": "",
        "authentication_id": "",
        "encrypted_payment_token": build_encrypted_field(urlsafe_b64=True),
        "token": "",
        "token_confirmation": token_confirmation,
        "access_token": tokens["access_token"],
        "wallet_number": "",
        "encrypted_authentication_id": build_encrypted_field(urlsafe_b64=True),
        "additional_data": {
            "original_price": 0,
            "is_spend_limit_temporary": False,
            "migration_type": "",
            "akrab_m2m_group_id": "",
            "spend_limit_amount": 0,
            "is_spend_limit": False,
            "mission_id": "",
            "tax": 0,
            "benefit_type": "",
            "quota_bonus": 0,
            "cashtag": "",
            "is_family_plan": False,
            "combo_details": [],
            "is_switch_plan": False,
            "discount_recurring": 0,
            "is_akrab_m2m": False,
            "balance_type": "",
            "has_bonus": False,
            "discount_promo": 0
        },
        "total_amount": 0,
        "is_using_autobuy": False,
        "items": [{
            "item_code": payment_target,
            "product_type": "",
            "item_price": price,
            "item_name": item_name,
            "tax": 0
        }]
    }
        
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method="POST",
        path=path,
        id_token=tokens["id_token"],
        payload=settlement_payload
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    sig_time_sec = (xtime // 1000)
    x_requested_at = datetime.fromtimestamp(sig_time_sec, tz=timezone.utc).astimezone()
    settlement_payload["timestamp"] = ts_to_sign
    
    body = encrypted_payload["encrypted_body"]
        
    x_sig = get_x_signature_bounty(
        api_key=api_key,
        access_token=tokens["access_token"],
        sig_time_sec=ts_to_sign,
        package_code=payment_target,
        token_payment=token_confirmation
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
    print("Sending bounty request...")
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        if decrypted_body["status"] != "SUCCESS":
            print("Failed to claim bounty.")
            print(f"Error: {decrypted_body}")
            return None
        
        print(decrypted_body)
        
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def settlement_loyalty(
    api_key: str,
    tokens: dict,
    token_confirmation: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
):
    # Settlement reuest
    path = "gamification/api/v8/loyalties/tiering/exchange"
    settlement_payload = {
        "item_code": payment_target,
        "amount": 0,
        "partner": "",
        "is_enterprise": False,
        "item_name": "",
        "lang": "en",
        "points": price,
        "timestamp": ts_to_sign,
        "token_confirmation": token_confirmation
    }

    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method="POST",
        path=path,
        id_token=tokens["id_token"],
        payload=settlement_payload
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    sig_time_sec = (xtime // 1000)
    x_requested_at = datetime.fromtimestamp(sig_time_sec, tz=timezone.utc).astimezone()
    settlement_payload["timestamp"] = ts_to_sign
    
    body = encrypted_payload["encrypted_body"]

    x_sig = get_x_signature_loyalty(
        api_key=api_key,
        sig_time_sec=ts_to_sign,
        package_code=payment_target,
        token_confirmation=token_confirmation,
        path=path
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
    print("Sending loyalty request...")
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        if decrypted_body["status"] != "SUCCESS":
            print("Failed purchase.")
            print(f"Error: {decrypted_body}")
            return None
        
        print(decrypted_body)
        
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def bounty_allotment(
    api_key: str,
    tokens: dict,
    ts_to_sign: int,
    destination_msisdn: str,
    item_name: str,
    item_code: str,
    token_confirmation: str,
):
    path = "gamification/api/v8/loyalties/tiering/bounties-allotment"
    
    settlement_payload = {
        "destination_msisdn": destination_msisdn,
        "item_code": item_code,
        "is_enterprise": False,
        "item_name": item_name,
        "lang": "en",
        "timestamp": int(datetime.now().timestamp()),
        "token_confirmation": token_confirmation,
    }
    
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method="POST",
        path=path,
        id_token=tokens["id_token"],
        payload=settlement_payload
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    sig_time_sec = (xtime // 1000)
    x_requested_at = datetime.fromtimestamp(sig_time_sec, tz=timezone.utc).astimezone()
    settlement_payload["timestamp"] = ts_to_sign
    
    body = encrypted_payload["encrypted_body"]
    
    x_sig = get_x_signature_bounty_allotment(
        api_key=api_key,
        sig_time_sec=ts_to_sign,
        package_code=item_code,
        token_confirmation=token_confirmation,
        destination_msisdn=destination_msisdn,
        path=path
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
    print("Sending bounty request...")
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        if decrypted_body["status"] != "SUCCESS":
            print("Failed to claim bounty.")
            print(f"Error: {decrypted_body}")
            return None
        
        print(decrypted_body)
        
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text
