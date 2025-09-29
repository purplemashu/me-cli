"""
Handles the user interface for browsing packages by family.
"""
from app.core.family import get_packages_by_family as get_packages_by_family_logic
from app.menus.util import clear_screen, pause
from app.menus.package import show_package_details
from app.service.auth import AuthInstance

def get_packages_by_family(family_code: str):
    """
    UI flow for fetching and displaying packages from a specific family.
    """
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()

    clear_screen()
    print(f"Mencari paket untuk family code: {family_code}...")

    family_data = get_packages_by_family_logic(api_key, tokens, family_code, is_enterprise=False) # Assuming not enterprise for now

    if not family_data:
        print("Gagal mengambil data family atau family tidak ditemukan.")
        pause()
        return

    print("-------------------------------------------------------")
    print(f"Paket untuk {family_data['name']}")
    print("---------------------------------")
    print(f"{family_data['description']}")
    print("-------------------------------------------------------")

    all_options = []
    for variant in family_data.get("package_variants", []):
        print(f"\n--- {variant['name']} ---")
        for option in variant.get("package_options", []):
            all_options.append(option)
            print(f"{len(all_options)}. {option['name']} - {option['price']}")

    if not all_options:
        print("Tidak ada paket yang tersedia untuk family ini.")
        pause()
        return

    print("-------------------------------------------------------")
    choice = input("Pilih paket (nomor) atau 99 untuk kembali: ")

    if choice == "99":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(all_options):
        selected_option = all_options[int(choice) - 1]
        show_package_details(api_key, tokens, selected_option['package_option_code'], is_enterprise=False)
    else:
        print("Pilihan tidak valid.")
        pause()