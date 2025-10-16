import os
import json
import time
from app.client.engsel import get_new_token
from app.util import ensure_api_key

class Auth:
    _instance_ = None
    _initialized_ = False

    api_key = ""

    refresh_tokens = []
    # Format of refresh_tokens: [{"number": int, "refresh_token": str}]

    active_users = {}
    # Format of active_users: {user_id: {"number": int, "tokens": {"refresh_token": str, "access_token": str, "id_token": str}, "last_refresh_time": int}}
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance_:
            cls._instance_ = super().__new__(cls)
        return cls._instance_
    
    def __init__(self):
        if not self._initialized_:
            if os.path.exists("refresh-tokens.json"):
                self.load_tokens()
            else:
                # Create empty file
                with open("refresh-tokens.json", "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)

            self.api_key = ensure_api_key()

            self._initialized_ = True
            
    def load_tokens(self):
        with open("refresh-tokens.json", "r", encoding="utf-8") as f:
            refresh_tokens = json.load(f)
            
            if len(refresh_tokens) !=  0:
                self.refresh_tokens = []

            # Validate and load tokens
            for rt in refresh_tokens:
                if "number" in rt and "refresh_token" in rt:
                    self.refresh_tokens.append(rt)
                else:
                    print(f"Invalid token entry: {rt}")

    def add_refresh_token(self, number: int, refresh_token: str):
        # Check if number already exist, if yes, replace it, if not append
        existing = next((rt for rt in self.refresh_tokens if rt["number"] == number), None)
        if existing:
            existing["refresh_token"] = refresh_token
        else:
            self.refresh_tokens.append({
                "number": int(number),
                "refresh_token": refresh_token
            })
        
        # Save to file
        self.write_tokens_to_file()

            
    def remove_refresh_token(self, number: int):
        self.refresh_tokens = [rt for rt in self.refresh_tokens if rt["number"] != number]
        
        # Save to file
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=4)
        
        # If the removed user was the active user, select a new active user if available
        if self.active_user and self.active_user["number"] == number:
            # Select the first user as active user by default
            if len(self.refresh_tokens) != 0:
                first_rt = self.refresh_tokens[0]
                tokens = get_new_token(first_rt["refresh_token"])
                if tokens:
                    self.set_active_user(first_rt["number"])
            else:
                input("No users left. Press Enter to continue...")
                self.active_user = None

    def set_active_user(self, user_id: int, number: int):
        rt_entry = next((rt for rt in self.refresh_tokens if rt["number"] == number), None)
        if not rt_entry:
            return False

        tokens = get_new_token(rt_entry["refresh_token"])
        if not tokens:
            return False

        self.active_users[user_id] = {
            "number": int(number),
            "tokens": tokens,
            "last_refresh_time": int(time.time())
        }
        return True

    def renew_user_token(self, user_id: int):
        if user_id in self.active_users:
            user_data = self.active_users[user_id]
            tokens = get_new_token(user_data["tokens"]["refresh_token"])
            if tokens:
                user_data["tokens"] = tokens
                user_data["last_refresh_time"] = int(time.time())
                self.add_refresh_token(user_data["number"], user_data["tokens"]["refresh_token"])
                return True
        return False
    
    def get_active_user(self, user_id: int):
        if user_id not in self.active_users:
            return None
        
        user_data = self.active_users[user_id]
        if (int(time.time()) - user_data["last_refresh_time"]) > 300:
            self.renew_user_token(user_id)
        
        return user_data
    
    def get_active_tokens(self, user_id: int) -> dict | None:
        user_data = self.get_active_user(user_id)
        return user_data["tokens"] if user_data else None
    
    def write_tokens_to_file(self):
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=4)

AuthInstance = Auth()
