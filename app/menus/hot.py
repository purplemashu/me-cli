"""
Handles the user interface for "Hot" packages.
"""
from app.core.hot import get_hot_packages, get_hot_package_details, prepare_hot_package_payment
from app.menus.package import show_package_details
from app.menus.util import clear_screen, pause
from app.client.ewallet import show_multipayment_v2
from app.client.qris import show_qris_payment_v2
from app.service.auth import AuthInstance

def show_hot_menu():
    """UI for the first Hot Packages menu."""
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    url = "https://me.mashu.lol/pg-hot.json"
    hot_packages = get_hot_packages(url)

    if hot_packages is None:
        print("Gagal mengambil data hot package.")
        pause()
        return

    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        print("=======================================================")
        print("====================🔥 Paket  Hot 🔥===================")
        print("=======================================================")

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['family_name']} - {p['variant_name']} - {p['option_name']}")
            print("-------------------------------------------------------")
        
        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        choice = input("Pilih paket (nomor): ")

        if choice == "00":
            in_hot_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_pkg_info = hot_packages[int(choice) - 1]
            package_details = get_hot_package_details(api_key, tokens, selected_pkg_info)

            if package_details and package_details.get("option_code"):
                show_package_details(api_key, tokens, package_details["option_code"], package_details["is_enterprise"])
            else:
                print("Gagal mengambil detail paket.")
                pause()
        else:
            print("Input tidak valid.")
            pause()

def show_hot_menu2():
    """UI for the second Hot Packages menu."""
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    url = "https://me.mashu.lol/pg-hot2.json"
    hot_packages = get_hot_packages(url)

    if hot_packages is None:
        print("Gagal mengambil data hot package.")
        pause()
        return

    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        print("=======================================================")
        print("===================🔥 Paket  Hot 2 🔥==================")
        print("=======================================================")

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['name']}\n   Harga: {p['price']}")
        
        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        choice = input("Pilih paket (nomor): ")

        if choice == "00":
            in_hot_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]

            payment_items = prepare_hot_package_payment(api_key, tokens, selected_package)
            if not payment_items:
                print("Gagal mempersiapkan item pembayaran.")
                pause()
                continue

            # --- Payment Menu ---
            clear_screen()
            print("=======================================================")
            print(f"Name: {selected_package['name']}")
            print(f"Price: {selected_package['price']}")
            print(f"Detail: {selected_package['detail']}")
            print("=======================================================")
            
            in_payment_menu = True
            while in_payment_menu:
                print("\nPilih Metode Pembelian:")
                print("1. E-Wallet")
                print("2. QRIS")
                print("00. Kembali")
                
                input_method = input("Pilih metode (nomor): ")
                if input_method == "1":

                    show_multipayment_v2(api_key, tokens, payment_items)

                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_hot_menu = False # Exit outer loop as well
                elif input_method == "2":
                    show_qris_payment_v2(api_key, tokens, payment_items)
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_hot_menu = False # Exit outer loop as well
                elif input_method == "00":
                    in_payment_menu = False
                else:
                    print("Metode tidak valid.")
                    pause()
        else:
            print("Input tidak valid.")
            pause()