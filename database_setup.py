import sqlite3
import os
import secrets

# Nama file database
DATABASE_FILE = "users.db"

def setup_database():
    """
    Fungsi ini membuat database SQLite dan tabel pengguna jika belum ada.
    Fungsi ini juga akan memasukkan satu pengguna contoh untuk pengujian.
    """
    # Hapus file database lama jika ada, untuk memastikan setup yang bersih
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Database lama '{DATABASE_FILE}' dihapus.")

    try:
        # Membuat koneksi ke database. File akan dibuat jika belum ada.
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Membuat tabel 'users'
        # Tabel ini akan menyimpan username, api_key (dienkripsi/hashed di dunia nyata),
        # dan otp_secret untuk 2FA.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                otp_secret TEXT
            )
        ''')
        print("Tabel 'users' berhasil dibuat.")

        # Membuat contoh pengguna untuk pengujian
        # Di aplikasi nyata, Anda akan memiliki sistem pendaftaran pengguna.
        test_username = "user_test"
        # Hasilkan API key acak yang aman untuk pengguna contoh
        test_api_key = secrets.token_hex(16)

        # Masukkan pengguna contoh ke dalam tabel
        cursor.execute('''
            INSERT INTO users (username, api_key)
            VALUES (?, ?)
        ''', (test_username, test_api_key))

        print(f"Pengguna contoh '{test_username}' berhasil ditambahkan.")
        print(f"API Key untuk '{test_username}': {test_api_key}")
        print("\nHarap simpan API Key ini untuk login ke aplikasi web.")

        # Simpan perubahan (commit) dan tutup koneksi
        conn.commit()
        conn.close()

        print(f"Database '{DATABASE_FILE}' berhasil disiapkan.")

    except sqlite3.Error as e:
        print(f"Terjadi error saat menyiapkan database: {e}")

if __name__ == '__main__':
    setup_database()
