from app.client.engsel import send_api_request

def get_family_list(
    api_key: str,
    tokens: dict,
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    path = "api/v8/xl-stores/options/search/family-list"
    payload = {
        "is_enterprise": is_enterprise,
        "subs_type": subs_type,
        "lang": "en"
    }
    
    res = send_api_request(api_key, path, payload, tokens["id_token"], "POST")
    if res["status"] != "SUCCESS":
        print("Failed to fetch family list.")
        print(f"Error: {res}")
        return None
    
    return res

def get_store_packages(
    api_key: str,
    tokens: dict,
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    path = "api/v9/xl-stores/options/search"
    payload = {
        "is_enterprise": is_enterprise,
        "filters": [
            {
                "unit": "THOUSAND",
                "id": "FIL_SEL_P",
                "type": "PRICE",
                "items": []
            },
            {
                "unit": "GB",
                "id": "FIL_SEL_MQ",
                "type": "DATA_TYPE",
                "items": []
            },
                {
                "unit": "PACKAGE_NAME",
                "id": "FIL_PKG_N",
                "type": "PACKAGE_NAME",
                "items": [{
                    "id": "",
                    "label": ""
                }]
            },
            {
                "unit": "DAY",
                "id": "FIL_SEL_V",
                "type": "VALIDITY",
                "items": []
            }
        ],
        "substype": subs_type,
        "text_search": "",
        "lang": "en"
    }
    
    res = send_api_request(api_key, path, payload, tokens["id_token"], "POST")
    if res["status"] != "SUCCESS":
        print("Failed to fetch store packages.")
        print(f"Error: {res}")
        return None
    
    return res