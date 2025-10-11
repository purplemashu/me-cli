import requests
from app.client.engsel import get_family, get_package_details
from app.menus.util import pause
from app.service.auth import AuthInstance
from app.type_dict import PaymentItem
from app.client.balance import settlement_balance

# Purchase
def purchase_by_family(
    family_code: str,
    use_decoy: bool,
    token_confirmation_idx: int = 0,
):
    api_key = AuthInstance.api_key
    tokens: dict = AuthInstance.get_active_tokens() or {}
    
    if use_decoy:
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
        
        balance_treshold = decoy_package_detail["package_option"]["price"]
        print(f"Pastikan sisa balance KURANG DARI Rp{balance_treshold}!!!")
        balance_answer = input("Apakah anda yakin ingin melanjutkan pembelian? (y/n): ")
        if balance_answer.lower() != "y":
            print("Pembelian dibatalkan oleh user.")
            pause()
            return None
    
    family_data = get_family(api_key, tokens, family_code)
    if not family_data:
        print(f"Failed to get family data for code: {family_code}.")
        pause()
        return None
    
    family_name = family_data["package_family"]["name"]
    variants = family_data["package_variants"]
    
    print("-------------------------------------------------------")
    successful_purchases = []
    for variant in variants:
        variant_name = variant["name"]
        for option in variant["package_options"]:
            tokens = AuthInstance.get_active_tokens()
            
            option_name = option["name"]
            option_order = option["order"]
            option_price = option["price"]
            
            print(f"Trying to buy: {variant_name} - {option_order}. {option_name} - {option['price']}")
            
            payment_items = []
            
            try:
                if use_decoy:
                    decoy_package_detail = get_package_details(
                        api_key,
                        tokens,
                        decoy_data["family_code"],
                        decoy_data["variant_code"],
                        decoy_data["order"],
                        decoy_data["is_enterprise"],
                        decoy_data["migration_type"],
                    )
                
                target_package_detail = get_package_details(
                    api_key,
                    tokens,
                    family_code,
                    variant["package_variant_code"],
                    option["order"],
                    None,
                    None,
                )
            except Exception as e:
                print(f"Exception occurred while fetching package details: {e}")
                print(f"Failed to get package details for {variant_name} - {option_name}. Skipping.")
                continue
            
            payment_items.append(
                PaymentItem(
                    item_code=target_package_detail["package_option"]["package_option_code"],
                    product_type="",
                    item_price=target_package_detail["package_option"]["price"],
                    item_name=str(option["order"]) + target_package_detail["package_option"]["name"],
                    tax=0,
                    token_confirmation=target_package_detail["token_confirmation"],
                )
            )
            
            if use_decoy:
                payment_items.append(
                    PaymentItem(
                        item_code=decoy_package_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=decoy_package_detail["package_option"]["price"],
                        item_name=str(option["order"]) + decoy_package_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=decoy_package_detail["token_confirmation"],
                    )
                )
            
            res = None
            try:
                res = settlement_balance(
                    api_key,
                    tokens,
                    payment_items,
                    "BUY_PACKAGE",
                    False,
                    overwrite_amount=decoy_package_detail["package_option"]["price"]
                    +target_package_detail["package_option"]["price"],
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
                            successful_purchases.append(
                                f"{variant_name}|{option_order}. {option_name} - {option_price}"
                            )
                            print("Purchase successful!")
                else:
                    successful_purchases.append(
                        f"{variant_name}|{option_order}. {option_name} - {option_price}"
                    )
                    print("Purchase successful!")

            except Exception as e:
                print(f"Exception occurred while creating order: {e}")
                res = None
            print("-------------------------------------------------------")
    
    print(f"Total successful purchases for family {family_name}: {len(successful_purchases)}")
    if len(successful_purchases) > 0:
        print("-------------------------------------------------------")
        print("Successful purchases:")
        for purchase in successful_purchases:
            print(f"- {purchase}")
    print("-------------------------------------------------------")
    pause()