"""
Bot entry point for the MyXL CLI application.

This file provides a set of functions that can be easily integrated with a bot
framework (e.g., Telegram, Discord, etc.). It uses the core logic of the
application to perform actions without dealing with the command-line interface.

How to use:
1. Import the functions you need into your bot's main script.
2. Initialize the application by calling `initialize_bot()`.
3. Use the functions to interact with the MyXL service.

Example:
    from bot import initialize_bot, bot_list_accounts, bot_get_balance

    def main():
        initialize_bot()
        accounts = bot_list_accounts()
        print("Available accounts:", accounts)
        balance = bot_get_balance()
        if balance:
            print(f"Current balance: Rp {balance['remaining']}")

    if __name__ == "__main__":
        main()
"""
from dotenv import load_dotenv
from app.service.auth import AuthInstance
from app.core.account import (
    list_accounts,
    set_active_account,
    get_active_account,
    get_account_balance
)
from app.core.package import get_my_package_list, list_packages_in_family
from app.core.hot import get_hot_packages
from app.core.bookmark import get_all_bookmarks, get_package_details_for_bookmark

def initialize_bot():
    """
    Initializes the bot environment.
    This must be called once before any other bot functions.
    """
    print("Initializing bot...")
    load_dotenv()
    AuthInstance.load_tokens()
    print("Bot initialized.")

# --- Account Functions ---

def bot_list_accounts():
    """
    Lists all saved user accounts.
    Returns a list of account dictionaries.
    """
    return list_accounts()

def bot_set_active_account(phone_number: int):
    """
    Sets the active account.
    Returns True if successful, False otherwise.
    """
    accounts = list_accounts()
    if any(acc['number'] == phone_number for acc in accounts):
        set_active_account(phone_number)
        return True
    return False

def bot_get_active_account():
    """
    Gets the currently active account.
    Returns the active account dictionary or None.
    """
    return get_active_account()

def bot_get_balance():
    """
    Gets the balance for the active account.
    Returns a dictionary with 'remaining' and 'expired_at' keys, or None.
    """
    return get_account_balance()

# --- Package Functions ---

def bot_list_my_packages():
    """
    Lists the packages owned by the active user.
    Returns a list of package dictionaries or None.
    """
    active_user = get_active_account()
    if not active_user:
        return None
    api_key = AuthInstance.api_key
    tokens = active_user.get("tokens")
    return get_my_package_list(api_key, tokens)

def bot_list_packages_by_family(family_code: str):
    """
    Lists all packages available in a given family.
    Returns the raw family data dictionary or None.
    """
    active_user = get_active_account()
    if not active_user:
        return None
    api_key = AuthInstance.api_key
    tokens = active_user.get("tokens")
    return list_packages_in_family(api_key, tokens, family_code)


# --- Hot & Bookmark Functions ---

def bot_list_hot_packages(url: str = "https://me.mashu.lol/pg-hot.json"):
    """
    Lists hot packages from a given URL.
    """
    return get_hot_packages(url)

def bot_list_bookmarks():
    """
    Lists all saved bookmarks.
    """
    return get_all_bookmarks()

def bot_get_bookmarked_package_details(bookmark_index: int):
    """
    Gets the details needed to purchase a bookmarked package.
    Returns a dictionary with 'option_code' and 'is_enterprise', or None.
    """
    return get_package_details_for_bookmark(bookmark_index)


if __name__ == '__main__':
    # This is an example of how you could use these functions.
    # You would typically call these from your actual bot code.

    initialize_bot()

    print("\n--- Testing Account Functions ---")
    accounts = bot_list_accounts()
    if not accounts:
        print("No accounts found. Please run main.py to add an account first.")
    else:
        print(f"Found {len(accounts)} accounts.")
        print(accounts)
        first_account_number = accounts[0]['number']
        print(f"Setting active account to: {first_account_number}")
        success = bot_set_active_account(first_account_number)
        if success:
            active_acc = bot_get_active_account()
            print(f"Active account is now: {active_acc['number']}")

            balance = bot_get_balance()
            if balance:
                print(f"Balance: Rp {balance['remaining']}, Expires: {balance['expired_at']}")
            else:
                print("Could not retrieve balance.")
        else:
            print("Failed to set active account.")

    print("\n--- Testing Package Functions ---")
    my_packages = bot_list_my_packages()
    if my_packages:
        print(f"User has {len(my_packages)} packages.")
        if my_packages:
            print(my_packages[0]) # print first one
    else:
        print("Could not retrieve user's packages.")

    print("\n--- Testing Hot Packages ---")
    hot_packages = bot_list_hot_packages()
    if hot_packages:
        print(f"Found {len(hot_packages)} hot packages.")
        if hot_packages:
            print(hot_packages[0]) # print first one
    else:
        print("Could not retrieve hot packages.")