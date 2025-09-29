"""
Handles the core logic for fetching package families.
"""
from app.client.engsel import get_family

def get_packages_by_family(api_key: str, tokens, family_code: str, is_enterprise: bool = False):
    """
    Fetches package data for a given family code.
    """
    return get_family(api_key, tokens, family_code, is_enterprise)