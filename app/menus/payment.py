from datetime import datetime, timedelta

from app.client.engsel import get_transaction_history
from app.menus.util import clear_screen

def show_transaction_history(api_key, tokens):
    in_transaction_menu = True

    while in_transaction_menu:
        clear_screen()
        print("-------------------------------------------------------")
        print("Riwayat Transaksi")
        print("-------------------------------------------------------")

        data = None
        history = []
        try:
            data = get_transaction_history(api_key, tokens)
            history = data.get("list", [])
        except Exception as e:
            print(f"Gagal mengambil riwayat transaksi: {e}")
            history = []
        
        if len(history) == 0:
            print("Tidak ada riwayat transaksi.")
        
        for idx, transaction in enumerate(history, start=1):
            transaction_timestamp = transaction.get("timestamp", 0)
            dt = datetime.fromtimestamp(transaction_timestamp)
            dt_jakarta = dt - timedelta(hours=7)

            formatted_time = dt_jakarta.strftime("%d %B %Y | %H:%M WIB")

            print(f"{idx}. {transaction['title']} - {transaction['price']}")
            print(f"   Tanggal: {formatted_time}")
            print(f"   Metode Pembayaran: {transaction['payment_method_label']}")
            print(f"   Status Transaksi: {transaction['status']}")
            print(f"   Status Pembayaran: {transaction['payment_status']}")
            print("-------------------------------------------------------")

        # Option
        print("0. Refresh")
        print("00. Kembali ke Menu Utama")
        choice = input("Pilih opsi: ")
        if choice == "0":
            continue
        elif choice == "00":
            in_transaction_menu = False
        else:
            print("Opsi tidak valid. Silakan coba lagi.")