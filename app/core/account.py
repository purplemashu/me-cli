"""
Handles the core logic for account management.
"""
from app.client.engsel import get_otp, submit_otp, get_balance
from app.service.auth import AuthInstance

def login(phone_number: str):
    """Requests an OTP for the given phone number."""
    return get_otp(phone_number)

def verify_otp(phone_number: str, otp: str):
    """Submits the OTP to get authentication tokens."""
    api_key = AuthInstance.api_key
    return submit_otp(api_key, phone_number, otp)

def add_account(phone_number: int, refresh_token: str):
    """Adds a new account to the auth instance."""
    AuthInstance.add_refresh_token(phone_number, refresh_token)

def remove_account(phone_number: int):
    """Removes an account from the auth instance."""
    AuthInstance.remove_refresh_token(phone_number)

def list_accounts():
    """Lists all saved accounts."""
    return AuthInstance.refresh_tokens

def set_active_account(phone_number: int):
    """Sets the active user."""
    AuthInstance.set_active_user(phone_number)

def get_active_account():
    """Gets the currently active user."""
    return AuthInstance.get_active_user()

def get_account_balance():
    """Gets the balance for the currently active user."""
    active_user = AuthInstance.get_active_user()
    if not active_user:
        print("No active user found.")
        return None

    api_key = AuthInstance.api_key
    id_token = active_user["tokens"]["id_token"]

    balance_info = get_balance(api_key, id_token)

    if balance_info:
        return {
            "remaining": balance_info.get("remaining"),
            "expired_at": balance_info.get("expired_at")
        }
    return None