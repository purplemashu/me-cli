import os
import json
import uuid
import requests

from datetime import datetime, timezone

from app.client.encrypt import (
    encryptsign_xdata,
    java_like_timestamp,
    decrypt_xdata,
    API_KEY,
)

BASE_API_URL = os.getenv("BASE_API_URL")
if not BASE_API_URL:
    raise ValueError("BASE_API_URL environment variable not set")

UA = os.getenv("UA")

def send_api_request(
    api_key: str,
    path: str,
    payload_dict: dict,
    id_token: str,
    method: str = "POST",
):
    encrypted_payload = encryptsign_xdata(
        api_key=api_key,
        method=method,
        path=path,
        id_token=id_token,
        payload=payload_dict
    )
    
    xtime = int(encrypted_payload["encrypted_body"]["xtime"])
    
    now = datetime.now(timezone.utc).astimezone()
    sig_time_sec = (xtime // 1000)

    body = encrypted_payload["encrypted_body"]
    x_sig = encrypted_payload["x_signature"]
    
    headers = {
        "host": BASE_API_URL.replace("https://", ""),
        "content-type": "application/json; charset=utf-8",
        "user-agent": UA,
        "x-api-key": API_KEY,
        "authorization": f"Bearer {id_token}",
        "x-hv": "v3",
        "x-signature-time": str(sig_time_sec),
        "x-signature": x_sig,
        "x-request-id": str(uuid.uuid4()),
        "x-request-at": java_like_timestamp(now),
        "x-version-app": "8.9.0",
    }

    url = f"{BASE_API_URL}/{path}"
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    
    # print(f"Headers: {json.dumps(headers, indent=2)}")
    # print(f"Response body: {resp.text}")

    try:
        decrypted_body = decrypt_xdata(api_key, json.loads(resp.text))
        # print(f"Decrypted body: {json.dumps(decrypted_body, indent=2)}")
        return decrypted_body
    except Exception as e:
        print("[decrypt err]", e)
        return resp.text

def get_profile(api_key: str, access_token: str, id_token: str) -> dict:
    path = "api/v8/profile"

    raw_payload = {
        "access_token": access_token,
        "app_version": "8.9.0",
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching profile...")
    res = send_api_request(api_key, path, raw_payload, id_token, "POST")

    return res.get("data")

def get_balance(api_key: str, id_token: str) -> dict:
    path = "api/v8/packages/balance-and-credit"
    
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }
    
    print("Fetching balance...")
    res = send_api_request(api_key, path, raw_payload, id_token, "POST")
    
    if "data" in res:
        if "balance" in res["data"]:
            return res["data"]["balance"]
    else:
        print("Error getting balance:", res.get("error", "Unknown error"))
        return None

def get_family(
    api_key: str,
    tokens: dict,
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
) -> dict:
    print("Fetching package family...")
    
    is_enterprise_list = [
        False,
        True
    ]

    migration_type_list = [
        "NONE",
        "PRE_TO_PRIOH",
        "PRIOH_TO_PRIO",
        "PRIO_TO_PRIOH"
    ]

    if is_enterprise is not None:
        is_enterprise_list = [is_enterprise]

    if migration_type is not None:
        migration_type_list = [migration_type]

    path = "api/v8/xl-stores/options/list"
    id_token = tokens.get("id_token")

    family_data = None

    for mt in migration_type_list:
        if family_data is not None:
            break

        for ie in is_enterprise_list:
            if family_data is not None:
                break
        
            print(f"Trying is_enterprise={ie}, migration_type={mt}.")

            payload_dict = {
                "is_show_tagging_tab": True,
                "is_dedicated_event": True,
                "is_transaction_routine": False,
                "migration_type": mt,
                "package_family_code": family_code,
                "is_autobuy": False,
                "is_enterprise": ie,
                "is_pdlp": True,
                "referral_code": "",
                "is_migration": False,
                "lang": "en"
            }
        
            res = send_api_request(api_key, path, payload_dict, id_token, "POST")

            if res.get("status") != "SUCCESS":
                continue
            
            family_name = res["data"]["package_family"].get("name", "")
            if family_name != "":
                family_data = res["data"]
                print(f"Success with is_enterprise={ie}, migration_type={mt}. Family name: {family_name}")


    if family_data is None:
        print(f"Failed to get valid family data for {family_code}")
        return None

    return family_data

def get_families(api_key: str, tokens: dict, package_category_code: str) -> dict:
    print("Fetching families...")
    path = "api/v8/xl-stores/families"
    payload_dict = {
        "migration_type": "",
        "is_enterprise": False,
        "is_shareable": False,
        "package_category_code": package_category_code,
        "with_icon_url": True,
        "is_migration": False,
        "lang": "en"
    }
    
    res = send_api_request(api_key, path, payload_dict, tokens["id_token"], "POST")
    if res.get("status") != "SUCCESS":
        print(f"Failed to get families for category {package_category_code}")
        print(f"Res:{json.dumps(res, indent=2)}")
        input("Press Enter to continue...")
        return None
    return res["data"]

def get_package(
    api_key: str,
    tokens: dict,
    package_option_code: str,
    package_family_code: str = "",
    package_variant_code: str = ""
    ) -> dict:
    path = "api/v8/xl-stores/options/detail"
    
    raw_payload = {
        "is_transaction_routine": False,
        "migration_type": "NONE",
        "package_family_code": package_family_code,
        "family_role_hub": "",
        "is_autobuy": False,
        "is_enterprise": False,
        "is_shareable": False,
        "is_migration": False,
        "lang": "en",
        "package_option_code": package_option_code,
        "is_upsell_pdp": False,
        "package_variant_code": package_variant_code
    }
    
    print("Fetching package...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if "data" not in res:
        print(json.dumps(res, indent=2))
        print("Error getting package:", res.get("error", "Unknown error"))
        return None
        
    return res["data"]

def get_addons(api_key: str, tokens: dict, package_option_code: str) -> dict:
    path = "api/v8/xl-stores/options/addons-pinky-box"
    
    raw_payload = {
        "is_enterprise": False,
        "lang": "en",
        "package_option_code": package_option_code
    }
    
    print("Fetching addons...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if "data" not in res:
        print("Error getting addons:", res.get("error", "Unknown error"))
        return None
        
    return res["data"]

def intercept_page(
    api_key: str,
    tokens: dict,
    option_code: str,
    is_enterprise: bool = False
):
    path = "misc/api/v8/utility/intercept-page"
    
    raw_payload = {
        "is_enterprise": is_enterprise,
        "lang": "en",
        "package_option_code": option_code
    }
    
    print("Fetching intercept page...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if "status" in res:
        print(f"Intercept status: {res['status']}")
    else:
        print("Intercept error")

def login_info(
    api_key: str,
    tokens: dict,
    is_enterprise: bool = False
):
    path = "api/v8/auth/login"
    
    raw_payload = {
        "access_token": tokens["access_token"],
        "is_enterprise": is_enterprise,
        "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if "data" not in res:
        print(json.dumps(res, indent=2))
        print("Error getting package:", res.get("error", "Unknown error"))
        return None
        
    return res["data"]

def get_package_details(
    api_key: str,
    tokens: dict,
    family_code: str,
    variant_code: str,
    option_order: int,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
) -> dict | None:
    family_data = get_family(api_key, tokens, family_code, is_enterprise, migration_type)
    if not family_data:
        print(f"Gagal mengambil data family untuk {family_code}.")
        return None
    
    package_options = []
    
    package_variants = family_data["package_variants"]
    option_code = None
    for variant in package_variants:
        if variant["package_variant_code"] == variant_code:
            selected_variant = variant
            package_options = selected_variant["package_options"]
            for option in package_options:
                if option["order"] == option_order:
                    selected_option = option
                    option_code = selected_option["package_option_code"]
                    break

    if option_code is None:
        print("Gagal menemukan opsi paket yang sesuai.")
        return None
        
    package_details_data = get_package(api_key, tokens, option_code)
    if not package_details_data:
        print("Gagal mengambil detail paket.")
        return None
    
    return package_details_data

def get_notifications(
    api_key: str,
    tokens: dict,
):
    path = "api/v8/notification-non-grouping"
    
    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }
    
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        print("Error getting notifications:", res.get("error", "Unknown error"))
        return None
        
    return res

def get_notification_detail(
    api_key: str,
    tokens: dict,
    notification_id: str
):
    path = "api/v8/notification/detail"
    
    raw_payload = {
        "is_enterprise": False,
        "lang": "en",
        "notification_id": notification_id
    }
    
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    if isinstance(res, dict) and res.get("status") != "SUCCESS":
        print("Error getting notification detail:", res.get("error", "Unknown error"))
        return None

    return res

def get_pending_transaction(api_key: str, tokens: dict) -> dict:
    # @TODO: implement this function properly
    path = "api/v8/profile"

    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching pending transactions...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    # {
    #     "code": "000",
    #     "data": {
    #         "pending_payment": [
    #             {
    #                 "payment_for": "BUY_PACKAGE",
    #                 "reference_id": "xxx-xxx",
    #                 "formated_date": "05 October 2025 | 11:10 WIB",
    #                 "title": "Package Purchase",
    #                 "payment_with_label": "QRIS",
    #                 "payment_id": "1234567890",
    #                 "price": "IDRxx.xxx",
    #                 "package_name": "Package Purchase",
    #                 "payment_with": "QRIS",
    #                 "payment_with_icon": "",
    #                 "raw_price": xxxxx,
    #                 "status": "FINISHED",
    #                 "timestamp": xxxxxxxxxxx,
    #             }
    #         ]
    #     },
    #     "status": "SUCCESS"
    # }

    return res.get("data")

def get_transaction_history(api_key: str, tokens: dict) -> dict:
    path = "payments/api/v8/transaction-history"

    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching transaction history...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    # print(json.dumps(res, indent=4))

# {
#   "code": "000",
#   "data": {"list": [
#     {
#       "show_time": false,
#       "code": "to get detail",
#       "payment_method_icon": "",
#       "formated_date": "",
#       "payment_status": "REFUND-SUCCESS",
#       "icon": "",
#       "title": "Xtra Edukasi 2GB, 1hr",
#       "trx_code": "",
#       "price": "IDR 2000",
#       "target_msisdn": "",
#       "payment_method_label": "XQRIS",
#       "validity": "1 Day",
#       "category": "",
#       "payment_method": "XQRIS",
#       "raw_price": 2000,
#       "timestamp": 1759523623,
#       "status": "FAILED"
#     }
#   ]},
#   "status": "SUCCESS"
# }

    return res.get("data")

def get_tiering_info(api_key: str, tokens: dict) -> dict:
    path = "gamification/api/v8/loyalties/tiering/info"

    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    # {
    # "code": "000",
    #     "data": {
    #         "latest_tier_up_date": 1755955498,
    #         "tier": 0,
    #         "current_spending": 84000,
    #         "current_point": 418,
    #         "flag_upgrade_downgrade": "NONE"
    #     },
    # "status": "SUCCESS"
    # }

    print("Fetching tiering info...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    # print(json.dumps(res, indent=4))
    
    if res:
        return res.get("data", {})
    return {}

def unsubscribe(
    api_key: str,
    tokens: dict,
    quota_code: str,
    product_domain: str,
    product_subscription_type: str,
) -> bool:
    path = "api/v8/packages/unsubscribe"

    raw_payload = {
        "product_subscription_type": product_subscription_type,
        "quota_code": quota_code,
        "product_domain": product_domain,
        "is_enterprise": False,
        "unsubscribe_reason_code": "",
        "lang": "en",
        "family_member_id": ""
    }
    
    # print(f"Payload: {json.dumps(raw_payload, indent=4)}")

    try:
        res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
        print(json.dumps(res, indent=4))

        if res and res.get("code") == "000":
            return True
        else:
            return False
    except Exception as e:
        return False

def dashboard_segments(
    api_key: str,
    tokens: dict,
) -> dict:
    path = "dashboard/api/v8/segments"

    raw_payload = {
        "access_token": tokens["access_token"],
        # "app_version": "",
        # "model_name": "",
        # "is_enterprise": False,
        # "current_balance": 0,
        # "family_plan_role": "",
        # "manufacturer_name": "",
        # "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res
