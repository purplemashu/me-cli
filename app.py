# -*- coding: utf-8 -*-

# =================================================================================================
# PERUBAHAN 1: Impor library yang diperlukan
# -------------------------------------------------------------------------------------------------
# - `load_dotenv` untuk memuat environment variables dari file .env.
# - `sqlite3` untuk berinteraksi dengan database SQLite.
# - `secrets` (opsional, tapi praktik yang baik) untuk menghasilkan kunci yang aman.
# =================================================================================================
from dotenv import load_dotenv
import os
import sqlite3
import pyotp
import base64
import io
from flask import Flask, render_template, session, redirect, url_for, request, flash, g
import qrcode

# Panggil load_dotenv() di paling atas untuk memastikan semua variabel lingkungan dimuat
# sebelum digunakan di bagian lain aplikasi.
load_dotenv()

app = Flask(__name__)

# =================================================================================================
# PERUBAHAN 2: Konfigurasi SECRET_KEY dari Environment Variable
# -------------------------------------------------------------------------------------------------
# - `app.secret_key` sekarang dimuat dari environment variable 'SECRET_KEY'.
# - Jika 'SECRET_KEY' tidak ditemukan, aplikasi akan berhenti dengan pesan error yang jelas.
#   Ini adalah praktik keamanan yang penting untuk mencegah penggunaan kunci yang lemah di produksi.
# =================================================================================================
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise ValueError("SECRET_KEY tidak diatur di environment. Harap atur di file .env")

# --- Konfigurasi Database ---
DATABASE_FILE = "users.db"

def get_db():
    """Membuka koneksi baru ke database untuk setiap request dan menyimpannya di `g`."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_FILE)
        # Menggunakan Row Factory agar hasil query bisa diakses seperti dictionary
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Menutup koneksi database di akhir setiap request."""
    db = getattr(g, '_database', None)
    if db is not in None:
        db.close()


# =================================================================================================
# PERUBAHAN 3: Fungsi Otentikasi Berbasis Database
# -------------------------------------------------------------------------------------------------
# - Fungsi `find_user_by_api_key` mencari pengguna di tabel 'users' berdasarkan api_key.
# - Fungsi `update_otp_secret_for_user` menyimpan otp_secret baru ke database.
# - Ini menggantikan logika hardcoded yang lama.
# =================================================================================================
def find_user_by_api_key(api_key):
    """Mencari pengguna di database berdasarkan API key."""
    try:
        cursor = get_db().cursor()
        user = cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,)).fetchone()
        return user
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def update_otp_secret_for_user(username, secret):
    """Menyimpan atau memperbarui otp_secret untuk pengguna di database."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET otp_secret = ? WHERE username = ?", (secret, username))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error saat update OTP secret: {e}")


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Ambil username dari session untuk menampilkan info yang relevan
    username = session.get('username', 'Pengguna')
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        user = find_user_by_api_key(api_key)

        if user:
            # Jika API Key valid, simpan username di session untuk langkah selanjutnya
            session['api_key_validated'] = True
            session['username'] = user['username']

            if user['otp_secret']:
                # Jika OTP sudah di-setup, lanjut ke verifikasi
                return redirect(url_for('verify_otp'))
            else:
                # Jika ini pertama kali, lanjut ke setup OTP
                return redirect(url_for('setup_otp'))
        else:
            flash("API Key tidak valid!", "error")

    return render_template('login.html')

@app.route('/setup-otp')
def setup_otp():
    if not session.get('api_key_validated'):
        return redirect(url_for('login'))

    username = session.get('username')
    if not username:
        flash("Sesi tidak valid. Silakan login kembali.", "error")
        return redirect(url_for('login'))

    # Buat dan simpan secret OTP baru ke database
    secret = pyotp.random_base32()
    update_otp_secret_for_user(username, secret)

    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="Ukons Dor App"
    )

    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_code_data = base64.b64encode(buf.getvalue()).decode('ascii')

    return render_template('setup_otp.html', qr_code_data=qr_code_data)


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if not session.get('api_key_validated'):
        return redirect(url_for('login'))

    username = session.get('username')
    if not username:
        flash("Sesi tidak valid.", "error")
        return redirect(url_for('login'))

    # Ambil OTP secret dari database
    cursor = get_db().cursor()
    user = cursor.execute("SELECT otp_secret FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not user['otp_secret']:
        flash("Setup OTP tidak ditemukan. Silakan coba setup kembali.", "error")
        return redirect(url_for('setup_otp'))

    secret = user['otp_secret']
    totp = pyotp.TOTP(secret)

    if request.method == 'POST':
        otp_code = request.form.get('otp')
        if totp.verify(otp_code):
            # OTP benar, login-kan pengguna sepenuhnya
            session['logged_in'] = True
            session.pop('api_key_validated', None)
            flash(f"Login sebagai {username} berhasil!", "success")
            return redirect(url_for('index'))
        else:
            flash("Kode OTP salah!", "error")

    return render_template('verify_otp.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for('login'))

# =================================================================================================
# PERUBAHAN 4: Mengamankan `app.run`
# -------------------------------------------------------------------------------------------------
# - `app.run()` sekarang hanya dieksekusi jika file ini dijalankan secara langsung
#   (misalnya, `python app.py`).
# - Ini mencegah server development berjalan saat file ini diimpor oleh server produksi
#   (seperti Gunicorn atau uWSGI), yang merupakan praktik terbaik keamanan.
# =================================================================================================
if __name__ == '__main__':
    # Pastikan database ada sebelum aplikasi dijalankan
    if not os.path.exists(DATABASE_FILE):
        print("Database tidak ditemukan. Menjalankan setup...")
        # Ini adalah cara sederhana, di aplikasi besar Anda mungkin ingin
        # menggunakan tool migrasi seperti Flask-Migrate.
        import database_setup
        database_setup.setup_database()

    app.run(debug=True, host='0.0.0.0')
