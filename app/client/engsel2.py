import json
from app.client.engsel import send_api_request


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