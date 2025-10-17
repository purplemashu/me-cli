from app.client.engsel import get_otp, submit_otp
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance

def show_login_menu():
    clear_screen()
    print("-------------------------------------------------------")
    print("Login ke MyXL")
    print("-------------------------------------------------------")
    print("1. Request OTP")
    print("2. Submit OTP")
    print("99. Tutup aplikasi")
    print("-------------------------------------------------------")
    
def login_prompt(api_key: str):
    clear_screen()
    print("-------------------------------------------------------")
    print("Login ke MyXL")
    print("-------------------------------------------------------")
    print("Masukan nomor XL (Contoh 6281234567890):")
    phone_number = input("Nomor: ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        print("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        return None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            return None
        print("OTP Berhasil dikirim ke nomor Anda.")
        
        try_count = 5
        while try_count > 0:
            print(f"Sisa percobaan: {try_count}")
            otp = input("Masukkan OTP yang telah dikirim: ")
            if not otp.isdigit() or len(otp) != 6:
                print("OTP tidak valid. Pastikan OTP terdiri dari 6 digit angka.")
                continue
            
            tokens = submit_otp(api_key, phone_number, otp)
            if not tokens:
                print("OTP salah. Silahkan coba lagi.")
                try_count -= 1
                continue
            
            print("Berhasil login!")
            return phone_number, tokens["refresh_token"]

        print("Gagal login setelah beberapa percobaan. Silahkan coba lagi nanti.")
        return None, None
    except Exception as e:
        return None, None

def show_account_menu():
    clear_screen()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()
    
    # print(f"users: {users}")
    
    in_account_menu = True
    add_user = False
    while in_account_menu:
        clear_screen()
        print("-------------------------------------------------------")
        if AuthInstance.get_active_user() is None or add_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                print("Gagal menambah akun. Silahkan coba lagi.")
                pause()
                continue
            
            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()
            
            
            if add_user:
                add_user = False
            continue
        
        print("Akun Tersimpan:")
        if not users or len(users) == 0:
            print("Tidak ada akun tersimpan.")

        for idx, user in enumerate(users):
            is_active = active_user and user["number"] == active_user["number"]
            active_marker = " (Aktif)" if is_active else ""
            print(f"{idx + 1}. {user['number']}{active_marker}")
        
        print("Command:")
        print("0: Tambah Akun")
        print("00: Kembali ke menu utama")
        print("99: Hapus Akun aktif")
        print("Masukan nomor akun untuk berganti.")
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
                AuthInstance.remove_refresh_token(active_user["number"])
                # AuthInstance.load_tokens()
                users = AuthInstance.refresh_tokens
                active_user = AuthInstance.get_active_user()
                print("Akun berhasil dihapus.")
                pause()
            else:
                print("Penghapusan akun dibatalkan.")
                pause()
            continue
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']
        else:
            print("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue