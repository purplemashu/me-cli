"""
Handles the user interface for package management.
"""
import json
from app.menus.util import clear_screen, pause, display_html
from app.core.package import (
    get_package_full_details,
    list_packages_in_family,
    get_my_package_list,
    purchase_with_balance,
    purchase_with_ewallet,
    purchase_with_qris,
    claim_package_as_bonus,
)
from app.core.bookmark import add_bookmark
from app.service.auth import AuthInstance

def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1):
    """Displays details for a specific package and provides purchase options."""
    clear_screen()
    print("Fetching package details...")

    details = get_package_full_details(api_key, tokens, package_option_code)
    if not details:
        print("Failed to load package details.")
        pause()
        return False

    package = details["package"]
    addons = details["addons"]
    payment_items = details["payment_items"]

    # Extract data for display
    price = package["package_option"]["price"]
    tnc_html = package["package_option"]["tnc"]
    validity = package["package_option"]["validity"]
    family_name = package.get("package_family", {}).get("name", "")
    variant_name = package.get("package_detail_variant", {}).get("name", "")
    option_name = package.get("package_option", {}).get("name", "")
    title = f"{family_name} - {variant_name} - {option_name}".strip()
    
    # Print details
    print("-------------------------------------------------------")
    print("Detail Paket")
    print("-------------------------------------------------------")
    print(f"Nama: {title}")
    print(f"Harga: Rp {price}")
    print(f"Masa Aktif: {validity}")
    print(f"Point: {package['package_option']['point']}")
    print(f"Plan Type: {package['package_family']['plan_type']}")
    print("-------------------------------------------------------")

    # Print benefits
    benefits = package["package_option"]["benefits"]
    if benefits and isinstance(benefits, list):
        print("Benefits:")
        for benefit in benefits:
            print("-------------------------------------------------------")
            # ... (benefit display logic remains the same) ...
    print("-------------------------------------------------------")
    
    # Print TnC
    print(f"SnK MyXL:\n{display_html(tnc_html)}")
    print("-------------------------------------------------------")

    # Menu loop
    in_package_detail_menu = True
    while in_package_detail_menu:
        print("Options:")
        print("1. Beli dengan Pulsa")
        print("2. Beli dengan E-Wallet")
        print("3. Bayar dengan QRIS")
        
        if package["package_family"]["payment_for"] == "REDEEM_VOUCHER":
            print("4. Ambil sebagai bonus (jika tersedia)")
        
        if option_order != -1:
            print("0. Tambah ke Bookmark")
        print("00. Kembali")

        choice = input("Pilihan: ")
        if choice == "00":
            return False

        if choice == "0" and option_order != -1:
            success = add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code",""),
                is_enterprise=is_enterprise,
                family_name=family_name,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            if success:
                print("Paket berhasil ditambahkan ke bookmark.")
            else:
                print("Paket sudah ada di bookmark.")
            pause()
            continue
        
        if choice == '1':
            purchase_with_balance(api_key, tokens, payment_items)
            input("Silahkan cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '2':
            purchase_with_ewallet(api_key, tokens, payment_items)
            input("Silahkan lakukan pembayaran & cek hasil pembelian. Tekan Enter untuk kembali.")
            return True
        elif choice == '3':
            purchase_with_qris(api_key, tokens, payment_items)
            input("Silahkan lakukan pembayaran & cek hasil pembelian. Tekan Enter untuk kembali.")
            return True
        elif choice == '4' and package["package_family"]["payment_for"] == "REDEEM_VOUCHER":
            claim_package_as_bonus(api_key, tokens, details)
            input("Silahkan cek hasil pengambilan bonus di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        else:
            print("Pilihan tidak valid.")
            pause()


def show_family_packages_menu(family_code: str, is_enterprise: bool = False):
    """UI for browsing and selecting packages from a family."""
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    data = list_packages_in_family(api_key, tokens, family_code, is_enterprise)
    if not data:
        print("Gagal memuat data family.")
        pause()
        return

    in_package_menu = True
    while in_package_menu:
        clear_screen()
        print("-------------------------------------------------------")        
        print(f"Family Name: {data['package_family']['name']}")
        # ... (other family details) ...
        print("-------------------------------------------------------")
        print("Paket Tersedia")
        print("-------------------------------------------------------")
        
        # This part needs to be adapted to the new core function's return value
        all_options = []
        option_number = 1
        for variant in data["package_variants"]:
            print(f"--- {variant['name']} ---")
            for option in variant["package_options"]:
                all_options.append(option)
                print(f"  {option_number}. {option['name']} - Rp {option['price']}")
                option_number += 1

        print("-------------------------------------------------------")
        print("00. Kembali")
        pkg_choice = input("Pilih paket (nomor): ")

        if pkg_choice == "00":
            return
        
        if pkg_choice.isdigit() and 1 <= int(pkg_choice) <= len(all_options):
            selected_option = all_options[int(pkg_choice) - 1]
            # Now call the detail view
            is_done = show_package_details(
                api_key,
                tokens,
                selected_option['package_option_code'],
                is_enterprise,
                option_order=selected_option['order']
            )
            if is_done:
                in_package_menu = False # Exit after purchase
        else:
            print("Pilihan tidak valid.")
            pause()

def show_my_packages_menu():
    """UI for displaying and re-buying user's active packages."""
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    clear_screen()
    print("Fetching my packages...")
    my_packages = get_my_package_list(api_key, tokens)

    if my_packages is None:
        print("Gagal mengambil daftar paket.")
        pause()
        return

    clear_screen()
    print("=======================================================")
    print("======================My Packages======================")
    print("=======================================================")
    
    if not my_packages:
        print("Tidak ada paket aktif.")
        pause()
        return

    for idx, pkg in enumerate(my_packages):
        print(f"{idx + 1}. {pkg['name']}")
        print(f"   Quota Code: {pkg['quota_code']}")
        print(f"   Family Code: {pkg['family_code']}")
        print("-------------------------------------------------------")

    choice = input("Pilih paket untuk dibeli ulang (nomor), atau 00 untuk kembali: ")
    if choice == "00":
        return
    
    if choice.isdigit() and 1 <= int(choice) <= len(my_packages):
        selected_pkg = my_packages[int(choice) - 1]
        show_package_details(api_key, tokens, selected_pkg['quota_code'], is_enterprise=False)
    else:
        print("Pilihan tidak valid.")
        pause()