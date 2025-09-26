import requests

from app.client.engsel import get_family, get_package_details
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause
from app.client.ewallet import show_multipayment_v2
from app.client.qris import show_qris_payment_v2
from app.type_dict import PaymentItem

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print("=======================================================")
        print("====================🔥 Paket  Hot 🔥===================")
        print("=======================================================")
        
        url = "https://me.mashu.lol/pg-hot.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print("Gagal mengambil data hot package.")
            pause()
            return None

        hot_packages = response.json()

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['family_name']} - {p['variant_name']} - {p['option_name']}")
            print("-------------------------------------------------------")
        
        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        choice = input("Pilih paket (nomor): ")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print("Gagal mengambil data family.")
                pause()
                continue
            
            package_variants = family_data["package_variants"]
            option_code = None
            for variant in package_variants:
                if variant["name"] == selected_bm["variant_name"]:
                    selected_variant = variant
                    
                    package_options = selected_variant["package_options"]
                    for option in package_options:
                        if option["order"] == selected_bm["order"]:
                            selected_option = option
                            option_code = selected_option["package_option_code"]
                            break
            
            if option_code:
                print(f"{option_code}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue

def show_hot_menu2():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print("=======================================================")
        print("===================🔥 Paket  Hot 2 🔥==================")
        print("=======================================================")
        
        url = "https://me.mashu.lol/pg-hot2.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print("Gagal mengambil data hot package.")
            pause()
            return None

        hot_packages = response.json()

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['name']}\n   Harga: {p['price']}")
        
        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        choice = input("Pilih paket (nomor): ")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if len(packages) == 0:
                print("Paket tidak tersedia.")
                pause()
                continue
            
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
                
                # Force failed when one of the package detail is None
                if not package_detail:
                    print(f"Gagal mengambil detail paket untuk {package['family_code']}.")
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
            
            clear_screen()
            print("=======================================================")
            print(f"Name: {selected_package['name']}")
            print(f"Price: {selected_package['price']}")
            print(f"Detail: {selected_package['detail']}")
            print("=======================================================")
            
            in_payment_menu = True
            while in_payment_menu:
                print("Pilih Metode Pembelian:")
                print("1. E-Wallet")
                print("2. QRIS")
                print("00. Kembali ke menu sebelumnya")
                
                input_method = input("Pilih metode (nomor): ")
                if input_method == "1":
                    show_multipayment_v2(
                        api_key,
                        tokens,
                        payment_items
                    )
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_bookmark_menu = False
                    return None
                elif input_method == "2":
                    show_qris_payment_v2(
                        api_key,
                        tokens,
                        payment_items
                    )
                    input("Tekan enter untuk kembali...")
                    in_payment_menu = False
                    in_bookmark_menu = False
                    return None
                elif input_method == "00":
                    in_payment_menu = False
                    continue
                else:
                    print("Metode tidak valid. Silahkan coba lagi.")
                    pause()
                    continue       
            
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue
