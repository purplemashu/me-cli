from dotenv import load_dotenv
load_dotenv()

import sys, os, json
from ui import *
from api_request import *
from paket_xut import get_package_xut
from my_package import fetch_my_packages
from paket_custom_family import get_packages_by_family
from auth_helper import AuthInstance


def login_flow():
    """Handle login or switch active user"""
    selected_user_number = show_account_menu()
    if selected_user_number:
        AuthInstance.set_active_user(selected_user_number)
    else:
        print("No user selected or failed to load user.")


def save_family_codes(family_list):
    with open("family_code.json", "w", encoding="utf-8") as f:
        json.dump(family_list, f, indent=4)


def add_family_code(family_list, type_="normal"):
    name = input(f"Masukkan nama paket baru ({type_.capitalize()}): ").strip()
    code = input("Masukkan code baru: ").strip()
    if not name or not code:
        print("Nama atau code tidak boleh kosong.")
    elif any(fc['code'] == code for fc in family_list):
        print("Code sudah ada.")
    else:
        family_list.append({"name": name, "code": code, "type": type_})
        save_family_codes(family_list)
        print(f"{type_.capitalize()} Family code berhasil ditambahkan.")
    pause()


def delete_family_code(family_list):
    del_idx = input("Masukkan nomor family code yang ingin dihapus: ").strip()
    if del_idx.isdigit() and 1 <= int(del_idx) <= len(family_list):
        removed = family_list.pop(int(del_idx)-1)
        save_family_codes(family_list)
        print(f"Family code '{removed.get('name')}' berhasil dihapus.")
    else:
        print("Pilihan tidak valid.")
    pause()


def family_code_menu():
    json_file = "family_code.json"
    if not os.path.exists(json_file):
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    with open(json_file, "r", encoding="utf-8") as f:
        family_list = json.load(f)

    while True:
        clear_screen()
        print("==== FAMILY CODE LIST ====")
        
        normal_codes = [fc for fc in family_list if fc.get("type") == "normal"]
        enterprise_codes = [fc for fc in family_list if fc.get("type") == "enterprise"]

        # Buat display list gabungan untuk mapping nomor
        display_list = normal_codes + enterprise_codes

        print("\n-- Normal Family Codes --")
        if normal_codes:
            for idx, fc in enumerate(normal_codes, start=1):
                print(f"{idx}. {fc.get('name','')} | {fc.get('code','')}")
        else:
            print("Tidak ada normal family code.")

        print("\n-- Enterprise Family Codes --")
        if enterprise_codes:
            for idx, fc in enumerate(enterprise_codes, start=1+len(normal_codes)):
                print(f"{idx}. {fc.get('name','')} | {fc.get('code','')}")
        else:
            print("Tidak ada enterprise family code.")

        print("\n==== COMMANDS ====")
        print("A. Tambah Family Code (Normal)")
        print("E. Tambah Family Code (Enterprise)")
        print("H. Hapus Family Code")
        print("99. Kembali")

        selection = input("\nPilihan: ").strip().upper()

        if selection == "99":
            break
        elif selection == "A":
            add_family_code(family_list, type_="normal")
        elif selection == "E":
            add_family_code(family_list, type_="enterprise")
        elif selection == "H":
            delete_family_code(family_list)
        elif selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(display_list):
                fc = display_list[idx]
                is_enterprise = fc.get("type") == "enterprise"
                get_packages_by_family(fc.get("code"), is_enterprise=is_enterprise)
                pause()
            else:
                print("Pilihan tidak valid.")
                pause()
        else:
            print("Pilihan tidak valid.")
            pause()


def main():
    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"]) or {}
            balance_remaining = balance.get("remaining", 0)
            balance_expired_at = balance.get("expired_at", "N/A")

            show_main_menu(active_user["number"], balance_remaining, balance_expired_at)

            choice = input("Pilih menu: ").strip()
            if choice == "1":
                login_flow()
            elif choice == "2":
                fetch_my_packages()
            elif choice == "3":
                # XUT
                packages = get_package_xut()
                show_package_menu(packages)
            elif choice == "4":
                family_code = input("Enter family code (or '99' to cancel): ").strip()
                if family_code != "99":
                    get_packages_by_family(family_code)
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ").strip()
                if family_code != "99":
                    get_packages_by_family(family_code, is_enterprise=True)
            elif choice == "6":
                # FAMILY CODE MANAGEMENT
                family_code_menu()
            elif choice == "99":
                print("Exiting the application.")
                return
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            login_flow()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    except Exception as e:
        print(f"An error occurred: {e}")
            elif choice == "3":
                # XUT 
                packages = get_package_xut()
                
                show_package_menu(packages)
            elif choice == "4":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "5":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code, is_enterprise=True)
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
                pause()
        else:
            # Not logged in
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
            else:
                print("No user selected or failed to load user.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
