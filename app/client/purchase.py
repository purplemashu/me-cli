from datetime import datetime, timezone, timedelta
import json
import uuid
import base64
import qrcode

import time
import requests
from app.client.engsel import *
from app.client.encrypt import API_KEY, build_encrypted_field, decrypt_xdata, encryptsign_xdata, java_like_timestamp, get_x_signature_payment, get_x_signature_bounty

BASE_API_URL = os.getenv("BASE_API_URL")
AX_DEVICE_ID = os.getenv("AX_DEVICE_ID")
AX_FP = os.getenv("AX_FP")
UA = os.getenv("UA")

def get_payment_methods(
    api_key: str,
    tokens: dict,
    token_confirmation: str,
    payment_target: str,
):
    payment_path = "payments/api/v8/payment-methods-option"
    payment_payload = {
        "payment_type": "PURCHASE",
        "is_enterprise": False,
        "payment_target": payment_target,
        "lang": "en",
        "is_referral": False,
        "token_confirmation": token_confirmation
    }
    
    payment_res = send_api_request(api_key, payment_path, payment_payload, tokens["id_token"], "POST")
    if payment_res["status"] != "SUCCESS":
        print("Failed to fetch payment methods.")
        print(f"Error: {payment_res}")
        return None
    
    
    
    return payment_res["data"]

def settlement_qris(
    api_key: str,
    tokens: dict,
    token_payment: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
    item_name: str = "",
):  
    amount_str = input(f"Total amount is {price}.\nEnter value if you need to overwrite, press enter to ignore & use default amount: ")
    amount_int = price
    
    if amount_str != "":
        try:
            amount_int = int(amount_str)
        except ValueError:
            print("Invalid overwrite input, using original price.")
            return None
    
    # Settlement request
    path = "payments/api/v8/settlement-multipayment/qris"
    settlement_payload = {
        "akrab": {
            "akrab_members": [],
            "akrab_parent_alias": "",
            "members": []
        },
        "can_trigger_rating": False,
        "total_discount": 0,
        "coupon": "",
        "payment_for": "BUY_PACKAGE",
        "topup_number": "",
        "is_enterprise": False,
        "autobuy": {
            "is_using_autobuy": False,
            "activated_autobuy_code": "",
            "autobuy_threshold_setting": {
            "label": "",
            "type": "",
            "value": 0
            }
        },
        "access_token": tokens["access_token"],
        "is_myxl_wallet": False,
        "additional_data": {
            "original_price": price,
            "is_spend_limit_temporary": False,
            "migration_type": "",
            "spend_limit_amount": 0,
            "is_spend_limit": False,
            "tax": 0,
            "benefit_type": "",
            "quota_bonus": 0,
            "cashtag": "",
            "is_family_plan": False,
            "combo_details": [],
            "is_switch_plan": False,
            "discount_recurring": 0,
            "has_bonus": False,
            "discount_promo": 0
        },
        "total_amount": amount_int,
        "total_fee": 0,
        "is_use_point": False,
        "lang": "en",
        "items": [{
            "item_code": payment_target,
            "product_type": "",
            "item_price": price,
            "item_name": item_name,
            "tax": 0
        }],
        "verification_token": token_payment,
        "payment_method": "QRIS",
        "timestamp": int(time.time())
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
    x_sig = get_x_signature_payment(
            api_key,
            tokens["access_token"],
            ts_to_sign,
            payment_target,
            token_payment,
            "QRIS"
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
        "x-version-app": "8.7.0",
    }
    
    url = f"{BASE_API_URL}/{path}"
    print("Sending settlement request...")
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        if decrypted_body["status"] != "SUCCESS":
            print("Failed to initiate settlement.")
            print(f"Error: {decrypted_body}")
            return None
        
        transaction_id = decrypted_body["data"]["transaction_code"]
        
        return transaction_id
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text
    
def get_qris_code(
    api_key: str,
    tokens: dict,
    transaction_id: str
):
    path = "payments/api/v8/pending-detail"
    payload = {
        "transaction_id": transaction_id,
        "is_enterprise": False,
        "lang": "en",
        "status": ""
    }
    
    res = send_api_request(api_key, path, payload, tokens["id_token"], "POST")
    if res["status"] != "SUCCESS":
        print("Failed to fetch QRIS code.")
        print(f"Error: {res}")
        return None
    
    return res["data"]["qr_code"]

def show_qris_payment(api_key: str, tokens: dict, package_option_code: str, token_confirmation: str, price: int, item_name: str = ""):
    print("Fetching payment method details...")
    
    payment_methods_data = get_payment_methods(
        api_key=api_key,
        tokens=tokens,
        token_confirmation=token_confirmation,
        payment_target=package_option_code,
    )
    
    token_payment = payment_methods_data["token_payment"]
    ts_to_sign = payment_methods_data["timestamp"]
    
    transaction_id = settlement_qris(
        api_key,
        tokens,
        token_payment,
        ts_to_sign,
        package_option_code,
        price,
        item_name
    )
    
    if not transaction_id:
        print("Failed to create QRIS transaction.")
        return
    
    print("Fetching QRIS code...")
    qris_code = get_qris_code(api_key, tokens, transaction_id)
    if not qris_code:
        print("Failed to get QRIS code.")
        return
    print(f"QRIS data:\n{qris_code}")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(qris_code)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    
    qris_b64 = base64.urlsafe_b64encode(qris_code.encode()).decode()
    qris_url = f"https://ki-ar-kod.netlify.app/?data={qris_b64}"
    
    print(f"Atau buka link berikut untuk melihat QRIS:\n{qris_url}")
    
    return

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
        "x-version-app": "8.7.0",
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
