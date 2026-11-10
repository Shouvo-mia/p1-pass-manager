import sqlite3
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DB_NAME = "passwords.db"

# মাস্টার কি থেকে এনক্রিপশন চাবি (Key) তৈরি করার ফাংশন
def generate_key_from_master(master_key: str) -> bytes:
    password = master_key.encode()
    salt = b'fixed_salt_for_app' # বাস্তব অ্যাপে এটি পরিবর্তনশীল হওয়া উচিত
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

# ডাটাবেজ টেবিল তৈরি
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT UNIQUE,
            username TEXT,
            encrypted_password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# নতুন পাসওয়ার্ড সেভ বা আপডেট করার ফাংশন
def save_or_update_account(site, username, password, master_key):
    init_db()
    key = generate_key_from_master(master_key)
    f = Fernet(key)
    encrypted_pass = f.encrypt(password.encode()).decode()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # যদি সাইটটি আগে থেকেই থাকে তবে আপডেট হবে, না থাকলে নতুন তৈরি হবে
    cursor.execute('''
        INSERT INTO accounts (site_name, username, encrypted_password)
        VALUES (?, ?, ?)
        ON CONFLICT(site_name) DO UPDATE SET
        username=excluded.username,
        encrypted_password=excluded.encrypted_password
    ''', (site.lower(), username, encrypted_pass))
    conn.commit()
    conn.close()

# সব অ্যাকাউন্টের লিস্ট দেখার ফাংশন
def get_all_accounts():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT site_name, username FROM accounts')
    rows = cursor.fetchall()
    conn.close()
    return rows

# নির্দিষ্ট পাসওয়ার্ড আনলক করে পড়ার ফাংশন
def get_password(site, master_key):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT encrypted_password FROM accounts WHERE site_name = ?', (site.lower(),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try:
            key = generate_key_from_master(master_key)
            f = Fernet(key)
            decrypted_pass = f.decrypt(row[0].encode()).decode()
            return decrypted_pass
        except Exception:
            return None # ভুল মাস্টার কি হলে None রিটার্ন করবে
    return None
