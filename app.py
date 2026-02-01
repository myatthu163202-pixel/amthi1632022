# main_app.py - Complete 2D Betting System with Admin & Agent in One App

import streamlit as st
import pandas as pd
import time
import hashlib
import re
from datetime import datetime, timedelta
import pytz
import json
import os
from typing import Dict, List, Tuple, Optional

# ==================== CONFIGURATION ====================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
PRICE_PER_NUMBER = 50000  # 2D ဂဏန်းတစ်လုံးဈေး
ADMIN_USERNAME = "AMTHI"
ADMIN_PASSWORD = "1632022"
DATA_FILE = "betting_data.json"  # ဒေတာသိမ်းမယ့်ဖိုင်

# ==================== CUSTOM CSS ====================
def load_custom_css():
    """Custom CSS styles"""
    return """
    <style>
    /* Main Title */
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 4px solid #3B82F6;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sub Title */
    .sub-title {
        font-size: 2.0rem;
        color: #1E40AF;
        margin-bottom: 1.2rem;
        padding-left: 10px;
        border-left: 5px solid #60A5FA;
        font-weight: 600;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #7DD3FC;
        margin: 1.2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #FBBF24;
        margin: 1.2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #10B981;
        margin: 1.2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* User Card */
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    /* Metric Card */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Entry Card */
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
    
    /* Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #D1D5DB;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
            'user_configs': st.session_state.user_configs
        }
        
        # Convert datetime objects to strings
        for key in ['users_db', 'today_entries']:
            if key in data:
                data[key] = {
                    k: {k2: (v2.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v2, datetime) else v2) 
                        for k2, v2 in v.items()} 
                    for k, v in data[key].items()
                }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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
            
            # Restore datetime objects
            for key in ['users_db', 'today_entries']:
                if key in data:
                    for user_key, user_data in data[key].items():
                        for field, value in user_data.items():
                            if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):
                                try:
                                    data[key][user_key][field] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                except:
                                    pass
            
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
        'user_configs': {},
        'hidden_sections': {},
        'selected_menu': '🏠 Dashboard',
        'editing_entry': None,
        'show_add_agent': False
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def init_default_data():
    """Default data များစတင်ခြင်း"""
    if not st.session_state.users_db:
        # Admin account (hardcoded)
        st.session_state.users_db[ADMIN_USERNAME] = {
            'password': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
            'role': 'admin',
            'name': 'စီမံခန့်ခွဲသူ',
            'email': 'admin@2dsystem.com',
            'phone': '',
            'address': '',
            'created_at': datetime.now(),
            'last_login': datetime.now(),
            'sheet_url': '',
            'daily_limit': 0,
            'status': 'active'
        }
        
        # Default agent account
        st.session_state.users_db['agent1'] = {
            'password': hashlib.sha256('agent123'.encode()).hexdigest(),
            'role': 'agent',
            'name': 'အေဂျင့်တစ်',
            'email': 'agent1@2dsystem.com',
            'phone': '09123456789',
            'address': 'ရန်ကုန်',
            'created_at': datetime.now(),
            'last_login': datetime.now(),
            'sheet_url': '',
            'daily_limit': 1000000,
            'commission_rate': 10,  # 10%
            'status': 'active'
        }
        
        # Auto-save data
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
        if not (0 <= int(number_str) <= 99):
            return False, "2D ဂဏန်းသည် 00 မှ 99 အတွင်းဖြစ်ရမည်"
        return True, "2D ဂဏန်း"
    
    elif len(number_str) == 3:
        if not (0 <= int(number_str) <= 999):
            return False, "3D ဂဏန်းသည် 000 မှ 999 အတွင်းဖြစ်ရမည်"
        return True, "3D ဂဏန်း"
    
    else:
        return False, "ဂဏန်းသည် ၂ လုံး သို့မဟုတ် ၃ လုံးဖြစ်ရမည်"

def validate_name(name: str) -> Tuple[bool, str]:
    """နာမည်စစ်ဆေးခြင်း"""
    if not name or len(name.strip()) < 2:
        return False, "နာမည်အနည်းဆုံး ၂ လုံးထည့်ပါ"
    
    if len(name.strip()) > 50:
        return False, "နာမည်အရှည်လွန်းသည်"
    
    return True, ""

def calculate_amount(number_str: str, quantity: int) -> int:
    """စုစုပေါင်းပမာဏတွက်ချက်ခြင်း"""
    base_price = PRICE_PER_NUMBER
    if len(number_str) == 3:  # 3D ဆိုပိုဈေးကြီး
        base_price = PRICE_PER_NUMBER * 10
    
    return base_price * quantity

def log_activity(action: str, details: str = ""):
    """လုပ်ဆောင်ချက်မှတ်တမ်းထားရှိခြင်း"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        
        # Auto-save
        save_data()
        
    except Exception as e:
        st.error(f"Activity log error: {str(e)}")

# ==================== AUTHENTICATION ====================
def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """အသုံးပြုသူအတည်ပြုခြင်း"""
    username = username.strip()
    
    # Admin authentication
    if username.upper() == ADMIN_USERNAME.upper():
        if password == ADMIN_PASSWORD:
            # Create admin account if not exists
            if ADMIN_USERNAME not in st.session_state.users_db:
                st.session_state.users_db[ADMIN_USERNAME] = {
                    'password': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
                    'role': 'admin',
                    'name': 'စီမံခန့်ခွဲသူ',
                    'email': '',
                    'phone': '',
                    'address': '',
                    'created_at': datetime.now(),
                    'last_login': datetime.now(),
                    'sheet_url': '',
                    'daily_limit': 0,
                    'status': 'active'
                }
                save_data()
            
            st.session_state.users_db[ADMIN_USERNAME]['last_login'] = datetime.now()
            log_activity("Login", f"Admin: {ADMIN_USERNAME}")
            return True, 'admin'
    
    # Other users authentication
    for stored_username, user_data in st.session_state.users_db.items():
        if stored_username.lower() == username.lower():
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user_data['password'] == hashed_password:
                if user_data.get('status', 'active') != 'active':
                    return False, "အကောင့်ပိတ်ထားသည်"
                
                user_data['last_login'] = datetime.now()
                log_activity("Login", f"User: {stored_username} ({user_data['role']})")
                return True, user_data['role']
    
    return False, None

# ==================== USER MANAGEMENT ====================
def add_new_user(username: str, password: str, role: str, name: str, 
                 email: str = "", phone: str = "", address: str = "") -> Tuple[bool, str]:
    """အသုံးပြုသူအသစ်ထည့်ခြင်း"""
    try:
        # Validation
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
        
        # Create user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        st.session_state.users_db[username] = {
            'password': hashed_password,
            'role': role,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'created_at': datetime.now(),
            'last_login': datetime.now(),
            'sheet_url': '',
            'daily_limit': 1000000 if role == 'agent' else 0,
            'commission_rate': 10 if role == 'agent' else 0,
            'status': 'active'
        }
        
        # Initialize user data
        if role == 'agent':
            st.session_state.today_entries[username] = []
            st.session_state.user_configs[username] = {
                'sheet_url': '',
                'script_url': ''
            }
        
        log_activity("Add User", f"New user: {username} ({role}) - {name}")
        save_data()
        return True, f"အကောင့် '{username}' အောင်မြင်စွာထည့်သွင်းပြီးပါပြီ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_user_info(username: str, **kwargs) -> Tuple[bool, str]:
    """အသုံးပြုသူအချက်အလက်ပြင်ဆင်ခြင်း"""
    try:
        if username in st.session_state.users_db:
            for key, value in kwargs.items():
                if key == 'password' and value:
                    st.session_state.users_db[username][key] = hashlib.sha256(value.encode()).hexdigest()
                elif value or value == 0:
                    st.session_state.users_db[username][key] = value
            
            log_activity("Update User", f"Updated: {username}")
            save_data()
            return True, "အချက်အလက်ပြင်ဆင်ပြီးပါပြီ။"
        
        return False, "အသုံးပြုသူမတွေ့ပါ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_user_account(username: str) -> Tuple[bool, str]:
    """အသုံးပြုသူဖျက်ခြင်း"""
    try:
        if username in st.session_state.users_db:
            if username == st.session_state.current_user:
                return False, "မိမိကိုယ်တိုင်ဖျက်ရန်မဖြစ်နိုင်ပါ။"
            
            if username == ADMIN_USERNAME:
                return False, "Admin အကောင့်ဖျက်လို့မရပါ။"
            
            del st.session_state.users_db[username]
            
            # Remove related data
            if username in st.session_state.today_entries:
                del st.session_state.today_entries[username]
            if username in st.session_state.user_configs:
                del st.session_state.user_configs[username]
            
            log_activity("Delete User", f"Deleted: {username}")
            save_data()
            return True, f"အကောင့် '{username}' ဖျက်ပြီးပါပြီ။"
        
        return False, "အသုံးပြုသူမတွေ့ပါ။"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== LOGIN PAGE ====================
def render_login_page():
    """Login page for all users"""
    st.markdown(load_custom_css(), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">🎰 2D ထီထိုးစနစ်</h1>', unsafe_allow_html=True)
        
        # Myanmar Time Display
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
                    placeholder="AMTHI သို့မဟုတ် agent1",
                    key="login_username"
                )
                
                password = st.text_input(
                    "🔒 **စကားဝှက်**", 
                    type="password",
                    placeholder="password",
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
                                
                                # Initialize user data for agents
                                if role_or_error == 'agent':
                                    if username not in st.session_state.today_entries:
                                        st.session_state.today_entries[username] = []
                                    if username not in st.session_state.user_configs:
                                        st.session_state.user_configs[username] = {
                                            'sheet_url': st.session_state.users_db.get(username, {}).get('sheet_url', ''),
                                            'script_url': ''
                                        }
                                
                                st.success(f"✅ **{role_or_error.upper()}** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {role_or_error if role_or_error else 'အကောင့်မှန်ကန်မှုမရှိပါ။'}")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ အသုံးပြုသူအမည်နှင့် စကားဝှက်ထည့်ပါ။")
            
            # Information section
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### ℹ️ အကောင့်အချက်အလက်")
            st.markdown("""
            **Default Credentials:**
            - **Admin:** `AMTHI` / `1632022`
            - **Agent:** `agent1` / `agent123`
            
            **မှတ်ချက်:** Admin အကောင့်ဖြင့်ဝင်ပါက Agent များကိုစီမံနိုင်သည်။
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>"
            "© 2024 2D Betting System | Version 1.0.0"
            "</div>",
            unsafe_allow_html=True
        )

# ==================== ADMIN PANEL ====================
def render_admin_panel():
    """Admin panel main function"""
    
    # Sidebar
    with st.sidebar:
        user_info = st.session_state.users_db.get(st.session_state.current_user, {})
        
        # User Info Card
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
            <p><strong>📊 Status:</strong> <span style="color: #10B981;">● Active</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation Menu
        st.markdown("### 🧭 မီနူးရွေးချယ်ရန်")
        
        menu_options = {
            "🏠 Dashboard": "dashboard",
            "👥 Agent Management": "agents",
            "📊 Reports & Analytics": "reports",
            "⚙️ System Settings": "settings",
            "💾 Backup & Restore": "backup"
        }
        
        selected_key = st.radio(
            "Menu Selection",
            options=list(menu_options.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_menu = menu_options[selected_key]
        
        st.divider()
        
        # Quick Stats
        st.markdown("### 📈 စနစ်အခြေအနေ")
        
        total_users = len(st.session_state.users_db)
        agent_count = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'agent')
        active_agents = sum(1 for u in st.session_state.users_db.values() 
                          if u.get('role') == 'agent' and u.get('status') == 'active')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Total Agents", agent_count)
        
        st.metric("Active Agents", active_agents, delta=f"{active_agents}/{agent_count}")
        
        st.divider()
        
        # Logout Button
        if st.button("🚪 အကောင့်ထွက်ရန်", use_container_width=True, type="secondary"):
            log_activity("Logout", f"Admin: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main Content based on selected menu
    if st.session_state.selected_menu == 'dashboard':
        render_admin_dashboard()
    elif st.session_state.selected_menu == 'agents':
        render_agent_management()
    elif st.session_state.selected_menu == 'reports':
        render_admin_reports()
    elif st.session_state.selected_menu == 'settings':
        render_admin_settings()
    elif st.session_state.selected_menu == 'backup':
        render_backup_restore()

def render_admin_dashboard():
    """Admin dashboard"""
    st.markdown('<h1 class="main-title">📊 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(st.session_state.users_db)
        st.metric("Total Users", total_users, help="စနစ်တွင်ရှိသောအသုံးပြုသူအားလုံး")
    
    with col2:
        admin_count = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'admin')
        st.metric("Admins", admin_count, help="စီမံခန့်ခွဲသူအရေအတွက်")
    
    with col3:
        agent_count = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'agent')
        st.metric("Agents", agent_count, help="အေဂျင့်အရေအတွက်")
    
    with col4:
        activity_count = len(st.session_state.activity_log)
        st.metric("Activities", activity_count, help="လုပ်ဆောင်ချက်မှတ်တမ်းအရေအတွက်")
    
    st.divider()
    
    # System Overview
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Recent Activities
        st.markdown("### 📝 လတ်တလောလုပ်ဆောင်ချက်များ")
        
        recent_activities = st.session_state.activity_log[-20:] if st.session_state.activity_log else []
        
        if recent_activities:
            for activity in reversed(recent_activities):
                with st.container():
                    icon = "🔔" if "Login" in activity['action'] else "📝" if "Entry" in activity['action'] else "⚙️"
                    st.markdown(f"""
                    <div class="entry-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{icon} {activity['action']}</strong>
                                <div style="color: #6B7280; font-size: 0.9rem; margin-top: 5px;">
                                    👤 {activity['user']} | 🕐 {activity['timestamp']}
                                    {f"<br>📋 {activity['details']}" if activity['details'] else ""}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No activities recorded yet.")
    
    with col_right:
        # Quick Actions
        st.markdown("### 🚀 မြန်ဆန်လုပ်ဆောင်ချက်များ")
        
        quick_actions = [
            {"icon": "➕", "label": "Add New Agent", "func": lambda: st.session_state.update({"show_add_agent": True})},
            {"icon": "📊", "label": "Generate Report", "func": None},
            {"icon": "⚙️", "label": "System Settings", "func": None},
            {"icon": "💾", "label": "Backup Data", "func": lambda: save_data()}
        ]
        
        for action in quick_actions:
            if st.button(f"{action['icon']} {action['label']}", use_container_width=True):
                if action['func']:
                    action['func']()
                    if action['label'] == "Add New Agent":
                        st.session_state.selected_menu = 'agents'
                    st.rerun()
        
        st.divider()
        
        # System Status
        st.markdown("### 🟢 စနစ်အခြေအနေ")
        
        status_items = [
            ("Database", "🟢 Online", "success"),
            ("Authentication", "🟢 Active", "success"),
            ("Data Backup", "🟡 Manual", "warning"),
            ("User Activity", f"🟢 {len(recent_activities)} recent", "success")
        ]
        
        for item, status, color in status_items:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>{item}</span>
                <span style="color: {'#10B981' if color == 'success' else '#F59E0B'}">{status}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Agent Summary
    st.markdown("### 👥 Agent Summary")
    
    agents = []
    for username, details in st.session_state.users_db.items():
        if details.get('role') == 'agent':
            today_entries = st.session_state.today_entries.get(username, [])
            today_total = sum(entry.get('amount', 0) for entry in today_entries)
            
            agents.append({
                'Username': username,
                'Name': details.get('name', 'N/A'),
                'Status': details.get('status', 'active').title(),
                'Today Entries': len(today_entries),
                'Today Amount': f"{today_total:,} Ks",
                'Daily Limit': f"{details.get('daily_limit', 0):,} Ks"
            })
    
    if agents:
        df = pd.DataFrame(agents)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Agent status"
                )
            }
        )
    else:
        st.info("No agents found in the system.")

def render_agent_management():
    """Agent management system"""
    st.markdown('<h1 class="main-title">👥 Agent Management System</h1>', unsafe_allow_html=True)
    
    # Tabs for different agent management functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add New Agent", 
        "📋 Agent List", 
        "✏️ Edit Agent", 
        "📊 Agent Statistics"
    ])
    
    with tab1:
        render_add_agent_form()
    
    with tab2:
        render_agent_list()
    
    with tab3:
        render_edit_agent_form()
    
    with tab4:
        render_agent_statistics()

def render_add_agent_form():
    """Form to add new agent"""
    st.markdown('<h3 class="sub-title">➕ Add New Agent</h3>', unsafe_allow_html=True)
    
    with st.form("add_agent_form", clear_on_submit=True):
        st.markdown("### 👤 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input(
                "Username *",
                placeholder="agent2",
                help="English letters, numbers and underscore only (3-20 characters)"
            )
            
            new_password = st.text_input(
                "Password *",
                type="password",
                placeholder="Minimum 6 characters",
                help="Strong password with at least 6 characters"
            )
            
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password"
            )
        
        with col2:
            new_name = st.text_input(
                "Full Name *",
                placeholder="Agent Two",
                help="Agent's full name"
            )
            
            new_email = st.text_input(
                "Email Address",
                placeholder="agent2@company.com",
                help="Valid email address"
            )
        
        st.markdown("### 📞 Contact Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            new_phone = st.text_input(
                "Phone Number",
                placeholder="09123456789",
                help="Mobile phone number"
            )
        
        with col4:
            new_address = st.text_input(
                "Address",
                placeholder="City, Township",
                help="Current address"
            )
        
        st.markdown("### ⚙️ Agent Configuration")
        
        col5, col6 = st.columns(2)
        
        with col5:
            sheet_url = st.text_input(
                "Google Sheets URL",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                help="Agent's personal Google Sheets for data storage"
            )
        
        with col6:
            max_daily_limit = st.number_input(
                "Daily Betting Limit (Ks) *",
                min_value=100000,
                max_value=10000000,
                value=1000000,
                step=100000,
                help="Maximum daily betting amount in Kyats"
            )
        
        commission_rate = st.slider(
            "Commission Rate (%)",
            min_value=0,
            max_value=50,
            value=10,
            step=1,
            help="Percentage commission for this agent"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ **Add New Agent**",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            errors = []
            
            if not all([new_username, new_password, new_name]):
                errors.append("Please fill all required fields (*)")
            
            if new_password != confirm_password:
                errors.append("Passwords do not match")
            
            if len(new_password) < 6:
                errors.append("Password must be at least 6 characters")
            
            if not re.match("^[a-zA-Z0-9_]+$", new_username):
                errors.append("Username can only contain letters, numbers and underscore")
            
            if len(new_username) < 3 or len(new_username) > 20:
                errors.append("Username must be 3-20 characters")
            
            if new_email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', new_email):
                errors.append("Invalid email format")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                success, message = add_new_user(
                    new_username, new_password, 'agent', new_name, 
                    new_email, new_phone, new_address
                )
                
                if success:
                    # Add additional settings
                    update_data = {
                        'sheet_url': sheet_url if sheet_url else '',
                        'daily_limit': max_daily_limit,
                        'commission_rate': commission_rate
                    }
                    update_user_info(new_username, **update_data)
                    
                    st.success(f"✅ {message}")
                    st.balloons()
                    log_activity("Agent Added", f"New agent: {new_username} - {new_name}")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def render_agent_list():
    """Display list of all agents"""
    st.markdown('<h3 class="sub-title">📋 Agent List</h3>', unsafe_allow_html=True)
    
    # Search and filter
    col_search, col_filter, col_export = st.columns([2, 1, 1])
    
    with col_search:
        search_query = st.text_input("🔍 Search Agents", placeholder="Search by name or username")
    
    with col_filter:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "Active", "Inactive"],
            index=0
        )
    
    # Get agent data
    agents = []
    for username, details in st.session_state.users_db.items():
        if details.get('role') == 'agent':
            # Apply filters
            if status_filter != "All" and details.get('status', 'active') != status_filter.lower():
                continue
            
            if search_query and search_query.lower() not in username.lower() and search_query.lower() not in details.get('name', '').lower():
                continue
            
            today_entries = st.session_state.today_entries.get(username, [])
            today_total = sum(entry.get('amount', 0) for entry in today_entries)
            
            agents.append({
                'Username': username,
                'Name': details.get('name', 'N/A'),
                'Email': details.get('email', 'N/A'),
                'Phone': details.get('phone', 'N/A'),
                'Status': details.get('status', 'active').title(),
                'Created': details.get('created_at', datetime.now()).strftime('%Y-%m-%d'),
                'Last Login': details.get('last_login', datetime.now()).strftime('%Y-%m-%d %H:%M'),
                'Today Entries': len(today_entries),
                'Today Amount': today_total,
                'Daily Limit': details.get('daily_limit', 0),
                'Commission': f"{details.get('commission_rate', 0)}%"
            })
    
    if agents:
        # Summary stats
        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a['Status'] == 'Active')
        total_today_entries = sum(a['Today Entries'] for a in agents)
        total_today_amount = sum(a['Today Amount'] for a in agents)
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("Total Agents", total_agents)
        with col_stat2:
            st.metric("Active Agents", active_agents)
        with col_stat3:
            st.metric("Today's Entries", total_today_entries)
        with col_stat4:
            st.metric("Today's Amount", f"{total_today_amount:,} Ks")
        
        st.divider()
        
        # Display agent table
        df = pd.DataFrame(agents)
        
        # Format columns
        display_df = df.copy()
        display_df['Today Amount'] = display_df['Today Amount'].apply(lambda x: f"{x:,} Ks")
        display_df['Daily Limit'] = display_df['Daily Limit'].apply(lambda x: f"{x:,} Ks")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Agent status",
                    width="small"
                ),
                "Today Entries": st.column_config.NumberColumn(
                    "Today Entries",
                    help="Number of entries today",
                    width="small"
                ),
                "Today Amount": st.column_config.TextColumn(
                    "Today Amount",
                    help="Total amount today"
                )
            }
        )
        
        st.divider()
        
        # Export options
        with col_export:
            if st.button("📥 Export to CSV", use_container_width=True):
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                today_date = datetime.now().strftime('%Y%m%d')
                
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"agents_list_{today_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("No agents found matching the criteria.")

def render_edit_agent_form():
    """Form to edit existing agent"""
    st.markdown('<h3 class="sub-title">✏️ Edit Agent Information</h3>', unsafe_allow_html=True)
    
    # Get agent list
    agent_list = [u for u in st.session_state.users_db.keys() 
                 if st.session_state.users_db[u].get('role') == 'agent']
    
    if not agent_list:
        st.info("No agents available to edit.")
        return
    
    # Agent selection
    selected_agent = st.selectbox(
        "Select Agent to Edit",
        agent_list,
        help="Choose an agent to edit their information"
    )
    
    if selected_agent:
        agent_info = st.session_state.users_db[selected_agent]
        
        # Display current info
        with st.expander("📋 Current Agent Information", expanded=True):
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Username:** `{selected_agent}`")
                st.markdown(f"**Name:** {agent_info.get('name', 'N/A')}")
                st.markdown(f"**Email:** {agent_info.get('email', 'N/A')}")
                st.markdown(f"**Phone:** {agent_info.get('phone', 'N/A')}")
            
            with col_info2:
                st.markdown(f"**Status:** {agent_info.get('status', 'active').title()}")
                st.markdown(f"**Created:** {agent_info.get('created_at', datetime.now()).strftime('%Y-%m-%d')}")
                st.markdown(f"**Last Login:** {agent_info.get('last_login', datetime.now()).strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Daily Limit:** {agent_info.get('daily_limit', 0):,} Ks")
        
        st.divider()
        
        # Edit form
        with st.form("edit_agent_form"):
            st.markdown("### ✏️ Edit Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Full Name", value=agent_info.get('name', ''))
                edit_email = st.text_input("Email", value=agent_info.get('email', ''))
                edit_phone = st.text_input("Phone", value=agent_info.get('phone', ''))
                edit_address = st.text_input("Address", value=agent_info.get('address', ''))
            
            with col2:
                edit_sheet_url = st.text_input(
                    "Google Sheets URL",
                    value=agent_info.get('sheet_url', ''),
                    placeholder="https://docs.google.com/spreadsheets/d/..."
                )
                
                edit_daily_limit = st.number_input(
                    "Daily Limit (Ks)",
                    min_value=0,
                    value=agent_info.get('daily_limit', 1000000),
                    step=100000,
                    help="Maximum daily betting amount"
                )
                
                edit_commission_rate = st.slider(
                    "Commission Rate (%)",
                    min_value=0,
                    max_value=50,
                    value=agent_info.get('commission_rate', 10),
                    step=1
                )
                
                edit_status = st.selectbox(
                    "Status",
                    ["active", "inactive"],
                    index=0 if agent_info.get('status', 'active') == 'active' else 1,
                    format_func=lambda x: "Active" if x == "active" else "Inactive"
                )
            
            # Password change section
            st.markdown("### 🔒 Change Password (Optional)")
            
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Enter new password to change",
                help="Leave empty to keep current password"
            )
            
            confirm_new_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Confirm new password"
            )
            
            # Action buttons
            col_save, col_reset, col_delete = st.columns(3)
            
            with col_save:
                save_changes = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_reset:
                reset_form = st.form_submit_button(
                    "🔄 Reset Form",
                    use_container_width=True,
                    type="secondary"
                )
            
            with col_delete:
                delete_agent = st.form_submit_button(
                    "🗑️ Delete Agent",
                    use_container_width=True,
                    type="secondary"
                )
            
            if save_changes:
                # Validate password if changed
                if new_password:
                    if new_password != confirm_new_password:
                        st.error("❌ New passwords do not match!")
                        return
                    
                    if len(new_password) < 6:
                        st.error("❌ New password must be at least 6 characters!")
                        return
                
                # Prepare update data
                update_data = {
                    'name': edit_name,
                    'email': edit_email,
                    'phone': edit_phone,
                    'address': edit_address,
                    'sheet_url': edit_sheet_url,
                    'daily_limit': edit_daily_limit,
                    'commission_rate': edit_commission_rate,
                    'status': edit_status
                }
                
                if new_password:
                    update_data['password'] = new_password
                
                # Update agent information
                success, message = update_user_info(selected_agent, **update_data)
                
                if success:
                    st.success("✅ Agent information updated successfully!")
                    log_activity("Agent Updated", f"Updated: {selected_agent}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            
            if delete_agent:
                st.warning(f"⚠️ Are you sure you want to delete agent: **{selected_agent}**?")
                confirm_delete = st.checkbox("Yes, I confirm deletion")
                
                if confirm_delete:
                    success, message = delete_user_account(selected_agent)
                    if success:
                        st.success(f"✅ {message}")
                        log_activity("Agent Deleted", f"Deleted: {selected_agent}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

def render_agent_statistics():
    """Display agent statistics"""
    st.markdown('<h3 class="sub-title">📊 Agent Performance Statistics</h3>', unsafe_allow_html=True)
    
    # Date range selection
    col_date1, col_date2, col_refresh = st.columns([2, 2, 1])
    
    with col_date1:
        start_date = st.date_input("Start Date", datetime.now().date())
    
    with col_date2:
        end_date = st.date_input("End Date", datetime.now().date())
    
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Calculate statistics
    agents_stats = []
    for username, details in st.session_state.users_db.items():
        if details.get('role') == 'agent':
            # Get agent's entries
            agent_entries = st.session_state.today_entries.get(username, [])
            
            # Filter by date range (simplified - using today's entries only)
            total_entries = len(agent_entries)
            total_amount = sum(entry.get('amount', 0) for entry in agent_entries)
            
            agents_stats.append({
                'Agent': details.get('name', username),
                'Username': username,
                'Total Entries': total_entries,
                'Total Amount': total_amount,
                'Average Per Entry': total_amount / total_entries if total_entries > 0 else 0,
                'Daily Limit': details.get('daily_limit', 0),
                'Limit Used %': (total_amount / details.get('daily_limit', 1)) * 100 if details.get('daily_limit', 0) > 0 else 0,
                'Status': details.get('status', 'active').title()
            })
    
    if agents_stats:
        df_stats = pd.DataFrame(agents_stats)
        
        # Display metrics
        st.markdown("### 📈 Performance Metrics")
        
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        
        with col_metric1:
            total_agents = len(df_stats)
            st.metric("Total Agents", total_agents)
        
        with col_metric2:
            total_entries = df_stats['Total Entries'].sum()
            st.metric("Total Entries", total_entries)
        
        with col_metric3:
            total_amount = df_stats['Total Amount'].sum()
            st.metric("Total Amount", f"{total_amount:,} Ks")
        
        with col_metric4:
            avg_per_agent = total_amount / total_agents if total_agents > 0 else 0
            st.metric("Avg per Agent", f"{avg_per_agent:,.0f} Ks")
        
        st.divider()
        
        # Performance chart
        st.markdown("### 📊 Agent Performance Chart")
        
        chart_data = df_stats[['Agent', 'Total Amount']].sort_values('Total Amount', ascending=False)
        st.bar_chart(chart_data.set_index('Agent'))
        
        st.divider()
        
        # Detailed statistics table
        st.markdown("### 📋 Detailed Statistics")
        
        # Format the dataframe for display
        display_stats = df_stats.copy()
        display_stats['Total Amount'] = display_stats['Total Amount'].apply(lambda x: f"{x:,} Ks")
        display_stats['Average Per Entry'] = display_stats['Average Per Entry'].apply(lambda x: f"{x:,.0f} Ks")
        display_stats['Daily Limit'] = display_stats['Daily Limit'].apply(lambda x: f"{x:,} Ks")
        display_stats['Limit Used %'] = display_stats['Limit Used %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            display_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Agent status"
                ),
                "Limit Used %": st.column_config.ProgressColumn(
                    "Limit Used %",
                    help="Percentage of daily limit used",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
        
        # Export statistics
        st.divider()
        if st.button("📤 Export Statistics Report", use_container_width=True):
            report_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create comprehensive report
            report_data = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'date_range': f"{start_date} to {end_date}",
                'summary': {
                    'total_agents': total_agents,
                    'total_entries': int(total_entries),
                    'total_amount': int(total_amount),
                    'average_per_agent': float(avg_per_agent)
                },
                'agent_details': agents_stats
            }
            
            # Convert to JSON for download
            report_json = json.dumps(report_data, indent=2, default=str)
            
            st.download_button(
                label="💾 Download JSON Report",
                data=report_json,
                file_name=f"agent_statistics_{report_date}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("No agent statistics available.")

def render_admin_reports():
    """Admin reports section"""
    st.markdown('<h1 class="main-title">📊 System Reports & Analytics</h1>', unsafe_allow_html=True)
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        [
            "System Summary",
            "Financial Report", 
            "User Activity Report",
            "Agent Performance Report",
            "Daily Transaction Report"
        ],
        index=0
    )
    
    # Date range selection
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", datetime.now().date())
    with col_date2:
        end_date = st.date_input("End Date", datetime.now().date())
    
    # Generate report button
    if st.button("📊 Generate Report", use_container_width=True, type="primary"):
        with st.spinner(f"Generating {report_type}..."):
            time.sleep(1)  # Simulate processing
            
            if report_type == "System Summary":
                render_system_summary_report(start_date, end_date)
            elif report_type == "Financial Report":
                render_financial_report(start_date, end_date)
            elif report_type == "User Activity Report":
                render_user_activity_report(start_date, end_date)
            elif report_type == "Agent Performance Report":
                render_agent_performance_report(start_date, end_date)
            elif report_type == "Daily Transaction Report":
                render_daily_transaction_report(start_date, end_date)

def render_system_summary_report(start_date, end_date):
    """Generate system summary report"""
    st.markdown("### 📈 System Summary Report")
    
    # System statistics
    total_users = len(st.session_state.users_db)
    admin_count = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'admin')
    agent_count = sum(1 for u in st.session_state.users_db.values() if u.get('role') == 'agent')
    active_agents = sum(1 for u in st.session_state.users_db.values() 
                      if u.get('role') == 'agent' and u.get('status') == 'active')
    
    # Activity statistics
    total_activities = len(st.session_state.activity_log)
    today_activities = len([a for a in st.session_state.activity_log 
                          if a['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))])
    
    # Transaction statistics (simulated)
    total_transactions = 0
    total_amount = 0
    for entries in st.session_state.today_entries.values():
        total_transactions += len(entries)
        total_amount += sum(entry.get('amount', 0) for entry in entries)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", total_users)
        st.metric("Admins", admin_count)
    
    with col2:
        st.metric("Total Agents", agent_count)
        st.metric("Active Agents", active_agents)
    
    with col3:
        st.metric("Total Activities", total_activities)
        st.metric("Today's Activities", today_activities)
    
    with col4:
        st.metric("Total Transactions", total_transactions)
        st.metric("Total Amount", f"{total_amount:,} Ks")
    
    st.divider()
    
    # Recent system activities
    st.markdown("### 📝 Recent System Activities")
    
    recent_activities = st.session_state.activity_log[-10:] if st.session_state.activity_log else []
    
    if recent_activities:
        for activity in reversed(recent_activities):
            st.markdown(f"""
            - **{activity['timestamp']}** - *{activity['user']}*: {activity['action']}
              {f"  - *Details*: {activity['details']}" if activity['details'] else ""}
            """)
    else:
        st.info("No recent activities found.")
    
    st.divider()
    
    # Export option
    if st.button("📤 Export Summary Report", use_container_width=True):
        report_data = {
            "report_type": "System Summary",
            "date_range": f"{start_date} to {end_date}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_stats": {
                "total_users": total_users,
                "admins": admin_count,
                "total_agents": agent_count,
                "active_agents": active_agents,
                "total_activities": total_activities,
                "today_activities": today_activities,
                "total_transactions": total_transactions,
                "total_amount": total_amount
            },
            "recent_activities": recent_activities[-20:]  # Last 20 activities
        }
        
        report_json = json.dumps(report_data, indent=2, default=str)
        
        st.download_button(
            label="💾 Download Report",
            data=report_json,
            file_name=f"system_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def render_financial_report(start_date, end_date):
    """Generate financial report"""
    st.markdown("### 💰 Financial Report")
    
    # Calculate financial data (simulated for now)
    total_revenue = 0
    total_payout = 0
    commission_total = 0
    
    for entries in st.session_state.today_entries.values():
        for entry in entries:
            total_revenue += entry.get('amount', 0)
            # Simulate payout (50% of winning entries)
            if entry.get('status') == 'Won':
                total_payout += entry.get('amount', 0) * 0.5
    
    net_profit = total_revenue - total_payout - commission_total
    
    # Financial metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"{total_revenue:,} Ks")
    
    with col2:
        st.metric("Total Payout", f"{total_payout:,} Ks", delta=f"-{total_payout:,} Ks")
    
    with col3:
        st.metric("Commission", f"{commission_total:,} Ks")
    
    with col4:
        st.metric("Net Profit", f"{net_profit:,} Ks", 
                 delta_color="normal" if net_profit >= 0 else "inverse")
    
    st.divider()
    
    # Revenue chart (simulated data)
    st.markdown("### 📈 Revenue Trend")
    
    # Simulated monthly data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue_data = [450000, 520000, 480000, 550000, 600000, 650000]
    
    chart_df = pd.DataFrame({
        'Month': months,
        'Revenue (Ks)': revenue_data
    })
    
    st.line_chart(chart_df.set_index('Month'))
    
    st.divider()
    
    # Top agents by revenue
    st.markdown("### 🏆 Top Performing Agents")
    
    agent_revenues = []
    for username, details in st.session_state.users_db.items():
        if details.get('role') == 'agent':
            entries = st.session_state.today_entries.get(username, [])
            total = sum(entry.get('amount', 0) for entry in entries)
            if total > 0:
                agent_revenues.append({
                    'Agent': details.get('name', username),
                    'Revenue': total,
                    'Entries': len(entries)
                })
    
    if agent_revenues:
        agent_revenues.sort(key=lambda x: x['Revenue'], reverse=True)
        
        for i, agent in enumerate(agent_revenues[:5], 1):
            st.markdown(f"""
            **{i}. {agent['Agent']}**
            - Revenue: {agent['Revenue']:,} Ks
            - Entries: {agent['Entries']}
            """)
    else:
        st.info("No agent revenue data available.")

def render_user_activity_report(start_date, end_date):
    """Generate user activity report"""
    st.markdown("### 👥 User Activity Report")
    
    if st.session_state.activity_log:
        # Convert to DataFrame for analysis
        activity_df = pd.DataFrame(st.session_state.activity_log)
        
        # User activity count
        user_activity = activity_df['user'].value_counts().reset_index()
        user_activity.columns = ['User', 'Activity Count']
        
        # Display top users
        st.markdown("#### 🏆 Most Active Users")
        st.dataframe(
            user_activity.head(10),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Activity type distribution
        st.markdown("#### 📊 Activity Type Distribution")
        activity_types = activity_df['action'].value_counts()
        
        col_chart, col_stats = st.columns([2, 1])
        
        with col_chart:
            st.bar_chart(activity_types)
        
        with col_stats:
            st.markdown("**Activity Summary:**")
            for action, count in activity_types.head(5).items():
                st.markdown(f"- {action}: **{count}**")
        
        st.divider()
        
        # Recent activity timeline
        st.markdown("#### 📅 Recent Activity Timeline")
        
        # Get recent activities
        recent_df = activity_df.tail(20).copy()
        recent_df['timestamp'] = pd.to_datetime(recent_df['timestamp'])
        recent_df = recent_df.sort_values('timestamp', ascending=False)
        
        for _, row in recent_df.iterrows():
            st.markdown(f"""
            **{row['timestamp'].strftime('%H:%M')}** - *{row['user']}*: {row['action']}
            {f"  *{row['details']}*" if row['details'] else ""}
            """)
    
    else:
        st.info("No activity data available for the selected period.")

def render_agent_performance_report(start_date, end_date):
    """Generate agent performance report"""
    st.markdown("### 🏆 Agent Performance Report")
    
    # Calculate agent performance metrics
    performance_data = []
    
    for username, details in st.session_state.users_db.items():
        if details.get('role') == 'agent':
            entries = st.session_state.today_entries.get(username, [])
            
            if entries:
                total_entries = len(entries)
                total_amount = sum(entry.get('amount', 0) for entry in entries)
                win_count = sum(1 for entry in entries if entry.get('status') == 'Won')
                loss_count = sum(1 for entry in entries if entry.get('status') == 'Lost')
                
                win_rate = (win_count / total_entries * 100) if total_entries > 0 else 0
                
                performance_data.append({
                    'Agent': details.get('name', username),
                    'Username': username,
                    'Total Entries': total_entries,
                    'Win Rate': f"{win_rate:.1f}%",
                    'Total Amount': f"{total_amount:,} Ks",
                    'Wins': win_count,
                    'Losses': loss_count,
                    'Commission Rate': f"{details.get('commission_rate', 0)}%",
                    'Status': details.get('status', 'active').title()
                })
    
    if performance_data:
        # Display performance metrics
        st.markdown("#### 📈 Performance Overview")
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(
            perf_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Performance comparison chart
        st.markdown("#### 📊 Amount Comparison")
        
        # Prepare chart data
        chart_data = []
        for perf in performance_data:
            amount = int(perf['Total Amount'].replace(' Ks', '').replace(',', ''))
            chart_data.append({
                'Agent': perf['Agent'],
                'Total Amount': amount
            })
        
        if chart_data:
            chart_df = pd.DataFrame(chart_data)
            chart_df = chart_df.sort_values('Total Amount', ascending=False)
            st.bar_chart(chart_df.set_index('Agent'))
        
        st.divider()
        
        # Export performance report
        if st.button("📤 Export Performance Report", use_container_width=True):
            report_data = {
                "report_type": "Agent Performance",
                "date_range": f"{start_date} to {end_date}",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "performance_data": performance_data
            }
            
            report_json = json.dumps(report_data, indent=2, default=str)
            
            st.download_button(
                label="💾 Download Report",
                data=report_json,
                file_name=f"agent_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    else:
        st.info("No agent performance data available for the selected period.")

def render_daily_transaction_report(start_date, end_date):
    """Generate daily transaction report"""
    st.markdown("### 💳 Daily Transaction Report")
    
    # Collect all transactions
    all_entries = []
    for username, entries in st.session_state.today_entries.items():
        for entry in entries:
            all_entries.append({
                'Agent': username,
                'Time': entry.get('time', ''),
                'Customer': entry.get('customer', ''),
                'Number': entry.get('number', ''),
                'Quantity': entry.get('quantity', 0),
                'Amount': entry.get('amount', 0),
                'Status': entry.get('status', 'Pending'),
                'Note': entry.get('note', '')
            })
    
    if all_entries:
        # Create DataFrame
        trans_df = pd.DataFrame(all_entries)
        
        # Summary statistics
        total_transactions = len(trans_df)
        total_amount = trans_df['Amount'].sum()
        avg_amount = trans_df['Amount'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Transactions", total_transactions)
        with col2:
            st.metric("Total Amount", f"{total_amount:,} Ks")
        with col3:
            st.metric("Average Amount", f"{avg_amount:,.0f} Ks")
        
        st.divider()
        
        # Transaction details
        st.markdown("#### 📋 Transaction Details")
        
        st.dataframe(
            trans_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(
                    "Amount (Ks)",
                    format="%d Ks"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Transaction status"
                )
            }
        )
        
        st.divider()
        
        # Status distribution
        st.markdown("#### 📊 Status Distribution")
        status_counts = trans_df['Status'].value_counts()
        
        col_chart, col_table = st.columns([2, 1])
        
        with col_chart:
            st.bar_chart(status_counts)
        
        with col_table:
            st.markdown("**Status Count:**")
            for status, count in status_counts.items():
                st.markdown(f"- {status}: **{count}**")
        
        st.divider()
        
        # Export transactions
        if st.button("📤 Export Transaction Report", use_container_width=True):
            # CSV export
            csv_data = trans_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        st.info("No transactions found for the selected period.")

def render_admin_settings():
    """Admin settings section"""
    st.markdown('<h1 class="main-title">⚙️ System Settings</h1>', unsafe_allow_html=True)
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 General Settings", 
        "🔐 Security Settings", 
        "💰 Financial Settings",
        "📊 System Configuration"
    ])
    
    with tab1:
        render_general_settings()
    
    with tab2:
        render_security_settings()
    
    with tab3:
        render_financial_settings()
    
    with tab4:
        render_system_configuration()

def render_general_settings():
    """General system settings"""
    st.markdown("### 🔧 General System Settings")
    
    with st.form("general_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            system_name = st.text_input(
                "System Name",
                value="2D Betting System",
                help="Display name of the system"
            )
            
            timezone = st.selectbox(
                "Timezone",
                ["Asia/Yangon", "UTC", "Asia/Bangkok", "Asia/Singapore"],
                index=0,
                help="System timezone"
            )
            
            default_language = st.selectbox(
                "Default Language",
                ["မြန်မာ", "English", "中文"],
                index=0,
                help="Default system language"
            )
        
        with col2:
            enable_notifications = st.checkbox(
                "Enable Email Notifications",
                value=True,
                help="Send email notifications for important events"
            )
            
            enable_sms = st.checkbox(
                "Enable SMS Notifications",
                value=False,
                help="Send SMS notifications (requires SMS gateway)"
            )
            
            auto_backup = st.checkbox(
                "Enable Automatic Backup",
                value=True,
                help="Automatically backup data daily"
            )
        
        # Save button
        if st.form_submit_button("💾 Save General Settings", use_container_width=True):
            st.success("✅ General settings saved successfully!")
            log_activity("Settings Update", "Updated general settings")

def render_security_settings():
    """Security settings"""
    st.markdown("### 🔐 Security Settings")
    
    with st.form("security_settings_form"):
        st.markdown("#### 🔒 Password Policy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_password_length = st.slider(
                "Minimum Password Length",
                min_value=6,
                max_value=20,
                value=8,
                help="Minimum characters required for passwords"
            )
            
            require_uppercase = st.checkbox(
                "Require Uppercase Letters",
                value=True,
                help="Password must contain uppercase letters"
            )
            
            require_numbers = st.checkbox(
                "Require Numbers",
                value=True,
                help="Password must contain numbers"
            )
        
        with col2:
            require_special_chars = st.checkbox(
                "Require Special Characters",
                value=False,
                help="Password must contain special characters (!@#$%^&*)"
            )
            
            password_expiry_days = st.slider(
                "Password Expiry (Days)",
                min_value=30,
                max_value=180,
                value=90,
                help="Days until password expires"
            )
            
            max_login_attempts = st.slider(
                "Max Login Attempts",
                min_value=3,
                max_value=10,
                value=5,
                help="Maximum failed login attempts before lockout"
            )
        
        st.markdown("#### 🛡️ Login Security")
        
        session_timeout = st.slider(
            "Session Timeout (Minutes)",
            min_value=15,
            max_value=240,
            value=60,
            help="Automatic logout after inactivity"
        )
        
        enable_2fa = st.checkbox(
            "Enable Two-Factor Authentication",
            value=False,
            help="Require 2FA for admin accounts"
        )
        
        ip_whitelist = st.text_area(
            "IP Whitelist (Optional)",
            placeholder="Enter one IP per line\nExample:\n192.168.1.1\n10.0.0.1",
            help="Restrict access to specific IP addresses"
        )
        
        # Save button
        if st.form_submit_button("💾 Save Security Settings", use_container_width=True):
            st.success("✅ Security settings saved successfully!")
            log_activity("Settings Update", "Updated security settings")

def render_financial_settings():
    """Financial settings"""
    st.markdown("### 💰 Financial Settings")
    
    with st.form("financial_settings_form"):
        st.markdown("#### 🎰 Betting Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            price_2d = st.number_input(
                "2D Number Price (Ks)",
                min_value=1000,
                max_value=100000,
                value=PRICE_PER_NUMBER,
                step=1000,
                help="Price per 2D number"
            )
            
            price_3d = st.number_input(
                "3D Number Price (Ks)",
                min_value=5000,
                max_value=500000,
                value=PRICE_PER_NUMBER * 10,
                step=5000,
                help="Price per 3D number"
            )
        
        with col2:
            min_bet_amount = st.number_input(
                "Minimum Bet Amount (Ks)",
                min_value=1000,
                max_value=10000,
                value=PRICE_PER_NUMBER,
                step=1000
            )
            
            max_bet_amount = st.number_input(
                "Maximum Bet Amount (Ks)",
                min_value=100000,
                max_value=1000000,
                value=PRICE_PER_NUMBER * 20,
                step=10000
            )
        
        st.markdown("#### 💸 Commission Settings")
        
        default_commission = st.slider(
            "Default Commission Rate (%)",
            min_value=0,
            max_value=50,
            value=10,
            step=1,
            help="Default commission percentage for agents"
        )
        
        commission_payout_days = st.selectbox(
            "Commission Payout Schedule",
            ["Daily", "Weekly", "Monthly", "Custom"],
            index=2,
            help="When to pay commissions to agents"
        )
        
        st.markdown("#### 💰 Payment Methods")
        
        payment_methods = st.multiselect(
            "Available Payment Methods",
            ["Cash", "Bank Transfer", "Mobile Money", "Credit Card", "Digital Wallet"],
            default=["Cash", "Bank Transfer", "Mobile Money"]
        )
        
        # Save button
        if st.form_submit_button("💾 Save Financial Settings", use_container_width=True):
            # Update PRICE_PER_NUMBER in session state
            st.session_state.price_2d = price_2d
            st.session_state.price_3d = price_3d
            
            st.success("✅ Financial settings saved successfully!")
            log_activity("Settings Update", "Updated financial settings")

def render_system_configuration():
    """System configuration"""
    st.markdown("### ⚙️ System Configuration")
    
    with st.form("system_config_form"):
        st.markdown("#### 🗃️ Database Settings")
        
        backup_frequency = st.selectbox(
            "Backup Frequency",
            ["Daily", "Weekly", "Monthly", "Manual Only"],
            index=0,
            help="How often to backup system data"
        )
        
        keep_backups_days = st.slider(
            "Keep Backups For (Days)",
            min_value=7,
            max_value=365,
            value=30,
            help="Number of days to keep backup files"
        )
        
        st.markdown("#### 📊 Reporting Settings")
        
        auto_report_generation = st.checkbox(
            "Auto-generate Daily Reports",
            value=True,
            help="Automatically generate daily reports"
        )
        
        report_recipients = st.text_area(
            "Report Recipients (Emails)",
            placeholder="admin@company.com\nmanager@company.com",
            help="Email addresses to receive automated reports"
        )
        
        st.markdown("#### 🔔 Notification Settings")
        
        notification_events = st.multiselect(
            "Events to Notify",
            [
                "New User Registration",
                "Large Bet Placed",
                "Daily Limit Reached",
                "System Error",
                "Backup Completed",
                "Unusual Activity"
            ],
            default=["New User Registration", "Large Bet Placed", "System Error"]
        )
        
        # System maintenance
        st.markdown("#### 🛠️ System Maintenance")
        
        maintenance_mode = st.checkbox(
            "Enable Maintenance Mode",
            value=False,
            help="Put system in maintenance mode (users cannot access)"
        )
        
        maintenance_message = st.text_area(
            "Maintenance Message",
            placeholder="System is under maintenance. Please try again later.",
            disabled=not maintenance_mode
        )
        
        # Save button
        col_save, col_maintenance = st.columns(2)
        
        with col_save:
            if st.form_submit_button("💾 Save Configuration", use_container_width=True):
                st.success("✅ System configuration saved successfully!")
                log_activity("Settings Update", "Updated system configuration")
        
        with col_maintenance:
            if maintenance_mode:
                if st.button("🚧 Activate Maintenance Mode", use_container_width=True, type="secondary"):
                    st.warning("⚠️ Maintenance mode activated! Users will not be able to access the system.")
                    log_activity("System", "Maintenance mode activated")
            else:
                if st.button("✅ Deactivate Maintenance", use_container_width=True, disabled=True):
                    pass

def render_backup_restore():
    """Backup and restore functions"""
    st.markdown('<h1 class="main-title">💾 Backup & Restore</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📥 Backup Data", "📤 Restore Data", "🗑️ Data Management"])
    
    with tab1:
        render_backup_data()
    
    with tab2:
        render_restore_data()
    
    with tab3:
        render_data_management()

def render_backup_data():
    """Backup system data"""
    st.markdown("### 📥 Create System Backup")
    
    col_info, col_stats = st.columns([2, 1])
    
    with col_info:
        st.markdown("""
        **Backup Information:**
        - Creates a complete backup of all system data
        - Includes users, transactions, settings, and logs
        - Backup files are encrypted for security
        - Recommended before system updates or changes
        """)
    
    with col_stats:
        # Calculate data size (simulated)
        total_users = len(st.session_state.users_db)
        total_entries = sum(len(entries) for entries in st.session_state.today_entries.values())
        total_activities = len(st.session_state.activity_log)
        
        st.metric("Total Users", total_users)
        st.metric("Total Entries", total_entries)
        st.metric("Total Activities", total_activities)
    
    st.divider()
    
    # Backup options
    st.markdown("#### ⚙️ Backup Options")
    
    backup_name = st.text_input(
        "Backup Name",
        value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Name for this backup"
    )
    
    include_types = st.multiselect(
        "Include Data Types",
        ["User Data", "Transaction Data", "Activity Logs", "System Settings"],
        default=["User Data", "Transaction Data", "Activity Logs", "System Settings"]
    )
    
    encryption_password = st.text_input(
        "Encryption Password (Optional)",
        type="password",
        help="Password to encrypt backup file"
    )
    
    st.divider()
    
    # Backup actions
    col_create, col_schedule = st.columns(2)
    
    with col_create:
        if st.button("💾 Create Backup Now", use_container_width=True, type="primary"):
            with st.spinner("Creating backup..."):
                time.sleep(2)  # Simulate backup process
                
                # Create backup data
                backup_data = {
                    'backup_name': backup_name,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': st.session_state.current_user,
                    'data': {
                        'users_db': st.session_state.users_db,
                        'today_entries': st.session_state.today_entries,
                        'activity_log': st.session_state.activity_log,
                        'user_configs': st.session_state.user_configs
                    }
                }
                
                # Convert to JSON
                backup_json = json.dumps(backup_data, indent=2, default=str)
                
                # Create download button
                st.success("✅ Backup created successfully!")
                
                st.download_button(
                    label="📥 Download Backup File",
                    data=backup_json,
                    file_name=f"{backup_name}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                log_activity("Backup", f"Created backup: {backup_name}")
    
    with col_schedule:
        st.markdown("#### 📅 Schedule Backup")
        
        schedule_frequency = st.selectbox(
            "Frequency",
            ["Daily", "Weekly", "Monthly"],
            index=0,
            key="schedule_freq"
        )
        
        if st.button("⏰ Schedule Auto-backup", use_container_width=True):
            st.info(f"Auto-backup scheduled for {schedule_frequency.lower()} backups")
            log_activity("Backup", f"Scheduled {schedule_frequency.lower()} backups")

def render_restore_data():
    """Restore system from backup"""
    st.markdown("### 📤 Restore from Backup")
    
    st.warning("""
    ⚠️ **Warning:** Restoring from backup will replace ALL current system data.
    This action cannot be undone. Make sure you have a current backup before proceeding.
    """)
    
    st.divider()
    
    # Restore options
    st.markdown("#### 📁 Upload Backup File")
    
    uploaded_file = st.file_uploader(
        "Choose backup file (.json)",
        type=['json'],
        help="Select a backup file to restore"
    )
    
    if uploaded_file is not None:
        try:
            # Read and parse backup file
            backup_data = json.load(uploaded_file)
            
            st.success("✅ Backup file loaded successfully!")
            
            # Display backup info
            st.markdown("#### 📋 Backup Information")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown(f"**Backup Name:** {backup_data.get('backup_name', 'Unknown')}")
                st.markdown(f"**Created At:** {backup_data.get('created_at', 'Unknown')}")
            
            with col_info2:
                st.markdown(f"**Created By:** {backup_data.get('created_by', 'Unknown')}")
                
                # Check data contents
                data_keys = list(backup_data.get('data', {}).keys())
                st.markdown(f"**Contains:** {', '.join(data_keys)}")
            
            st.divider()
            
            # Restore confirmation
            st.markdown("#### 🔄 Restore Options")
            
            restore_options = st.multiselect(
                "Select Data to Restore",
                ["Users", "Transactions", "Activity Logs", "Settings"],
                default=["Users", "Transactions", "Activity Logs", "Settings"]
            )
            
            confirm_restore = st.checkbox(
                "I understand this will replace current data",
                value=False
            )
            
            if st.button("🔄 Restore from Backup", 
                        use_container_width=True,
                        type="primary",
                        disabled=not confirm_restore):
                
                with st.spinner("Restoring data..."):
                    time.sleep(2)  # Simulate restore process
                    
                    # Create current backup before restore
                    current_backup = {
                        'backup_name': f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'created_by': st.session_state.current_user,
                        'data': {
                            'users_db': st.session_state.users_db,
                            'today_entries': st.session_state.today_entries,
                            'activity_log': st.session_state.activity_log,
                            'user_configs': st.session_state.user_configs
                        }
                    }
                    
                    # Restore selected data
                    data_to_restore = backup_data.get('data', {})
                    
                    if "Users" in restore_options and 'users_db' in data_to_restore:
                        st.session_state.users_db = data_to_restore['users_db']
                    
                    if "Transactions" in restore_options and 'today_entries' in data_to_restore:
                        st.session_state.today_entries = data_to_restore['today_entries']
                    
                    if "Activity Logs" in restore_options and 'activity_log' in data_to_restore:
                        st.session_state.activity_log = data_to_restore['activity_log']
                    
                    if "Settings" in restore_options and 'user_configs' in data_to_restore:
                        st.session_state.user_configs = data_to_restore['user_configs']
                    
                    # Save restored data
                    save_data()
                    
                    st.success("✅ Data restored successfully!")
                    log_activity("Restore", f"Restored from backup: {backup_data.get('backup_name')}")
                    
                    # Offer download of pre-restore backup
                    current_backup_json = json.dumps(current_backup, indent=2, default=str)
                    
                    st.download_button(
                        label="📥 Download Pre-restore Backup",
                        data=current_backup_json,
                        file_name=f"{current_backup['backup_name']}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    time.sleep(2)
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error reading backup file: {str(e)}")

def render_data_management():
    """Data management functions"""
    st.markdown("### 🗃️ Data Management")
    
    # Data statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        total_users = len(st.session_state.users_db)
        st.metric("Total Users", total_users)
    
    with col_stat2:
        total_entries = sum(len(entries) for entries in st.session_state.today_entries.values())
        st.metric("Total Entries", total_entries)
    
    with col_stat3:
        total_activities = len(st.session_state.activity_log)
        st.metric("Total Activities", total_activities)
    
    st.divider()
    
    # Data management actions
    st.markdown("#### 🧹 Data Cleanup")
    
    cleanup_options = st.multiselect(
        "Select Data to Cleanup",
        [
            "Old Activity Logs (keep last 1000)",
            "Empty User Accounts",
            "Test Data",
            "Temporary Files"
        ],
        default=["Old Activity Logs (keep last 1000)"]
    )
    
    if st.button("🧹 Run Data Cleanup", use_container_width=True):
        with st.spinner("Cleaning up data..."):
            time.sleep(1)
            
            changes_made = []
            
            if "Old Activity Logs (keep last 1000)" in cleanup_options:
                if len(st.session_state.activity_log) > 1000:
                    st.session_state.activity_log = st.session_state.activity_log[-1000:]
                    changes_made.append("Kept last 1000 activity logs")
            
            if "Empty User Accounts" in cleanup_options:
                # Find and remove empty user accounts (no recent activity)
                users_to_remove = []
                for username, user_data in st.session_state.users_db.items():
                    if user_data.get('role') != 'admin':
                        last_login = user_data.get('last_login')
                        if isinstance(last_login, str):
                            try:
                                last_login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
                                if (datetime.now() - last_login_date).days > 90:  # 90 days inactive
                                    users_to_remove.append(username)
                            except:
                                pass
                
                for username in users_to_remove:
                    if username in st.session_state.users_db:
                        del st.session_state.users_db[username]
                        changes_made.append(f"Removed inactive user: {username}")
            
            if changes_made:
                save_data()
                st.success("✅ Data cleanup completed!")
                for change in changes_made:
                    st.markdown(f"- {change}")
                log_activity("Data Cleanup", f"Performed cleanup: {', '.join(cleanup_options)}")
            else:
                st.info("No data needed cleanup.")
    
    st.divider()
    
    # Export all data
    st.markdown("#### 📤 Export All Data")
    
    export_format = st.radio(
        "Export Format",
        ["JSON", "CSV", "Excel"],
        horizontal=True
    )
    
    if st.button("📊 Export Complete Dataset", use_container_width=True):
        with st.spinner("Preparing export..."):
            time.sleep(1)
            
            export_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == "JSON":
                # Export as JSON
                export_data = {
                    'export_date': export_date,
                    'exported_by': st.session_state.current_user,
                    'data': {
                        'users': st.session_state.users_db,
                        'transactions': st.session_state.today_entries,
                        'activities': st.session_state.activity_log,
                        'configs': st.session_state.user_configs
                    }
                }
                
                export_json = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="💾 Download JSON",
                    data=export_json,
                    file_name=f"system_export_{export_date}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            elif export_format == "CSV":
                # Export users as CSV
                users_list = []
                for username, details in st.session_state.users_db.items():
                    users_list.append({
                        'username': username,
                        'name': details.get('name', ''),
                        'role': details.get('role', ''),
                        'email': details.get('email', ''),
                        'status': details.get('status', ''),
                        'created': details.get('created_at', ''),
                        'last_login': details.get('last_login', '')
                    })
                
                users_df = pd.DataFrame(users_list)
                users_csv = users_df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="💾 Download Users CSV",
                    data=users_csv,
                    file_name=f"users_export_{export_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            elif export_format == "Excel":
                st.info("Excel export requires additional libraries. Use JSON or CSV format.")
            
            log_activity("Data Export", f"Exported all data as {export_format}")

# ==================== 2D AGENT APPLICATION ====================
def render_2d_app():
    """Main 2D Agent application interface"""
    
    # Sidebar
    with st.sidebar:
        user_info = st.session_state.users_db.get(st.session_state.current_user, {})
        
        # Agent Info Card
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
            <p><strong>💰 Daily Limit:</strong> {user_info.get('daily_limit', 0):,} Ks</p>
            <p><strong>💸 Commission:</strong> {user_info.get('commission_rate', 0)}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Myanmar Time Display
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
        
        # Navigation Menu
        st.markdown("### 🧭 လမ်းညွှန်")
        
        menu_options = {
            "🎯 Enter Numbers": "entry",
            "📋 Today's Entries": "entries", 
            "📊 My Reports": "reports",
            "⚙️ Settings": "settings"
        }
        
        selected_key = st.radio(
            "မီနူးရွေးချယ်ရန်",
            options=list(menu_options.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_menu = menu_options[selected_key]
        
        st.divider()
        
        # Today's Summary
        st.markdown("### 📈 ယနေ့အခြေအနေ")
        
        today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
        total_entries = len(today_entries)
        total_amount = sum(entry.get('amount', 0) for entry in today_entries)
        daily_limit = user_info.get('daily_limit', 1000000)
        limit_used_percent = (total_amount / daily_limit * 100) if daily_limit > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ယနေ့စာရင်း", total_entries)
        with col2:
            st.metric("စုစုပေါင်း", f"{total_amount:,} Ks")
        
        # Progress bar for daily limit
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>Daily Limit</span>
                <span>{total_amount:,} / {daily_limit:,} Ks</span>
            </div>
            <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 4px;">
                <div style="background: {'#10B981' if limit_used_percent < 80 else '#F59E0B' if limit_used_percent < 100 else '#EF4444'}; 
                            height: 100%; width: {min(limit_used_percent, 100)}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick Actions
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("🚪 အကောင့်ထွက်ရန်", use_container_width=True, type="secondary"):
            log_activity("Logout", f"Agent: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main Content based on selected menu
    if st.session_state.selected_menu == 'entry':
        render_agent_number_entry()
    elif st.session_state.selected_menu == 'entries':
        render_agent_today_entries()
    elif st.session_state.selected_menu == 'reports':
        render_agent_reports()
    elif st.session_state.selected_menu == 'settings':
        render_agent_settings()

def render_agent_number_entry():
    """Agent number entry form"""
    st.markdown('<h1 class="main-title">🎯 Enter 2D/3D Numbers</h1>', unsafe_allow_html=True)
    
    # Check if Google Sheets is configured
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    
    if not user_config.get('sheet_url'):
        render_agent_sheet_configuration()
        return
    
    # Today's summary
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    today_total = sum(entry.get('amount', 0) for entry in today_entries)
    daily_limit = user_info.get('daily_limit', 1000000)
    remaining_limit = max(0, daily_limit - today_total)
    
    # Display limits
    col_limit1, col_limit2, col_limit3 = st.columns(3)
    with col_limit1:
        st.metric("Today's Total", f"{today_total:,} Ks")
    with col_limit2:
        st.metric("Daily Limit", f"{daily_limit:,} Ks")
    with col_limit3:
        st.metric("Remaining", f"{remaining_limit:,} Ks")
    
    st.divider()
    
    # Entry form
    with st.form("agent_number_entry_form", clear_on_submit=True):
        st.markdown("### 📝 ထိုးကြေးထည့်သွင်းရန်")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input(
                "၁။ ဝယ်ယူသူအမည် *",
                placeholder="ဥပမာ - ကိုကျော်ကျော်",
                help="ဝယ်ယူသူ၏အမည်ထည့်ပါ"
            )
            
            number = st.text_input(
                "၂။ ဂဏန်း *",
                placeholder="ဥပမာ - 55 (2D) သို့မဟုတ် 123 (3D)",
                help="2D (00-99) သို့မဟုတ် 3D (000-999) ဂဏန်းထည့်ပါ"
            )
            
            winning_number = st.text_input(
                "၃။ ထီပေါက်ဂဏန်း (မဖြစ်မနေ မဟုတ်)",
                placeholder="ထီပေါက်ပါက ဂဏန်းထည့်ပါ",
                help="ထီပေါက်ဂဏန်းသိပါက ထည့်သွင်းနိုင်သည်"
            )
        
        with col2:
            quantity = st.number_input(
                "၄။ အကြိမ်အရေအတွက် *",
                min_value=1,
                max_value=100,
                value=1,
                help="ထိုးကြေးအကြိမ်အရေအတွက်"
            )
            
            # Auto-calculate amount
            amount = 0
            amount_details = ""
            if number and quantity:
                is_valid, validation_msg = validate_number(number)
                if is_valid:
                    amount = calculate_amount(number, quantity)
                    if len(number) == 2:
                        amount_details = f"2D ဂဏန်း - {PRICE_PER_NUMBER:,} Ks x {quantity} = {amount:,} Ks"
                    else:
                        amount_details = f"3D ဂဏန်း - {PRICE_PER_NUMBER * 10:,} Ks x {quantity} = {amount:,} Ks"
            
            # Amount display
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                        color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; font-weight: bold;">စုစုပေါင်းပမာဏ</div>
                    <div style="font-size: 2.5rem; font-weight: bold; margin: 10px 0;">{amount:,} Ks</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">{amount_details}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            note = st.text_area(
                "၅။ မှတ်ချက် (မဖြစ်မနေ မဟုတ်)",
                placeholder="အထူးမှတ်ချက်ရှိပါက ထည့်သွင်းပါ",
                height=60
            )
        
        # Validation warnings
        if amount > 0:
            if amount > remaining_limit:
                st.error(f"❌ နေ့စဉ်ကန့်သတ်ချက်ထက်ကျော်လွန်နေပါသည်။ ကျန်ငွေ: {remaining_limit:,} Ks")
            elif amount > remaining_limit * 0.8:
                st.warning(f"⚠️ နေ့စဉ်ကန့်သတ်ချက်နီးကပ်နေပါသည်။ ကျန်ငွေ: {remaining_limit:,} Ks")
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ **ထိုးကြေးအတည်ပြုရန်** (ဤခလုတ်ကိုနှိပ်ပါ)",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            errors = []
            
            is_name_valid, name_error = validate_name(customer_name)
            if not is_name_valid:
                errors.append(f"ဝယ်ယူသူအမည်: {name_error}")
            
            is_number_valid, number_error = validate_number(number)
            if not is_number_valid:
                errors.append(f"ဂဏန်း: {number_error}")
            
            if quantity <= 0:
                errors.append("အကြိမ်အရေအတွက် အနည်းဆုံး ၁ ဖြစ်ရမည်")
            
            if amount > remaining_limit:
                errors.append(f"နေ့စဉ်ကန့်သတ်ချက်ထက်ကျော်လွန်နေပါသည်။ ကျန်ငွေ: {remaining_limit:,} Ks")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create entry
                entry_id = len(today_entries) + 1
                entry_time = format_myanmar_time()
                
                entry = {
                    'id': entry_id,
                    'time': entry_time,
                    'customer': customer_name,
                    'number': number,
                    'quantity': quantity,
                    'amount': amount,
                    'winning_number': winning_number if winning_number else '',
                    'status': 'Pending',
                    'note': note if note else '',
                    'agent': st.session_state.current_user
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
                **အချက်အလက်:**
                - စာရင်းနံပါတ်: #{entry_id}
                - အချိန်: {entry_time}
                - ဝယ်ယူသူ: {customer_name}
                - ဂဏန်း: {number}
                - အကြိမ်အရေအတွက်: {quantity}
                - ပမာဏ: {amount:,} Ks
                """)
                
                log_activity("2D Entry", f"Added: {number} for {customer_name} - {amount:,} Ks")
                
                st.balloons()
                time.sleep(2)
                st.rerun()

def render_agent_sheet_configuration():
    """Google Sheets configuration for agents"""
    st.markdown('<h1 class="main-title">🔗 Google Sheets Configuration</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>📋 Google Sheets ချိတ်ဆက်မှု လိုအပ်ပါသည်</h3>
    <p>2D ထီထိုးစနစ်ကိုအသုံးပြုရန် သင့်၏ Google Sheets URL ကိုချိတ်ဆက်ရန် လိုအပ်ပါသည်။</p>
    <p>ကျေးဇူးပြု၍ Admin ထံမှ သင့်၏ Google Sheets URL ကိုရယူပါ။</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("agent_sheet_config_form"):
        st.markdown("### 🔗 Google Sheets URL ထည့်သွင်းရန်")
        
        sheet_url = st.text_input(
            "Google Sheets URL *",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="သင်၏ Google Sheets URL လင့်ကိုထည့်ပါ"
        )
        
        st.markdown("""
        **အကြံပြုချက်:**
        1. Google Sheets တစ်ခုဖန်တီးပါ
        2. လင့်ကို copy ကူးပါ
        3. ဤနေရာတွင် paste လုပ်ပါ
        4. Save ခလုတ်ကိုနှိပ်ပါ
        """)
        
        if st.form_submit_button("💾 Save Configuration", use_container_width=True, type="primary"):
            if sheet_url:
                if "docs.google.com/spreadsheets" not in sheet_url:
                    st.error("❌ မှန်ကန်သော Google Sheets URL ဖြစ်ရမည်")
                else:
                    # Save configuration
                    st.session_state.user_configs[st.session_state.current_user] = {
                        'sheet_url': sheet_url,
                        'script_url': ''
                    }
                    
                    # Update in users_db
                    if st.session_state.current_user in st.session_state.users_db:
                        st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                    
                    # Save data
                    save_data()
                    
                    st.success("✅ Google Sheets configuration saved successfully!")
                    log_activity("Sheet Config", f"Updated Google Sheets URL")
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("❌ Google Sheets URL ထည့်ပါ")

def render_agent_today_entries():
    """Display today's entries for agent"""
    st.markdown('<h1 class="main-title">📋 ယနေ့စာရင်းများ</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    
    if not today_entries:
        st.info("ယနေ့အတွက် မည်သည့်စာရင်းမှ မရှိသေးပါ။")
        return
    
    # Summary statistics
    total_entries = len(today_entries)
    total_quantity = sum(entry.get('quantity', 0) for entry in today_entries)
    total_amount = sum(entry.get('amount', 0) for entry in today_entries)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("စုစုပေါင်းစာရင်း", total_entries)
    with col2:
        st.metric("စုစုပေါင်းအကြိမ်", total_quantity)
    with col3:
        st.metric("စုစုပေါင်းပမာဏ", f"{total_amount:,} Ks")
    with col4:
        avg_amount = total_amount / total_entries if total_entries > 0 else 0
        st.metric("ပျမ်းမျှပမာဏ", f"{avg_amount:,.0f} Ks")
    
    st.divider()
    
    # Search and filter
    col_search, col_filter, col_export = st.columns([2, 1, 1])
    
    with col_search:
        search_query = st.text_input("🔍 ရှာဖွေရန်", placeholder="ဝယ်ယူသူအမည် သို့မဟုတ် ဂဏန်း")
    
    with col_filter:
        status_filter = st.selectbox(
            "အခြေအနေစစ်ထုတ်ရန်",
            ["အားလုံး", "Pending", "Won", "Lost", "Paid"],
            index=0
        )
    
    # Filter entries
    filtered_entries = today_entries.copy()
    
    if search_query:
        filtered_entries = [e for e in filtered_entries 
                          if search_query.lower() in e.get('customer', '').lower() 
                          or search_query in e.get('number', '')]
    
    if status_filter != "အားလုံး":
        filtered_entries = [e for e in filtered_entries if e.get('status') == status_filter]
    
    st.divider()
    
    # Display entries
    if filtered_entries:
        st.markdown(f"### 📝 စာရင်းများ ({len(filtered_entries)} ခု)")
        
        for i, entry in enumerate(filtered_entries):
            # Status color
            status_colors = {
                'Pending': '#F59E0B',  # Yellow
                'Won': '#10B981',      # Green
                'Lost': '#EF4444',     # Red
                'Paid': '#3B82F6'      # Blue
            }
            
            status_color = status_colors.get(entry.get('status', 'Pending'), '#6B7280')
            
            with st.expander(f"#{entry['id']} - {entry['customer']} ({entry['number']}) - {entry['amount']:,} Ks", 
                           expanded=(i == 0 and len(filtered_entries) < 5)):
                
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    # Display entry details
                    st.markdown(f"""
                    **အချိန်:** {entry['time']}  
                    **ဝယ်ယူသူ:** {entry['customer']}  
                    **ဂဏန်း:** {entry['number']} ({'2D' if len(entry['number']) == 2 else '3D'})  
                    **အကြိမ်အရေအတွက်:** {entry['quantity']}  
                    **ပမာဏ:** {entry['amount']:,} Ks  
                    """)
                    
                    if entry.get('winning_number'):
                        st.markdown(f"**ထီပေါက်ဂဏန်း:** {entry['winning_number']}")
                    
                    st.markdown(f"**အခြေအနေ:** <span style='color: {status_color}; font-weight: bold;'>{entry['status']}</span>", 
                              unsafe_allow_html=True)
                    
                    if entry.get('note'):
                        st.markdown(f"**မှတ်ချက်:** {entry['note']}")
                
                with col_actions:
                    # Edit button
                    if st.button("✏️ ပြင်ဆင်ရန်", key=f"edit_{i}"):
                        st.session_state.editing_entry = i
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ ဖျက်ရန်", key=f"delete_{i}"):
                        st.session_state.deleting_entry = i
                        st.rerun()
        
        # Edit form
        if 'editing_entry' in st.session_state:
            entry_index = st.session_state.editing_entry
            if entry_index < len(filtered_entries):
                # Find original index in today_entries
                entry_id = filtered_entries[entry_index]['id']
                original_index = next((i for i, e in enumerate(today_entries) if e['id'] == entry_id), None)
                
                if original_index is not None:
                    entry = today_entries[original_index]
                    
                    st.markdown("---")
                    st.markdown("### ✏️ စာရင်းပြင်ဆင်ရန်")
                    
                    with st.form(f"edit_entry_form_{original_index}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edited_customer = st.text_input("ဝယ်ယူသူအမည်", value=entry['customer'])
                            edited_number = st.text_input("ဂဏန်း", value=entry['number'])
                            edited_winning = st.text_input("ထီပေါက်ဂဏန်း", value=entry.get('winning_number', ''))
                        
                        with col2:
                            edited_quantity = st.number_input("အကြိမ်အရေအတွက်", min_value=1, value=entry['quantity'])
                            edited_status = st.selectbox(
                                "အခြေအနေ",
                                ["Pending", "Won", "Lost", "Paid"],
                                index=["Pending", "Won", "Lost", "Paid"].index(entry['status'])
                            )
                            edited_note = st.text_area("မှတ်ချက်", value=entry.get('note', ''), height=80)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 သိမ်းဆည်းရန်", use_container_width=True):
                                # Update entry
                                today_entries[original_index]['customer'] = edited_customer
                                today_entries[original_index]['number'] = edited_number
                                today_entries[original_index]['quantity'] = edited_quantity
                                today_entries[original_index]['amount'] = calculate_amount(edited_number, edited_quantity)
                                today_entries[original_index]['winning_number'] = edited_winning
                                today_entries[original_index]['status'] = edited_status
                                today_entries[original_index]['note'] = edited_note
                                
                                # Save data
                                save_data()
                                
                                del st.session_state.editing_entry
                                st.success("✅ စာရင်းပြင်ဆင်ပြီးပါပြီ။")
                                log_activity("Edit Entry", f"Edited entry #{entry['id']}")
                                time.sleep(1)
                                st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ ပယ်ဖျက်ရန်", use_container_width=True):
                                del st.session_state.editing_entry
                                st.rerun()
        
        # Delete confirmation
        if 'deleting_entry' in st.session_state:
            entry_index = st.session_state.deleting_entry
            if entry_index < len(filtered_entries):
                entry_id = filtered_entries[entry_index]['id']
                original_index = next((i for i, e in enumerate(today_entries) if e['id'] == entry_id), None)
                
                if original_index is not None:
                    st.warning(f"⚠️ ဤစာရင်းကို ဖျက်ရန်သေချာပါသလား?")
                    st.markdown(f"**စာရင်း #{entry_id} - {filtered_entries[entry_index]['customer']} ({filtered_entries[entry_index]['number']})**")
                    
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ ဟုတ်ကဲ့၊ ဖျက်ပါ", use_container_width=True):
                            # Remove entry
                            today_entries.pop(original_index)
                            
                            # Reindex remaining entries
                            for i, e in enumerate(today_entries):
                                e['id'] = i + 1
                            
                            # Save data
                            save_data()
                            
                            del st.session_state.deleting_entry
                            st.success("✅ စာရင်းဖျက်ပြီးပါပြီ။")
                            log_activity("Delete Entry", f"Deleted entry #{entry_id}")
                            time.sleep(1)
                            st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ မဖျက်တော့ပါ", use_container_width=True):
                            del st.session_state.deleting_entry
                            st.rerun()
        
        st.divider()
        
        # Export and clear options
        with col_export:
            if st.button("📤 Export လုပ်ရန်", use_container_width=True):
                # Create DataFrame for export
                export_data = []
                for entry in today_entries:
                    export_data.append({
                        'ID': entry['id'],
                        'Time': entry['time'],
                        'Customer': entry['customer'],
                        'Number': entry['number'],
                        'Quantity': entry['quantity'],
                        'Amount': entry['amount'],
                        'Winning Number': entry.get('winning_number', ''),
                        'Status': entry['status'],
                        'Note': entry.get('note', '')
                    })
                
                df_export = pd.DataFrame(export_data)
                csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                
                today_date = datetime.now().strftime('%Y%m%d')
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"2d_entries_{st.session_state.current_user}_{today_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Clear all entries button
        if st.button("🗑️ ယနေ့စာရင်းအားလုံးဖျက်ရန်", type="secondary", use_container_width=True):
            st.warning("⚠️ ယနေ့စာရင်းအားလုံးကို ဖျက်ရန်သေချာပါသလား?")
            
            if st.checkbox("ဟုတ်ကဲ့၊ စာရင်းအားလုံးဖျက်ရန် သဘောတူပါသည်"):
                if st.button("✅ အားလုံးဖျက်ပါ", type="primary", use_container_width=True):
                    st.session_state.today_entries[st.session_state.current_user] = []
                    save_data()
                    st.success("✅ ယနေ့စာရင်းအားလုံး ဖျက်ပြီးပါပြီ။")
                    log_activity("Clear All", "Cleared all today's entries")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("ရှာဖွေမှုနှင့်ကိုက်ညီသော စာရင်းများမတွေ့ရှိပါ။")

def render_agent_reports():
    """Agent reports"""
    st.markdown('<h1 class="main-title">📊 ကိုယ်ပိုင်အစီရင်ခံစာများ</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    
    # Quick statistics
    total_entries = len(today_entries)
    total_amount = sum(entry.get('amount', 0) for entry in today_entries)
    win_count = sum(1 for entry in today_entries if entry.get('status') == 'Won')
    loss_count = sum(1 for entry in today_entries if entry.get('status') == 'Lost')
    pending_count = sum(1 for entry in today_entries if entry.get('status') == 'Pending')
    
    win_rate = (win_count / total_entries * 100) if total_entries > 0 else 0
    commission_rate = user_info.get('commission_rate', 10)
    commission_amount = total_amount * commission_rate / 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("စုစုပေါင်းစာရင်း", total_entries)
    with col2:
        st.metric("စုစုပေါင်းပမာဏ", f"{total_amount:,} Ks")
    with col3:
        st.metric("ထီပေါက်နှုန်း", f"{win_rate:.1f}%")
    with col4:
        st.metric("ကော်မရှင်", f"{commission_amount:,.0f} Ks")
    
    st.divider()
    
    # Status distribution
    st.markdown("### 📊 အခြေအနေအလိုက်ဖြန့်ဝေမှု")
    
    if total_entries > 0:
        status_data = pd.DataFrame({
            'Status': ['Won', 'Lost', 'Pending', 'Paid'],
            'Count': [win_count, loss_count, pending_count, total_entries - win_count - loss_count - pending_count]
        })
        
        st.bar_chart(status_data.set_index('Status'))
    
    st.divider()
    
    # Recent activity
    st.markdown("### 📝 လတ်တလောလုပ်ဆောင်ချက်များ")
    
    # Filter agent's activities
    agent_activities = []
    for activity in st.session_state.activity_log[-20:]:
        if activity['user'] == st.session_state.current_user:
            agent_activities.append(activity)
    
    if agent_activities:
        for activity in reversed(agent_activities):
            st.markdown(f"""
            - **{activity['timestamp']}** - {activity['action']}
              {f"  *{activity['details']}*" if activity['details'] else ""}
            """)
    else:
        st.info("မည်သည့်လုပ်ဆောင်ချက်မှ မရှိသေးပါ။")
    
    st.divider()
    
    # Generate detailed report
    if st.button("📄 အသေးစိတ်အစီရင်ခံစာထုတ်ရန်", use_container_width=True):
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_data = {
            'agent': st.session_state.current_user,
            'name': user_info.get('name', ''),
            'report_date': report_date,
            'summary': {
                'total_entries': total_entries,
                'total_amount': total_amount,
                'win_count': win_count,
                'loss_count': loss_count,
                'pending_count': pending_count,
                'win_rate': win_rate,
                'commission_rate': commission_rate,
                'commission_amount': commission_amount
            },
            'entries': today_entries
        }
        
        report_json = json.dumps(report_data, indent=2, default=str)
        
        st.download_button(
            label="💾 အစီရင်ခံစာဒေါင်းလုပ်ဆွဲရန်",
            data=report_json,
            file_name=f"agent_report_{st.session_state.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

def render_agent_settings():
    """Agent settings"""
    st.markdown('<h1 class="main-title">⚙️ ကိုယ်ပိုင်ဆက်တင်များ</h1>', unsafe_allow_html=True)
    
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    tab1, tab2 = st.tabs(["🔗 Google Sheets", "👤 ကိုယ်ရေးကိုယ်တာအချက်အလက်"])
    
    with tab1:
        st.markdown("### 🔗 Google Sheets ချိတ်ဆက်မှု")
        
        with st.form("agent_sheets_settings_form"):
            current_sheet_url = user_config.get('sheet_url', '')
            
            sheet_url = st.text_input(
                "Google Sheets URL",
                value=current_sheet_url,
                placeholder="https://docs.google.com/spreadsheets/d/...",
                help="သင်၏ Google Sheets URL ကို ပြောင်းလဲလိုပါက ဤနေရာတွင်ပြင်ဆင်ပါ"
            )
            
            st.markdown("""
            **မှတ်ချက်:**
            - Google Sheets URL ပြောင်းလဲပါက စာရင်းအားလုံးကို ယခု Sheets သို့ကူးပြောင်းမည်
            - မူလဒေတာများ မဆုံးရှုံးစေရန် သေချာစွာစစ်ဆေးပါ
            """)
            
            if st.form_submit_button("💾 သိမ်းဆည်းရန်", use_container_width=True):
                if sheet_url and sheet_url != current_sheet_url:
                    if "docs.google.com/spreadsheets" not in sheet_url:
                        st.error("❌ မှန်ကန်သော Google Sheets URL ဖြစ်ရမည်")
                    else:
                        # Update configuration
                        st.session_state.user_configs[st.session_state.current_user] = {
                            'sheet_url': sheet_url,
                            'script_url': ''
                        }
                        
                        # Update in users_db
                        st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                        
                        # Save data
                        save_data()
                        
                        st.success("✅ Google Sheets settings updated successfully!")
                        log_activity("Sheet Update", "Updated Google Sheets URL")
                        time.sleep(1)
                        st.rerun()
                elif sheet_url == current_sheet_url:
                    st.info("Google Sheets URL မပြောင်းလဲပါ။")
                else:
                    st.error("❌ Google Sheets URL ထည့်ပါ")
    
    with tab2:
        st.markdown("### 👤 ကိုယ်ရေးကိုယ်တာအချက်အလက်")
        
        with st.form("agent_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("အမည်", value=user_info.get('name', ''))
                email = st.text_input("အီးမေးလ်", value=user_info.get('email', ''))
            
            with col2:
                phone = st.text_input("ဖုန်းနံပါတ်", value=user_info.get('phone', ''))
                address = st.text_input("လိပ်စာ", value=user_info.get('address', ''))
            
            st.markdown("### 🔒 စကားဝှက်ပြောင်းလဲရန်")
            
            new_password = st.text_input(
                "စကားဝှက်အသစ်",
                type="password",
                placeholder="စကားဝှက်အသစ်ထည့်ပါ",
                help="စကားဝှက်မပြောင်းလဲလိုပါက ဗလာထားခဲ့ပါ"
            )
            
            confirm_password = st.text_input(
                "စကားဝှက်အတည်ပြုရန်",
                type="password",
                placeholder="စကားဝှက်အသစ်ကိုပြန်ရိုက်ပါ"
            )
            
            if st.form_submit_button("💾 အချက်အလက်များသိမ်းဆည်းရန်", use_container_width=True):
                update_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'address': address
                }
                
                # Check if password is being changed
                if new_password:
                    if new_password != confirm_password:
                        st.error("❌ စကားဝှက်နှစ်ခုမတူညီပါ")
                    elif len(new_password) < 6:
                        st.error("❌ စကားဝှက်အနည်းဆုံး ၆ လုံးပါဝင်ရမည်")
                    else:
                        update_data['password'] = new_password
                
                success, message = update_user_info(st.session_state.current_user, **update_data)
                
                if success:
                    st.success("✅ ကိုယ်ရေးကိုယ်တာအချက်အလက်များ သိမ်းဆည်းပြီးပါပြီ။")
                    log_activity("Profile Update", "Updated profile information")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    
    # Load CSS
    st.markdown(load_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Initialize default data if empty
    if not st.session_state.users_db:
        init_default_data()
    
    # Try to load saved data
    if not st.session_state.logged_in:
        saved_data = load_data()
        if saved_data:
            # Restore data from file
            st.session_state.users_db.update(saved_data.get('users_db', {}))
            st.session_state.today_entries.update(saved_data.get('today_entries', {}))
            st.session_state.activity_log.extend(saved_data.get('activity_log', []))
            st.session_state.user_configs.update(saved_data.get('user_configs', {}))
    
    # Page configuration
    st.set_page_config(
        page_title="2D Betting System",
        page_icon="🎰",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo',
            'Report a bug': 'https://github.com/your-repo/issues',
            'About': '# 2D Betting System v1.0\nA complete betting system for 2D/3D lottery'
        }
    )
    
    # Check authentication and render appropriate page
    if not st.session_state.logged_in:
        render_login_page()
    else:
        if st.session_state.user_role == 'admin':
            render_admin_panel()
        elif st.session_state.user_role == 'agent':
            render_2d_app()
        else:
            st.error("Invalid user role. Please contact administrator.")
            st.session_state.logged_in = False
            st.rerun()

# ==================== APPLICATION START ====================
if __name__ == "__main__":
    main()
