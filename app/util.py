import os
import sys
import requests

# Load API key from text file named api.key
def load_api_key() -> str:
    if os.path.exists("api.key"):
        with open("api.key", "r", encoding="utf8") as f:
            api_key = f.read().strip()
        if api_key:
            print("API key loaded successfully.")
            return api_key
        else:
            print("API key file is empty.")
            return ""
    else:
        print("API key file not found.")
        return ""
    
def save_api_key(api_key: str):
    with open("api.key", "w", encoding="utf8") as f:
        f.write(api_key)
    print("API key saved successfully.")
    
def delete_api_key():
    if os.path.exists("api.key"):
        os.remove("api.key")
        print("API key file deleted.")
    else:
        print("API key file does not exist.")

def verify_api_key(api_key: str, *, timeout: float = 10.0) -> bool:
    """
    Returns True iff the verification endpoint responds with HTTP 200.
    Any network error or non-200 is treated as invalid.
    """
    try:
        url = f"https://crypto.mashu.lol/api/verify?key={api_key}"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            json_resp = resp.json()
            print(
                f"API key is valid.\n"
                f"Id: {json_resp.get('user_id')}\n"
                f"Owner: @{json_resp.get('username')}\n"
                f"Credit: {json_resp.get('credit')}\n"
                f"Premium Credit: {json_resp.get('premium_credit')}\n"
            )

            return True
        else:
            print(f"API key is invalid. Server responded with status code {resp.status_code}.")
            return False
    except requests.RequestException as e:
        print(f"Failed to verify API key: {e}")
        return False

def get_user_info(api_key: str, *, timeout: float = 10.0) -> dict:
    """
    Fetch user info from the API.
    Raises an exception if the request fails or the API key is invalid.
    """
    try:
        url = f"https://crypto.mashu.lol/api/verify?key={api_key}"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Failed to fetch user info: {resp.status_code} {resp.text}")
    except requests.RequestException as e:
        raise Exception(f"Network error while fetching user info: {e}") from e

def ensure_api_key() -> str:
    """
    Load api.key if present; otherwise use a dummy key.
    No verification required - authentication removed.
    """
    # Try to load an existing key
    current = load_api_key()
    if current:
        print("API key loaded from file.")
        return current

    # Use dummy key if no key file exists
    print("No API key file found. Using default configuration.")
    print("Note: Some features may require a valid crypto service endpoint.")

    # Create a dummy API key
    dummy_key = "no-auth-required"
    save_api_key(dummy_key)
    return dummy_key
