import os
import hashlib
import requests
import base64

from random import randint
from datetime import datetime, timezone, timedelta

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dataclasses import dataclass

API_KEY = os.getenv("API_KEY")
AES_KEY_ASCII = os.getenv("AES_KEY_ASCII")
AX_FP_KEY = os.getenv("AX_FP_KEY")

BASE_CRYPTO_URL = "https://crypto.mashu.lol/api/880"
# BASE_CRYPTO_URL = "http://127.0.0.1:5000/api/880"  # For local testing

XDATA_DECRYPT_URL = f"{BASE_CRYPTO_URL}/decrypt"
XDATA_ENCRYPT_SIGN_URL = f"{BASE_CRYPTO_URL}/encryptsign"
PAYMENT_SIGN_URL = f"{BASE_CRYPTO_URL}/sign-payment"
BOUNTY_SIGN_URL = f"{BASE_CRYPTO_URL}/sign-bounty"
LOYALTY_SIGN_URL = f"{BASE_CRYPTO_URL}/sign-loyalty"
AX_SIGN_URL = f"{BASE_CRYPTO_URL}/sign-ax"

@dataclass
class DeviceInfo:
    manufacturer: str
    model: str
    lang: str
    resolution: str       # "WxH"
    tz_short: str         # contoh log kamu: "GMT07:00" (tanpa tanda +)
    ip: str
    font_scale: float     # 1.0 dsb
    android_release: str  # "13"
    msisdn: str
    
def build_fingerprint_plain(dev: DeviceInfo) -> str:
    return (
        f"{dev.manufacturer}|{dev.model}|{dev.lang}|{dev.resolution}|"
        f"{dev.tz_short}|{dev.ip}|{dev.font_scale}|Android {dev.android_release}|{dev.msisdn}"
    )

def ax_fingerprint(dev: DeviceInfo, secret_key_32hex_ascii: str) -> str:
    key = secret_key_32hex_ascii.encode("ascii")
    iv  = b"\x00" * 16
    pt  = build_fingerprint_plain(dev).encode("utf-8")
    ct  = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(pt, 16))
    return base64.b64encode(ct).decode("ascii")

def load_ax_fp() -> str:
    fp_path = "ax.fp"
    if os.path.exists(fp_path):
        with open(fp_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
    
    # Generate new if not found/empty
    dev = DeviceInfo(
        manufacturer="samsung",
        model="SM-N93" + str(randint(1000, 9999)),  # biar beda2
        lang="en",
        resolution="720x1540",
        tz_short="GMT07:00",
        ip="192.168.0.55",
        font_scale=1.0,
        android_release="13",
        msisdn="6287863683554",
    )
    new_fp = ax_fingerprint(dev, AX_FP_KEY)
    with open(fp_path, "w", encoding="utf-8") as f:
        f.write(new_fp)
    return new_fp
    

def random_iv_hex16() -> str:
    return os.urandom(8).hex()

def b64(data: bytes, urlsafe: bool) -> str:
    enc = base64.urlsafe_b64encode if urlsafe else base64.b64encode
    return enc(data).decode("ascii")


def build_encrypted_field(iv_hex16: str | None = None, urlsafe_b64: bool = False) -> str:
    key = AES_KEY_ASCII.encode("ascii")
    iv_hex = iv_hex16 or random_iv_hex16()
    iv = iv_hex.encode("ascii") 

    pt = pad(b"", AES.block_size)
    ct = AES.new(key, AES.MODE_CBC, iv=iv).encrypt(pt)

    return b64(ct, urlsafe_b64) + iv_hex

def java_like_timestamp(now: datetime) -> str:
    ms2 = f"{int(now.microsecond/10000):02d}"
    tz = now.strftime("%z"); tz_colon = tz[:-2] + ":" + tz[-2:] if tz else "+00:00"
    return now.strftime(f"%Y-%m-%dT%H:%M:%S.{ms2}") + tz_colon

def ts_gmt7_without_colon(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
    else:
        dt = dt.astimezone(timezone(timedelta(hours=7)))
    millis = f"{int(dt.microsecond / 1000):03d}"
    tz = dt.strftime("%z")
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{millis}") + tz

def ax_api_signature(
        api_key: str,
        ts_for_sign: str,
        contact: str,
        code: str,
        contact_type: str
    ) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    request_body = {
        "ts_for_sign": ts_for_sign,
        "contact": contact,
        "code": code,
        "contact_type": contact_type
    }
    
    response = requests.request("POST", AX_SIGN_URL, json=request_body, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json().get("ax_signature")
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Signature generation failed: {response.text}")
    
def encryptsign_xdata(
        api_key: str,
        method: str,
        path: str,
        id_token: str,
        payload: dict
    ) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    request_body = {
        "id_token": id_token,
        "method": method,
        "path": path,
        "body": payload
    }

    response = requests.request("POST", XDATA_ENCRYPT_SIGN_URL, json=request_body, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Encryption failed: {response.text}")
    
def decrypt_xdata(
    api_key: str,
    encrypted_payload: dict
    ) -> dict:
    if not isinstance(encrypted_payload, dict) or "xdata" not in encrypted_payload or "xtime" not in encrypted_payload:
        raise ValueError("Invalid encrypted data format. Expected a dictionary with 'xdata' and 'xtime' keys.")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    response = requests.request("POST", XDATA_DECRYPT_URL, json=encrypted_payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json().get("plaintext")
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Decryption failed: {response.text}")

def get_x_signature_payment(
        api_key: str,
        access_token: str,
        sig_time_sec: int,
        package_code: str,
        token_payment: str,
        payment_method: str,
        payment_for: str,
        path: str,
    ) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    request_body = {
        "access_token": access_token,
        "sig_time_sec": sig_time_sec,
        "package_code": package_code,
        "token_payment": token_payment,
        "payment_method": payment_method,
        "payment_for": payment_for,
        "path": path,
    }
    
    response = requests.request("POST", PAYMENT_SIGN_URL, json=request_body, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json().get("x_signature")
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Signature generation failed: {response.text}")
    
def get_x_signature_bounty(
        api_key: str,
        access_token: str,
        sig_time_sec: int,
        package_code: str,
        token_payment: str
    ) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    request_body = {
        "access_token": access_token,
        "sig_time_sec": sig_time_sec,
        "package_code": package_code,
        "token_payment": token_payment
    }
    
    response = requests.request("POST", BOUNTY_SIGN_URL, json=request_body, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json().get("x_signature")
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Signature generation failed: {response.text}")

def ax_device_id() -> str:
    android_id = load_ax_fp() # Actually just b*llsh*tting
    return hashlib.md5(android_id.encode("utf-8")).hexdigest()

def get_x_signature_loyalty(
        api_key: str,
        sig_time_sec: int,
        package_code: str,
        token_confirmation: str,
        path: str
    ) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    
    request_body = {
        "sig_time_sec": sig_time_sec,
        "package_code": package_code,
        "token_confirmation": token_confirmation,
        "path": path
    }
    
    response = requests.request("POST", LOYALTY_SIGN_URL, json=request_body, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json().get("x_signature")
    elif response.status_code == 402:
        raise Exception("Insufficient API credit.")
    else:
        raise Exception(f"Signature generation failed: {response.text}")
