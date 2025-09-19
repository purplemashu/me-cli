from app.client.engsel import get_package, send_api_request
from app.menus.util import clear_screen, pause
import json
from datetime import datetime
from app.service.auth import AuthInstance
from time import sleep
import threading
import sys
import os


def enter_sentry_mode():
    api_key = AuthInstance.api_key
    active_user = AuthInstance.get_active_user()
    if active_user is None:
        print("No active user. Please login first.")
        pause()
        return
    
    tokens = active_user["tokens"]

    clear_screen()
    print("Entering Sentry Mode...")
    print("Press Ctrl+C or type 'q' + Enter to exit.")
    
    if not os.path.exists("sentry"):
        os.makedirs("sentry")

    file_name = os.path.join(
        "sentry",
        f"sentry_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    )

    stop_flag = {"stop": False}

    # Background listener for "q"
    def listen_for_quit():
        while True:
            user_input = sys.stdin.readline()
            if not user_input:  # Ignore empty input (prevents instant exit)
                continue
            if user_input.strip().lower() == "q":
                stop_flag["stop"] = True
                break

    listener_thread = threading.Thread(target=listen_for_quit, daemon=True)
    listener_thread.start()

    id_token = tokens.get("id_token")
    
    path = "api/v8/packages/quota-details"
    
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }
    
    try:
        with open(file_name, 'a') as f:
            while not stop_flag["stop"]:
                sleep(1)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                try:
                    print(f"Fetching data at {timestamp}...", end="\r")
                    
                    res = send_api_request(api_key, path, payload, id_token, "POST")
                    if res.get("status") != "SUCCESS":
                        print("Failed to fetch packages")
                        print("Response:", res)
                        pause()
                        return None
                    
                    quotas = res["data"]["quotas"]

                    data_point = {
                        "time": timestamp,
                        "quotas": quotas
                    }

                    f.write(json.dumps(data_point) + "\n")
                    f.flush()
                except Exception as e:
                    print(f"Error during fetch at {timestamp}: {e}")
                    continue

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting Sentry Mode...")
    finally:
        print(f"\nSentry Mode exited. Data saved to {file_name}.")
        pause()
