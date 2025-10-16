import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime
from app.client.engsel import get_otp, submit_otp, get_balance, get_profile, send_api_request
from app.client.engsel2 import get_tiering_info
from app.client.purchase import settlement_balance
from app.menus.package import get_packages_by_family, get_package
from app.service.auth import AuthInstance
from app.type_dict import PaymentItem

load_dotenv()

LOGIN_PHONE, LOGIN_OTP = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Welcome to the MyXL Bot! Use /login to get started.")

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the login process by asking for a phone number."""
    await update.message.reply_text("Please enter your phone number (e.g., 6281234567890):")
    return LOGIN_PHONE

async def login_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the phone number input and requests an OTP."""
    phone_number = update.message.text
    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        await update.message.reply_text("Invalid phone number. Please try again.")
        return LOGIN_PHONE

    context.user_data['phone_number'] = phone_number
    subscriber_id = get_otp(phone_number)
    if not subscriber_id:
        await update.message.reply_text("Failed to request OTP. Please try again later.")
        return ConversationHandler.END

    await update.message.reply_text("An OTP has been sent to your phone. Please enter the OTP:")
    return LOGIN_OTP

async def login_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the OTP input and completes the login."""
    otp_code = update.message.text
    phone_number = context.user_data.get('phone_number')
    user_id = update.effective_user.id

    if not otp_code.isdigit() or len(otp_code) != 6:
        await update.message.reply_text("Invalid OTP format. Please enter a 6-digit OTP.")
        return LOGIN_OTP

    tokens = submit_otp(AuthInstance.api_key, phone_number, otp_code)
    if not tokens:
        await update.message.reply_text("Login failed. Please check the OTP and try again.")
        return ConversationHandler.END

    AuthInstance.add_refresh_token(int(phone_number), tokens["refresh_token"])
    AuthInstance.set_active_user(user_id, int(phone_number))
    await update.message.reply_text("Login successful!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the login process."""
    await update.message.reply_text("Login process cancelled.")
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        print("TELEGRAM_TOKEN environment variable not set. Please add it to your .env file or environment.")
        sys.exit(1)

    application = Application.builder().token(telegram_token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login_start)],
        states={
            LOGIN_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_phone)],
            LOGIN_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_otp)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("packages", my_packages))

    purchase_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('purchase', purchase_start)],
        states={
            PURCHASE_FAMILY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, purchase_family_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    buy_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('buy', buy_package_start)],
        states={
            BUY_PACKAGE_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_package_payment_method)],
            BUY_PACKAGE_EWALLET_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_package_ewallet_number)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(purchase_conv_handler)
    application.add_handler(buy_conv_handler)

    application.run_polling()
PURCHASE_FAMILY_CODE = range(1)
BUY_PACKAGE_PAYMENT_METHOD, BUY_PACKAGE_EWALLET_NUMBER = range(2, 4)

async def purchase_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the family code:")
    return PURCHASE_FAMILY_CODE

async def purchase_family_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    family_code = update.message.text
    user_id = update.effective_user.id
    active_user = AuthInstance.get_active_user(user_id)
    if not active_user:
        await update.message.reply_text("Please /login first.")
        return ConversationHandler.END

    api_key = AuthInstance.api_key
    tokens = active_user["tokens"]

    await update.message.reply_text(f"Fetching packages for family code: {family_code}")

    packages = get_packages_by_family(family_code)

    if not packages:
        await update.message.reply_text("No packages found for this family code.")
        return ConversationHandler.END

    message = "Available packages:\n\n"
    for pkg in packages:
        message += f"*{pkg['variant_name']} - {pkg['option_name']}*\n"
        message += f"Price: {pkg['price']}\n"
        message += f"To purchase, use the command: `/buy {pkg['code']}`\n\n"

    await update.message.reply_text(message)
    return ConversationHandler.END

async def buy_package_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.args:
        await update.message.reply_text("Usage: /buy <package_option_code>")
        return ConversationHandler.END

    package_option_code = context.args[0]
    context.user_data['package_option_code'] = package_option_code

    await update.message.reply_text("Please choose a payment method:\n1. Balance\n2. E-Wallet\n3. QRIS")
    return BUY_PACKAGE_PAYMENT_METHOD

async def buy_package_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    package_option_code = context.user_data.get('package_option_code')
    user_id = update.effective_user.id
    active_user = AuthInstance.get_active_user(user_id)

    if not active_user:
        await update.message.reply_text("Please /login first.")
        return ConversationHandler.END

    api_key = AuthInstance.api_key
    tokens = active_user["tokens"]
    package_details = get_package(api_key, tokens, package_option_code)
    if not package_details:
        await update.message.reply_text("Failed to get package details.")
        return ConversationHandler.END

    payment_items = [
        PaymentItem(
            item_code=package_option_code,
            product_type="",
            item_price=package_details["package_option"]["price"],
            item_name=package_details["package_option"]["name"],
            tax=0,
            token_confirmation=package_details["token_confirmation"],
        )
    ]
    payment_for = package_details["package_family"]["payment_for"] or "BUY_PACKAGE"
    context.user_data['payment_items'] = payment_items
    context.user_data['payment_for'] = payment_for

    if choice == "1":
        res = settlement_balance(api_key, tokens, payment_items, payment_for, False, -1)
        if res and res.get("status") == "SUCCESS":
            await update.message.reply_text("Purchase successful!")
        else:
            await update.message.reply_text(f"Purchase failed: {res.get('message', 'Unknown error')}")
        return ConversationHandler.END
    elif choice == "2":
        await update.message.reply_text("Please enter your e-wallet number (e.g., 081234567890):")
        return BUY_PACKAGE_EWALLET_NUMBER
    elif choice == "3":
        transaction_id = settlement_qris(api_key, tokens, payment_items, payment_for, False, -1)
        if not transaction_id:
            await update.message.reply_text("Failed to create QRIS transaction.")
            return ConversationHandler.END
        qris_code = get_qris_code(api_key, tokens, transaction_id)
        if not qris_code:
            await update.message.reply_text("Failed to get QRIS code.")
            return ConversationHandler.END
        await update.message.reply_text(f"QRIS Code:\n{qris_code}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Invalid choice. Please try again.")
        return BUY_PACKAGE_PAYMENT_METHOD

async def buy_package_ewallet_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    wallet_number = update.message.text
    user_id = update.effective_user.id
    active_user = AuthInstance.get_active_user(user_id)
    payment_items = context.user_data.get('payment_items')
    payment_for = context.user_data.get('payment_for')

    res = settlement_multipayment(AuthInstance.api_key, active_user["tokens"], payment_items, wallet_number, "DANA", payment_for, False, -1)
    if res and res.get("status") == "SUCCESS":
        await update.message.reply_text("Purchase successful! Check your e-wallet to complete the payment.")
    else:
        await update.message.reply_text(f"Purchase failed: {res.get('message', 'Unknown error')}")
    return ConversationHandler.END
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_user = AuthInstance.get_active_user(user_id)
    if not active_user:
        await update.message.reply_text("Please /login first.")
        return

    api_key = AuthInstance.api_key
    tokens = active_user["tokens"]
    balance_data = get_balance(api_key, tokens["id_token"])
    profile_data = get_profile(api_key, tokens["access_token"], tokens["id_token"])

    if not balance_data or not profile_data:
        await update.message.reply_text("Failed to fetch balance or profile.")
        return

    balance_remaining = balance_data.get("remaining")
    balance_expired_at = datetime.fromtimestamp(balance_data.get("expired_at")).strftime("%Y-%m-%d")
    sub_type = profile_data["profile"]["subscription_type"]
    point_info = "Points: N/A | Tier: N/A"

    if sub_type == "PREPAID":
        tiering_data = get_tiering_info(api_key, tokens)
        tier = tiering_data.get("tier", 0)
        current_point = tiering_data.get("current_point", 0)
        point_info = f"Points: {current_point} | Tier: {tier}"

    message = (
        f"Nomor: {active_user['number']}\n"
        f"Type: {sub_type}\n"
        f"Pulsa: Rp {balance_remaining}\n"
        f"Aktif sampai: {balance_expired_at}\n"
        f"{point_info}"
    )
    await update.message.reply_text(message)

async def my_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_user = AuthInstance.get_active_user(user_id)
    if not active_user:
        await update.message.reply_text("Please /login first.")
        return

    api_key = AuthInstance.api_key
    tokens = active_user["tokens"]
    id_token = tokens.get("id_token")

    path = "api/v8/packages/quota-details"
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }

    await update.message.reply_text("Fetching your packages...")
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        await update.message.reply_text("Failed to fetch packages.")
        return

    quotas = res["data"]["quotas"]
    if not quotas:
        await update.message.reply_text("You have no active packages.")
        return

    message = "Your packages:\n\n"
    for quota in quotas:
        quota_name = quota["name"]
        message += f"*{quota_name}*\n"
        benefits = quota.get("benefits", [])
        for benefit in benefits:
            name = benefit.get("name", "")
            data_type = benefit.get("data_type", "N/A")
            remaining = benefit.get("remaining", 0)
            total = benefit.get("total", 0)

            if data_type == "DATA":
                if remaining >= 1_000_000_000:
                    remaining_str = f"{remaining / (1024 ** 3):.2f} GB"
                elif remaining >= 1_000_000:
                    remaining_str = f"{remaining / (1024 ** 2):.2f} MB"
                else:
                    remaining_str = f"{remaining / 1024:.2f} KB"
                if total >= 1_000_000_000:
                    total_str = f"{total / (1024 ** 3):.2f} GB"
                elif total >= 1_000_000:
                    total_str = f"{total / (1024 ** 2):.2f} MB"
                else:
                    total_str = f"{total / 1024:.2f} KB"
                message += f"- {name}: {remaining_str} / {total_str}\n"
            elif data_type == "VOICE":
                message += f"- {name}: {remaining/60:.2f} / {total/60:.2f} minutes\n"
            elif data_type == "TEXT":
                 message += f"- {name}: {remaining} / {total} SMS\n"
            else:
                message += f"- {name}: {remaining} / {total}\n"
        message += "\n"

    await update.message.reply_text(message)

if __name__ == "__main__":
    main()