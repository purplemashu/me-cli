from datetime import datetime, timezone, timedelta
import json
import uuid

import time
import requests
from app.client.engsel import *
from app.client.encrypt import API_KEY, build_encrypted_field, decrypt_xdata, encryptsign_xdata, java_like_timestamp, get_x_signature_payment, get_x_signature_bounty
from app. client.purchase import get_payment_methods

from app.type_dict import PaymentItem

def settlement_multipayment(
    api_key: str,
    tokens: dict,
    token_payment: str,
    ts_to_sign: int,
    payment_target: str,
    price: int,
    amount_int: int,
    wallet_number: str,
    item_name: str = "",
    payment_method: str = "DANA"
):
    # Settlement request
    path = "payments/api/v8/settlement-multipayment/ewallet"
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
        "cc_payment_type": "",
        "access_token": tokens["access_token"],
        "is_myxl_wallet": False,
        "wallet_number": wallet_number,
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
        "payment_method": payment_method,
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
            payment_method
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
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def show_multipayment(api_key: str, tokens: dict, package_option_code: str, token_confirmation: str, price: int, item_name: str = ""):
    print("Fetching available payment methods...")
    
    payment_methods_data = get_payment_methods(
        api_key=api_key,
        tokens=tokens,
        token_confirmation=token_confirmation,
        payment_target=package_option_code,
    )
    
    token_payment = payment_methods_data["token_payment"]
    ts_to_sign = payment_methods_data["timestamp"]
    
    amount_str = input(f"Total amount is {price}.\nEnter value if you need to overwrite, press enter to ignore & use default amount: ")
    amount_int = price
    
    if amount_str != "":
        try:
            amount_int = int(amount_str)
        except ValueError:
            print("Invalid overwrite input, using original price.")
            return None
    
    choosing_payment_method = True
    while choosing_payment_method:
        payment_method = ""
        wallet_number = ""
        print("Pilihan multipayment:")
        print("1. DANA\n2. ShopeePay\n3. GoPay\n4. OVO")
        choice = input("Pilih metode pembayaran: ")
        if choice == "1":
            payment_method = "DANA"
            wallet_number = input("Masukkan nomor DANA (contoh: 08123456789): ")
            # Validate number format
            if not wallet_number.startswith("08") or not wallet_number.isdigit() or len(wallet_number) < 10 or len(wallet_number) > 13:
                print("Nomor DANA tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            choosing_payment_method = False
        elif choice == "2":
            payment_method = "SHOPEEPAY"
            choosing_payment_method = False
        elif choice == "3":
            payment_method = "GOPAY"
            choosing_payment_method = False
        elif choice == "4":
            payment_method = "OVO"
            wallet_number = input("Masukkan nomor OVO (contoh: 08123456789): ")
            # Validate number format
            if not wallet_number.startswith("08") or not wallet_number.isdigit() or len(wallet_number) < 10 or len(wallet_number) > 13:
                print("Nomor OVO tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            choosing_payment_method = False
        else:
            print("Pilihan tidak valid.")
            continue
    
    settlement_response = settlement_multipayment(
        api_key,
        tokens,
        token_payment,
        ts_to_sign,
        package_option_code,
        price,
        amount_int,
        wallet_number,
        item_name,
        payment_method
    )
    
    # print(f"Settlement response: {json.dumps(settlement_response, indent=2)}")
    if settlement_response["status"] != "SUCCESS":
        print("Failed to initiate settlement.")
        print(f"Error: {settlement_response}")
        return
    
    if payment_method != "OVO":
        deeplink = settlement_response["data"].get("deeplink", "")
        if deeplink:
            print(f"Silahkan selesaikan pembayaran melalui link berikut:\n{deeplink}")
    else:
        print("Silahkan buka aplikasi OVO Anda untuk menyelesaikan pembayaran.")
    return

def settlement_multipayment_v2(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    wallet_number: str,
    payment_method,
    payment_for,
    ask_overwrite: bool,
):
    token_confirmation = items[0]["token_confirmation"]
    payment_targets = ""
    for item in items:
        if payment_targets != "":
            payment_targets += ";"
        payment_targets += item["item_code"]
        
    amount_int = items[-1]["item_price"]
    
    # Overwrite
    if ask_overwrite:
        print(f"Total amount is {amount_int}.\nEnter new amount if you need to overwrite.")
        amount_str = input("Press enter to ignore & use default amount: ")
        if amount_str != "":
            try:
                amount_int = int(amount_str)
            except ValueError:
                print("Invalid overwrite input, using original price.")
                # return None
    
    intercept_page(api_key, tokens, items[0]["item_code"], False)
    
    # Get payment methods
    payment_path = "payments/api/v8/payment-methods-option"
    payment_payload = {
        "payment_type": "PURCHASE",
        "is_enterprise": False,
        "payment_target": items[0]["item_code"],
        "lang": "en",
        "is_referral": False,
        "token_confirmation": token_confirmation
    }
    
    print("Getting payment methods...")
    payment_res = send_api_request(api_key, payment_path, payment_payload, tokens["id_token"], "POST")
    if payment_res["status"] != "SUCCESS":
        print("Failed to fetch payment methods.")
        print(f"Error: {payment_res}")
        return None
    
    token_payment = payment_res["data"]["token_payment"]
    ts_to_sign = payment_res["data"]["timestamp"]
    
    

    # Settlement request
    path = "payments/api/v8/settlement-multipayment/ewallet"
    settlement_payload = {
        "akrab": {
            "akrab_members": [],
            "akrab_parent_alias": "",
            "members": []
        },
        "can_trigger_rating": False,
        "total_discount": 0,
        "coupon": "",
        "payment_for": payment_for,
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
        "cc_payment_type": "",
        "access_token": tokens["access_token"],
        "is_myxl_wallet": False,
        "wallet_number": wallet_number,
        "additional_data": {},
        "total_amount": amount_int,
        "total_fee": 0,
        "is_use_point": False,
        "lang": "en",
        "items": items,
        "verification_token": token_payment,
        "payment_method": payment_method,
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
            payment_targets,
            token_payment,
            payment_method,
            payment_for
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
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def settlement_multipayment_v3(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    wallet_number: str,
    payment_method,
    payment_for,
    ask_overwrite: bool,
):
    token_confirmation = items[0]["token_confirmation"]
    payment_targets = ""
    for item in items:
        if payment_targets != "":
            payment_targets += ";"
        payment_targets += item["item_code"]
        
    amount_int = items[-1]["item_price"]
    
    # Overwrite
    if ask_overwrite:
        print(f"Total amount is {amount_int}.\nEnter new amount if you need to overwrite.")
        amount_str = input("Press enter to ignore & use default amount: ")
        if amount_str != "":
            try:
                amount_int = int(amount_str)
            except ValueError:
                print("Invalid overwrite input, using original price.")
                # return None
    
    intercept_page(api_key, tokens, items[0]["item_code"], False)
    
    # Get payment methods
    payment_path = "payments/api/v8/payment-methods-option"
    payment_payload = {
        "payment_type": "PURCHASE",
        "is_enterprise": False,
        "payment_target": items[0]["item_code"],
        "lang": "en",
        "is_referral": False,
        "token_confirmation": token_confirmation
    }
    
    print("Getting payment methods...")
    payment_res = send_api_request(api_key, payment_path, payment_payload, tokens["id_token"], "POST")
    if payment_res["status"] != "SUCCESS":
        print("Failed to fetch payment methods.")
        print(f"Error: {payment_res}")
        return None
    
    token_payment = payment_res["data"]["token_payment"]
    ts_to_sign = payment_res["data"]["timestamp"]

    # Settlement request
    path = "payments/api/v8/settlement-multipayment"
    settlement_payload = {
        "total_discount": 0,
        "is_enterprise": False,
        "payment_token": "",
        "token_payment": token_payment,
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
        "payment_method": payment_method,
        "timestamp": int(time.time()),
        "points_gained": 0,
        "can_trigger_rating": False,
        "akrab_members": [],
        "akrab_parent_alias": "",
        "referral_unique_code": "",
        "coupon": "",
        "payment_for": payment_for,
        "with_upsell": False,
        "topup_number": "",
        "stage_token": "",
        "authentication_id": "",
        "encrypted_payment_token": build_encrypted_field(urlsafe_b64=True),
        "token": "",
        "token_confirmation": "",
        "access_token": tokens["access_token"],
        "wallet_number": wallet_number,
        "encrypted_authentication_id": build_encrypted_field(urlsafe_b64=True),
        "additional_data": {
            "original_price": items[-1]["item_price"],
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
        "total_amount": amount_int,
        "is_using_autobuy": False,
        "items": items
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
            payment_targets,
            token_payment,
            payment_method,
            payment_for
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
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def show_multipayment_v2(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for,
    ask_overwrite: bool,
):
    choosing_payment_method = True
    while choosing_payment_method:
        payment_method = ""
        wallet_number = ""
        print("Pilihan multipayment:")
        print("1. DANA\n2. ShopeePay\n3. GoPay\n4. OVO")
        choice = input("Pilih metode pembayaran: ")
        if choice == "1":
            payment_method = "DANA"
            wallet_number = input("Masukkan nomor DANA (contoh: 08123456789): ")
            # Validate number format
            if not wallet_number.startswith("08") or not wallet_number.isdigit() or len(wallet_number) < 10 or len(wallet_number) > 13:
                print("Nomor DANA tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            choosing_payment_method = False
        elif choice == "2":
            payment_method = "SHOPEEPAY"
            choosing_payment_method = False
        elif choice == "3":
            payment_method = "GOPAY"
            choosing_payment_method = False
        elif choice == "4":
            payment_method = "OVO"
            wallet_number = input("Masukkan nomor OVO (contoh: 08123456789): ")
            # Validate number format
            if not wallet_number.startswith("08") or not wallet_number.isdigit() or len(wallet_number) < 10 or len(wallet_number) > 13:
                print("Nomor OVO tidak valid. Pastikan nomor diawali dengan '08' dan memiliki panjang yang benar.")
                continue
            choosing_payment_method = False
        else:
            print("Pilihan tidak valid.")
            continue
    
    settlement_response = settlement_multipayment_v2(
        api_key,
        tokens,
        items,
        wallet_number,
        payment_method,
        payment_for,
        ask_overwrite
    )
    
    # print(f"Settlement response: {json.dumps(settlement_response, indent=2)}")
    if settlement_response["status"] != "SUCCESS":
        print("Failed to initiate settlement.")
        print(f"Error: {settlement_response}")
        return
    
    if payment_method != "OVO":
        deeplink = settlement_response["data"].get("deeplink", "")
        if deeplink:
            print(f"Silahkan selesaikan pembayaran melalui link berikut:\n{deeplink}")
    else:
        print("Silahkan buka aplikasi OVO Anda untuk menyelesaikan pembayaran.")
    return