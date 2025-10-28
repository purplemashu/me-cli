# Decoy package management

import os
import json
import time

import requests
from app.client.engsel import get_new_token, get_profile, get_package_details
from app.util import ensure_api_key
from app.service.auth import AuthInstance

class DecoyPackage:
    _instance_ = None
    _initialized_ = False
    
    decoy_base_url = "https://me.mashu.lol/pg-decoy-"
    last_subscriber_id = None
    
    decoys = {}
    initial_decoys = {
        "default-balance": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
        "default-qris": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
        "default-qris0": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
        "prio-balance": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
        "prio-qris": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
        "prio-qris0": {
            "option_code": "",
            "price": 0,
            "last_fetched_at": 0
        },
    }
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance_:
            cls._instance_ = super().__new__(cls)
        return cls._instance_
    
    def __init__(self):
        if not self._initialized_:
            self.decoys = self.initial_decoys.copy()
            self._initialized_ = True
    
    def check_subscriber_change(self):
        active_user = AuthInstance.get_active_user()
        if active_user is None:
            return
        
        current_subscriber_id = active_user.get("subscriber_id", "")
        if self.last_subscriber_id != current_subscriber_id:
            print(f"Subscriber ID changed from {self.last_subscriber_id} to {current_subscriber_id}. Resetting decoy data.")
            self.reset_decoys()
            self.last_subscriber_id = current_subscriber_id
    
    def fetch_decoy_data(self, decoy_name):
        active_user = AuthInstance.get_active_user()
        if active_user is None:
            print("No active user. Cannot fetch decoy package.")
            return None
        
        api_key = AuthInstance.api_key
        tokens = active_user["tokens"]
        
        url = self.decoy_base_url + decoy_name + ".json"

        try:
            print(f"Refreshing decoy data for: {decoy_name}")
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print("Gagal mengambil data decoy package.")
                return None
            
            decoy_data = response.json()
            decoy_package_detail = get_package_details(
                api_key,
                tokens,
                decoy_data["family_code"],
                decoy_data["variant_code"],
                decoy_data["order"],
                decoy_data["is_enterprise"],
                decoy_data["migration_type"],
            )
            
            self.decoys[decoy_name] = {
                "option_code": decoy_package_detail["package_option"]["package_option_code"],
                "last_fetched_at": int(time.time()),
                "price": decoy_data["price"]
            }
            
            print(f"Decoy data for {decoy_name} refreshed successfully.")
        except Exception as e:
            print(f"Error fetching decoy data: {e}")
    
    def get_decoy(self, decoy_name):
        self.check_subscriber_change()
        
        selected_decoy = self.decoys.get(decoy_name)
        if selected_decoy is None:
            return None
        
        # Refresh decoy data if older than 5 minutes
        if int(time.time()) - selected_decoy["last_fetched_at"] > 300:
            self.fetch_decoy_data(decoy_name)
            selected_decoy = self.decoys.get(decoy_name)
            
        return selected_decoy
    
    def reset_decoys(self):
        self.decoys = self.initial_decoys.copy()

DecoyInstance = DecoyPackage()
