from app.client.engsel import send_api_request

def validate_puk(
    api_key: str,
    msisdn: str,
    puk: str,
) -> dict:
    path = "api/v8/infos/validate-puk"

    raw_payload = {
        "is_enterprise": False,
        "puk": puk,
        "is_enc": False,
        "msisdn": msisdn,
        "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, "", "POST")

    return res

def dukcapil(
    api_key: str,
    msisdn: str,
    kk: str,
    nik: str,
) -> dict:
    path = "api/v8/auth/regist/dukcapil"

    raw_payload = {
        "msisdn": msisdn,
        "kk": kk,
        "nik": nik,
        "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, "", "POST")

    return res
