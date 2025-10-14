import json
import sys

import requests
from app.service.auth import AuthInstance
from app.client.engsel import get_family, get_package, get_addons, get_package_details, send_api_request
from app.service.bookmark import BookmarkInstance
from app.client.purchase import settlement_bounty, settlement_loyalty
from app.menus.util import clear_screen, pause, display_html
from app.client.qris import show_qris_payment
from app.client.ewallet import show_multipayment
from app.client.balance import settlement_balance
from app.type_dict import PaymentItem
from app.menus.purchase import purchase_n_times


def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order = -1):
    clear_screen()
    print("-------------------------------------------------------")
    print("Detail Paket")
    print("-------------------------------------------------------")
    package = get_package(api_key, tokens, package_option_code)
    # print(f"[SPD-202]:\n{json.dumps(package, indent=1)}")
    if not package:
        print("Failed to load package details.")
        pause()
        return False

    price = package["package_option"]["price"]
    detail = display_html(package["package_option"]["tnc"])
    validity = package["package_option"]["validity"]

    option_name = package.get("package_option", {}).get("name","") #Vidio
    family_name = package.get("package_family", {}).get("name","") #Unlimited Turbo
    variant_name = package.get("package_detail_variant", "").get("name","") #For Xtra Combo
    option_name = package.get("package_option", {}).get("name","") #Vidio
    
    title = f"{family_name} - {variant_name} - {option_name}".strip()
    
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"]
    
    payment_items = [
        PaymentItem(
            item_code=package_option_code,
            product_type="",
            item_price=price,
            item_name=f"{variant_name} {option_name}".strip(),
            tax=0,
            token_confirmation=token_confirmation,
        )
    ]
    
    print("-------------------------------------------------------")
    print(f"Nama: {title}")
    print(f"Harga: Rp {price}")
    print(f"Payment For: {payment_for}")
    print(f"Masa Aktif: {validity}")
    print(f"Point: {package['package_option']['point']}")
    print(f"Plan Type: {package['package_family']['plan_type']}")
    print("-------------------------------------------------------")
    benefits = package["package_option"]["benefits"]
    if benefits and isinstance(benefits, list):
        print("Benefits:")
        for benefit in benefits:
            print("-------------------------------------------------------")
            print(f" Name: {benefit['name']}")
            print(f"  Item id: {benefit['item_id']}")
            data_type = benefit['data_type']
            if data_type == "VOICE" and benefit['total'] > 0:
                print(f"  Total: {benefit['total']/60} menit")
            elif data_type == "TEXT" and benefit['total'] > 0:
                print(f"  Total: {benefit['total']} SMS")
            elif data_type == "DATA" and benefit['total'] > 0:
                if benefit['total'] > 0:
                    quota = int(benefit['total'])
                    # It is in byte, make it in GB
                    if quota >= 1_000_000_000:
                        quota_gb = quota / (1024 ** 3)
                        print(f"  Quota: {quota_gb:.2f} GB")
                    elif quota >= 1_000_000:
                        quota_mb = quota / (1024 ** 2)
                        print(f"  Quota: {quota_mb:.2f} MB")
                    elif quota >= 1_000:
                        quota_kb = quota / 1024
                        print(f"  Quota: {quota_kb:.2f} KB")
                    else:
                        print(f"  Total: {quota}")
            elif data_type not in ["DATA", "VOICE", "TEXT"]:
                print(f"  Total: {benefit['total']} ({data_type})")
            
            if benefit["is_unlimited"]:
                print("  Unlimited: Yes")
    print("-------------------------------------------------------")
    addons = get_addons(api_key, tokens, package_option_code)
    

    bonuses = addons.get("bonuses", [])
    
    # Pick 1st bonus if available, need more testing
    # if len(bonuses) > 0:
    #     payment_items.append(
    #         PaymentItem(
    #             item_code=bonuses[0]["package_option_code"],
    #             product_type="",
    #             item_price=0,
    #             item_name=bonuses[0]["name"],
    #             tax=0,
    #             token_confirmation="",
    #         )
    #     )
    
    # Pick all bonuses, need more testing
    # for bonus in bonuses:
    #     payment_items.append(
    #         PaymentItem(
    #             item_code=bonus["package_option_code"],
    #             product_type="",
    #             item_price=0,
    #             item_name=bonus["name"],
    #             tax=0,
    #             token_confirmation="",
    #         )
    #     )

    print(f"Addons:\n{json.dumps(addons, indent=2)}")
    print("-------------------------------------------------------")
    print(f"SnK MyXL:\n{detail}")
    print("-------------------------------------------------------")
    
    in_package_detail_menu = True
    while in_package_detail_menu:
        print("Options:")
        print("1. Beli dengan Pulsa")
        print("2. Beli dengan E-Wallet")
        print("3. Bayar dengan QRIS")
        print("4. Pulsa + Decoy XCP")
        print("5. Pulsa + Decoy XCP V2")
        print("6. Pulsa N kali")
        print("7. QRIS + Decoy Edu")
        
        # Sometimes payment_for is empty, so we set default to BUY_PACKAGE
        if payment_for == "":
            payment_for = "BUY_PACKAGE"
        
        if payment_for == "REDEEM_VOUCHER":
            print("B. Ambil sebagai bonus (jika tersedia)")
            print("L. Beli dengan Poin (jika tersedia)")
        
        if option_order != -1:
            print("0. Tambah ke Bookmark")
        print("00. Kembali ke daftar paket")

        choice = input("Pilihan: ")
        if choice == "00":
            return False
        if choice == "0" and option_order != -1:
            # Add to bookmark
            success = BookmarkInstance.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code",""),
                family_name=package.get("package_family", {}).get("name",""),
                is_enterprise=is_enterprise,
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
            settlement_balance(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True
            )
            input("Silahkan cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '2':
            show_multipayment(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '3':
            show_qris_payment(
                api_key,
                tokens,
                payment_items,
                payment_for,
                True,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '4':
            # Balance; Decoy XCP
            url = "https://me.mashu.lol/pg-decoy-xcp.json"
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print("Gagal mengambil data decoy package.")
                pause()
                return None
            
            decoy_data = response.json()
            decoy_package_detail = get_package_details(
                api_key,
                tokens,
                decoy_data["family_code"],
                decoy_data["variant_code"],
                decoy_data["order"],
                decoy_data["is_enterprise"],
                decoy_data["migration_type"],
            )

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )

            overwrite_amount = price + decoy_package_detail["package_option"]["price"]
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                "BUY_PACKAGE",
                False,
                overwrite_amount,
            )
            
            if res and res.get("status", "") != "SUCCESS":
                error_msg = res.get("message", "Unknown error")
                if "Bizz-err.Amount.Total" in error_msg:
                    error_msg_arr = error_msg.split("=")
                    valid_amount = int(error_msg_arr[1].strip())
                    
                    print(f"Adjusted total amount to: {valid_amount}")
                    res = settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        "BUY_PACKAGE",
                        False,
                        valid_amount,
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        print("Purchase successful!")
            else:
                print("Purchase successful!")
            pause()
            return True
        elif choice == '5':
            # Balance; Decoy XCP V2
            url = "https://me.mashu.lol/pg-decoy-xcp.json"
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print("Gagal mengambil data decoy package.")
                pause()
                return None
            
            decoy_data = response.json()
            decoy_package_detail = get_package_details(
                api_key,
                tokens,
                decoy_data["family_code"],
                decoy_data["variant_code"],
                decoy_data["order"],
                decoy_data["is_enterprise"],
                decoy_data["migration_type"],
            )

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )

            overwrite_amount = price + decoy_package_detail["package_option"]["price"]
            res = settlement_balance(
                api_key,
                tokens,
                payment_items,
                "BUY_PACKAGE",
                False,
                overwrite_amount,
                token_confirmation_idx=-1
            )
            
            if res and res.get("status", "") != "SUCCESS":
                error_msg = res.get("message", "Unknown error")
                if "Bizz-err.Amount.Total" in error_msg:
                    error_msg_arr = error_msg.split("=")
                    valid_amount = int(error_msg_arr[1].strip())
                    
                    print(f"Adjusted total amount to: {valid_amount}")
                    res = settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        "BUY_PACKAGE",
                        False,
                        valid_amount,
                        token_confirmation_idx=-1
                    )
                    if res and res.get("status", "") == "SUCCESS":
                        print("Purchase successful!")
            else:
                print("Purchase successful!")
            pause()
            return True
        elif choice == '6':
            use_decoy_for_n_times = input("Use decoy package? (y/n): ").strip().lower() == 'y'
            n_times_str = input("Enter number of times to purchase (e.g., 3): ").strip()

            delay_seconds_str = input("Enter delay between purchases in seconds (e.g., 25): ").strip()
            if not delay_seconds_str.isdigit():
                delay_seconds_str = "0"

            try:
                n_times = int(n_times_str)
                if n_times < 1:
                    raise ValueError("Number must be at least 1.")
            except ValueError:
                print("Invalid number entered. Please enter a valid integer.")
                pause()
                continue
            purchase_n_times(
                n_times,
                family_code=package.get("package_family", {}).get("package_family_code",""),
                variant_code=package.get("package_detail_variant", {}).get("package_variant_code",""),
                option_order=option_order,
                use_decoy=use_decoy_for_n_times,
                delay_seconds=int(delay_seconds_str),
                pause_on_success=False,
            )
                
        elif choice.lower() == 'b':
            settlement_bounty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
                item_name=variant_name
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '7':
            # QRIS; Decoy Edu
            url = "https://me.mashu.lol/pg-decoy-edu.json"
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print("Gagal mengambil data decoy package.")
                pause()
                return None
            
            decoy_data = response.json()
            decoy_package_detail = get_package_details(
                api_key,
                tokens,
                decoy_data["family_code"],
                decoy_data["variant_code"],
                decoy_data["order"],
                decoy_data["is_enterprise"],
                decoy_data["migration_type"],
            )

            payment_items.append(
                PaymentItem(
                    item_code=decoy_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=decoy_package_detail["package_option"]["price"],
                    item_name=decoy_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=decoy_package_detail["token_confirmation"],
                )
            )
            
            print("-"*55)
            print(f"Harga Paket Utama: Rp {price}")
            print(f"Harga Decoy Paket Edu: Rp {decoy_package_detail['package_option']['price']}")
            print(f"Silahkan sesuaikan amount (trial & error)")
            print("-"*55)

            show_qris_payment(
                api_key,
                tokens,
                payment_items,
                "SHARE_PACKAGE",
                True,
                token_confirmation_idx=1
            )
            
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice.lower() == 'l':
            settlement_loyalty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
            )
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        else:
            print("Purchase cancelled.")
            return False
    pause()
    sys.exit(0)

def get_packages_by_family(
    family_code: str,
    is_enterprise: bool | None = None,
    migration_type: str | None = None
):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None
    
    packages = []
    
    data = get_family(
        api_key,
        tokens,
        family_code,
        is_enterprise,
        migration_type
    )
    
    if not data:
        print("Failed to load family data.")
        pause()
        return None
    price_currency = "Rp"
    rc_bonus_type = data["package_family"].get("rc_bonus_type", "")
    if rc_bonus_type == "MYREWARDS":
        price_currency = "Poin"
    
    in_package_menu = True
    while in_package_menu:
        clear_screen()
        # print(f"[GPBF-283]:\n{json.dumps(data, indent=2)}")
        print("-------------------------------------------------------")        
        print(f"Family Name: {data['package_family']['name']}")
        print(f"Family Code: {family_code}")
        print(f"Family Type: {data['package_family']['package_family_type']}")
        # print(f"Enterprise: {'Yes' if is_enterprise else 'No'}")
        print(f"Variant Count: {len(data['package_variants'])}")
        print("-------------------------------------------------------")
        print("Paket Tersedia")
        print("-------------------------------------------------------")
        
        package_variants = data["package_variants"]
        
        option_number = 1
        variant_number = 1
        
        for variant in package_variants:
            variant_name = variant["name"]
            variant_code = variant["package_variant_code"]
            print(f" Variant {variant_number}: {variant_name}")
            print(f" Code: {variant_code}")
            for option in variant["package_options"]:
                option_name = option["name"]
                
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                                
                print(f"   {option_number}. {option_name} - {price_currency} {option['price']}")
                
                option_number += 1
            
            if variant_number < len(package_variants):
                print("-------------------------------------------------------")
            variant_number += 1
        print("-------------------------------------------------------")

        print("00. Kembali ke menu utama")
        print("-------------------------------------------------------")
        pkg_choice = input("Pilih paket (nomor): ")
        if pkg_choice == "00":
            in_package_menu = False
            return None
        selected_pkg = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        
        if not selected_pkg:
            print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
            continue
        
        is_done = show_package_details(api_key, tokens, selected_pkg["code"], is_enterprise, option_order=selected_pkg["option_order"])
        if is_done:
            in_package_menu = False
            return None
        else:
            continue
        
    return packages

def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None
    
    id_token = tokens.get("id_token")
    
    path = "api/v8/packages/quota-details"
    
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }
    
    print("Fetching my packages...")
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        print("Failed to fetch packages")
        print("Response:", res)
        pause()
        return None
    
    quotas = res["data"]["quotas"]
    
    clear_screen()
    print("=======================================================")
    print("======================My Packages======================")
    print("=======================================================")
    my_packages =[]
    num = 1
    for quota in quotas:
        quota_code = quota["quota_code"] # Can be used as option_code
        group_code = quota["group_code"]
        group_name = quota["group_name"]
        quota_name = quota["name"]
        family_code = "N/A"
        
        benefit_infos = []
        benefits = quota.get("benefits", [])
        if len(benefits) > 0:
            for benefit in benefits:
                benefit_id = benefit.get("id", "")
                name = benefit.get("name", "")
                data_type = benefit.get("data_type", "N/A")
                benefit_info = "  -----------------------------------------------------\n"
                benefit_info += f"  ID    : {benefit_id}\n"
                benefit_info += f"  Name  : {name}\n"
                benefit_info += f"  Type  : {data_type}\n"
                

                remaining = benefit.get("remaining", 0)
                total = benefit.get("total", 0)

                if data_type == "DATA":
                    if remaining >= 1_000_000_000:
                        remaining_gb = remaining / (1024 ** 3)
                        remaining_str = f"{remaining_gb:.2f} GB"
                    elif remaining >= 1_000_000:
                        remaining_mb = remaining / (1024 ** 2)
                        remaining_str = f"{remaining_mb:.2f} MB"
                    elif remaining >= 1_000:
                        remaining_kb = remaining / 1024
                        remaining_str = f"{remaining_kb:.2f} KB"
                    else:
                        remaining_str = str(remaining)
                    
                    if total >= 1_000_000_000:
                        total_gb = total / (1024 ** 3)
                        total_str = f"{total_gb:.2f} GB"
                    elif total >= 1_000_000:
                        total_mb = total / (1024 ** 2)
                        total_str = f"{total_mb:.2f} MB"
                    elif total >= 1_000:
                        total_kb = total / 1024
                        total_str = f"{total_kb:.2f} KB"
                    else:
                        total_str = str(total)
                    
                    benefit_info += f"  Kuota : {remaining_str} / {total_str}"
                elif data_type == "VOICE":
                    benefit_info += f"  Kuota : {remaining/60:.2f} / {total/60:.2f} menit"
                elif data_type == "TEXT":
                    benefit_info += f"  Kuota : {remaining} / {total} SMS"
                else:
                    benefit_info += f"  Kuota : {remaining} / {total}"

                benefit_infos.append(benefit_info)
            
        
        print(f"fetching package no. {num} details...")
        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]
        
        print("=======================================================")
        print(f"Package {num}")
        print(f"Name: {quota_name}")
        print("Benefits:")
        if len(benefit_infos) > 0:
            for bi in benefit_infos:
                print(bi)
            print("  -----------------------------------------------------")
        print(f"Group Name: {group_name}")
        print(f"Quota Code: {quota_code}")
        print(f"Family Code: {family_code}")
        print(f"Group Code: {group_code}")
        print("=======================================================")
        
        my_packages.append({
            "number": num,
            "quota_code": quota_code,
        })
        
        num += 1
    
    print("Rebuy package? Input package number to rebuy, or '00' to back.")
    choice = input("Choice: ")
    if choice == "00":
        return None
    selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
    
    if not selected_pkg:
        print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
        return None
    
    is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
    if is_done:
        return None
        
    pause()
