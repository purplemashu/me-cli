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
    
    # users = []
    
    active_user = None
    # Format of active_user: {"number": int, "tokens": {"refresh_token": str, "access_token": str, "id_token": str}}
    
    last_refresh_time = None
    
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

            # Select the first user as active user by default
            if self.refresh_tokens and len(self.refresh_tokens) != 0:
                first_rt = self.refresh_tokens[0]
                tokens = get_new_token(first_rt["refresh_token"])
                if tokens:
                    self.active_user = {
                        "number": int(first_rt["number"]),
                        "tokens": tokens
                    }
                
            self.api_key = ensure_api_key()
            self.last_refresh_time = int(time.time())

            self._initialized_ = True
            
    def load_tokens(self):
        with open("refresh-tokens.json", "r", encoding="utf-8") as f:
            refresh_tokens = json.load(f)
            
            if len(refresh_tokens) !=  0:
                self.refresh_tokens = []
                # self.users = []

            # Validate and load tokens
            # n = 0
            for rt in refresh_tokens:
                if "number" in rt and "refresh_token" in rt:
                    self.refresh_tokens.append(rt)
                else:
                    print(f"Invalid token entry: {rt}")
                
                # try:
                #     n += 1
                #     print(f"Refreshing token for number {n}/{len(refresh_tokens)}: {rt['number']}")
                #     tokens = get_new_token(rt["refresh_token"])
                #     self.users.append({
                #         "number": int(rt["number"]),
                #         "tokens": tokens
                #     })
                #     time.sleep(1)  # To avoid hitting rate limits
                # except Exception as e:
                #     if "Bad Request" in str(e):
                #         print(f"Refresh token for number {rt['number']} is invalid or expired. Removing it.")
                #         self.remove_refresh_token(rt["number"])
                #     print(f"Failed to refresh token for number: {rt['number']}")
        
        # Update file
        # for user in self.users:
        #     matching_rt = next((rt for rt in self.refresh_tokens if int(rt["number"]) == int(user["number"])), None)
        #     if matching_rt:
        #         matching_rt["refresh_token"] = user["tokens"]["refresh_token"]
                

        # with open("refresh-tokens.json", "w", encoding="utf-8") as f:
        #     json.dump(self.refresh_tokens, f, indent=2)

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
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=2)
            
        
            
        # Set active user to newly added
        self.set_active_user(number)
            
    def remove_refresh_token(self, number: int):
        self.refresh_tokens = [rt for rt in self.refresh_tokens if rt["number"] != number]

        # self.users = [user for user in self.users if user["number"] != number]
        
        # Save to file
        with open("refresh-tokens.json", "w", encoding="utf-8") as f:
            json.dump(self.refresh_tokens, f, indent=4)
            
        # Refresh user tokens
        # self.load_tokens()
        
        # If the removed user was the active user, select a new active user if available
        if self.active_user and self.active_user["number"] == number:
            # Select the first user as active user by default
            if len(self.refresh_tokens) != 0:
                first_rt = self.refresh_tokens[0]
                tokens = get_new_token(first_rt["refresh_token"])
                if tokens:
                    self.active_user = {
                        "number": int(first_rt["number"]),
                        "tokens": tokens
                    }
            else:
                input("No users left. Press Enter to continue...")
                self.active_user = None

    # def get_user_tokens(self, number: int):
    #     user = next((user for user in self.users if user["number"] == number), None)
    #     return user["tokens"] if user else None

    def set_active_user(self, number: int):
        # Get refresh token for the number from refresh_tokens
        rt_entry = next((rt for rt in self.refresh_tokens if rt["number"] == number), None)
        if not rt_entry:
            print(f"No refresh token found for number: {number}")
            input("Press Enter to continue...")
            return False

        tokens = get_new_token(rt_entry["refresh_token"])
        if not tokens:
            print(f"Failed to get tokens for number: {number}. The refresh token might be invalid or expired.")
            input("Press Enter to continue...")
            return False

        self.active_user = {
            "number": int(number),
            "tokens": tokens
        }

    def renew_active_user_token(self):
        if self.active_user:
            tokens = get_new_token(self.active_user["tokens"]["refresh_token"])
            if tokens:
                self.active_user["tokens"] = tokens
                self.last_refresh_time = int(time.time())
                self.add_refresh_token(self.active_user["number"], self.active_user["tokens"]["refresh_token"])
                
                print("Active user token renewed successfully.")
                return True
            else:
                print("Failed to renew active user token.")
                input("Press Enter to continue...")
        else:
            print("No active user set or missing refresh token.")
            input("Press Enter to continue...")
        return False
    
    def get_active_user(self):
        if not self.active_user:
            # Choose the first user if available
            if len(self.refresh_tokens) != 0:
                first_rt = self.refresh_tokens[0]
                tokens = get_new_token(first_rt["refresh_token"])
                if tokens:
                    self.active_user = {
                        "number": int(first_rt["number"]),
                        "tokens": tokens
                    }
            return None
        
        if self.last_refresh_time is None or (int(time.time()) - self.last_refresh_time) > 300:
            self.renew_active_user_token()
            self.last_refresh_time = time.time()
        
        return self.active_user
    
    def get_active_tokens(self) -> dict | None:
        active_user = self.get_active_user()
        return active_user["tokens"] if active_user else None
    
AuthInstance = Auth()
