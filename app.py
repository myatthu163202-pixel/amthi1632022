# main_app.py - Enhanced 2D Betting System with Winning Number Check
import streamlit as st
import pandas as pd
import time
import hashlib
import re
import random
from datetime import datetime, timedelta
import pytz
import json
import os
from typing import Dict, List, Tuple, Optional

# ==================== CONFIGURATION ====================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
ADMIN_USERNAME = "AMTHI"
ADMIN_PASSWORD = "1632022"
DATA_FILE = "betting_data.json"

# ==================== CUSTOM CSS ====================
def load_custom_css():
    """Custom CSS styles"""
    return """
    <style>
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 4px solid #3B82F6;
        font-weight: bold;
    }
    
    .sub-title {
        font-size: 2.0rem;
        color: #1E40AF;
        margin-bottom: 1.2rem;
        padding-left: 10px;
        border-left: 5px solid #60A5FA;
        font-weight: 600;
    }
    
    .info-box {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #7DD3FC;
        margin: 1.2rem 0;
    }
    
    .winning-box {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #10B981;
        margin: 1.2rem 0;
    }
    
    .payout-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #F59E0B;
        margin: 1.2rem 0;
    }
    
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 20px;
        margin: 1.5rem 0;
    }
    
    .entry-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    .entry-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 10px 10px 0px 0px;
        gap: 5px;
        padding-top: 15px;
        padding-bottom: 15px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    
    /* Fix for sidebar scrolling */
    [data-testid="stSidebar"] {
        overflow: visible !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        overflow: visible !important;
    }
    </style>
    """

# ==================== DATA MANAGEMENT ====================
def save_data():
    """ဒေတာများကို JSON file ထဲသိမ်းခြင်း"""
    try:
        data = {
            'users_db': st.session_state.users_db,
            'today_entries': st.session_state.today_entries,
            'activity_log': st.session_state.activity_log,
            'winning_numbers': st.session_state.winning_numbers,
            'payout_log': st.session_state.payout_log
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"ဒေတာသိမ်းရာတွင်အမှားအယွင်း: {str(e)}")
        return False

def load_data():
    """ဒေတာများကို JSON file မှဖတ်ခြင်း"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        return None
    except Exception as e:
        st.error(f"ဒေတာဖတ်ရာတွင်အမှားအယွင်း: {str(e)}")
        return None

# ==================== INITIALIZATION ====================
def init_session_state():
    """Session state initialization"""
    default_states = {
        'logged_in': False,
        'user_role': '',
        'current_user': '',
        'users_db': {},
        'today_entries': {},
        'activity_log': [],
        'winning_numbers': {},  # ပေါက်ဂဏန်းများသိမ်းရန်
        'payout_log': [],  # လျော်ကြေးများမှတ်တမ်း
        'selected_menu': '🏠 Dashboard',
        'editing_entry': None,
        'checking_winning': False,
        'current_winning_number': '',
        'winning_number_to_check': '',  # ပေါက်ဂဏန်းစစ်ဆေးရန်
        'new_user_temp_data': {}  # အေဂျင့်သစ်ဖွင့်ရန်ဒေတာ
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def init_default_data():
    """Default data များစတင်ခြင်း"""
    if not st.session_state.users_db:
        # Admin account
        st.session_state.users_db[ADMIN_USERNAME] = {
            'password': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
            'role': 'admin',
            'name': 'စီမံခန့်ခွဲသူ',
            'created_at': datetime.now(MYANMAR_TZ),
            'last_login': datetime.now(MYANMAR_TZ),
            'status': 'active'
        }
        
        # Default agent account
        st.session_state.users_db['agent1'] = {
            'password': hashlib.sha256('agent123'.encode()).hexdigest(),
            'role': 'agent',
            'name': 'အေဂျင့်တစ်',
            'created_at': datetime.now(MYANMAR_TZ),
            'last_login': datetime.now(MYANMAR_TZ),
            'status': 'active'
        }
        
        # Initialize empty entries
        st.session_state.today_entries['agent1'] = []
        
        # Initialize winning numbers
        today_date = datetime.now(MYANMAR_TZ).strftime('%Y-%m-%d')
        st.session_state.winning_numbers[today_date] = {
            '2d': '',
            '3d': '',
            'set_by': '',
            'set_time': ''
        }
        
        save_data()

# ==================== HELPER FUNCTIONS ====================
def get_myanmar_time() -> datetime:
    """မြန်မာစံတော်ချိန်ရယူခြင်း"""
    return datetime.now(MYANMAR_TZ)

def format_myanmar_time(dt: Optional[datetime] = None) -> str:
    """မြန်မာစံတော်ချိန်ဖော်ပြခြင်း"""
    if dt is None:
        dt = get_myanmar_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def validate_number(number_str: str) -> Tuple[bool, str]:
    """ဂဏန်းစစ်ဆေးခြင်း (2D/3D)"""
    if not number_str:
        return False, "ဂဏန်းထည့်ပါ"
    
    if not re.match(r'^\d+$', number_str):
        return False, "ဂဏန်းသာထည့်ပါ"
    
    if len(number_str) == 2:
        return True, "2D ဂဏန်း"
    
    elif len(number_str) == 3:
        return True, "3D ဂဏန်း"
    
    else:
        return False, "ဂဏန်းသည် ၂ လုံး သို့မဟုတ် ၃ လုံးဖြစ်ရမည်"

def validate_customer_name(name: str) -> Tuple[bool, str]:
    """ဝယ်ယူသူနာမည်စစ်ဆေးခြင်း"""
    if not name or len(name.strip()) < 2:
        return False, "နာမည်အနည်းဆုံး ၂ လုံးထည့်ပါ"
    
    if len(name.strip()) > 50:
        return False, "နာမည်အရှည်လွန်းသည်"
    
    # မြန်မာစာလုံးများနှင့် အင်္ဂလိပ်စာလုံးများသာလက်ခံ
    if not re.match(r'^[\u1000-\u109F\uAA60-\uAA7Fa-zA-Z\s]+$', name):
        return False, "မြန်မာစာလုံးသို့မဟုတ် အင်္ဂလိပ်စာလုံးများသာပါဝင်ရမည်"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """Username စစ်ဆေးခြင်း"""
    if not username or len(username.strip()) < 3:
        return False, "Username အနည်းဆုံး ၃ လုံးထည့်ပါ"
    
    if len(username.strip()) > 20:
        return False, "Username အရှည်လွန်းသည်"
    
    # အင်္ဂလိပ်စာလုံးများနှင့် ဂဏန်းများသာလက်ခံ
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username တွင် အင်္ဂလိပ်စာလုံး၊ ဂဏန်းနှင့် underscore သာပါဝင်ရမည်"
    
    # Check if username already exists
    if username.lower() in [u.lower() for u in st.session_state.users_db.keys()]:
        return False, "Username ဤအမည်ဖြင့်ရှိပြီးသားဖြစ်သည်"
    
    return True, ""

def calculate_amount(number_str: str, amount: int) -> int:
    """စုစုပေါင်းပမာဏတွက်ချက်ခြင်း - ကိုယ်ထည့်တဲ့ amount အတိုင်းပဲသုံး"""
    return amount

def calculate_payout_amount(bet_amount: int, number_type: str) -> int:
    """လျော်ကြေးပမာဏတွက်ချက်ခြင်း"""
    if number_type == "2D":
        return bet_amount * 85  # 2D အတွက် 85 ဆ
    else:  # 3D
        return bet_amount * 800  # 3D အတွက် 800 ဆ

def check_winning_number(bet_number: str, winning_number: str, number_type: str) -> Tuple[bool, Optional[str]]:
    """ပေါက်မပေါက်စစ်ဆေးခြင်း"""
    if not winning_number:
        return False, "ပေါက်ဂဏန်းမရှိသေးပါ"
    
    if number_type == "2D":
        # 2D အတွက် နောက်ဆုံး ၂ လုံးကိုကြည့်
        if len(winning_number) >= 2:
            last_two = winning_number[-2:]
            if bet_number == last_two:
                return True, f"ပေါက်ပြီး! ({bet_number} = {last_two})"
    else:  # 3D
        if bet_number == winning_number:
            return True, f"ပေါက်ပြီး! ({bet_number} = {winning_number})"
    
    return False, "မပေါက်ပါ"

def log_activity(action: str, details: str = ""):
    """လုပ်ဆောင်ချက်မှတ်တမ်းထားရှိခြင်း"""
    try:
        timestamp = format_myanmar_time()
        user = st.session_state.current_user if st.session_state.logged_in else "Guest"
        
        activity = {
            'timestamp': timestamp,
            'user': user,
            'action': action,
            'details': details
        }
        
        st.session_state.activity_log.append(activity)
        
        # Keep only last 1000 activities
        if len(st.session_state.activity_log) > 1000:
            st.session_state.activity_log = st.session_state.activity_log[-1000:]
        
        save_data()
        
    except Exception as e:
        st.error(f"Activity log error: {str(e)}")

def log_payout(customer_name: str, bet_number: str, bet_amount: int, 
               payout_amount: int, winning_number: str, agent: str):
    """လျော်ကြေးမှတ်တမ်းထားရှိခြင်း"""
    try:
        timestamp = format_myanmar_time()
        
        payout_record = {
            'timestamp': timestamp,
            'customer': customer_name,
            'bet_number': bet_number,
            'bet_amount': bet_amount,
            'payout_amount': payout_amount,
            'winning_number': winning_number,
            'agent': agent,
            'status': 'Paid'
        }
        
        st.session_state.payout_log.append(payout_record)
        save_data()
        
    except Exception as e:
        st.error(f"Payout log error: {str(e)}")

# ==================== AUTHENTICATION ====================
def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """အသုံးပြုသူအတည်ပြုခြင်း"""
    username = username.strip()
    
    # Admin authentication
    if username.upper() == ADMIN_USERNAME.upper():
        if password == ADMIN_PASSWORD:
            st.session_state.users_db[ADMIN_USERNAME]['last_login'] = datetime.now(MYANMAR_TZ)
            log_activity("Login", f"Admin: {ADMIN_USERNAME}")
            return True, 'admin'
    
    # Other users authentication
    for stored_username, user_data in st.session_state.users_db.items():
        if stored_username.lower() == username.lower():
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user_data['password'] == hashed_password:
                if user_data.get('status', 'active') != 'active':
                    return False, "အကောင့်ပိတ်ထားသည်"
                
                user_data['last_login'] = datetime.now(MYANMAR_TZ)
                log_activity("Login", f"User: {stored_username} ({user_data['role']})")
                return True, user_data['role']
    
    return False, "အသုံးပြုသူအမည် သို့မဟုတ် စကားဝှက် မှားယွင်းနေပါသည်"

# ==================== USER MANAGEMENT ====================
def create_agent_account(username: str, password: str, name: str) -> Tuple[bool, str]:
    """အေဂျင့်အကောင့်အသစ်ဖွင့်ခြင်း"""
    try:
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return False, f"Username: {error_msg}"
        
        # Validate password
        if len(password) < 6:
            return False, "စကားဝှက် အနည်းဆုံး ၆ လုံးဖြစ်ရမည်"
        
        # Validate name
        if len(name.strip()) < 2:
            return False, "အမည် အနည်းဆုံး ၂ လုံးဖြစ်ရမည်"
        
        # Check if username already exists
        if username in st.session_state.users_db:
            return False, "Username ဤအမည်ဖြင့်ရှိပြီးသားဖြစ်သည်"
        
        # Create new user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        st.session_state.users_db[username] = {
            'password': hashed_password,
            'role': 'agent',
            'name': name,
            'created_at': datetime.now(MYANMAR_TZ),
            'last_login': datetime.now(MYANMAR_TZ),
            'status': 'active'
        }
        
        # Initialize empty entries for new agent
        st.session_state.today_entries[username] = []
        
        # Save data
        save_data()
        
        log_activity("Create Agent", f"New agent: {username} ({name})")
        
        return True, f"အေဂျင့်အကောင့် '{username}' အောင်မြင်စွာဖွင့်လှစ်ပြီးပါပြီ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_agent_status(username: str, status: str) -> Tuple[bool, str]:
    """အေဂျင့်အခြေအနေပြောင်းလဲခြင်း"""
    try:
        if username not in st.session_state.users_db:
            return False, "User မတွေ့ပါ"
        
        if username.upper() == ADMIN_USERNAME.upper():
            return False, "Admin အကောင့်ကိုမပြင်နိုင်ပါ"
        
        st.session_state.users_db[username]['status'] = status
        save_data()
        
        status_text = "ပိတ်ပြီး" if status == 'inactive' else "ပြန်ဖွင့်ပြီး"
        log_activity("Update Agent Status", f"{username}: {status_text}")
        
        return True, f"အေဂျင့် {username} ကို {status_text}ပါပြီ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def reset_agent_password(username: str, new_password: str) -> Tuple[bool, str]:
    """အေဂျင့်စကားဝှက်ပြန်လည်သတ်မှတ်ခြင်း"""
    try:
        if username not in st.session_state.users_db:
            return False, "User မတွေ့ပါ"
        
        if len(new_password) < 6:
            return False, "စကားဝှက် အနည်းဆုံး ၆ လုံးဖြစ်ရမည်"
        
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        st.session_state.users_db[username]['password'] = hashed_password
        save_data()
        
        log_activity("Reset Password", f"Agent: {username}")
        
        return True, f"အေဂျင့် {username} ၏ စကားဝှက်အောင်မြင်စွာပြောင်းလဲပြီးပါပြီ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== WINNING NUMBER MANAGEMENT ====================
def set_winning_number(number_type: str, winning_number: str, set_by: str) -> Tuple[bool, str]:
    """ပေါက်ဂဏန်းသတ်မှတ်ခြင်း"""
    try:
        today_date = datetime.now(MYANMAR_TZ).strftime('%Y-%m-%d')
        
        if today_date not in st.session_state.winning_numbers:
            st.session_state.winning_numbers[today_date] = {
                '2d': '',
                '3d': '',
                'set_by': '',
                'set_time': ''
            }
        
        # Validate winning number
        is_valid, validation_msg = validate_number(winning_number)
        if not is_valid:
            return False, f"မှားယွင်းသောပေါက်ဂဏန်း: {validation_msg}"
        
        # Check number type consistency
        if number_type == "2D" and len(winning_number) != 2:
            return False, "2D ပေါက်ဂဏန်းသည် ၂ လုံးဖြစ်ရမည်"
        elif number_type == "3D" and len(winning_number) != 3:
            return False, "3D ပေါက်ဂဏန်းသည် ၃ လုံးဖြစ်ရမည်"
        
        # Set winning number
        st.session_state.winning_numbers[today_date][number_type.lower()] = winning_number
        st.session_state.winning_numbers[today_date]['set_by'] = set_by
        st.session_state.winning_numbers[today_date]['set_time'] = format_myanmar_time()
        
        # Auto-check winning entries
        auto_check_winning_entries(today_date, number_type, winning_number)
        
        log_activity("Set Winning Number", f"{number_type}: {winning_number}")
        save_data()
        
        return True, f"{number_type} ပေါက်ဂဏန်း {winning_number} အောင်မြင်စွာသတ်မှတ်ပြီးပါပြီ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def auto_check_winning_entries(date: str, number_type: str, winning_number: str):
    """ပေါက်ဂဏန်းသတ်မှတ်ပြီးနောက် အလိုအလျောက်စစ်ဆေးခြင်း"""
    for agent, entries in st.session_state.today_entries.items():
        for entry in entries:
            if entry.get('status') == 'Pending':
                # Check if entry matches the number type
                entry_number_type = "2D" if len(entry.get('number', '')) == 2 else "3D"
                
                if entry_number_type.lower() == number_type.lower():
                    is_winning, message = check_winning_number(
                        entry['number'], 
                        winning_number, 
                        number_type
                    )
                    
                    if is_winning:
                        entry['status'] = 'Won'
                        entry['winning_message'] = message
                        entry['winning_time'] = format_myanmar_time()
                        
                        # Calculate payout
                        payout_amount = calculate_payout_amount(
                            entry['amount'],
                            number_type
                        )
                        entry['payout_amount'] = payout_amount
                        
                        log_activity("Auto Win Check", 
                                   f"{entry['customer']} - {entry['number']} won {payout_amount:,} Ks")

def get_today_winning_numbers():
    """ယနေ့၏ပေါက်ဂဏန်းများရယူခြင်း"""
    today_date = datetime.now(MYANMAR_TZ).strftime('%Y-%m-%d')
    
    if today_date in st.session_state.winning_numbers:
        return st.session_state.winning_numbers[today_date]
    else:
        return {'2d': '', '3d': '', 'set_by': '', 'set_time': ''}

# ==================== LOGIN PAGE ====================
def render_login_page():
    """Login page for all users"""
    st.markdown(load_custom_css(), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">🎰 2D/3D ဂဏန်းထိုးစနစ်</h1>', unsafe_allow_html=True)
        
        current_time = format_myanmar_time()
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                        color: white; padding: 1rem; border-radius: 15px; display: inline-block;">
                <div style="font-size: 1.2rem; font-weight: bold;">မြန်မာစံတော်ချိန်</div>
                <div style="font-size: 2rem; font-weight: bold;">{current_time.split()[1]}</div>
                <div style="font-size: 1rem;">{current_time.split()[0]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 အကောင့်ဝင်ရန်")
            st.write("ကျေးဇူးပြု၍ သင့်အကောင့်ဖြင့် ဝင်ရောက်ပါ။")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "👤 **အသုံးပြုသူအမည်**", 
                    placeholder="သင့်အသုံးပြုသူအမည်ထည့်ပါ",
                    key="login_username"
                )
                
                password = st.text_input(
                    "🔒 **စကားဝှက်**", 
                    type="password",
                    placeholder="သင့်စကားဝှက်ထည့်ပါ",
                    key="login_password"
                )
                
                login_button = st.form_submit_button(
                    "🚀 **အကောင့်ဝင်ရန်**", 
                    use_container_width=True,
                    type="primary"
                )
                
                if login_button:
                    if username and password:
                        with st.spinner("ဝင်ရောက်နေသည်..."):
                            time.sleep(0.5)
                            authenticated, role_or_error = authenticate_user(username, password)
                            
                            if authenticated:
                                st.session_state.logged_in = True
                                st.session_state.user_role = role_or_error
                                st.session_state.current_user = username.upper() if username.upper() == ADMIN_USERNAME.upper() else username
                                
                                if role_or_error == 'agent':
                                    if username not in st.session_state.today_entries:
                                        st.session_state.today_entries[username] = []
                                
                                st.success(f"✅ **{role_or_error.upper()}** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {role_or_error if role_or_error else 'အကောင့်မှန်ကန်မှုမရှိပါ။'}")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ အသုံးပြုသူအမည်နှင့် စကားဝှက်ထည့်ပါ။")
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>"
            "© 2024 2D/3D Betting System | Version 2.0"
            "</div>",
            unsafe_allow_html=True
        )

# ==================== ADMIN PANEL ====================
def render_admin_panel():
    """Admin panel main function"""
    
    with st.sidebar:
        user_info = st.session_state.users_db.get(st.session_state.current_user, {})
        
        st.markdown(f"""
        <div class="user-card">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div style="font-size: 2.5rem;">👑</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.5rem;">{user_info.get('name', 'Admin')}</h3>
                    <p style="margin: 5px 0; opacity: 0.9;">ADMINISTRATOR</p>
                </div>
            </div>
            <p><strong>👤 User:</strong> {st.session_state.current_user}</p>
            <p><strong>📅 Last Login:</strong><br>{user_info.get('last_login', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 🧭 မီနူးရွေးချယ်ရန်")
        
        # Use Tabs instead of radio buttons
        admin_tabs = st.tabs([
            "🏠 Dashboard", 
            "🎯 Winning Numbers", 
            "📊 Reports", 
            "💰 Payout", 
            "👥 User Management"
        ])
        
        # Determine which tab is active
        if admin_tabs[0]._active:
            st.session_state.selected_menu = 'dashboard'
        elif admin_tabs[1]._active:
            st.session_state.selected_menu = 'winning_numbers'
        elif admin_tabs[2]._active:
            st.session_state.selected_menu = 'reports'
        elif admin_tabs[3]._active:
            st.session_state.selected_menu = 'payout'
        elif admin_tabs[4]._active:
            st.session_state.selected_menu = 'users'
        
        st.divider()
        
        # Today's winning numbers
        winning_info = get_today_winning_numbers()
        st.markdown("### 🏆 ယနေ့ပေါက်ဂဏန်းများ")
        
        if winning_info['2d']:
            st.markdown(f"**2D:** `{winning_info['2d']}`")
        else:
            st.markdown("**2D:** မသတ်မှတ်ရသေး")
            
        if winning_info['3d']:
            st.markdown(f"**3D:** `{winning_info['3d']}`")
        else:
            st.markdown("**3D:** မသတ်မှတ်ရသေး")
        
        if winning_info['set_time']:
            st.markdown(f"*သတ်မှတ်ချိန်:* {winning_info['set_time']}")
        
        st.divider()
        
        if st.button("🚪 အကောင့်ထွက်ရန်", use_container_width=True, type="secondary"):
            log_activity("Logout", f"Admin: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main Content - Render based on selected menu
    if st.session_state.selected_menu == 'dashboard':
        render_admin_dashboard()
    elif st.session_state.selected_menu == 'winning_numbers':
        render_winning_numbers_setting()
    elif st.session_state.selected_menu == 'reports':
        render_admin_reports()
    elif st.session_state.selected_menu == 'payout':
        render_payout_management()
    elif st.session_state.selected_menu == 'users':
        render_user_management()

def render_admin_dashboard():
    """Admin dashboard - SHOWS ONLY AGGREGATE DATA, NOT INDIVIDUAL AGENT DATA"""
    st.markdown('<h1 class="main-title">📊 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Statistics - SHOW ONLY TOTALS, NOT PER AGENT
    total_agents = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'agent')
    active_agents = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'agent' and u.get('status') == 'active')
    
    # Calculate totals WITHOUT showing individual agent data
    total_entries = 0
    total_amount = 0
    won_entries = 0
    total_payout = 0
    
    for agent, entries in st.session_state.today_entries.items():
        total_entries += len(entries)
        for entry in entries:
            total_amount += entry.get('amount', 0)
            if entry.get('status') == 'Won':
                won_entries += 1
                total_payout += entry.get('payout_amount', 0)
    
    net_profit = total_amount - total_payout
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Agents", total_agents, f"{active_agents} active")
    with col2:
        st.metric("Total Entries", total_entries)
    with col3:
        st.metric("Total Bet Amount", f"{total_amount:,} Ks")
    with col4:
        st.metric("Net Profit", f"{net_profit:,} Ks", 
                 delta_color="normal" if net_profit >= 0 else "inverse")
    
    st.divider()
    
    # Financial summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Won Entries", won_entries)
    with col2:
        st.metric("Total Payout", f"{total_payout:,} Ks")
    with col3:
        profit_percentage = (net_profit / total_amount * 100) if total_amount > 0 else 0
        st.metric("Profit %", f"{profit_percentage:.1f}%")
    
    st.divider()
    
    # Recent activities - ADMIN ONLY SEES SYSTEM ACTIVITIES
    st.markdown("### 📝 လတ်တလောလုပ်ဆောင်ချက်များ (System)")
    recent_activities = []
    for activity in st.session_state.activity_log[-15:]:
        # Filter out agent-specific activities that should not be visible to admin
        action = activity.get('action', '')
        user = activity.get('user', '')
        
        # Show only system-level activities
        if ('Login' in action or 'Logout' in action or 'Set Winning' in action or 
            'Create Agent' in action or 'Update Agent' in action or 'Reset Password' in action or
            'Auto Win Check' in action or 'Manual Payout' in action):
            recent_activities.append(activity)
    
    if recent_activities:
        for activity in reversed(recent_activities):
            st.markdown(f"""
            **{activity['timestamp']}** - *{activity['user']}*: {activity['action']}
            {f"  - {activity['details']}" if activity['details'] else ""}
            """)
    else:
        st.info("No recent system activities")

def render_winning_numbers_setting():
    """Set winning numbers"""
    st.markdown('<h1 class="main-title">🎯 ပေါက်ဂဏန်းသတ်မှတ်ရန်</h1>', unsafe_allow_html=True)
    
    winning_info = get_today_winning_numbers()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 2D ပေါက်ဂဏန်း")
        current_2d = winning_info['2d']
        
        if current_2d:
            st.markdown(f"<div class='winning-box'><h3>Current 2D: {current_2d}</h3></div>", unsafe_allow_html=True)
        
        with st.form("set_2d_form"):
            winning_2d = st.text_input(
                "2D Winning Number",
                value=current_2d,
                placeholder="00",
                max_chars=2,
                help="Enter 2-digit winning number"
            )
            
            submit_2d = st.form_submit_button("💾 Set 2D Winning Number", use_container_width=True)
            
            if submit_2d:
                if winning_2d:
                    success, message = set_winning_number("2D", winning_2d, st.session_state.current_user)
                    if success:
                        st.success(message)
                        log_activity("Set 2D Winning", f"Number: {winning_2d}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter 2D winning number")
    
    with col2:
        st.markdown("### 3D ပေါက်ဂဏန်း")
        current_3d = winning_info['3d']
        
        if current_3d:
            st.markdown(f"<div class='winning-box'><h3>Current 3D: {current_3d}</h3></div>", unsafe_allow_html=True)
        
        with st.form("set_3d_form"):
            winning_3d = st.text_input(
                "3D Winning Number",
                value=current_3d,
                placeholder="000",
                max_chars=3,
                help="Enter 3-digit winning number"
            )
            
            submit_3d = st.form_submit_button("💾 Set 3D Winning Number", use_container_width=True)
            
            if submit_3d:
                if winning_3d:
                    success, message = set_winning_number("3D", winning_3d, st.session_state.current_user)
                    if success:
                        st.success(message)
                        log_activity("Set 3D Winning", f"Number: {winning_3d}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter 3D winning number")
    
    st.divider()
    
    # Check all entries against winning numbers
    st.markdown("### 🔍 Check All Entries")
    
    if st.button("🔄 Check All Entries Against Winning Numbers", use_container_width=True):
        with st.spinner("Checking all entries..."):
            winning_info = get_today_winning_numbers()
            checked_count = 0
            won_count = 0
            
            for agent, entries in st.session_state.today_entries.items():
                for entry in entries:
                    if entry.get('status') == 'Pending':
                        entry_number_type = "2D" if len(entry.get('number', '')) == 2 else "3D"
                        winning_number = winning_info['2d'] if entry_number_type == "2D" else winning_info['3d']
                        
                        if winning_number:
                            is_winning, message = check_winning_number(
                                entry['number'],
                                winning_number,
                                entry_number_type
                            )
                            
                            if is_winning:
                                entry['status'] = 'Won'
                                entry['winning_message'] = message
                                entry['winning_time'] = format_myanmar_time()
                                entry['payout_amount'] = calculate_payout_amount(
                                    entry['amount'],
                                    entry_number_type
                                )
                                won_count += 1
                        
                        checked_count += 1
            
            save_data()
            st.success(f"✅ Checked {checked_count} entries. Found {won_count} winning entries.")

def render_admin_reports():
    """Admin reports - SHOWS ONLY AGGREGATE DATA"""
    st.markdown('<h1 class="main-title">📊 အစီရင်ခံစာများ (Aggregate Only)</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📈 Financial Report", "📊 Summary Report"])
    
    with tab1:
        # Financial report - AGGREGATE ONLY
        total_bet_amount = 0
        total_payout_amount = 0
        total_entries = 0
        won_entries = 0
        
        for entries in st.session_state.today_entries.values():
            for entry in entries:
                total_entries += 1
                total_bet_amount += entry.get('amount', 0)
                if entry.get('status') == 'Won':
                    total_payout_amount += entry.get('payout_amount', 0)
                    won_entries += 1
        
        net_profit = total_bet_amount - total_payout_amount
        profit_percentage = (net_profit / total_bet_amount * 100) if total_bet_amount > 0 else 0
        
        st.markdown("### 💰 ဘဏ္ဍာရေးအစီရင်ခံစာ (စုစုပေါင်း)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entries", total_entries)
        with col2:
            st.metric("Total Bet Amount", f"{total_bet_amount:,} Ks")
        with col3:
            st.metric("Total Payout", f"{total_payout_amount:,} Ks")
        with col4:
            st.metric("Net Profit", f"{net_profit:,} Ks", 
                     delta_color="normal" if net_profit >= 0 else "inverse")
        
        st.markdown("### 📊 အနှစ်ချုပ်")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Won Entries", won_entries, f"{(won_entries/total_entries*100):.1f}%" if total_entries > 0 else "0%")
        with col2:
            st.metric("Profit Percentage", f"{profit_percentage:.1f}%")
        with col3:
            avg_bet = total_bet_amount / total_entries if total_entries > 0 else 0
            st.metric("Average Bet", f"{avg_bet:,.0f} Ks")
    
    with tab2:
        # Summary report - NO INDIVIDUAL AGENT DATA
        st.markdown("### 📋 အေဂျင့်စာရင်း (အရေအတွက်သာ)")
        
        agent_stats = []
        for username, user_data in st.session_state.users_db.items():
            if user_data.get('role') == 'agent':
                entries = st.session_state.today_entries.get(username, [])
                total_agent_entries = len(entries)
                total_agent_amount = sum(entry.get('amount', 0) for entry in entries)
                won_agent_entries = sum(1 for entry in entries if entry.get('status') == 'Won')
                
                agent_stats.append({
                    'Username': username,
                    'Name': user_data.get('name', ''),
                    'Status': user_data.get('status', 'active').title(),
                    'Entries': total_agent_entries,
                    'Total Bet': f"{total_agent_amount:,} Ks",
                    'Won': won_agent_entries
                })
        
        if agent_stats:
            df_stats = pd.DataFrame(agent_stats)
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No agent data available")
        
        st.markdown("""
        **မှတ်ချက်:** ဤဇယားတွင် အေဂျင့်တစ်ဦးချင်း၏ စာရင်းအသေးစိတ်များကို မပြသပါ။ 
        စုစုပေါင်းအရေအတွက်နှင့် ပမာဏများကိုသာ ပြသထားပါသည်။
        """)

def render_payout_management():
    """Payout management - ADMIN CAN MANUALLY ADD PAYOUTS"""
    st.markdown('<h1 class="main-title">💰 လျော်ကြေးစီမံခန့်ခွဲမှု</h1>', unsafe_allow_html=True)
    
    # Payout form
    with st.form("payout_form"):
        st.markdown("### 💸 လျော်ကြေးထည့်သွင်းရန်")
        
        col1, col2 = st.columns(2)
        
        with col1:
            payout_customer = st.text_input("ဝယ်ယူသူအမည်", help="ပေါက်သူ၏အမည်")
            payout_number = st.text_input("ထိုးထားသောဂဏန်း", help="ပေါက်သောဂဏန်း")
            payout_type = st.selectbox("ဂဏန်းအမျိုးအစား", ["2D", "3D"])
        
        with col2:
            payout_bet_amount = st.number_input("ထိုးကြေးပမာဏ (Ks)", min_value=1000, step=1000)
            payout_winning_number = st.text_input("ပေါက်ဂဏန်း", help="ပေါက်သောဂဏန်း")
            payout_agent = st.selectbox(
                "အေဂျင့်အမည်",
                options=[username for username, data in st.session_state.users_db.items() if data.get('role') == 'agent']
            )
        
        # Calculate payout
        if payout_bet_amount > 0 and payout_type:
            payout_amount = calculate_payout_amount(payout_bet_amount, payout_type)
            st.markdown(f"""
            <div class="payout-box">
                <h4>လျော်ကြေးတွက်ချက်မှု</h4>
                <p><strong>ထိုးကြေး:</strong> {payout_bet_amount:,} Ks</p>
                <p><strong>ဂဏန်းအမျိုးအစား:</strong> {payout_type}</p>
                <p><strong>လျော်ကြေးပမာဏ:</strong> {payout_amount:,} Ks</p>
            </div>
            """, unsafe_allow_html=True)
        
        submit_payout = st.form_submit_button("✅ လျော်ကြေးအတည်ပြုရန်", use_container_width=True)
        
        if submit_payout:
            if all([payout_customer, payout_number, payout_winning_number, payout_agent]):
                # Log payout
                log_payout(
                    payout_customer,
                    payout_number,
                    payout_bet_amount,
                    payout_amount,
                    payout_winning_number,
                    payout_agent
                )
                
                st.success(f"✅ လျော်ကြေး {payout_amount:,} Ks အတည်ပြုပြီးပါပြီ။")
                log_activity("Manual Payout", f"{payout_customer} - {payout_amount:,} Ks")
                time.sleep(1)
                st.rerun()
            else:
                st.error("လိုအပ်သောအချက်အလက်များဖြည့်ပါ")
    
    st.divider()
    
    # Payout history - ADMIN SEES ALL PAYOUTS
    st.markdown("### 📋 လျော်ကြေးမှတ်တမ်း (All Agents)")
    
    if st.session_state.payout_log:
        df_payouts = pd.DataFrame(st.session_state.payout_log)
        st.dataframe(df_payouts, use_container_width=True, hide_index=True)
        
        # Total payout
        total_payout = sum(payout.get('payout_amount', 0) for payout in st.session_state.payout_log)
        st.metric("စုစုပေါင်းလျော်ကြေး", f"{total_payout:,} Ks")
    else:
        st.info("လျော်ကြေးမှတ်တမ်းမရှိပါ")

def render_user_management():
    """User management - CREATE, EDIT, DELETE AGENTS"""
    st.markdown('<h1 class="main-title">👥 အသုံးပြုသူစီမံခန့်ခွဲမှု</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Create New Agent", "📋 Manage Existing Agents"])
    
    with tab1:
        # Create new agent
        st.markdown("### ➕ အေဂျင့်အသစ်ဖွင့်ရန်")
        
        with st.form("create_agent_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input(
                    "Username *",
                    placeholder="agent2",
                    help="အင်္ဂလိပ်စာလုံး၊ ဂဏန်းနှင့် underscore သာပါဝင်ရမည်"
                )
                new_password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="********",
                    help="အနည်းဆုံး ၆ လုံးဖြစ်ရမည်"
                )
            
            with col2:
                new_name = st.text_input(
                    "အမည် *",
                    placeholder="အေဂျင့်နှစ်",
                    help="မြန်မာစာလုံးသို့မဟုတ် အင်္ဂလိပ်စာလုံးများသာပါဝင်ရမည်"
                )
                confirm_password = st.text_input(
                    "Confirm Password *",
                    type="password",
                    placeholder="********"
                )
            
            st.markdown("**သတိပေးချက်:** Username နှင့် Password ကို အေဂျင့်အားပေးပါ။")
            
            create_button = st.form_submit_button(
                "✅ အေဂျင့်အကောင့်ဖွင့်ရန်",
                use_container_width=True,
                type="primary"
            )
            
            if create_button:
                errors = []
                
                if not new_username:
                    errors.append("Username ထည့်ပါ")
                if not new_password:
                    errors.append("Password ထည့်ပါ")
                if not new_name:
                    errors.append("အမည်ထည့်ပါ")
                if new_password != confirm_password:
                    errors.append("Password မတူညီပါ")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    with st.spinner("အေဂျင့်အကောင့်ဖွင့်နေသည်..."):
                        success, message = create_agent_account(new_username, new_password, new_name)
                        if success:
                            st.success(f"✅ {message}")
                            st.markdown(f"""
                            <div class="info-box">
                                <h4>အေဂျင့်အကောင့်အသေးစိတ်:</h4>
                                <p><strong>Username:</strong> {new_username}</p>
                                <p><strong>Password:</strong> {new_password} (ဤ password ကိုမှတ်သားထားပါ)</p>
                                <p><strong>အမည်:</strong> {new_name}</p>
                                <p><strong>အကောင့်အမျိုးအစား:</strong> Agent</p>
                                <p><strong>ဖွင့်လှစ်ချိန်:</strong> {format_myanmar_time()}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
    
    with tab2:
        # Manage existing agents
        st.markdown("### 📋 ရှိပြီးသားအေဂျင့်များစီမံခန့်ခွဲရန်")
        
        # List all agents
        agents_data = []
        for username, details in st.session_state.users_db.items():
            if details.get('role') == 'agent':
                entries = st.session_state.today_entries.get(username, [])
                total_entries = len(entries)
                total_amount = sum(entry.get('amount', 0) for entry in entries)
                
                agents_data.append({
                    'Username': username,
                    'Name': details.get('name', ''),
                    'Status': details.get('status', 'active').title(),
                    'Created': details.get('created_at', ''),
                    'Last Login': details.get('last_login', ''),
                    'Entries': total_entries,
                    'Total Bet': f"{total_amount:,} Ks"
                })
        
        if agents_data:
            df_agents = pd.DataFrame(agents_data)
            st.dataframe(df_agents, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Agent management actions
            st.markdown("### ⚙️ အေဂျင့်လုပ်ဆောင်ချက်များ")
            
            col_sel, col_action = st.columns([2, 1])
            
            with col_sel:
                selected_agent = st.selectbox(
                    "အေဂျင့်ရွေးချယ်ရန်",
                    options=[agent['Username'] for agent in agents_data]
                )
            
            with col_action:
                action = st.selectbox(
                    "လုပ်ဆောင်ချက်ရွေးချယ်ရန်",
                    options=["Status Change", "Reset Password", "View Summary"]
                )
            
            # Action forms
            if action == "Status Change":
                with st.form("status_change_form"):
                    current_status = st.session_state.users_db[selected_agent].get('status', 'active')
                    new_status = st.selectbox(
                        "အခြေအနေပြောင်းလဲရန်",
                        options=["active", "inactive"],
                        index=0 if current_status == "active" else 1
                    )
                    
                    status_btn = st.form_submit_button("🔄 အခြေအနေပြောင်းလဲရန်", use_container_width=True)
                    
                    if status_btn:
                        if new_status != current_status:
                            success, message = update_agent_status(selected_agent, new_status)
                            if success:
                                st.success(f"✅ {message}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            elif action == "Reset Password":
                with st.form("reset_password_form"):
                    new_password = st.text_input(
                        "New Password",
                        type="password",
                        placeholder="အသစ်စကားဝှက်"
                    )
                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="အသစ်စကားဝှက်အတည်ပြု"
                    )
                    
                    reset_btn = st.form_submit_button("🔑 စကားဝှက်ပြန်လည်သတ်မှတ်ရန်", use_container_width=True)
                    
                    if reset_btn:
                        if not new_password:
                            st.error("စကားဝှက်ထည့်ပါ")
                        elif new_password != confirm_password:
                            st.error("စကားဝှက်မတူညီပါ")
                        elif len(new_password) < 6:
                            st.error("စကားဝှက် အနည်းဆုံး ၆ လုံးဖြစ်ရမည်")
                        else:
                            success, message = reset_agent_password(selected_agent, new_password)
                            if success:
                                st.success(f"✅ {message}")
                                st.info(f"**အသစ်စကားဝှက်:** {new_password}")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            elif action == "View Summary":
                entries = st.session_state.today_entries.get(selected_agent, [])
                total_entries = len(entries)
                total_amount = sum(entry.get('amount', 0) for entry in entries)
                won_entries = sum(1 for entry in entries if entry.get('status') == 'Won')
                total_payout = sum(entry.get('payout_amount', 0) for entry in entries if entry.get('status') == 'Won')
                
                st.markdown(f"""
                <div class="info-box">
                    <h4>အေဂျင့် {selected_agent} ၏ ယနေ့အခြေအနေ</h4>
                    <p><strong>စုစုပေါင်းစာရင်း:</strong> {total_entries}</p>
                    <p><strong>စုစုပေါင်းပမာဏ:</strong> {total_amount:,} Ks</p>
                    <p><strong>ပေါက်သောစာရင်း:</strong> {won_entries}</p>
                    <p><strong>လျော်ကြေး:</strong> {total_payout:,} Ks</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show summary but NOT individual entries
                st.info("**မှတ်ချက်:** အေဂျင့်တစ်ဦးချင်း၏ စာရင်းအသေးစိတ်များကို Admin မြင်ရန်မလိုအပ်ပါ။")
        else:
            st.info("မည်သည့်အေဂျင့်မှမရှိသေးပါ")

# ==================== 2D AGENT APPLICATION ====================
def render_2d_app():
    """Main 2D Agent application interface"""
    
    with st.sidebar:
        user_info = st.session_state.users_db.get(st.session_state.current_user, {})
        
        st.markdown(f"""
        <div class="user-card">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div style="font-size: 2.5rem;">👤</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.5rem;">{user_info.get('name', 'Agent')}</h3>
                    <p style="margin: 5px 0; opacity: 0.9;">AGENT</p>
                </div>
            </div>
            <p><strong>👤 Username:</strong> {st.session_state.current_user}</p>
            <p><strong>📅 Last Login:</strong><br>{user_info.get('last_login', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        current_time = format_myanmar_time()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    color: white; padding: 1rem; border-radius: 15px; margin: 1rem 0;">
            <div style="text-align: center;">
                <div style="font-size: 1rem; font-weight: bold;">မြန်မာစံတော်ချိန်</div>
                <div style="font-size: 2rem; font-weight: bold;">{current_time.split()[1]}</div>
                <div style="font-size: 1rem;">{current_time.split()[0]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 🧭 လမ်းညွှန်မီနူး")
        
        # Use Tabs instead of radio buttons for agent
        agent_tabs = st.tabs([
            "🎯 နံပါတ်ထည့်ရန်",
            "🏆 ပေါက်စစ်ဆေးရန်", 
            "📋 ယနေ့စာရင်း",
            "💰 လျော်ကြေးစာရင်း"
        ])
        
        # Determine which tab is active
        if agent_tabs[0]._active:
            st.session_state.selected_menu = 'entry'
        elif agent_tabs[1]._active:
            st.session_state.selected_menu = 'check_winning'
        elif agent_tabs[2]._active:
            st.session_state.selected_menu = 'entries'
        elif agent_tabs[3]._active:
            st.session_state.selected_menu = 'payouts'
        
        st.divider()
        
        # Today's summary - AGENT SEES ONLY THEIR OWN DATA
        today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
        total_entries = len(today_entries)
        total_amount = sum(entry.get('amount', 0) for entry in today_entries)
        won_amount = sum(entry.get('payout_amount', 0) for entry in today_entries if entry.get('status') == 'Won')
        
        st.markdown("### 📈 ယနေ့အခြေအနေ (သင့်အေဂျင့်)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("စုစုပေါင်းစာရင်း", total_entries)
        with col2:
            st.metric("စုစုပေါင်းပမာဏ", f"{total_amount:,} Ks")
        
        if won_amount > 0:
            st.markdown(f"**🏆 လျော်ကြေး:** {won_amount:,} Ks")
        
        st.divider()
        
        # Today's winning numbers
        winning_info = get_today_winning_numbers()
        st.markdown("### 🎯 ယနေ့ပေါက်ဂဏန်းများ")
        
        if winning_info['2d']:
            st.markdown(f"**2D:** `{winning_info['2d']}`")
        else:
            st.markdown("**2D:** မသတ်မှတ်ရသေး")
            
        if winning_info['3d']:
            st.markdown(f"**3D:** `{winning_info['3d']}`")
        else:
            st.markdown("**3D:** မသတ်မှတ်ရသေး")
        
        st.divider()
        
        if st.button("🔄 ဒေတာပြန်လည်စတင်ရန်", use_container_width=True):
            st.rerun()
        
        if st.button("🚪 အကောင့်ထွက်ရန်", use_container_width=True, type="secondary"):
            log_activity("Logout", f"Agent: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main Content - Render based on selected menu
    if st.session_state.selected_menu == 'entry':
        render_agent_number_entry()
    elif st.session_state.selected_menu == 'check_winning':
        render_check_winning()
    elif st.session_state.selected_menu == 'entries':
        render_agent_today_entries()
    elif st.session_state.selected_menu == 'payouts':
        render_agent_payouts()

def render_agent_number_entry():
    """Agent number entry form"""
    st.markdown('<h1 class="main-title">🎯 2D/3D နံပါတ်ထည့်သွင်းရန်</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    today_total = sum(entry.get('amount', 0) for entry in today_entries)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                color: white; padding: 1rem; border-radius: 15px; margin-bottom: 2rem;">
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; font-weight: bold;">ယနေ့စုစုပေါင်း</div>
            <div style="font-size: 2.5rem; font-weight: bold;">{today_total:,} Ks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("agent_number_entry_form", clear_on_submit=False):
        st.markdown("### 📝 ထိုးကြေးထည့်သွင်းရန်")
        
        # ၁။ ဝယ်ယူသူအမည်
        st.markdown("#### ၁။ ဝယ်ယူသူအမည် *")
        customer_name = st.text_input(
            "ဝယ်ယူသူအမည်",
            placeholder="ဥပမာ - ကိုကျော်ကျော်",
            help="မြန်မာစာလုံးသို့မဟုတ် အင်္ဂလိပ်စာလုံးများသာပါဝင်ရမည်",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ၂။ ထိုးမည့်ဂဏန်း
            st.markdown("#### ၂။ ထိုးမည့်ဂဏန်း *")
            number = st.text_input(
                "ဂဏန်း",
                placeholder="55 (2D) သို့မဟုတ် 123 (3D)",
                help="2D သို့မဟုတ် 3D ဂဏန်းထည့်ပါ",
                label_visibility="collapsed"
            )
        
        with col2:
            # ၃။ ပိုက်ဆံပမာဏ
            st.markdown("#### ၃။ ပိုက်ဆံပမာဏ *")
            
            # ပိုက်ဆံပမာဏကိုကိုယ်တိုင်ထည့်သွင်းရန်
            amount = st.number_input(
                "ပိုက်ဆံပမာဏ (Ks)",
                min_value=50,  # အနည်းဆုံး ၅၀ ကျပ်
                value=1000,
                step=50,
                help="ပိုက်ဆံပမာဏကိုကိုယ်တိုင်ထည့်သွင်းပါ",
                label_visibility="collapsed"
            )
        
        # ၄။ မှတ်ချက် (မဖြစ်မနေမဟုတ်)
        st.markdown("#### ၄။ မှတ်ချက် (မဖြစ်မနေမဟုတ်)")
        note = st.text_area(
            "မှတ်ချက်",
            placeholder="အထူးမှတ်ချက်ရှိပါက ထည့်သွင်းပါ",
            height=60,
            label_visibility="collapsed"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            "✅ **ထိုးကြေးအတည်ပြုရန်**",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            # Validation
            errors = []
            
            # Customer name validation
            if not customer_name or len(customer_name.strip()) < 2:
                errors.append("ဝယ်ယူသူအမည် အနည်းဆုံး ၂ လုံးထည့်ပါ")
            
            # Number validation
            is_number_valid, number_error = validate_number(number)
            if not is_number_valid:
                errors.append(f"ဂဏန်း: {number_error}")
            
            # Amount validation
            if amount < 50:
                errors.append("ပိုက်ဆံပမာဏ အနည်းဆုံး ၅၀ ကျပ်ဖြစ်ရမည်")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Determine number type
                number_type = "2D" if len(number) == 2 else "3D"
                
                # Create entry
                entry_id = len(today_entries) + 1
                entry_time = format_myanmar_time()
                
                entry = {
                    'id': entry_id,
                    'time': entry_time,
                    'customer': customer_name,
                    'number': number,
                    'amount': amount,
                    'number_type': number_type,
                    'status': 'Pending',
                    'note': note if note else '',
                    'agent': st.session_state.current_user,
                    'winning_time': '',
                    'winning_message': '',
                    'payout_amount': 0
                }
                
                # Add to today's entries
                if st.session_state.current_user not in st.session_state.today_entries:
                    st.session_state.today_entries[st.session_state.current_user] = []
                
                st.session_state.today_entries[st.session_state.current_user].append(entry)
                
                # Save data
                save_data()
                
                # Success message
                st.success(f"✅ ထိုးကြေးအောင်မြင်စွာထည့်သွင်းပြီးပါပြီ။")
                st.markdown(f"""
                <div style="background: #D1FAE5; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                    <h4 style="margin-top: 0;">📋 ထည့်သွင်းပြီးသောအချက်အလက်:</h4>
                    <p><strong>စာရင်းနံပါတ်:</strong> #{entry_id}</p>
                    <p><strong>အချိန်:</strong> {entry_time}</p>
                    <p><strong>ဝယ်ယူသူ:</strong> {customer_name}</p>
                    <p><strong>ဂဏန်း:</strong> {number} ({number_type})</p>
                    <p><strong>ပမာဏ:</strong> {amount:,} Ks</p>
                </div>
                """, unsafe_allow_html=True)
                
                log_activity("2D/3D Entry", f"{customer_name} - {number} - {amount:,} Ks")
                
                st.balloons()
                time.sleep(2)
                st.rerun()

def render_check_winning():
    """Check winning numbers for agent's entries"""
    st.markdown('<h1 class="main-title">🏆 ပေါက်စစ်ဆေးရန်</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    winning_info = get_today_winning_numbers()
    
    # Display current winning numbers
    col1, col2 = st.columns(2)
    with col1:
        if winning_info['2d']:
            st.markdown(f"<div class='winning-box'><h3>2D ပေါက်ဂဏန်း: {winning_info['2d']}</h3></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'><h3>2D ပေါက်ဂဏန်း: မသတ်မှတ်ရသေး</h3></div>", unsafe_allow_html=True)
    
    with col2:
        if winning_info['3d']:
            st.markdown(f"<div class='winning-box'><h3>3D ပေါက်ဂဏန်း: {winning_info['3d']}</h3></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'><h3>3D ပေါက်ဂဏန်း: မသတ်မှတ်ရသေး</h3></div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Check individual entry with custom winning number
    st.markdown("### 🔍 ပေါက်ဂဏန်းထည့်သွင်း၍စစ်ဆေးရန်")
    
    col_input, col_check = st.columns([2, 1])
    
    with col_input:
        # Input winning number to check
        st.markdown("#### ပေါက်ဂဏန်းထည့်သွင်းရန်")
        winning_number_input = st.text_input(
            "ပေါက်ဂဏန်း",
            placeholder="2D သို့မဟုတ် 3D ပေါက်ဂဏန်းထည့်ပါ",
            key="winning_number_input"
        )
        
        if winning_number_input:
            # Determine number type
            if len(winning_number_input) == 2:
                number_type = "2D"
            elif len(winning_number_input) == 3:
                number_type = "3D"
            else:
                number_type = ""
                st.warning("ပေါက်ဂဏန်းသည် ၂ လုံး သို့မဟုတ် ၃ လုံးဖြစ်ရမည်")
    
    with col_check:
        st.markdown("#### စစ်ဆေးရန်")
        if st.button("✅ ပေါက်ဂဏန်းနှင့်စစ်ဆေးရန်", use_container_width=True):
            if winning_number_input:
                st.session_state.winning_number_to_check = winning_number_input
                st.success(f"✅ ပေါက်ဂဏန်း {winning_number_input} ထည့်သွင်းပြီးပါပြီ။")
            else:
                st.error("ပေါက်ဂဏန်းထည့်သွင်းပါ")
    
    st.divider()
    
    # Check entries against the entered winning number
    if today_entries and st.session_state.winning_number_to_check:
        winning_number = st.session_state.winning_number_to_check
        number_type = "2D" if len(winning_number) == 2 else "3D"
        
        st.markdown(f"### 📋 {winning_number} နှင့်စစ်ဆေးမည့်စာရင်းများ")
        
        # Filter entries by number type
        entries_to_check = [e for e in today_entries if 
                          (number_type == "2D" and len(e['number']) == 2) or 
                          (number_type == "3D" and len(e['number']) == 3)]
        
        if entries_to_check:
            checked_count = 0
            won_count = 0
            total_payout = 0
            
            for entry in entries_to_check:
                if entry.get('status') == 'Pending':
                    is_winning, message = check_winning_number(
                        entry['number'],
                        winning_number,
                        number_type
                    )
                    
                    if is_winning:
                        entry['status'] = 'Won'
                        entry['winning_message'] = message
                        entry['winning_time'] = format_myanmar_time()
                        payout_amount = calculate_payout_amount(entry['amount'], number_type)
                        entry['payout_amount'] = payout_amount
                        total_payout += payout_amount
                        won_count += 1
                        
                        # Log payout
                        log_payout(
                            entry['customer'],
                            entry['number'],
                            entry['amount'],
                            payout_amount,
                            winning_number,
                            st.session_state.current_user
                        )
                    else:
                        entry['status'] = 'Lost'
                        entry['winning_message'] = message
                        entry['winning_time'] = format_myanmar_time()
                    
                    checked_count += 1
            
            save_data()
            
            if won_count > 0:
                st.success(f"✅ {checked_count} ခုစစ်ဆေးပြီး {won_count} ခုပေါက်ပါသည်။")
                st.markdown(f"""
                <div class="payout-box">
                    <h4>စုစုပေါင်းလျော်ကြေး</h4>
                    <p><strong>ပေါက်ခုအရေအတွက်:</strong> {won_count}</p>
                    <p><strong>စုစုပေါင်းလျော်ကြေး:</strong> {total_payout:,} Ks</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"✅ {checked_count} ခုစစ်ဆေးပြီး မည်သည့်စာရင်းမှ မပေါက်ပါ။")
            
            log_activity("Manual Win Check", f"Checked {checked_count} with number {winning_number}, Won {won_count}")
            time.sleep(2)
            st.rerun()
        else:
            st.info(f"{number_type} ဂဏန်းထိုးထားသော စာရင်းများမရှိပါ။")
    
    st.divider()
    
    # Auto check all pending entries with system winning numbers
    st.markdown("### ⚡ အလိုအလျောက်စစ်ဆေးရန် (System ပေါက်ဂဏန်းများဖြင့်)")
    
    if st.button("🔄 ယနေ့စာရင်းအားလုံးကို အလိုအလျောက်စစ်ဆေးရန်", use_container_width=True):
        with st.spinner("စစ်ဆေးနေသည်..."):
            checked_count = 0
            won_count = 0
            total_payout = 0
            
            for entry in today_entries:
                if entry.get('status') == 'Pending':
                    entry_number_type = entry['number_type']
                    winning_number = winning_info['2d'] if entry_number_type == "2D" else winning_info['3d']
                    
                    if winning_number:
                        is_winning, message = check_winning_number(
                            entry['number'],
                            winning_number,
                            entry_number_type
                        )
                        
                        if is_winning:
                            entry['status'] = 'Won'
                            entry['winning_message'] = message
                            entry['winning_time'] = format_myanmar_time()
                            payout_amount = calculate_payout_amount(entry['amount'], entry_number_type)
                            entry['payout_amount'] = payout_amount
                            total_payout += payout_amount
                            won_count += 1
                            
                            # Log payout
                            log_payout(
                                entry['customer'],
                                entry['number'],
                                entry['amount'],
                                payout_amount,
                                winning_number,
                                st.session_state.current_user
                            )
                        else:
                            entry['status'] = 'Lost'
                            entry['winning_message'] = message
                            entry['winning_time'] = format_myanmar_time()
                        
                        checked_count += 1
            
            save_data()
            
            st.success(f"✅ {checked_count} ခုစစ်ဆေးပြီး {won_count} ခုပေါက်ပါသည်။")
            
            if won_count > 0:
                st.markdown(f"""
                <div class="payout-box">
                    <h4>စုစုပေါင်းလျော်ကြေး</h4>
                    <p><strong>ပေါက်ခုအရေအတွက်:</strong> {won_count}</p>
                    <p><strong>စုစုပေါင်းလျော်ကြေး:</strong> {total_payout:,} Ks</p>
                </div>
                """, unsafe_allow_html=True)
            
            log_activity("Auto Win Check", f"Checked {checked_count}, Won {won_count}")
            time.sleep(2)
            st.rerun()

def render_agent_today_entries():
    """Display today's entries for agent - AGENT SEES ONLY THEIR OWN ENTRIES"""
    st.markdown('<h1 class="main-title">📋 ယနေ့စာရင်းများ (သင့်အေဂျင့်)</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    
    if not today_entries:
        st.info("ယနေ့အတွက် မည်သည့်စာရင်းမှ မရှိသေးပါ။")
        return
    
    # Summary statistics - ONLY FOR THIS AGENT
    total_entries = len(today_entries)
    pending_entries = sum(1 for e in today_entries if e.get('status') == 'Pending')
    won_entries = sum(1 for e in today_entries if e.get('status') == 'Won')
    lost_entries = sum(1 for e in today_entries if e.get('status') == 'Lost')
    total_amount = sum(e.get('amount', 0) for e in today_entries)
    total_payout = sum(e.get('payout_amount', 0) for e in today_entries if e.get('status') == 'Won')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("စုစုပေါင်းစာရင်း", total_entries)
    with col2:
        st.metric("Pending", pending_entries)
    with col3:
        st.metric("ပေါက်", won_entries)
    with col4:
        st.metric("လျော်ကြေး", f"{total_payout:,} Ks")
    
    st.divider()
    
    # Filter options
    col_filter, col_search, col_export = st.columns([1, 2, 1])
    
    with col_filter:
        status_filter = st.selectbox(
            "အခြေအနေစစ်ထုတ်ရန်",
            ["အားလုံး", "Pending", "Won", "Lost"],
            index=0
        )
    
    with col_search:
        search_query = st.text_input("🔍 ရှာဖွေရန်", placeholder="ဝယ်ယူသူအမည် သို့မဟုတ် ဂဏန်း")
    
    # Filter entries
    filtered_entries = today_entries.copy()
    
    if status_filter != "အားလုံး":
        filtered_entries = [e for e in filtered_entries if e.get('status') == status_filter]
    
    if search_query:
        filtered_entries = [e for e in filtered_entries 
                          if search_query.lower() in e.get('customer', '').lower() 
                          or search_query in e.get('number', '')]
    
    # Display entries
    if filtered_entries:
        st.markdown(f"### 📝 စာရင်းများ ({len(filtered_entries)} ခု)")
        
        for i, entry in enumerate(filtered_entries):
            # Status color and icon
            status_config = {
                'Pending': {'color': '#F59E0B', 'icon': '⏳'},
                'Won': {'color': '#10B981', 'icon': '🏆'},
                'Lost': {'color': '#EF4444', 'icon': '❌'}
            }
            
            status_info = status_config.get(entry.get('status', 'Pending'), {'color': '#6B7280', 'icon': '❓'})
            
            with st.expander(f"{status_info['icon']} #{entry['id']} - {entry['customer']} ({entry['number']}) - {entry['amount']:,} Ks", 
                           expanded=(i == 0)):
                
                col_info, col_status = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
                    **အချိန်:** {entry['time']}  
                    **ဝယ်ယူသူ:** {entry['customer']}  
                    **ဂဏန်း:** {entry['number']} ({entry['number_type']})  
                    **ပမာဏ:** {entry['amount']:,} Ks  
                    """)
                    
                    if entry.get('note'):
                        st.markdown(f"**မှတ်ချက်:** {entry['note']}")
                    
                    if entry.get('winning_message'):
                        st.markdown(f"**ပေါက်အခြေအနေ:** {entry['winning_message']}")
                    
                    if entry.get('winning_time'):
                        st.markdown(f"**ပေါက်ချိန်:** {entry['winning_time']}")
                    
                    if entry.get('payout_amount', 0) > 0:
                        st.markdown(f"**လျော်ကြေး:** {entry['payout_amount']:,} Ks")
                
                with col_status:
                    st.markdown(f"<span style='color: {status_info['color']}; font-weight: bold;'>{entry['status']}</span>", 
                              unsafe_allow_html=True)
                    
                    # Edit button for pending entries
                    if entry.get('status') == 'Pending':
                        if st.button("✏️ ပြင်ဆင်ရန်", key=f"edit_{entry['id']}"):
                            st.session_state.editing_entry = entry['id']
                            st.rerun()
        
        # Edit form
        if 'editing_entry' in st.session_state and st.session_state.editing_entry:
            entry_id_to_edit = st.session_state.editing_entry
            entry_index = next((i for i, e in enumerate(today_entries) if e['id'] == entry_id_to_edit), None)
            
            if entry_index is not None:
                entry = today_entries[entry_index]
                
                st.markdown("---")
                st.markdown("### ✏️ စာရင်းပြင်ဆင်ရန်")
                
                with st.form(f"edit_entry_form_{entry['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edited_customer = st.text_input("ဝယ်ယူသူအမည်", value=entry['customer'])
                        edited_number = st.text_input("ဂဏန်း", value=entry['number'])
                    
                    with col2:
                        edited_amount = st.number_input("ပမာဏ", min_value=50, value=entry['amount'])
                        edited_note = st.text_input("မှတ်ချက်", value=entry.get('note', ''))
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save_btn = st.form_submit_button("💾 သိမ်းဆည်းရန်", use_container_width=True)
                        if save_btn:
                            # Update entry
                            today_entries[entry_index]['customer'] = edited_customer
                            today_entries[entry_index]['number'] = edited_number
                            today_entries[entry_index]['amount'] = edited_amount
                            today_entries[entry_index]['note'] = edited_note
                            today_entries[entry_index]['number_type'] = "2D" if len(edited_number) == 2 else "3D"
                            
                            save_data()
                            
                            del st.session_state.editing_entry
                            st.success("✅ စာရင်းပြင်ဆင်ပြီးပါပြီ။")
                            log_activity("Edit Entry", f"Edited entry #{entry['id']}")
                            time.sleep(1)
                            st.rerun()
                    
                    with col_cancel:
                        cancel_btn = st.form_submit_button("❌ ပယ်ဖျက်ရန်", use_container_width=True)
                        if cancel_btn:
                            del st.session_state.editing_entry
                            st.rerun()
        
        # Export option
        with col_export:
            if st.button("📤 Export လုပ်ရန်", use_container_width=True):
                export_data = []
                for entry in today_entries:
                    export_data.append({
                        'ID': entry['id'],
                        'Time': entry['time'],
                        'Customer': entry['customer'],
                        'Number': entry['number'],
                        'Type': entry['number_type'],
                        'Amount': entry['amount'],
                        'Status': entry['status'],
                        'Winning Time': entry.get('winning_time', ''),
                        'Winning Message': entry.get('winning_message', ''),
                        'Payout Amount': entry.get('payout_amount', 0),
                        'Note': entry.get('note', '')
                    })
                
                df_export = pd.DataFrame(export_data)
                csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                
                today_date = datetime.now().strftime('%Y%m%d')
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"betting_entries_{st.session_state.current_user}_{today_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("ရှာဖွေမှုနှင့်ကိုက်ညီသော စာရင်းများမတွေ့ရှိပါ။")

def render_agent_payouts():
    """Display agent's payout records - AGENT SEES ONLY THEIR OWN PAYOUTS"""
    st.markdown('<h1 class="main-title">💰 လျော်ကြေးစာရင်း (သင့်အေဂျင့်)</h1>', unsafe_allow_html=True)
    
    # Filter agent's payouts
    agent_payouts = [p for p in st.session_state.payout_log 
                     if p.get('agent') == st.session_state.current_user]
    
    if agent_payouts:
        total_payout = sum(p.get('payout_amount', 0) for p in agent_payouts)
        st.metric("စုစုပေါင်းလျော်ကြေး", f"{total_payout:,} Ks")
        
        st.divider()
        
        # Display payouts
        st.markdown("### 📋 လျော်ကြေးမှတ်တမ်း")
        
        for payout in reversed(agent_payouts[-20:]):  # Show last 20 payouts
            st.markdown(f"""
            <div class="entry-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong>{payout['customer']}</strong>
                        <div style="color: #6B7280; font-size: 0.9rem;">
                            {payout['timestamp']} | {payout['bet_number']} ({'2D' if len(payout['bet_number']) == 2 else '3D'})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: bold; color: #10B981;">
                            {payout['payout_amount']:,} Ks
                        </div>
                        <div style="font-size: 0.9rem; color: #6B7280;">
                            Bet: {payout['bet_amount']:,} Ks
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9rem;">
                    <strong>ပေါက်ဂဏန်း:</strong> {payout['winning_number']} | 
                    <strong>အခြေအနေ:</strong> {payout.get('status', 'Paid')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("လျော်ကြေးမှတ်တမ်းမရှိပါ။")

# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    
    init_session_state()
    
    if not st.session_state.users_db:
        init_default_data()
    
    if not st.session_state.logged_in:
        saved_data = load_data()
        if saved_data:
            st.session_state.users_db.update(saved_data.get('users_db', {}))
            st.session_state.today_entries.update(saved_data.get('today_entries', {}))
            st.session_state.activity_log.extend(saved_data.get('activity_log', []))
            st.session_state.winning_numbers.update(saved_data.get('winning_numbers', {}))
            st.session_state.payout_log.extend(saved_data.get('payout_log', []))
    
    st.set_page_config(
        page_title="2D/3D Betting System",
        page_icon="🎰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(load_custom_css(), unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        render_login_page()
    else:
        if st.session_state.user_role == 'admin':
            render_admin_panel()
        elif st.session_state.user_role == 'agent':
            render_2d_app()
        else:
            st.error("Invalid user role")
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()
