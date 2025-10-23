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
