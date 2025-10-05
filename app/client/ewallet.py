import json
import uuid
import time
import requests

from datetime import datetime, timezone, timedelta

from app.client.engsel import BASE_API_URL, UA, intercept_page, send_api_request
from app.client.encrypt import API_KEY, decrypt_xdata, encryptsign_xdata, java_like_timestamp, get_x_signature_payment
from app.type_dict import PaymentItem

def settlement_multipayment_v2(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    wallet_number: str,
    payment_method,
    payment_for,
    ask_overwrite: bool,
    amount_used: str = ""
):
    token_confirmation = items[0]["token_confirmation"]
    payment_targets = ""
    for item in items:
        if payment_targets != "":
            payment_targets += ";"
        payment_targets += item["item_code"]
        
    amount_int = items[-1]["item_price"]
    if amount_used == "first":
        amount_int = items[0]["item_price"]
    
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
            payment_for,
            path
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

def show_multipayment(
    api_key: str,
    tokens: dict,
    items: list[PaymentItem],
    payment_for,
    ask_overwrite: bool,
    amount_used: str = "",
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
        ask_overwrite,
        amount_used,
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