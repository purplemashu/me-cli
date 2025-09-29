"""
Handles the core logic for "Hot" packages.
"""
import requests
from app.client.engsel import get_family_v2, get_package_details
from app.type_dict import PaymentItem

def get_hot_packages(url: str):
    """Fetches hot package data from a given URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_hot_package_details(api_key: str, tokens, package_info: dict):
    """
    Retrieves package details for a selected hot package.
    """
    family_code = package_info.get("family_code")
    is_enterprise = package_info.get("is_enterprise")
    variant_name = package_info.get("variant_name")
    order = package_info.get("order")

    family_data = get_family_v2(api_key, tokens, family_code, is_enterprise)
    if not family_data:
        return None

    package_variants = family_data.get("package_variants", [])
    for variant in package_variants:
        if variant.get("name") == variant_name:
            package_options = variant.get("package_options", [])
            for option in package_options:
                if option.get("order") == order:
                    return {
                        "option_code": option.get("package_option_code"),
                        "is_enterprise": is_enterprise
                    }
    return None

def prepare_hot_package_payment(api_key: str, tokens, selected_package: dict):
    """
    Prepares a list of PaymentItem objects for a multi-package purchase.
    """
    packages = selected_package.get("packages", [])
    if not packages:
        return None

    payment_items = []
    for package in packages:
        package_detail = get_package_details(
            api_key,
            tokens,
            package["family_code"],
            package["variant_code"],
            package["order"],
            package["is_enterprise"],
        )

        if not package_detail:
            # If one package fails, the whole transaction fails.
            return None

        payment_items.append(
            PaymentItem(
                item_code=package_detail["package_option"]["package_option_code"],
                product_type="",
                item_price=package_detail["package_option"]["price"],
                item_name=package_detail["package_option"]["name"],
                tax=0,
                token_confirmation=package_detail["token_confirmation"],
            )
        )
    return payment_items