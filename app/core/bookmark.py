"""
Handles the core logic for bookmark management.
"""
from app.client.engsel import get_family
from app.service.auth import AuthInstance
from app.service.bookmark import BookmarkInstance

def get_all_bookmarks():
    """Returns all saved bookmarks."""
    return BookmarkInstance.get_bookmarks()

def add_bookmark(family_code, is_enterprise, family_name, variant_name, option_name, order):
    """Adds a new bookmark."""
    BookmarkInstance.add_bookmark(family_code, is_enterprise, family_name, variant_name, option_name, order)

def remove_bookmark(family_code, is_enterprise, variant_name, order):
    """Removes a bookmark."""
    BookmarkInstance.remove_bookmark(family_code, is_enterprise, variant_name, order)

def remove_bookmark_by_index(index: int):
    """Removes a bookmark by its index in the list."""
    bookmarks = get_all_bookmarks()
    if 0 <= index < len(bookmarks):
        bm = bookmarks[index]
        remove_bookmark(
            bm["family_code"],
            bm["is_enterprise"],
            bm["variant_name"],
            bm["order"],
        )
        return True
    return False

def get_package_details_for_bookmark(index: int):
    """
    Retrieves package details for a bookmarked item.
    """
    bookmarks = get_all_bookmarks()
    if not (0 <= index < len(bookmarks)):
        return None

    selected_bm = bookmarks[index]
    family_code = selected_bm["family_code"]
    is_enterprise = selected_bm["is_enterprise"]

    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    family_data = get_family(api_key, tokens, family_code, is_enterprise)
    if not family_data:
        return None

    package_variants = family_data.get("package_variants", [])
    for variant in package_variants:
        if variant.get("name") == selected_bm["variant_name"]:
            package_options = variant.get("package_options", [])
            for option in package_options:
                if option.get("order") == selected_bm["order"]:
                    return {
                        "option_code": option.get("package_option_code"),
                        "is_enterprise": is_enterprise
                    }
    return None