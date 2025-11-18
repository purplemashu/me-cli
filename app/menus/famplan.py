from datetime import datetime
import json
from app.menus.util import pause, clear_screen, format_quota_byte
from app.client.famplan import get_family_data, change_member, remove_member, set_quota_limit, validate_msisdn

WIDTH = 55

def show_family_info(api_key: str, tokens: dict):
    in_family_menu = True
    while in_family_menu:
        clear_screen()
        res = get_family_data(api_key, tokens)
        if not res.get("data"):
            print("Failed to get family data.")
            pause()
            return
        
        family_detail = res["data"]
        plan_type = family_detail["member_info"]["plan_type"]
        
        if plan_type == "":
            print("You are not family plan organizer.")
            pause()
            return
        
        parent_msisdn = family_detail["member_info"]["parent_msisdn"]
        members = family_detail["member_info"]["members"]
        empyt_slots = [slot for slot in members if slot.get("msisdn") == ""]
        
        total_quota_byte = family_detail["member_info"].get("total_quota", 0)
        remaining_quota_byte = family_detail["member_info"].get("remaining_quota", 0)
        
        total_quota_human = format_quota_byte(total_quota_byte)
        remaining_quota_human = format_quota_byte(remaining_quota_byte)
        
        end_date_ts = family_detail["member_info"].get("end_date", 0)
        end_date = datetime.fromtimestamp(end_date_ts).strftime("%Y-%m-%d")
        
        clear_screen()
        print("-" * WIDTH)
        print(f"Plan: {plan_type} | Parent: {parent_msisdn}".center(WIDTH))
        print(f"Shared Quota: {remaining_quota_human} / {total_quota_human} | Exp: {end_date}".center(WIDTH))
        print("-" * WIDTH)
        
        print(f"Members: {len(members) - len(empyt_slots)}/{len(members)}:")
        for idx, member in enumerate(members, start=1):
            print("-" * WIDTH)
            msisdn = member.get("msisdn", "N/A")
            formatted_msisdn = f"{msisdn}"
            if msisdn == "":
                formatted_msisdn = "<Empty Slot>"
            
            alias = member.get("alias", "N/A")
            slot_id = member.get("slot_id", "N/A")
            family_member_id = member.get("family_member_id", "N/A")
            member_type = member.get("member_type", "N/A")
            end_date_ts = member.get("usage", {}).get("quota_expired_at", 0)
            
            quota_allocated_byte = member.get("usage", {}).get("quota_allocated", 0)
            formated_quota_allocated = format_quota_byte(quota_allocated_byte)
            
            add_chances = member.get("add_chances", 0)
            total_add_chances = member.get("total_add_chances", 0)
            
            quota_used_byte = member.get("usage", {}).get("quota_used", 0)
            formated_quota_used = format_quota_byte(quota_used_byte)
            
            end_date = datetime.fromtimestamp(end_date_ts).strftime("%Y-%m-%d") if end_date_ts else "N/A"
            print(f"{idx}. {formatted_msisdn} ({alias}) | {member_type} | Add Chances: {add_chances}/{total_add_chances}")
            print(f"   Usage: {formated_quota_used} / {formated_quota_allocated}")
        print("-" * WIDTH)
        print("")
        
        print("-" * WIDTH)
        print("Options:")
        print("-" * WIDTH)
        print("1. Change Member")
        
        print("-" * WIDTH)
        print("limit <Slot Number> <Quota limit in MB>. Set Quota limit for member.\n  Example: limit 2 1024 (to set 1024 MB quota for member in slot 2)")
        
        print("-" * WIDTH)
        print("del <Slot Number>. Remove member from slot.\n  Example: del 3 (to remove member in slot 3)")
        
        print("-" * WIDTH)
        print("00. Back to Main Menu")
        
        print("-" * WIDTH)
        
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            slot_idx = input("Enter the slot number: ").strip()
            target_msisdn = input("Enter the new member's phone number (start with 62): ").strip()
            parent_alias = input("Enter your alias: ").strip()
            child_alias = input("Enter the new member's alias: ").strip()
            
            try:
                slot_idx_int = int(slot_idx)
                if slot_idx_int < 1 or slot_idx_int > len(members):
                    print("Invalid slot number.")
                    pause()
                    return
                
                if members[slot_idx_int - 1].get("msisdn") != "":
                    print("Selected slot is not empty. Cannot change member.")
                    pause()
                    return
                
                family_member_id = members[slot_idx_int - 1]["family_member_id"]
                slot_id = members[slot_idx_int - 1]["slot_id"]
                
                # Checking MSISDN
                validation_res = validate_msisdn(api_key, tokens, target_msisdn)
                if validation_res.get("status").lower() != "success":
                    print(f"MSISDN validation failed: {json.dumps(validation_res, indent=2)}")
                    pause()
                    return
                print("MSISDN validation successful.")
                
                target_family_plan_role = validation_res["data"].get("family_plan_role", "")
                if target_family_plan_role != "NO_ROLE":
                    print(f"{target_msisdn} is already part of another family plan with role {target_family_plan_role}.")
                    pause()
                    return

                is_continue = input(f"Are you sure you want to assign {target_msisdn} to slot {slot_idx_int}? (y/n): ").strip().lower()
                if is_continue != "y":
                    print("Operation cancelled by user.")
                    pause()
                    return
                
                change_member_res = change_member(
                    api_key,
                    tokens,
                    parent_alias,
                    child_alias,
                    slot_id,
                    family_member_id,
                    target_msisdn,
                )
                if change_member_res.get("status") == "SUCCESS":
                    print("Member changed successfully.")
                else:
                    print(f"Failed to change member: {change_member_res.get('message', 'Unknown error')}")
                
                print(json.dumps(change_member_res, indent=4))
            except ValueError:
                print("Invalid input. Please enter a valid slot number.")
            pause()
        elif choice.startswith("del "):
            _, slot_num = choice.split(" ", 1)
            try:
                slot_idx_int = int(slot_num)
                if slot_idx_int < 1 or slot_idx_int > len(members):
                    print("Invalid slot number.")
                    pause()
                    return
                
                member = members[slot_idx_int - 1]
                if member.get("msisdn") == "":
                    print("Selected slot is already empty.")
                    pause()
                    return
                
                is_continue = input(f"Are you sure you want to remove member {member.get('msisdn')} from slot {slot_idx_int}? (y/n): ").strip().lower()
                if is_continue != "y":
                    print("Operation cancelled by user.")
                    pause()
                    return
                
                family_member_id = member["family_member_id"]
                res = remove_member(
                    api_key,
                    tokens,
                    family_member_id,
                )
                if res.get("status") == "SUCCESS":
                    print("Member removed successfully.")
                else:
                    print(f"Failed to remove member: {res.get('message', 'Unknown error')}")
                
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Invalid input. Please enter a valid slot number.")
            pause()
        elif choice.startswith("limit "):
            _, slot_num, new_quota_mb = choice.split(" ", 2)
            try:
                slot_idx_int = int(slot_num)
                new_quota_mb_int = int(new_quota_mb)
                if slot_idx_int < 1 or slot_idx_int > len(members):
                    print("Invalid slot number.")
                    pause()
                    return
                
                member = members[slot_idx_int - 1]
                if member.get("msisdn") == "":
                    print("Selected slot is empty. Cannot set quota limit.")
                    pause()
                    return
                
                family_member_id = member["family_member_id"]
                original_allocation_byte = member.get("usage", {}).get("quota_allocated", 0)
                new_allocation_byte = new_quota_mb_int * 1024 * 1024
                
                res = set_quota_limit(
                    api_key,
                    tokens,
                    original_allocation_byte,
                    new_allocation_byte,
                    family_member_id,
                )
                if res.get("status") == "SUCCESS":
                    print("Quota limit set successfully.")
                else:
                    print(f"Failed to set quota limit: {res.get('message', 'Unknown error')}")
                
                print(json.dumps(res, indent=4))
            except ValueError:
                print("Invalid input. Please enter a valid slot number.")
            pause()
        elif choice == "00":
            in_family_menu = False
            return