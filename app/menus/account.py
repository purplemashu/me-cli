"""
Handles the user interface for account management.
"""
from .util import clear_screen, pause
from app.core.account import (
    login,
    verify_otp,
    add_account,
    remove_account,
    list_accounts,
    set_active_account,
    get_active_account
)
from app.service.auth import AuthInstance

def login_prompt():
    """Handles the user-facing login flow."""
    clear_screen()
    print("-------------------------------------------------------")
    print("Login ke MyXL")
    print("-------------------------------------------------------")
    print("Masukan nomor XL Prabayar (Contoh 6281234567890):")
    phone_number = input("Nomor: ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        pause()
        return None

    print("Requesting OTP...")
    subscriber_id = login(phone_number)
    if not subscriber_id:
        print("Gagal mengirim OTP. Silahkan coba lagi.")
        pause()
        return None
        
    print("OTP Berhasil dikirim ke nomor Anda.")

    otp = input("Masukkan OTP yang telah dikirim: ")
    if not otp.isdigit() or len(otp) != 6:
        print("OTP tidak valid. Pastikan OTP terdiri dari 6 digit angka.")
        pause()
        return None

    tokens = verify_otp(phone_number, otp)
    if not tokens:
        print("Gagal login. Periksa OTP dan coba lagi.")
        pause()
        return None

    print("Berhasil login!")

    add_account(int(phone_number), tokens["refresh_token"])
    return phone_number

def show_account_menu():
    """Displays the account management menu."""
    AuthInstance.load_tokens()
    
    in_account_menu = True
    add_user = False
    while in_account_menu:
        clear_screen()
        users = list_accounts()
        active_user = get_active_account()

        if active_user is None or add_user:
            new_user_number = login_prompt()
            if not new_user_number:
                print("Gagal menambah akun. Silahkan coba lagi.")
                pause()
                add_user = False # reset flag
                if active_user is None: # If there was no active user, we can't continue in this menu
                    return None
                continue
            
            set_active_account(int(new_user_number))
            
            if add_user:
                add_user = False
            continue
        
        print("Akun Tersimpan:")
        if not users or len(users) == 0:
            print("Tidak ada akun tersimpan.")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                active_marker = " (Aktif)" if is_active else ""
                print(f"{idx + 1}. {user['number']}{active_marker}")
        
        print("-------------------------------------------------------")
        print("Command:")
        print("0: Tambah Akun")
        print("00: Kembali ke menu utama")
        print("99: Hapus Akun aktif")
        print("Masukan nomor akun untuk berganti.")
        print("-------------------------------------------------------")
        input_str = input("Pilihan:")
        if input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None
        elif input_str == "0":
            add_user = True
            continue
        elif input_str == "99":
            if not active_user:
                print("Tidak ada akun aktif untuk dihapus.")
                pause()
                continue
            confirm = input(f"Yakin ingin menghapus akun {active_user['number']}? (y/n): ")
            if confirm.lower() == 'y':
                remove_account(active_user["number"])
                print("Akun berhasil dihapus.")
                pause()
            else:
                print("Penghapusan akun dibatalkan.")
                pause()
            continue
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            set_active_account(selected_user['number'])
            return selected_user['number']
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue