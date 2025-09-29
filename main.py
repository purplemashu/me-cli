from dotenv import load_dotenv
load_dotenv() 

import sys
from datetime import datetime

# Import UI components from app.menus
from app.menus.util import clear_screen, pause
from app.menus.account import show_account_menu
from app.menus.bookmark import show_bookmark_menu
from app.menus.hot import show_hot_menu, show_hot_menu2
from app.menus.package import show_my_packages_menu
from app.menus.family import get_packages_by_family

# Import core components from app.core
from app.core.account import get_active_account, get_account_balance

# Other imports
from app.service.auth import AuthInstance
from app.service.sentry import enter_sentry_mode

def show_main_menu(number, balance, balance_expired_at):
    """Displays the main menu with account information."""
    clear_screen()
    
    expired_at_dt_str = "N/A"
    if balance_expired_at:
        try:
            # Convert timestamp to a readable date format
            expired_at_dt = datetime.fromtimestamp(balance_expired_at)
            expired_at_dt_str = expired_at_dt.strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            expired_at_dt_str = str(balance_expired_at)

    print("-------------------------------------------------------")
    print("Informasi Akun")
    print(f"Nomor: {number}")
    print(f"Pulsa: Rp {balance}")
    print(f"Masa aktif: {expired_at_dt_str}")
    print("-------------------------------------------------------")
    print("Menu:")
    print("1. Login/Ganti akun")
    print("2. Lihat Paket Saya")
    print("3. Beli Paket 🔥 HOT 🔥")
    print("4. Beli Paket 🔥 HOT-2 🔥")
    print("5. Beli Paket Berdasarkan Family Code")
    print("00. Bookmark Paket")
    print("99. Tutup aplikasi")
    print("-------------------------------------------------------")

def main():
    """Main application loop."""
    AuthInstance.load_tokens()  # Initialize AuthInstance once
    
    while True:
        active_user = get_active_account()

        if active_user:
            # User is logged in
            balance_info = get_account_balance()
            balance_remaining = balance_info.get("remaining") if balance_info else "N/A"
            balance_expired_at = balance_info.get("expired_at") if balance_info else None

            show_main_menu(active_user["number"], balance_remaining, balance_expired_at)

            choice = input("Pilih menu: ")
            if choice == "1":
                show_account_menu()
                continue
            elif choice == "2":
                show_my_packages_menu()
                continue
            elif choice == "3":
                show_hot_menu()
            elif choice == "4":
                show_hot_menu2()
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code != "99":
                    get_packages_by_family(family_code)
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice == "s":
                enter_sentry_mode()
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # User is not logged in, force login/account selection
            selected_user_number = show_account_menu()
            if not selected_user_number:
                # This occurs if the user cancels the login/selection process
                # and there are no accounts available.
                print("Tidak ada akun yang dipilih. Aplikasi akan ditutup.")
                sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Optionally log the full traceback here for debugging
        import traceback
        traceback.print_exc()