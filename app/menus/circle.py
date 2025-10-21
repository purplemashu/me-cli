from datetime import datetime
import json
from app.menus.util import pause, clear_screen, format_quota_byte
from app.client.engsel3 import get_group_data, get_group_members, validate_circle_member, invite_circle_member, remove_circle_member, accept_circle_invitation

from app.service.auth import AuthInstance
from app.client.encrypt import decrypt_circle_msisdn

WIDTH = 55

def show_circle_info(api_key: str, tokens: dict):
    in_circle_menu = True
    user: dict = AuthInstance.get_active_user()
    my_msisdn = user.get("number", "")

    while in_circle_menu:
        clear_screen()
        group_res = get_group_data(api_key, tokens)
        if group_res.get("status") != "SUCCESS":
            print("Failed to fetch circle data.")
            pause()
            return
        
        group_data = group_res.get("data", {})        
        group_id = group_data.get("group_id", "")

        if group_id == "":
            print("ou are not part of any Circle.")
            pause()
            return
        
        group_name = group_data.get("group_name", "N/A")
        owner_name = group_data.get("owner_name", "N/A")
        group_status = group_data.get("group_status", "N/A")
        
        members_res = get_group_members(api_key, tokens, group_id)
        if members_res.get("status") != "SUCCESS":
            print("Failed to fetch circle members.")
            pause()
            return
        
        members_data = members_res.get("data", {})
        members = members_data.get("members", [])
        if len(members) == 0:
            print("No members found in the Circle.")
            pause()
            return
        
        parent_member_id = ""
        parent_subs_id = ""
        parrent_msisdn = ""
        for member in members:
            if member.get("member_role", "") == "PARENT":
                parent_member_id = member.get("member_id", "")
                parent_subs_id = member.get("subscriber_number", "")
                parrent_msisdn_encrypted = member.get("msisdn", "")
                parrent_msisdn = decrypt_circle_msisdn(parrent_msisdn_encrypted, api_key)
        
        package = members_data.get("package", {})
        package_name = package.get("name", "N/A")
        benefit = package.get("benefit", {})
        allocation_byte = benefit.get("allocation", 0)
        consumption_byte = benefit.get("consumption", 0)
        remaining_byte = benefit.get("remaining", 0)
                
        clear_screen()
        
        print("=" * WIDTH)
        print(f"Circle Name: {group_name} ({group_status})".center(WIDTH))
        print(f"Owner: {owner_name} {parrent_msisdn}".center(WIDTH))
        print("=" * WIDTH)
        
        print("Members:")
        for idx, member in enumerate(members, start=1):
            encrypted_msisdn = member.get("msisdn", "")
            msisdn = decrypt_circle_msisdn(encrypted_msisdn, api_key)
            
            member_id = member.get("member_id", "")
            member_role = member.get("member_role", "N/A")
            member_subs_number = member.get("subscriber_number", "")
            
            join_date_ts = member.get("join_date", 0)
            slot_type = member.get("slot_type", "N/A")
            member_name = member.get("member_name", "N/A")
            member_allocation_byte = member.get("allocation", 0)
            member_remaining_byte = member.get("remaining", 0)
            member_status = member.get("status", "N/A")
            
            formatted_msisdn = f"{msisdn}"
            if msisdn == "":
                formatted_msisdn = "<No Number>"
            
            me_mark = ""
            if str(msisdn) == str(my_msisdn):
                me_mark = "(You)"
            
            member_type = "Parent" if member_role == "PARENT" else "Member"
            formated_quota_allocated = format_quota_byte(member_allocation_byte)
            formated_quota_used = format_quota_byte(member_allocation_byte - member_remaining_byte)
            print(f"{idx}. {formatted_msisdn} ({member_name}) | {member_type} {me_mark}")
            print(f"   Joined: {datetime.fromtimestamp(join_date_ts).strftime('%Y-%m-%d')} | Slot Type: {slot_type} | Status: {member_status}")
            print(f"   Usage: {formated_quota_used} / {formated_quota_allocated}")
            
            print("-" * WIDTH)
            
        print("-" * WIDTH)
        print("Options:")
        print("-" * WIDTH)
        print("1. Invite Member to Circle")
        print("del <number> - Remove Member from Circle (e.g., del 1)")
        print("acc <number> - Accept Invitation / Force Accept Member")
        print("00. Kembali ke menu utama")
        choice = input("Pilih opsi: ")
        if choice == "00":
            in_circle_menu = False
        elif choice == "1":
            msisdn_to_invite = input("Enter the MSISDN of the member to invite (e.g., 6281234567890): ")
            validate_res = validate_circle_member(api_key, tokens, msisdn_to_invite)
            if validate_res.get("status") == "SUCCESS":
                if validate_res.get("data", {}).get("response_code", "") != "200-2001":
                    print(f"Cannot invite {msisdn_to_invite}: {validate_res.get('data', {}).get('message', 'Unknown error')}")
                    pause()
                    continue
            
            member_name = input("Enter the name of the member to invite: ")
            
            invite_res = invite_circle_member(
                api_key,
                tokens,
                msisdn_to_invite,
                member_name,
                group_id,
                parent_member_id
            )
            if invite_res.get("status") == "SUCCESS":
                if invite_res.get("data", {}).get("response_code", "") == "200-00":
                    print(f"Invitation sent to {msisdn_to_invite} successfully.")
                else:
                    print(f"Failed to invite {msisdn_to_invite}: {invite_res.get('data', {}).get('message', 'Unknown error')}")
            pause()
        elif choice.startswith("del "):
            try:
                member_number = int(choice.split(" ")[1])
                if member_number < 1 or member_number > len(members):
                    print("Invalid member number.")
                    pause()
                    continue
                member_to_remove = members[member_number - 1]
                
                # Prevent removing parent
                if member_to_remove.get("member_role", "") == "PARENT":
                    print("Cannot remove the parent member from the Circle.")
                    pause()
                    continue
                
                member_id = member_to_remove.get("member_id", "")
                
                # Prevent removing last member
                is_last_member = len(members) == 2
                if is_last_member:
                    print("Cannot remove the last member from the Circle.")
                    pause()
                    continue
                
                msisdn_to_remove = decrypt_circle_msisdn(member_to_remove.get("msisdn", ""), api_key)
                confirm = input(f"Are you sure you want to remove {msisdn_to_remove} from the Circle? (y/n): ")
                if confirm.lower() != "y":
                    print("Removal cancelled.")
                    pause()
                    continue
                
                remove_res = remove_circle_member(
                    api_key,
                    tokens,
                    member_id,
                    group_id,
                    parent_member_id,
                    is_last_member
                )
                if remove_res.get("status") == "SUCCESS":
                    print(f"{msisdn_to_remove} has been removed from the Circle.")
                    print(json.dumps(remove_res, indent=2))
                else:
                    print(f"Error: {remove_res}")
            except ValueError:
                print("Invalid input format for deletion.")
            pause()
        elif choice.startswith("acc "):
            try:
                member_number = int(choice.split(" ")[1])
                if member_number < 1 or member_number > len(members):
                    print("Invalid member number.")
                    pause()
                    continue
                member_to_accept = members[member_number - 1]
                
                member_status = member_to_accept.get("status", "")
                if member_status != "INVITED":
                    print("This member is not in an invited state.")
                    pause()
                    continue
                
                member_id = member_to_accept.get("member_id", "")
                msisdn_to_accept = decrypt_circle_msisdn(member_to_accept.get("msisdn", ""), api_key)
                confirm = input(f"Do you want to accept the invitation for {msisdn_to_accept}? (y/n): ")
                if confirm.lower() != "y":
                    print("Acceptance cancelled.")
                    pause()
                    continue
                
                accept_res = accept_circle_invitation(
                    api_key,
                    tokens,
                    group_id,
                    member_id,
                    )

                if accept_res.get("status") == "SUCCESS":
                    print(f"Invitation for {msisdn_to_accept} has been accepted.")
                    print(json.dumps(accept_res, indent=2))
                else:
                    print(f"Error: {accept_res}")
            except ValueError:
                print("Invalid input format for acceptance.")
            pause()
        
            