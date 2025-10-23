import json
from app.client.store.segments import get_segments
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
from app.menus.package import show_package_details

WIDTH = 55

def show_store_segments_menu(is_enterprise: bool = False):
    in_store_segments_menu = True
    while in_store_segments_menu:
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        print("Fetching store segments...")
        segments_res = get_segments(api_key, tokens, is_enterprise)
        if not segments_res:
            print("No segments found.")
            in_store_segments_menu = False
            continue
        
        segments = segments_res.get("data", {}).get("store_segments", [])
        
        clear_screen()
        
        print("=" * WIDTH)
        print("Store Segments:")
        print("=" * WIDTH)
        
        packages = {}
        for i, segment in enumerate(segments):
            name = segment.get("title", "N/A")
            banners = segment.get("banners", [])
            
            letter = chr(65 + i)  # Convert 0 -> A, 1 -> B, etc.
            print("-" * WIDTH)
            print(f"{letter}. Banner: {name}")
            print("-" * WIDTH)
            
            for j, banner in enumerate(banners):
                discounted_price = banner.get("discounted_price", "N/A")
                title = banner.get("title", "N/A")
                validity = banner.get("validity", "N/A")
                family_name = banner.get("family_name", "N/A")
                
                action_param = banner.get("action_param", "")
                action_type = banner.get("action_type", "")
                
                packages[f"{letter.lower()}{j + 1}"] = {
                    "action_param": action_param,
                    "action_type": action_type
                }
                
                print(f"  {letter}{j + 1}. {family_name} - {title}")
                print(f"     Price: Rp{discounted_price}")
                print(f"     Validity: {validity}")
                print("-" * WIDTH)
                
                # print(json.dumps(banner, indent=4))  # Debug: Show full banner data
            
        print("00. Back to Main Menu")
        print("=" * WIDTH)
        choice = input("Enter your choice to view package details (e.g., A1, B2): ")
        if choice == "00":
            in_store_segments_menu = False
            continue
        
        selected_pkg = packages.get(choice.lower())
        if not selected_pkg:
            print("Invalid choice. Please enter a valid package code.")
            pause()
            continue
        
        action_param = selected_pkg["action_param"]
        action_type = selected_pkg["action_type"]
        
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
