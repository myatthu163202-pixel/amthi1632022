# shared_functions.py
import streamlit as st
import pandas as pd
import hashlib
import time
from datetime import datetime, timedelta
import pytz
import re

# ==================== CONFIGURATION ====================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
PRICE_PER_NUMBER = 50000

# ==================== SESSION STATE HELPERS ====================
def init_session_state():
    """အစကနေစပြီး Session State အားလုံးကို Initialize လုပ်ပါ"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''
    if 'current_user' not in st.session_state:
        st.session_state.current_user = ''
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []

def init_users_database():
    """User database ကိုအစကနေစပြီး ဖန်တီးပါ"""
    st.session_state.users_db = {
        'admin': {
            'password': hashlib.sha256('admin123'.encode()).hexdigest(),
            'role': 'admin',
            'name': 'စီမံခန့်ခွဲသူ',
            'email': 'admin@company.com',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sheet_url': ''
        },
        'agent1': {
            'password': hashlib.sha256('agent123'.encode()).hexdigest(),
            'role': 'agent',
            'name': 'အေဂျင့်တစ်',
            'email': 'agent1@company.com',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sheet_url': ''
        },
        'agent2': {
            'password': hashlib.sha256('agent123'.encode()).hexdigest(),
            'role': 'agent',
            'name': 'အေဂျင့်နှစ်',
            'email': 'agent2@company.com',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sheet_url': ''
        }
    }

# ==================== AUTHENTICATION FUNCTIONS ====================
def authenticate_user(username, password):
    """အသုံးပြုသူအတည်ပြုခြင်း"""
    if username in st.session_state.users_db:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if st.session_state.users_db[username]['password'] == hashed_password:
            # Update last login
            st.session_state.users_db[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_activity("Login", f"User: {username}")
            return True, st.session_state.users_db[username]['role']
    return False, None

def log_activity(action, details=""):
    """လုပ်ဆောင်ချက်မှတ်တမ်းထားရှိခြင်း"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = st.session_state.current_user if st.session_state.logged_in else "Guest"
    st.session_state.activity_log.append({
        'timestamp': timestamp,
        'user': user,
        'action': action,
        'details': details
    })

# ==================== 2D APP FUNCTIONS ====================
def get_myanmar_time():
    """မြန်မာစံတော်ချိန်ရယူခြင်း"""
    return datetime.now(MYANMAR_TZ)

def format_myanmar_time(dt=None):
    """မြန်မာစံတော်ချိန်ဖော်ပြခြင်း"""
    if dt is None:
        dt = get_myanmar_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def validate_number(number_str):
    """ဂဏန်းစစ်ဆေးခြင်း"""
    if not re.match(r'^\d{2,3}$', number_str):
        return False, "ဂဏန်းသည် ၂ လုံး သို့မဟုတ် ၃ လုံးဖြစ်ရမည်"
    
    if len(number_str) == 2:
        if not (0 <= int(number_str) <= 99):
            return False, "2D ဂဏန်းသည် 00 မှ 99 အတွင်းဖြစ်ရမည်"
    elif len(number_str) == 3:
        if not (0 <= int(number_str) <= 999):
            return False, "3D ဂဏန်းသည် 000 မှ 999 အတွင်းဖြစ်ရမည်"
    
    return True, ""

def validate_name(name):
    """နာမည်စစ်ဆေးခြင်း"""
    if not name or len(name.strip()) < 2:
        return False, "နာမည်အနည်းဆုံး ၂ လုံးထည့်ပါ"
    return True, ""

def calculate_amount(number_str, quantity):
    """စုစုပေါင်းပမာဏတွက်ချက်ခြင်း"""
    return PRICE_PER_NUMBER * quantity

# ==================== USER MANAGEMENT FUNCTIONS ====================
def add_new_user(username, password, role, name, email=""):
    """အသုံးပြုသူအသစ်ထည့်ခြင်း"""
    if not username or not password or not role or not name:
        return False, "လိုအပ်သောအချက်အလက်များကိုဖြည့်စွက်ပါ။"
    
    if len(username) < 3:
        return False, "အသုံးပြုသူအမည်သည် အနည်းဆုံး ၃ လုံးပါဝင်ရမည်။"
    
    if len(password) < 6:
        return False, "စကားဝှက်သည် အနည်းဆုံး ၆ လုံးပါဝင်ရမည်။"
    
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "အသုံးပြုသူအမည်တွင် အင်္ဂလိပ်အက္ခရာ၊ နံပါတ်နှင့် underscore သာပါဝင်နိုင်သည်။"
    
    if username in st.session_state.users_db:
        return False, "အသုံးပြုသူအမည်ရှိပြီးသားဖြစ်နေပါသည်။"
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    st.session_state.users_db[username] = {
        'password': hashed_password,
        'role': role,
        'name': name,
        'email': email,
        'created_at': datetime.now().strftime("%Y-%m-%d"),
        'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'sheet_url': ''
    }
    
    log_activity("Add User", f"New user: {username} ({role})")
    return True, f"အကောင့် '{username}' အောင်မြင်စွာထည့်သွင်းပြီးပါပြီ။"

def update_user_info(username, **kwargs):
    """အသုံးပြုသူအချက်အလက်ပြင်ဆင်ခြင်း"""
    if username in st.session_state.users_db:
        for key, value in kwargs.items():
            if key == 'password' and value:
                st.session_state.users_db[username][key] = hashlib.sha256(value.encode()).hexdigest()
            elif value:
                st.session_state.users_db[username][key] = value
        
        log_activity("Update User", f"Updated: {username}")
        return True, "အချက်အလက်ပြင်ဆင်ပြီးပါပြီ။"
    return False, "အသုံးပြုသူမတွေ့ပါ။"

def delete_user_account(username):
    """အသုံးပြုသူဖျက်ခြင်း"""
    if username in st.session_state.users_db:
        if username == st.session_state.current_user:
            return False, "မိမိကိုယ်တိုင်ဖျက်ရန်မဖြစ်နိုင်ပါ။"
        
        del st.session_state.users_db[username]
        log_activity("Delete User", f"Deleted: {username}")
        return True, f"အကောင့် '{username}' ဖျက်ပြီးပါပြီ။"
    return False, "အသုံးပြုသူမတွေ့ပါ။"

# ==================== CUSTOM CSS ====================
def load_css():
    """Custom CSS ထည့်သွင်းခြင်း"""
    return """
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
    }
    .sub-title {
        font-size: 1.8rem;
        color: #1E40AF;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #BFDBFE;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #FDE68A;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #A7F3D0;
        margin: 1rem 0;
    }
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    </style>
    """
