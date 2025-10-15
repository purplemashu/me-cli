# Add project root to the Python path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from serverless_wsgi import handle
from app.client.engsel import get_balance, get_profile, get_otp, submit_otp

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    # Check if user is logged in (api_key and tokens are in session)
    if 'api_key' not in session or 'tokens' not in session:
        return redirect(url_for('login'))

    # User is logged in, fetch their data using session data
    api_key = session['api_key']
    tokens = session['tokens']

    try:
        balance = get_balance(api_key, tokens["id_token"])
        profile_data = get_profile(api_key, tokens["access_token"], tokens["id_token"])

        profile = {
            "number": session.get('phone_number', 'N/A'),
            "balance": balance.get("remaining", "N/A"),
            "subscription_type": profile_data.get("profile", {}).get("subscription_type", "N/A")
        }

        # Check if the warning pop-up should be shown
        show_warning = session.pop('show_warning', False)

        return render_template('index.html', profile=profile, show_warning=show_warning)
    except Exception as e:
        # If tokens are invalid or another API error occurs, log out user
        session.clear()
        return redirect(url_for('login'))


@app.route('/login')
def login():
    # Simply render the login form
    return render_template('login.html')

@app.route('/request-otp', methods=['POST'])
def request_otp():
    data = request.json
    api_key = data.get('api_key')
    phone_number = data.get('phone_number')

    if not api_key or not phone_number:
        return jsonify({'success': False, 'message': 'API Key and phone number are required.'}), 400

    subscriber_id = get_otp(phone_number)

    if subscriber_id:
        session['api_key_temp'] = api_key
        session['phone_number_temp'] = phone_number
        return jsonify({'success': True, 'message': 'OTP sent successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP. Check the phone number.'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    otp_code = data.get('otp_code')

    api_key = session.get('api_key_temp')
    phone_number = session.get('phone_number_temp')

    if not otp_code or not api_key or not phone_number:
        return jsonify({'success': False, 'message': 'Missing OTP, API Key, or phone number in session.'}), 400

    tokens = submit_otp(api_key, phone_number, otp_code)

    if tokens:
        session['api_key'] = api_key
        session['phone_number'] = phone_number
        session['tokens'] = tokens
        session['show_warning'] = True # Flag to show the warning pop-up

        session.pop('api_key_temp', None)
        session.pop('phone_number_temp', None)

        return jsonify({'success': True, 'message': 'Login successful.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP or API Key.'}), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Netlify function handler
def handler(event, context):
    return handle(app, event, context)
