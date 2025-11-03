import json
from app.client.engsel import send_api_request
from app.menus.util import format_quota_byte


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

def get_family_data(
    api_key: str,
    tokens: dict,
) -> dict:
    path = "sharings/api/v8/family-plan/member-info"

    raw_payload = {
        "group_id": 0,
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching family data...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def validate_msisdn(
    api_key: str,
    tokens: dict,
    msisdn: str,
) -> dict:
    # path = "api/v8/auth/validate-msisdn"
    path = "api/v8/auth/check-dukcapil"

    raw_payload = {
        "with_bizon": True,
        "with_family_plan": True,
        "is_enterprise": False,
        "with_optimus": True,
        "lang": "en",
        "msisdn": msisdn,
        "with_regist_status": True,
        "with_enterprise": True
    }

    print(f"Validating msisdn {msisdn}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def change_member(
    api_key: str,
    tokens: dict,
    parent_alias: str,
    alias: str,
    slot_id: int,
    family_member_id: str,
    new_msisdn: str,
) -> dict:
    path = "sharings/api/v8/family-plan/change-member"

    raw_payload = {
        "parent_alias": parent_alias,
        "is_enterprise": False,
        "slot_id": slot_id,
        "alias": alias,
        "lang": "en",
        "msisdn": new_msisdn,
        "family_member_id": family_member_id
    }
    
    print(f"Assigning slot {slot_id} to {new_msisdn}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def remove_member(
    api_key: str,
    tokens: dict,
    family_member_id: str,
) -> dict:
    path = "sharings/api/v8/family-plan/remove-member"

    raw_payload = {
        "is_enterprise": False,
        "family_member_id": family_member_id,
        "lang": "en"
    }

    print(f"Removing family member {family_member_id}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def set_quota_limit(
    api_key: str,
    tokens: dict,
    original_allocation: int,
    new_allocation: int,
    family_member_id: str,
) -> dict:
    path = "sharings/api/v8/family-plan/allocate-quota"

    raw_payload = {
        "is_enterprise": False,
        "member_allocations": [{
            "new_text_allocation": 0,
            "original_text_allocation": 0,
            "original_voice_allocation": 0,
            "original_allocation": original_allocation,
            "new_voice_allocation": 0,
            "message": "",
            "new_allocation": new_allocation,
            "family_member_id": family_member_id,
            "status": ""
        }],
        "lang": "en"
    }
    
    formatted_new_allocation = format_quota_byte(new_allocation)

    print(f"Setting quota limit for family member {family_member_id} to {formatted_new_allocation} MB...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res
