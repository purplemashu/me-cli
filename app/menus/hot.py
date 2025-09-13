import requests

from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print("--------------------------")
        print("🔥 Paket Hot 🔥")
        print("--------------------------")
        
        url = "https://me.mashu.lol/pg-hot.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print("Gagal mengambil data hot package.")
            pause()
            return None

        hot_packages = response.json()

        for idx, p in enumerate(hot_packages):
            print(f"{idx + 1}. {p['family_name']} - {p['variant_name']} - {p['option_name']}")
        
        print("00. Kembali ke menu utama")
        print("--------------------------")
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
                        if option["name"] == selected_bm["option_name"]:
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