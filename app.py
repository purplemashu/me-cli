from dotenv import load_dotenv
load_dotenv()

import os
import json
from flask import Flask, render_template, session, redirect, url_for
from app.service.auth import AuthInstance
from app.client.engsel import get_balance, get_profile

app = Flask(__name__)
# A secret key is required to use Flask sessions.
# In a real application, this should be a more secure, randomly generated key.
app.secret_key = os.urandom(24)

def get_auth_instance():
    """Initializes and returns the AuthInstance."""
    # This ensures API key and tokens are loaded when the first request comes in.
    return AuthInstance

@app.route('/')
def index():
    # Check if a user is logged in (i.e., 'user_number' is in the session)
    if 'user_number' not in session:
        return redirect(url_for('login'))

    # User is logged in, fetch their data
    auth = get_auth_instance()

    # Manually set the active user for this request based on the session
    auth.set_active_user(session['user_number'])
    active_user = auth.get_active_user()

    if not active_user:
        # If token renewal fails or user is invalid, clear session and redirect to login
        session.clear()
        return redirect(url_for('login'))

    # Fetch data using the active user's tokens
    balance = get_balance(auth.api_key, active_user["tokens"]["id_token"])
    profile_data = get_profile(auth.api_key, active_user["tokens"]["access_token"], active_user["tokens"]["id_token"])

    profile = {
        "number": active_user["number"],
        "balance": balance.get("remaining", "N/A"),
        "subscription_type": profile_data.get("profile", {}).get("subscription_type", "N/A")
    }

    return render_template('index.html', profile=profile)

@app.route('/login')
def login():
    # Load available users to display on the login page
    auth = get_auth_instance()
    users = auth.refresh_tokens
    return render_template('login.html', users=users)

@app.route('/set-user/<int:number>')
def set_user(number):
    # "Log in" the user by storing their number in the session
    session['user_number'] = number
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
