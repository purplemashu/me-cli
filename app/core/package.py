"""
Handles the core logic for package management and purchasing.
"""
from app.client.engsel import get_package, get_addons, send_api_request, get_family_v2
from app.client.purchase import settlement_bounty
from app.client.ewallet import show_multipayment_v2
from app.client.qris import show_qris_payment_v2
from app.client.balance import settlement_balance
from app.type_dict import PaymentItem

def get_package_full_details(api_key: str, tokens, package_option_code: str):
    """
    Gathers all necessary details for a package: main info, addons, and payment items.
    """
    package = get_package(api_key, tokens, package_option_code)
    if not package:
        return None

    addons = get_addons(api_key, tokens, package_option_code)

    payment_items = [
        PaymentItem(
            item_code=package_option_code,
            product_type="",
            item_price=package["package_option"]["price"],
            item_name=package["package_option"]["name"],
            tax=0,
            token_confirmation=package["token_confirmation"],
        )
    ]

    # Here you could add logic to auto-select bonuses from addons if desired
    # For now, we'll keep it simple.

    return {
        "package": package,
        "addons": addons,
        "payment_items": payment_items,
        "token_confirmation": package.get("token_confirmation"),
        "timestamp": package.get("timestamp")
    }

def list_packages_in_family(api_key: str, tokens, family_code: str, is_enterprise: bool = False, migration_type: str = None):
    """
    Fetches the raw data for all packages within a specific family.
    """
    return get_family_v2(api_key, tokens, family_code, is_enterprise, migration_type)

def get_my_package_list(api_key: str, tokens):
    """
    Fetches the list of packages currently owned by the user.
    """
    id_token = tokens.get("id_token")
    path = "api/v8/packages/quota-details"
    payload = {"is_enterprise": False, "lang": "en", "family_member_id": ""}

    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        return None # Indicates failure

    quotas = res["data"]["quotas"]
    my_packages = []

    for quota in quotas:
        package_details = get_package(api_key, tokens, quota["quota_code"])
        family_code = "N/A"
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        my_packages.append({
            "name": quota["name"],
            "quota_code": quota["quota_code"],
            "family_code": family_code,
        })

    return my_packages

def purchase_with_balance(api_key: str, tokens, payment_items: list[PaymentItem]):
    """Initiates a purchase using the account's credit balance."""
    return settlement_balance(api_key, tokens, payment_items, ask_overwrite=True)

def purchase_with_ewallet(api_key: str, tokens, payment_items: list[PaymentItem]):
    """Initiates a purchase using an e-wallet."""
    return show_multipayment_v2(api_key, tokens, payment_items)

def purchase_with_qris(api_key: str, tokens, payment_items: list[PaymentItem]):
    """Initiates a purchase using QRIS."""
    return show_qris_payment_v2(api_key, tokens, payment_items)

def claim_package_as_bonus(api_key: str, tokens, package_details: dict):
    """Claims a package as a bonus (e.g., for voucher redemption)."""
    package = package_details["package"]
    return settlement_bounty(
        api_key=api_key,
        tokens=tokens,
        token_confirmation=package_details["token_confirmation"],
        ts_to_sign=package_details["timestamp"],
        payment_target=package["package_option"]["package_option_code"],
        price=package["package_option"]["price"],
        item_name=package["package_option"]["name"]
    )