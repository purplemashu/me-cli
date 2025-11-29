import json

from app.service.auth import AuthInstance
from app.menus.util import pause, clear_screen
from app.client.engsel import get_balance
from app.client.sharing import balance_allotment
from app.client.ciam import get_auth_code

WIDTH = 55

def show_balance_allotment_menu():
    active_user = AuthInstance.get_active_user()
    
    balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
    clear_screen()
    balance_remaining = balance.get("remaining")
    
    print("=" * WIDTH)
    print(f"BALANCE SHARING | Rp {balance_remaining}".center(WIDTH))
    print("-" * WIDTH)
    print("Make sure you've set up your transaction PIN in MyXL".center(WIDTH))
    print("=" * WIDTH)
    
    pin = input("Enter your 6-digit PIN: ")
    if len(pin) != 6 or not pin.isdigit():
        print("Invalid PIN format. Aborting balance sharing.")
        pause()
        return
    
    stage_token = get_auth_code(
        active_user["tokens"],
        pin,
        active_user["number"]
    )
    
    if stage_token is None:
        print("Failed to get stage token. Aborting balance allotment.")
        pause()
        return
    
    receiver_msisdn = input("Enter receiver MSISDN (628xxxx): ")
    amount_str = input("Enter amount to send (5000): ")
    amount = int(amount_str)
    
    res = balance_allotment(
        AuthInstance.api_key,
        active_user["tokens"],
        stage_token,
        receiver_msisdn,
        amount,
    )
    if res is None:
        print("Balance allotment failed.")
        pause()
        return
        
    print(json.dumps(res, indent=2))
    pause()
    return res
