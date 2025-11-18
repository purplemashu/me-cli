# CIRCLE
from app.client.engsel import send_api_request
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

def validate_circle_member(
    api_key: str,
    tokens: dict,
    msisdn: str,
) -> dict:
    path = "family-hub/api/v8/members/validate"
    
    encrypted_msisdn = encrypt_circle_msisdn(api_key, msisdn)

    raw_payload = {
        "msisdn": encrypted_msisdn,
        "is_enterprise": False,
        "lang": "en"
    }

    print(f"Validating {msisdn}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def invite_circle_member(
    api_key: str,
    tokens: dict,
    msisdn: str,
    name: str,
    group_id: str,
    member_id_parent: str,
) -> dict:
    path = "family-hub/api/v8/members/invite"
    
    encrypted_msisdn = encrypt_circle_msisdn(api_key, msisdn)
    print(f"Encrypted MSISDN: {encrypted_msisdn}")

    raw_payload = {
        "access_token": tokens["access_token"],
        "group_id": group_id,
        "is_enterprise": False,
        "members": [
            {
                "msisdn": encrypted_msisdn,
                "name": name
            }    
        ],
        "lang": "en",
        "member_id_parent": member_id_parent
    }
    
    print(f"Inviting {msisdn}...")
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

def create_circle(
    api_key: str,
    tokens: dict,
    parent_name: str,
    group_name: str,
    member_msisdn: str,
    member_name: str,
) -> dict:
    path = "family-hub/api/v8/groups/create"

    raw_payload = {
        "access_token": tokens["access_token"],
        "parent_name": parent_name,
        "group_name": group_name,
        "is_enterprise": False,
        "members": [
            {
                "msisdn": encrypt_circle_msisdn(api_key, member_msisdn),
                "name": member_name
            }
        ],
        "lang": "en",
    }
    
    print(f"Creating Circle with member {member_msisdn}...")
    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")
    
    return res

def spending_tracker(
    api_key: str,
    tokens: dict,
    parent_subs_id: str,
    family_id: str,
) -> dict:
    path = "gamification/api/v8/family-hub/spending-tracker"

    raw_payload = {
        "is_enterprise": False,
        "parent_subs_id": parent_subs_id,
        "family_id": family_id,
        "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res

def get_bonus_data(
    api_key: str,
    tokens: dict,
    parent_subs_id: str,
    family_id: str,
) -> dict:
    path = "gamification/api/v8/family-hub/bonus/list"

    raw_payload = {
        "is_enterprise": False,
        "parent_subs_id": parent_subs_id,
        "family_id": family_id,
        "lang": "en"
    }

    res = send_api_request(api_key, path, raw_payload, tokens["id_token"], "POST")

    return res
