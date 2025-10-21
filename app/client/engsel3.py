# CIRCLE
import json
from app.client.engsel import send_api_request
from app.menus.util import format_quota_byte
from app.client.encrypt import encrypt_circle_msisdn

def get_group_data(
    api_key: str,
    tokens: dict,
) -> dict:
    path = "family-hub/api/v8/groups/status"

    raw_payload = {
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching group detail...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def get_group_members(
    api_key: str,
    tokens: dict,
    group_id: str,
) -> dict:
    path = "family-hub/api/v8/members/info"

    raw_payload = {
        "group_id": group_id,
        "is_enterprise": False,
        "lang": "en"
    }

    print("Fetching group members...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def invite_circle_member(
    api_key: str,
    tokens: dict,
    msisdn: str,
) -> dict:
    path = "family-hub/api/v8/members/validate"
    
    encrypted_msisdn = encrypt_circle_msisdn(msisdn, api_key)

    raw_payload = {
        "msisdn": encrypted_msisdn,
        "is_enterprise": False,
        "lang": "en"
    }

    print(f"Inviting {msisdn} to Circle...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def remove_circle_member(
    api_key: str,
    tokens: dict,
    member_id: str,
    group_id: str,
    member_id_parent: str,
    is_last_member: bool = False,
) -> dict:
    path = "family-hub/api/v8/members/remove"

    raw_payload = {
        "member_id": member_id,
        "group_id": group_id,
        "is_enterprise": False,
        "is_last_member": is_last_member,
        "lang": "en",
        "member_id_parent": member_id_parent
    }
    
    print(f"Removing member {member_id} from Circle...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    return res

def accept_circle_invitation(
    api_key: str,
    tokens: dict,
    group_id: str,
    member_id: str,
) -> dict:
    path = "family-hub/api/v8/groups/accept-invitation"

    raw_payload = {
        "access_token": tokens["access_token"],
        "group_id": group_id,
        "member_id": member_id,
        "is_enterprise": False,
        "lang": "en"
    }

    print(f"Accepting invitation to Circle {group_id}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res