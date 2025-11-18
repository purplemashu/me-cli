from app.client.store.search import get_family_list, get_store_packages
from app.menus.package import get_packages_by_family, show_package_details
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
    
    pause()

def show_store_packages_menu(
    subs_type: str = "PREPAID",
    is_enterprise: bool = False,
):
    in_store_packages_menu = True
    while in_store_packages_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print("Fetching store packages...")
        store_packages_res = get_store_packages(api_key, tokens, subs_type, is_enterprise)
        if not store_packages_res:
            print("No store packages found.")
            in_store_packages_menu = False
            continue
        
        store_packages = store_packages_res.get("data", {}).get("results_price_only", [])
        
        clear_screen()
        
        print("=" * WIDTH)
        print("Store Packages:")
        print("=" * WIDTH)
        
        packages = {}
        for i, package in enumerate(store_packages):
            title = package.get("title", "N/A")
            
            
            original_price = package.get("original_price", 0)
            discounted_price = package.get("discounted_price", 0)
            
            price = original_price
            if discounted_price > 0:
                price = discounted_price
            
            validity = package.get("validity", "N/A")
            family_name = package.get("family_name", "N/A")
            
            action_type = package.get("action_type", "")
            action_param = package.get("action_param", "")
            
            packages[f"{i + 1}"] = {
                "action_type": action_type,
                "action_param": action_param
            }
            
            print(f"{i + 1}. {title}")
            print(f"   Family: {family_name}")
            print(f"   Price: Rp{price}")
            print(f"   Validity: {validity}")
            print("-" * WIDTH)
        
        print("00. Back to Main Menu")
        print("Input the number to view package details.")
        choice = input("Enter your choice: ")
        if choice == "00":
            in_store_packages_menu = False
        elif choice in packages:
            selected_package = packages[choice]
            
            action_type = selected_package["action_type"]
            action_param = selected_package["action_param"]
            
            if action_type == "PDP":
                _ = show_package_details(
                        api_key,
                        tokens,
                        action_param,
                        is_enterprise
                    )
            else:
                print("=" * WIDTH)
                print("Unhandled Action Type")
                print(f"Action type: {action_type}\nParam: {action_param}")
                pause()
        else:
            print("Invalid choice. Please enter a valid package number.")
            pause()