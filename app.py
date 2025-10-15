from dotenv import load_dotenv
load_dotenv()

import os
import json
import pyotp
import base64
import io
from flask import Flask, render_template, session, redirect, url_for, request, flash
from app.service.auth import AuthInstance
from app.client.engsel import get_balance, get_profile
import qrcode

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- KONFIGURASI LOGIN ---
# Ambil API key yang diharapkan dari environment variable.
# Ini adalah kunci "master" untuk mengakses aplikasi, bukan per pengguna.
EXPECTED_API_KEY = os.environ.get("API_KEY", "api_key")


def get_auth_instance():
    """Menginisialisasi dan mengembalikan AuthInstance."""
    return AuthInstance

@app.route('/')
def index():
    if not session.get('logged_in') or 'user_number' not in session:
        return redirect(url_for('login'))

    auth = get_auth_instance()
    # Pastikan active_user di-set dari session di setiap request
    auth.set_active_user(session['user_number'])
    active_user = auth.get_active_user()

    if not active_user:
        session.clear()
        flash("Sesi tidak valid atau token kadaluarsa. Silakan login kembali.", "error")
        return redirect(url_for('login'))

    balance = get_balance(auth.api_key, active_user["tokens"]["id_token"])
    profile_data = get_profile(auth.api_key, active_user["tokens"]["access_token"], active_user["tokens"]["id_token"])

    profile = {
        "number": active_user["number"],
        "balance": balance.get("remaining", "N/A"),
        "subscription_type": profile_data.get("profile", {}).get("subscription_type", "N/A")
    }
    return render_template('index.html', profile=profile)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        if api_key == EXPECTED_API_KEY:
            session['api_key_validated'] = True
            # Jika OTP secret sudah ada di session, langsung ke verifikasi
            if session.get('otp_secret'):
                return redirect(url_for('verify_otp'))
            # Jika tidak, mulai setup OTP baru
            return redirect(url_for('setup_otp'))
        else:
            flash("API Key tidak valid!", "error")

    return render_template('login.html')

@app.route('/setup-otp')
def setup_otp():
    if not session.get('api_key_validated'):
        return redirect(url_for('login'))

    # Buat dan simpan secret di session, bukan di memori global
    if 'otp_secret' not in session:
        session['otp_secret'] = pyotp.random_base32()

    secret = session['otp_secret']

    # Menggunakan nama aplikasi umum untuk QR code
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name="Ukons Dor",
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
    if 'otp_secret' not in session:
        return redirect(url_for('setup_otp'))

    if request.method == 'POST':
        otp_code = request.form.get('otp')
        secret = session['otp_secret']
        totp = pyotp.TOTP(secret)

        if totp.verify(otp_code):
            # OTP Benar. Sekarang, periksa apakah ada pengguna terkonfigurasi.
            auth = get_auth_instance()
            if auth.refresh_tokens:
                # Ambil pengguna pertama yang tersedia
                first_user_number = auth.refresh_tokens[0]['number']
                session['user_number'] = first_user_number
                session['logged_in'] = True
                session.pop('api_key_validated', None) # Hapus status validasi sementara
                flash("Login berhasil!", "success")
                return redirect(url_for('index'))
            else:
                # Tidak ada pengguna di refresh-tokens.json
                return render_template('no_users.html')
        else:
            flash("Kode OTP salah!", "error")

    return render_template('verify_otp.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
