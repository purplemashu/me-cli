from app.client.store.search import get_family_list
from app.menus.package import get_packages_by_family
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance

WIDTH = 55

def show_family_list_menu(
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    in_family_list_menu = True
    while in_family_list_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print("Fetching family list...")
        family_list_res = get_family_list(api_key, tokens, subs_type, is_enterprise)
        if not family_list_res:
            print("No family list found.")
            in_family_list_menu = False
            continue
        
        family_list = family_list_res.get("data", {}).get("results", [])
        
        clear_screen()
        
        print("=" * WIDTH)
        print("Family List:")
        print("=" * WIDTH)
        
        for i, family in enumerate(family_list):
            family_name = family.get("label", "N/A")
            family_code = family.get("id", "N/A")
            
            print(f"{i + 1}. {family_name}")
            print(f"   Family code: {family_code}")
            print("-" * WIDTH)
        
        print("00. Back to Main Menu")
        print("Input the number to view packages in that family.")
        choice = input("Enter your choice: ")
        if choice == "00":
            in_family_list_menu = False
        
        if choice.isdigit() and int(choice) > 0 and int(choice) <= len(family_list):
            selected_family = family_list[int(choice) - 1]
            family_code = selected_family.get("id", "")
            family_name = selected_family.get("label", "N/A")
            
            print(f"Fetching packages for family: {family_name}...")
            get_packages_by_family(family_code)
