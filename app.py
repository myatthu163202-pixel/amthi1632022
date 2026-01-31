import streamlit as st
import pandas as pd
import hashlib
import time
from datetime import datetime, timedelta
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import re

# ==================== CONFIGURATION ====================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
PRICE_PER_NUMBER = 50000  # ၅သောင်း

# ==================== SESSION STATE INITIALIZATION ====================
def init_session_state():
    """အစကနေစပြီး Session State အားလုံးကို Initialize လုပ်ပါ"""
    
    # 1. Authentication States
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''
    if 'current_user' not in st.session_state:
        st.session_state.current_user = ''
    
    # 2. 2D App States
    if 'sheet_url' not in st.session_state:
        st.session_state.sheet_url = ''
    if 'user_configs' not in st.session_state:
        st.session_state.user_configs = {}
    if 'today_entries' not in st.session_state:
        st.session_state.today_entries = {}
    if 'google_sheets' not in st.session_state:
        st.session_state.google_sheets = {}
    if 'last_reset_date' not in st.session_state:
        st.session_state.last_reset_date = get_myanmar_time().strftime('%Y-%m-%d')
    if 'hidden_sections' not in st.session_state:
        st.session_state.hidden_sections = {}
    
    # 3. User Management States (Panel ကနေ)
    if 'users_db' not in st.session_state:
        init_users_database()
    if 'number_limits_cache' not in st.session_state:
        st.session_state.number_limits_cache = {}
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    # 4. Navigation State
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '🏠 ပင်မစာမျက်နှာ'
    
    # 5. User-specific data initialize
    if st.session_state.logged_in and st.session_state.current_user:
        init_user_data()

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
        }
    }

def init_user_data():
    """User တစ်ယောက်ချင်းစီရဲ့ data ကို initialize လုပ်ပါ"""
    if st.session_state.current_user not in st.session_state.today_entries:
        st.session_state.today_entries[st.session_state.current_user] = []
    
    if st.session_state.current_user not in st.session_state.user_configs:
        st.session_state.user_configs[st.session_state.current_user] = {
            'sheet_url': st.session_state.users_db.get(st.session_state.current_user, {}).get('sheet_url', ''),
            'script_url': ''
        }

# ==================== HELPER FUNCTIONS ====================
def get_myanmar_time():
    """မြန်မာစံတော်ချိန်ရယူခြင်း"""
    return datetime.now(MYANMAR_TZ)

def format_myanmar_time(dt=None):
    """မြန်မာစံတော်ချိန်ဖော်ပြခြင်း"""
    if dt is None:
        dt = get_myanmar_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_today_date():
    """ယနေ့ရက်စွဲရယူခြင်း"""
    return get_myanmar_time().strftime('%Y-%m-%d')

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

def connect_to_google_sheets(sheet_url, credentials_json=None):
    """Google Sheets နှင့်ချိတ်ဆက်ခြင်း"""
    try:
        if not sheet_url:
            return None, "Sheet URL ထည့်ပါ"
        
        if sheet_url in st.session_state.google_sheets:
            return st.session_state.google_sheets[sheet_url], "ချိတ်ဆက်ပြီးသား"
        
        # For demo - real implementation would use Google API
        class MockSheet:
            def worksheet(self, title):
                class MockWorksheet:
                    def append_row(self, row):
                        print(f"📊 Google Sheets သို့သိမ်းဆည်းခြင်း: {row}")
                        return True
                    def row_count(self):
                        return 100
                return MockWorksheet()
            def add_worksheet(self, title, rows, cols):
                print(f"📄 Worksheet အသစ်ဖန်တီးခြင်း: {title}")
                return MockSheet().worksheet(title)
        
        mock_sheet = MockSheet()
        st.session_state.google_sheets[sheet_url] = mock_sheet
        return mock_sheet, "Demo mode - Mock connection established"
        
    except Exception as e:
        return None, f"ချိတ်ဆက်မှုမအောင်မြင်ပါ: {str(e)}"

def save_to_google_sheets(entry_data, sheet_url, script_url=""):
    """Google Sheets သို့သိမ်းဆည်းခြင်း"""
    try:
        sheet, message = connect_to_google_sheets(sheet_url)
        if not sheet:
            return False, message
        
        today = get_today_date()
        
        # Try to get or create worksheet
        try:
            worksheet = sheet.worksheet(today)
        except:
            worksheet = sheet.add_worksheet(title=today, rows="1000", cols="10")
            headers = ["အချိန်", "ထိုးသူအမည်", "ထိုးမည့်ဂဏန်း", "အရေအတွက်", 
                      "ပမာဏ", "ပေါက်ဂဏန်း", "အခြေအနေ", "မှတ်ချက်"]
            worksheet.append_row(headers)
        
        # Prepare row data
        row = [
            entry_data['time'],
            entry_data['name'],
            entry_data['number'],
            entry_data['quantity'],
            entry_data['amount'],
            entry_data.get('winning_number', ''),
            entry_data.get('status', 'စောင့်ဆိုင်းနေ'),
            entry_data.get('note', '')
        ]
        
        # Append to sheet
        worksheet.append_row(row)
        
        return True, "Google Sheets သို့သိမ်းဆည်းပြီးပါပြီ"
    except Exception as e:
        return False, f"သိမ်းဆည်းမှုမအောင်မြင်ပါ: {str(e)}"

def check_daily_reset():
    """နေ့စဉ်ဒေတာပြန်လည်စတင်ခြင်းစစ်ဆေးခြင်း"""
    today = get_today_date()
    
    if st.session_state.last_reset_date != today:
        # New day - reset today's entries
        for user in st.session_state.today_entries:
            st.session_state.today_entries[user] = []
        
        # Reset hidden sections
        st.session_state.hidden_sections = {}
        
        # Update reset date
        st.session_state.last_reset_date = today

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
        
        # Remove user's data
        if username in st.session_state.today_entries:
            del st.session_state.today_entries[username]
        if username in st.session_state.user_configs:
            del st.session_state.user_configs[username]
        
        # Remove from users database
        del st.session_state.users_db[username]
        
        log_activity("Delete User", f"Deleted: {username}")
        return True, f"အကောင့် '{username}' ဖျက်ပြီးပါပြီ။"
    return False, "အသုံးပြုသူမတွေ့ပါ။"

# ==================== MAIN APPLICATION ====================
def main():
    """အဓိက Application"""
    
    # Initialize session state
    init_session_state()
    
    # Check daily reset
    check_daily_reset()
    
    # Page configuration
    st.set_page_config(
        page_title="2D ထိုးစနစ်",
        page_icon="🎰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    # ==================== LOGIN PAGE ====================
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    # ==================== LOGGED IN ====================
    render_sidebar()
    
    # Page routing based on current_page
    current_page = st.session_state.get('current_page', '🏠 ပင်မစာမျက်နှာ')
    
    if current_page == "🏠 ပင်မစာမျက်နှာ":
        render_home_page()
    elif current_page == "🎰 2D ထိုးစနစ်":
        render_2d_system()
    elif current_page == "👥 အေဂျင့်မန်နေဂျာ":
        render_user_management()
    elif current_page == "📊 အစီရင်ခံစာများ":
        render_reports_page()
    elif current_page == "⚙️ ဆက်တင်များ":
        render_settings_page()

# ==================== LOGIN PAGE ====================
def render_login_page():
    """Login page render"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">🎰 2D ထိုးစနစ်</h1>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 အကောင့်ဝင်ရောက်ရန်")
            st.write("ကျေးဇူးပြု၍ သင့်အကောင့်ဖြင့် ဝင်ရောက်ပါ။")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 **အသုံးပြုသူအမည်**", 
                                       placeholder="သင့်အသုံးပြုသူအမည်ထည့်ပါ")
                
                password = st.text_input("🔒 **စကားဝှက်**", 
                                       type="password",
                                       placeholder="သင့်စကားဝှက်ထည့်ပါ")
                
                login_button = st.form_submit_button("🚀 **ဝင်ရောက်မည်**", 
                                                   use_container_width=True)
                
                if login_button:
                    if username and password:
                        authenticated, role = authenticate_user(username, password)
                        if authenticated:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.current_user = username
                            
                            # Initialize user data
                            init_user_data()
                            
                            st.success(f"✅ **{username}** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ အသုံးပြုသူအမည် သို့မဟုတ် စကားဝှက် မှားယွင်းနေပါသည်။")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ အသုံးပြုသူအမည်နှင့် စကားဝှက်ထည့်ပါ။")
            
            # Demo credentials
            with st.expander("📋 သက်သေခံအချက်အလက်များ"):
                col_demo1, col_demo2 = st.columns(2)
                with col_demo1:
                    st.markdown("**👑 Admin Account:**")
                    st.code("အသုံးပြုသူအမည်: admin\nစကားဝှက်: admin123")
                with col_demo2:
                    st.markdown("**👤 Agent Account:**")
                    st.code("အသုံးပြုသူအမည်: agent1\nစကားဝှက်: agent123")

# ==================== SIDEBAR ====================
def render_sidebar():
    """Sidebar render"""
    with st.sidebar:
        # User info card
        user_info = st.session_state.users_db[st.session_state.current_user]
        st.markdown(f"""
        <div class="user-card">
            <h3>👤 {user_info['name']}</h3>
            <p><strong>အခန်းကဏ္ဍ:</strong> {user_info['role'].upper()}</p>
            <p><strong>အသုံးပြုသူ:</strong> {st.session_state.current_user}</p>
            <p><strong>နောက်ဆုံးဝင်ရောက်ချိန်:</strong><br>{user_info['last_login']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Myanmar time
        current_time = format_myanmar_time()
        st.markdown(f"""
        <div class="info-box">
            <p><strong>မြန်မာစံတော်ချိန်:</strong></p>
            <h3 style="text-align: center; color: #1E40AF;">{current_time.split()[1]}</h3>
            <p style="text-align: center;">{current_time.split()[0]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("### 🗺️ လမ်းညွှန်မှု")
        
        if st.session_state.user_role == 'admin':
            page_options = [
                "🏠 ပင်မစာမျက်နှာ",
                "🎰 2D ထိုးစနစ်", 
                "👥 အေဂျင့်မန်နေဂျာ",
                "📊 အစီရင်ခံစာများ",
                "⚙️ ဆက်တင်များ"
            ]
        else:  # agent
            page_options = [
                "🏠 ပင်မစာမျက်နှာ",
                "🎰 2D ထိုးစနစ်",
                "⚙️ ဆက်တင်များ"
            ]
        
        selected_page = st.radio("စာမျက်နှာရွေးချယ်ရန်", page_options)
        st.session_state.current_page = selected_page
        
        st.divider()
        
        # Quick stats
        st.markdown("### 📈 အချက်အလက်အကျဉ်း")
        
        today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
        total_amount = sum(entry['amount'] for entry in today_entries)
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("ယနေ့အရေအတွက်", len(today_entries))
        with col_stat2:
            st.metric("ယနေ့ပမာဏ", f"{total_amount:,} Ks")
        
        st.divider()
        
        # Logout button
        if st.button("🚪 **ထွက်ခွာမည်**", use_container_width=True):
            log_activity("Logout", f"User: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()

# ==================== HOME PAGE ====================
def render_home_page():
    """Home page dashboard"""
    st.markdown('<h1 class="main-title">🏠 ပင်မစာမျက်နှာ</h1>', unsafe_allow_html=True)
    
    user_info = st.session_state.users_db[st.session_state.current_user]
    
    # Welcome message
    col_welcome, col_stats = st.columns([2, 1])
    
    with col_welcome:
        st.markdown(f"""
        <div class="info-box">
            <h2>👋 ကြိုဆိုပါတယ် {user_info['name']}!</h2>
            <p><strong>အခန်းကဏ္ဍ:</strong> {user_info['role']}</p>
            <p><strong>အကောင့်ဖွင့်သည့်ရက်:</strong> {user_info['created_at']}</p>
            <p><strong>နောက်ဆုံးဝင်ရောက်ချိန်:</strong> {user_info['last_login']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### 🚀 အမြန်လုပ်ဆောင်ချက်များ")
        
        if st.session_state.user_role == 'admin':
            col_act1, col_act2, col_act3 = st.columns(3)
            
            with col_act1:
                if st.button("🎯 2D ထိုးရန်", use_container_width=True):
                    st.session_state.current_page = "🎰 2D ထိုးစနစ်"
                    st.rerun()
            
            with col_act2:
                if st.button("👥 အေဂျင့်များ", use_container_width=True):
                    st.session_state.current_page = "👥 အေဂျင့်မန်နေဂျာ"
                    st.rerun()
            
            with col_act3:
                if st.button("📊 အစီရင်ခံစာ", use_container_width=True):
                    st.session_state.current_page = "📊 အစီရင်ခံစာများ"
                    st.rerun()
        else:  # agent
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                if st.button("🎯 2D ထိုးရန်", use_container_width=True):
                    st.session_state.current_page = "🎰 2D ထိုးစနစ်"
                    st.rerun()
            
            with col_act2:
                if st.button("📋 စာရင်းကြည့်ရန်", use_container_width=True):
                    st.session_state.current_page = "🎰 2D ထိုးစနစ်"
                    st.rerun()
    
    with col_stats:
        # System stats
        st.markdown("### 📊 စနစ်အချက်အလက်")
        
        total_users = len(st.session_state.users_db)
        
        if st.session_state.user_role == 'admin':
            admin_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'admin')
            agent_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
            
            st.metric("စုစုပေါင်းအသုံးပြုသူ", total_users)
            st.metric("Admin များ", admin_count)
            st.metric("အေဂျင့်များ", agent_count)
        
        # Today's entries summary
        today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
        if today_entries:
            st.markdown("### 📋 ယနေ့အကျဉ်းချုပ်")
            latest_entry = today_entries[-1]
            st.write(f"**နောက်ဆုံးထိုးချက်:**")
            st.write(f"- {latest_entry['name']}")
            st.write(f"- {latest_entry['number']}")
            st.write(f"- {latest_entry['amount']:,} Ks")

# ==================== 2D SYSTEM ====================
def render_2d_system():
    """2D betting system"""
    
    # Check if user has configured sheet URL
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    # If no sheet URL configured, show configuration page
    if not user_config.get('sheet_url'):
        render_sheet_configuration()
        return
    
    # Main 2D system with tabs
    tab1, tab2, tab3 = st.tabs(["🎯 ဂဏန်းထည့်ရန်", "📋 ယနေ့စာရင်း", "⚙️ ဆက်တင်များ"])
    
    with tab1:
        render_2d_entry_form()
    
    with tab2:
        render_2d_today_entries()
    
    with tab3:
        render_2d_settings()

def render_sheet_configuration():
    """Sheet configuration for first-time users"""
    st.markdown('<h1 class="main-title">🎰 2D ထိုးစနစ်</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>📋 Google Sheets ချိတ်ဆက်ရန်</h3>
    <p>2D ထိုးစနစ်ကိုအသုံးပြုရန် ကျေးဇူးပြု၍ သင့်ရဲ့ Google Sheets URL ကိုထည့်ပါ။</p>
    <p>ဒေတာများကို ဒီ Sheet ထဲသို့အလိုအလျောက်သိမ်းဆည်းပေးပါမည်။</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("sheet_config_form"):
        sheet_url = st.text_input(
            "Google Sheets URL *",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="သင့်ရဲ့ Google Sheets လင့်ကိုထည့်ပါ"
        )
        
        if st.form_submit_button("💾 သိမ်းဆည်းမည်", use_container_width=True):
            if sheet_url:
                # Update user configuration
                st.session_state.user_configs[st.session_state.current_user] = {
                    'sheet_url': sheet_url,
                    'script_url': ''
                }
                
                # Also update in users_db for persistence
                if st.session_state.current_user in st.session_state.users_db:
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                
                # Test connection
                sheet, message = connect_to_google_sheets(sheet_url)
                if sheet:
                    st.success(f"✅ ဆက်တင်များသိမ်းဆည်းပြီး Google Sheets ချိတ်ဆက်ပြီးပါပြီ။")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ ဆက်တင်များသိမ်းဆည်းပြီးသော်လည်း {message}")
            else:
                st.error("❌ Sheet URL ထည့်ပါ")

def render_2d_entry_form():
    """2D number entry form"""
    st.markdown('<h2 class="sub-title">🎯 ဂဏန်းထည့်သွင်းရန်</h2>', unsafe_allow_html=True)
    
    # Hide/show toggle
    col_hide, col_info = st.columns([1, 4])
    with col_hide:
        if st.button("🙈 ဖျောက်မည်", key="hide_2d_form"):
            st.session_state.hidden_sections['2d_form'] = True
            st.rerun()
    
    if st.session_state.hidden_sections.get('2d_form', False):
        if st.button("👁️ ပြမည်", key="show_2d_form"):
            st.session_state.hidden_sections['2d_form'] = False
            st.rerun()
        return
    
    with st.form("number_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            better_name = st.text_input(
                "ထိုးသူအမည် *",
                placeholder="ဥပမာ - ကိုကျော်မင်း",
                help="ထိုးသူ၏အမည်ကိုထည့်ပါ"
            )
            
            number = st.text_input(
                "ထိုးမည့်ဂဏန်း *",
                placeholder="ဥပမာ - 55 (2D) သို့မဟုတ် 123 (3D)",
                help="ဂဏန်း ၂ လုံး (2D) သို့မဟုတ် ၃ လုံး (3D) ထည့်ပါ"
            )
            
            winning_number = st.text_input(
                "ပေါက်ဂဏန်း (Optional)",
                placeholder="ထွက်သောဂဏန်း (ရလဒ်သိပါက)",
                help="ရလဒ်ထွက်ပါကထည့်နိုင်သည်"
            )
        
        with col2:
            quantity = st.number_input(
                "အရေအတွက် *",
                min_value=1,
                max_value=100,
                value=1,
                help="ထိုးမည့်အရေအတွက်"
            )
            
            # Auto-calculate amount
            amount = 0
            if number and quantity:
                is_valid, _ = validate_number(number)
                if is_valid:
                    amount = calculate_amount(number, quantity)
            
            st.markdown(f"""
            <div style="background-color: #F0F9FF; padding: 1rem; border-radius: 10px;">
                <p><strong>တွက်ချက်ထားသောပမာဏ:</strong></p>
                <h2 style="color: #1E40AF; text-align: center;">{amount:,} Ks</h2>
                <p style="text-align: center; font-size: 0.9rem; color: #6B7280;">
                (ဂဏန်းတစ်လုံးလျှင် {PRICE_PER_NUMBER:,} Ks)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            note = st.text_area(
                "မှတ်ချက် (Optional)",
                placeholder="အထူးမှတ်ချက်ရှိပါကထည့်ပါ",
                height=50
            )
        
        # Submit button with clear instruction
        submitted = st.form_submit_button(
            "✅ **ဂဏန်းထည့်သွင်းမည်** (ဤခလုတ်ကိုနှိပ်ပါ)",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            errors = []
            
            # Validate name
            is_name_valid, name_error = validate_name(better_name)
            if not is_name_valid:
                errors.append(name_error)
            
            # Validate number
            is_number_valid, number_error = validate_number(number)
            if not is_number_valid:
                errors.append(number_error)
            
            # Validate quantity
            if quantity <= 0:
                errors.append("အရေအတွက်သည် ၁ ထက်ကြီးရမည်")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create entry
                entry = {
                    'id': len(st.session_state.today_entries.get(st.session_state.current_user, [])) + 1,
                    'time': format_myanmar_time(),
                    'name': better_name,
                    'number': number,
                    'quantity': quantity,
                    'amount': amount,
                    'winning_number': winning_number if winning_number else '',
                    'status': 'စောင့်ဆိုင်းနေ',
                    'note': note if note else ''
                }
                
                # Add to today's entries
                if st.session_state.current_user not in st.session_state.today_entries:
                    st.session_state.today_entries[st.session_state.current_user] = []
                
                st.session_state.today_entries[st.session_state.current_user].append(entry)
                
                # Save to Google Sheets
                user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
                sheet_url = user_config.get('sheet_url', '')
                
                if sheet_url:
                    success, message = save_to_google_sheets(entry, sheet_url)
                    if success:
                        st.success(f"✅ ဂဏန်းထည့်သွင်းပြီး Google Sheets သို့သိမ်းဆည်းပြီးပါပြီ။")
                        log_activity("2D Entry", f"Added: {number} for {better_name}")
                    else:
                        st.warning(f"⚠️ ဂဏန်းထည့်သွင်းပြီးသော်လည်း {message}")
                else:
                    st.success("✅ ဂဏန်းထည့်သွင်းပြီးပါပြီ။")
                    log_activity("2D Entry", f"Added: {number} for {better_name}")
                
                st.balloons()

def render_2d_today_entries():
    """Today's 2D entries display"""
    st.markdown('<h2 class="sub-title">📋 ယနေ့ထည့်သွင်းထားသောဂဏန်းများ</h2>', unsafe_allow_html=True)
    
    # Hide/show toggle
    if st.button("🙈 ဤကဏ္ဍကိုဖျောက်မည်", key="hide_today_2d"):
        st.session_state.hidden_sections['today_2d'] = True
        st.rerun()
    
    if st.session_state.hidden_sections.get('today_2d', False):
        if st.button("👁️ ဤကဏ္ဍကိုပြမည်", key="show_today_2d"):
            st.session_state.hidden_sections['today_2d'] = False
            st.rerun()
        return
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    
    if not today_entries:
        st.info("ယနေ့အတွက် မည်သည့်ဂဏန်းမှမထည့်ရသေးပါ။")
        return
    
    # Summary stats
    total_quantity = sum(entry['quantity'] for entry in today_entries)
    total_amount = sum(entry['amount'] for entry in today_entries)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("စုစုပေါင်းအရေအတွက်", len(today_entries))
    with col2:
        st.metric("စုစုပေါင်းထိုးခြင်းအရေအတွက်", total_quantity)
    with col3:
        st.metric("စုစုပေါင်းပမာဏ", f"{total_amount:,} Ks")
    
    st.divider()
    
    # Edit/Delete functionality
    st.markdown("### ✏️ စာရင်းပြင်ဆင်ခြင်း/ဖျက်ခြင်း")
    
    for i, entry in enumerate(today_entries):
        with st.expander(f"#{i+1} - {entry['name']} ({entry['number']}) - {entry['amount']:,} Ks"):
            col_info, col_actions = st.columns([3, 1])
            
            with col_info:
                st.write(f"**အချိန်:** {entry['time']}")
                st.write(f"**ထိုးသူအမည်:** {entry['name']}")
                st.write(f"**ဂဏန်း:** {entry['number']}")
                st.write(f"**အရေအတွက်:** {entry['quantity']}")
                st.write(f"**ပမာဏ:** {entry['amount']:,} Ks")
                if entry['winning_number']:
                    st.write(f"**ပေါက်ဂဏန်း:** {entry['winning_number']}")
                st.write(f"**အခြေအနေ:** {entry['status']}")
                if entry['note']:
                    st.write(f"**မှတ်ချက်:** {entry['note']}")
            
            with col_actions:
                # Edit button
                if st.button("✏️ ပြင်မည်", key=f"edit_{i}"):
                    st.session_state.editing_entry = i
                    st.rerun()
                
                # Delete button
                if st.button("🗑️ ဖျက်မည်", key=f"delete_{i}"):
                    today_entries.pop(i)
                    st.success("✅ စာရင်းဖျက်ပြီးပါပြီ။")
                    log_activity("Delete Entry", f"Deleted entry #{i+1}")
                    time.sleep(1)
                    st.rerun()
    
    # Edit form if editing
    if 'editing_entry' in st.session_state:
        entry_index = st.session_state.editing_entry
        if entry_index < len(today_entries):
            entry = today_entries[entry_index]
            
            st.markdown("---")
            st.markdown("### ✏️ စာရင်းပြင်ဆင်ခြင်း")
            
            with st.form(f"edit_form_{entry_index}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edited_name = st.text_input("ထိုးသူအမည်", value=entry['name'])
                    edited_number = st.text_input("ဂဏန်း", value=entry['number'])
                    edited_winning = st.text_input("ပေါက်ဂဏန်း", value=entry.get('winning_number', ''))
                
                with col2:
                    edited_quantity = st.number_input("အရေအတွက်", 
                                                     min_value=1, 
                                                     value=entry['quantity'])
                    edited_status = st.selectbox(
                        "အခြေအနေ",
                        ["စောင့်ဆိုင်းနေ", "ထိုးပြီး", "ပေါက်ပြီး", "မပေါက်ပါ"],
                        index=["စောင့်ဆိုင်းနေ", "ထိုးပြီး", "ပေါက်ပြီး", "မပေါက်ပါ"]
                            .index(entry['status'])
                    )
                    edited_note = st.text_area("မှတ်ချက်", value=entry.get('note', ''))
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 သိမ်းဆည်းမည်"):
                        # Update entry
                        today_entries[entry_index]['name'] = edited_name
                        today_entries[entry_index]['number'] = edited_number
                        today_entries[entry_index]['quantity'] = edited_quantity
                        today_entries[entry_index]['amount'] = calculate_amount(edited_number, edited_quantity)
                        today_entries[entry_index]['winning_number'] = edited_winning
                        today_entries[entry_index]['status'] = edited_status
                        today_entries[entry_index]['note'] = edited_note
                        
                        # Update in Google Sheets if connected
                        user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
                        sheet_url = user_config.get('sheet_url', '')
                        if sheet_url:
                            edited_entry = today_entries[entry_index].copy()
                            edited_entry['note'] = f"(ပြင်ဆင်ထား) {edited_note}"
                            save_to_google_sheets(edited_entry, sheet_url)
                        
                        del st.session_state.editing_entry
                        st.success("✅ စာရင်းပြင်ဆင်ပြီးပါပြီ။")
                        log_activity("Edit Entry", f"Edited entry #{entry_index+1}")
                        time.sleep(1)
                        st.rerun()
                
                with col_cancel:
                    if st.form_submit_button("❌ ပယ်ဖျက်မည်"):
                        del st.session_state.editing_entry
                        st.rerun()

def render_2d_settings():
    """2D system settings"""
    st.markdown('<h2 class="sub-title">⚙️ 2D ဆက်တင်များ</h2>', unsafe_allow_html=True)
    
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    with st.form("2d_settings_form"):
        st.markdown("### 🔗 Google Sheets ဆက်တင်များ")
        
        current_sheet_url = st.text_input(
            "Google Sheets URL",
            value=user_config.get('sheet_url', ''),
            placeholder="https://docs.google.com/spreadsheets/d/..."
        )
        
        if st.form_submit_button("💾 ဆက်တင်များသိမ်းဆည်းမည်"):
            if current_sheet_url:
                st.session_state.user_configs[st.session_state.current_user] = {
                    'sheet_url': current_sheet_url,
                    'script_url': ''
                }
                
                # Also update in users_db
                if st.session_state.current_user in st.session_state.users_db:
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = current_sheet_url
                
                st.success("✅ ဆက်တင်များသိမ်းဆည်းပြီးပါပြီ။")
                log_activity("Update Settings", "Updated Google Sheets URL")
                st.rerun()
            else:
                st.error("❌ Sheet URL ထည့်ပါ")
    
    st.divider()
    
    # Data management
    st.markdown("### 🗃️ ဒေတာစီမံခန့်ခွဲမှု")
    
    col_reset, col_export = st.columns(2)
    
    with col_reset:
        if st.button("🔄 ယနေ့စာရင်းအားလုံးဖျက်ရန်"):
            if st.checkbox("သေချာပါသလား? ဤလုပ်ဆောင်ချက်ကိုပြန်လည်ရယူ၍မရပါ။"):
                st.session_state.today_entries[st.session_state.current_user] = []
                st.success("✅ ယနေ့စာရင်းအားလုံးဖျက်ပြီးပါပြီ။")
                log_activity("Reset Entries", "Cleared all today's entries")
                time.sleep(1)
                st.rerun()
    
    with col_export:
        if st.button("📤 ယနေ့ဒေတာထုတ်ယူရန်"):
            today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
            if today_entries:
                df = pd.DataFrame(today_entries)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                
                today_date = get_today_date()
                st.download_button(
                    label="💾 CSV ဖိုင်ဒေါင်းလုတ်လုပ်ရန်",
                    data=csv,
                    file_name=f"2d_entries_{st.session_state.current_user}_{today_date}.csv",
                    mime="text/csv"
                )
                log_activity("Export Data", f"Exported {len(today_entries)} entries")
            else:
                st.info("ℹ️ ယနေ့အတွက် မည်သည့်ဒေတာမှမရှိသေးပါ။")

# ==================== USER MANAGEMENT (Panel) ====================
def render_user_management():
    """User management panel (admin only)"""
    if st.session_state.user_role != 'admin':
        st.error("⚠️ ဤစနစ်ကို Admin များသာအသုံးပြုနိုင်ပါသည်။")
        return
    
    st.markdown('<h1 class="main-title">👥 အေဂျင့်မန်နေဂျာ</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ အေဂျင့်အသစ်ထည့်ခြင်း", "📋 အေဂျင့်စာရင်း", "🗑️ အေဂျင့်ဖျက်ခြင်း"])
    
    with tab1:
        render_add_agent_form()
    
    with tab2:
        render_agent_list()
    
    with tab3:
        render_delete_agent()

def render_add_agent_form():
    """Add new agent form"""
    st.markdown('<h3 class="sub-title">အေဂျင့်အသစ်ထည့်သွင်းရန်</h3>', unsafe_allow_html=True)
    
    with st.form("add_agent_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input(
                "အေဂျင့်အမည် *",
                placeholder="agent2",
                help="အင်္ဂလိပ်အက္ခရာများနှင့် နံပါတ်များသာ"
            )
            
            new_password = st.text_input(
                "စကားဝှက် *",
                type="password",
                placeholder="အနည်းဆုံး ၆ လုံး",
                help="အနည်းဆုံး ၆ လုံးပါဝင်ရန်"
            )
        
        with col2:
            new_name = st.text_input(
                "အမည်အပြည့်အစုံ *",
                placeholder="ဒေါ်နှင်းနှင်း"
            )
            
            new_email = st.text_input(
                "အီးမေးလ်",
                placeholder="agent2@company.com",
                help="Optional"
            )
        
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="ဤအေဂျင့်အတွက် Google Sheets URL"
        )
        
        submitted = st.form_submit_button(
            "✅ **အေဂျင့်အသစ်ထည့်သွင်းမည်**",
            use_container_width=True
        )
        
        if submitted:
            if not all([new_username, new_password, new_name]):
                st.error("❌ လိုအပ်သောအချက်အလက်အားလုံးကိုဖြည့်ပါ။")
                return
            
            if len(new_password) < 6:
                st.error("❌ စကားဝှက်အနည်းဆုံး ၆ လုံးဖြစ်ရမည်။")
                return
            
            success, message = add_new_user(new_username, new_password, 'agent', new_name, new_email)
            
            if success:
                # Add sheet URL if provided
                if sheet_url:
                    st.session_state.users_db[new_username]['sheet_url'] = sheet_url
                
                st.success(f"✅ {message}")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {message}")

def render_agent_list():
    """Agent list display"""
    st.markdown('<h3 class="sub-title">အေဂျင့်များစာရင်း</h3>', unsafe_allow_html=True)
    
    agents = []
    for username, details in st.session_state.users_db.items():
        if details['role'] == 'agent':
            # Get today's entries for this agent
            today_entries = st.session_state.today_entries.get(username, [])
            today_count = len(today_entries)
            today_amount = sum(entry['amount'] for entry in today_entries)
            
            agents.append({
                'အသုံးပြုသူအမည်': username,
                'အမည်': details['name'],
                'အီးမေးလ်': details.get('email', 'N/A'),
                'အကောင့်ဖွင့်သည့်ရက်': details['created_at'],
                'ယနေ့အရေအတွက်': today_count,
                'ယနေ့ပမာဏ': f"{today_amount:,} Ks",
                'Sheet URL': details.get('sheet_url', 'မရှိသေး')
            })
    
    if agents:
        df = pd.DataFrame(agents)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary stats
        total_agents = len(agents)
        total_today = sum(agent['ယနေ့အရေအတွက်'] for agent in agents)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("စုစုပေါင်းအေဂျင့်", total_agents)
        with col2:
            st.metric("ယနေ့စုစုပေါင်းအရေအတွက်", total_today)
    else:
        st.info("ℹ️ မည်သည့်အေဂျင့်မှမရှိသေးပါ။")

def render_delete_agent():
    """Delete agent form"""
    st.markdown('<h3 class="sub-title">အေဂျင့်ဖျက်ခြင်း</h3>', unsafe_allow_html=True)
    
    # Get all agents except current user
    deletable_agents = [u for u in st.session_state.users_db.keys() 
                       if st.session_state.users_db[u]['role'] == 'agent' 
                       and u != st.session_state.current_user]
    
    if deletable_agents:
        selected_agent = st.selectbox("ဖျက်လိုသောအေဂျင့်ရွေးချယ်ရန်", deletable_agents)
        
        if selected_agent:
            agent_info = st.session_state.users_db[selected_agent]
            
            st.markdown("### ဖျက်မည့်အေဂျင့်၏အချက်အလက်များ")
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write(f"**အသုံးပြုသူအမည်:** {selected_agent}")
                st.write(f"**အမည်:** {agent_info['name']}")
            
            with col_info2:
                st.write(f"**အကောင့်ဖွင့်သည့်ရက်:** {agent_info['created_at']}")
                if agent_info.get('email'):
                    st.write(f"**အီးမေးလ်:** {agent_info['email']}")
            
            # Get agent's today entries
            today_entries = st.session_state.today_entries.get(selected_agent, [])
            if today_entries:
                st.warning(f"⚠️ ဤအေဂျင့်တွင် ယနေ့ထိုးထားသောစာရင်း {len(today_entries)} ခုရှိပါသည်။")
            
            confirm_text = st.text_input(
                "အတည်ပြုခြင်း: အေဂျင့်ဖျက်ရန် သေချာပါသလား?",
                placeholder="ကျွန်ုပ်အေဂျင့်ဖျက်ရန်သဘောတူပါသည်"
            )
            
            col_del1, col_del2 = st.columns(2)
            
            with col_del1:
                if st.button("🗑️ **အေဂျင့်ဖျက်မည်**", 
                           disabled=confirm_text != "ကျွန်ုပ်အေဂျင့်ဖျက်ရန်သဘောတူပါသည်",
                           use_container_width=True):
                    success, message = delete_user_account(selected_agent)
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            with col_del2:
                if st.button("❌ လုပ်ဆောင်ချက်ပယ်ဖျက်မည်", use_container_width=True):
                    st.rerun()
    else:
        st.info("ℹ️ ဖျက်နိုင်သောအေဂျင့်များမရှိပါ။")

# ==================== REPORTS PAGE ====================
def render_reports_page():
    """Reports page (admin only)"""
    if st.session_state.user_role != 'admin':
        st.error("⚠️ ဤစနစ်ကို Admin များသာအသုံးပြုနိုင်ပါသည်။")
        return
    
    st.markdown('<h1 class="main-title">📊 အစီရင်ခံစာများ</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📈 စာရင်းဇယားများ", "📅 လုပ်ဆောင်ချက်မှတ်တမ်း"])
    
    with tab1:
        render_system_statistics()
    
    with tab2:
        render_activity_log()

def render_system_statistics():
    """System statistics report"""
    # User statistics
    total_users = len(st.session_state.users_db)
    admin_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'admin')
    agent_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
    
    # 2D statistics from all users
    total_2d_entries = 0
    total_2d_amount = 0
    for entries in st.session_state.today_entries.values():
        total_2d_entries += len(entries)
        total_2d_amount += sum(entry['amount'] for entry in entries)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("စုစုပေါင်းအသုံးပြုသူ", total_users)
    with col2:
        st.metric("Admin များ", admin_count)
    with col3:
        st.metric("အေဂျင့်များ", agent_count)
    with col4:
        st.metric("ယနေ့ 2D အရေအတွက်", total_2d_entries)
    
    st.divider()
    
    # Today's entries from all agents
    st.markdown("### 📋 ယနေ့စာရင်းများ (အေဂျင့်အားလုံး)")
    
    all_entries = []
    for username, entries in st.session_state.today_entries.items():
        user_role = st.session_state.users_db.get(username, {}).get('role', '')
        if user_role == 'agent':  # Only show agents' entries
            for entry in entries:
                entry_with_user = entry.copy()
                entry_with_user['အေဂျင့်'] = username
                all_entries.append(entry_with_user)
    
    if all_entries:
        # Create DataFrame
        df_data = []
        for entry in all_entries:
            df_data.append({
                'အချိန်': entry['time'],
                'အေဂျင့်': entry['အေဂျင့်'],
                'ထိုးသူအမည်': entry['name'],
                'ဂဏန်း': entry['number'],
                'အရေအတွက်': entry['quantity'],
                'ပမာဏ': f"{entry['amount']:,} Ks",
                'အခြေအနေ': entry.get('status', 'စောင့်ဆိုင်းနေ')
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        if st.button("📥 အစီရင်ခံစာထုတ်ယူရန်"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="💾 CSV ဖိုင်ဒေါင်းလုတ်လုပ်ရန်",
                data=csv,
                file_name=f"2d_report_all_{get_today_date()}.csv",
                mime="text/csv"
            )
            log_activity("Export Report", "Exported all agents report")
    else:
        st.info("ℹ️ ယနေ့အတွက် မည်သည့်စာရင်းမှမရှိသေးပါ။")

def render_activity_log():
    """Activity log viewer"""
    st.markdown('<h3 class="sub-title">လုပ်ဆောင်ချက်မှတ်တမ်း</h3>', unsafe_allow_html=True)
    
    if st.session_state.activity_log:
        # Display logs
        for log in reversed(st.session_state.activity_log[-20:]):  # Show last 20 activities
            with st.container():
                st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 10px;
                    border-radius: 8px;
                    border-left: 5px solid #3B82F6;
                    margin: 5px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">
                    <strong>{log['action']}</strong>
                    <div style="color: #6B7280; font-size: 12px;">
                        {log['timestamp']} - {log['user']}
                        {f"<br>{log['details']}" if log['details'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Clear log button
        if st.button("🧹 မှတ်တမ်းအားလုံးဖျက်ရန်"):
            if st.checkbox("သေချာပါသလား?"):
                st.session_state.activity_log = []
                st.success("✅ မှတ်တမ်းအားလုံးဖျက်ပြီးပါပြီ။")
                st.rerun()
    else:
        st.info("ℹ️ လုပ်ဆောင်ချက်မှတ်တမ်းများမရှိသေးပါ။")

# ==================== SETTINGS PAGE ====================
def render_settings_page():
    """Settings page"""
    st.markdown('<h1 class="main-title">⚙️ ဆက်တင်များ</h1>', unsafe_allow_html=True)
    
    if st.session_state.user_role == 'admin':
        tab1, tab2 = st.tabs(["🔧 အထွေထွေဆက်တင်များ", "📋 စနစ်အချက်အလက်"])
        
        with tab1:
            render_general_settings()
        
        with tab2:
            render_system_info()
    else:  # agent
        render_agent_settings()

def render_general_settings():
    """General settings for admin"""
    st.markdown("### 🔧 အထွေထွေဆက်တင်များ")
    
    with st.form("general_settings_form"):
        # Price per number setting
        st.markdown("#### 💰 ဂဏန်းဈေးနှုန်း")
        price = st.number_input(
            "ဂဏန်းတစ်လုံးဈေးနှုန်း (Ks)",
            min_value=1000,
            max_value=100000,
            value=PRICE_PER_NUMBER,
            step=1000
        )
        
        # Cache management
        st.markdown("#### 🗃️ Cache စီမံခန့်ခွဲမှု")
        cache_info = f"လက်ရှိ Cache အရွယ်အစား: {len(st.session_state.number_limits_cache)} items"
        st.info(cache_info)
        
        if st.checkbox("Cache အားလုံးဖယ်ရှားမည်"):
            st.warning("Cache အားလုံးဖယ်ရှားပါမည်။")
        
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.form_submit_button("💾 ဆက်တင်များသိမ်းဆည်းမည်"):
                # In a real app, you would save this to a config file or database
                st.success("✅ ဆက်တင်များသိမ်းဆည်းပြီးပါပြီ။")
                log_activity("Update Settings", f"Updated price to {price} Ks")
        
        with col_clear:
            if st.form_submit_button("🔄 ပြန်လည်စတင်မည်"):
                # Clear cache if selected
                if st.session_state.get('clear_cache', False):
                    st.session_state.number_limits_cache = {}
                    st.success("✅ Cache အားလုံးဖယ်ရှားပြီးပါပြီ။")
                st.rerun()

def render_system_info():
    """System information"""
    st.markdown("### 📋 စနစ်အချက်အလက်")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        **ဆော့ဖ်ဝဲအချက်အလက်:**
        - **အမည်:** 2D ထိုးစနစ်
        - **ဗားရှင်း:** 1.0.0
        - **ဖွံ့ဖြိုးမှု:** Streamlit
        - **ဘာသာစကား:** Python
        
        **ဒေတာဘေ့စ်:**
        - **အမျိုးအစား:** In-memory Session
        - **အသုံးပြုသူအရေအတွက်:** {}
        - **Cache အရွယ်အစား:** {} items
        """.format(len(st.session_state.users_db), len(st.session_state.number_limits_cache)))
    
    with col_info2:
        st.markdown("""
        **လုံခြုံရေးစနစ်:**
        - **စကားဝှက် Hashing:** SHA-256
        - **Session စီမံခန့်ခွဲမှု:** Streamlit Session State
        - **လုပ်ဆောင်ချက်မှတ်တမ်း:** ပြည့်စုံ
        
        **ပံ့ပိုးမှုများ:**
        - **Multi-role Access:** Admin/Agent
        - **Google Sheets Integration:** အလိုအလျောက်
        - **ဒေတာထုတ်ယူမှု:** CSV Export
        """)
    
    st.divider()
    
    # System maintenance
    st.markdown("### 🔧 စနစ်ထိန်းသိမ်းမှု")
    
    col_maint1, col_maint2 = st.columns(2)
    
    with col_maint1:
        if st.button("🔄 Cache ရှင်းလင်းရန်", use_container_width=True):
            st.session_state.number_limits_cache = {}
            st.success("✅ Cache ရှင်းလင်းပြီးပါပြီ။")
            log_activity("System", "Cleared cache")
            st.rerun()
    
    with col_maint2:
        if st.button("📊 Activity Log ရှင်းလင်းရန်", use_container_width=True):
            st.session_state.activity_log = []
            st.success("✅ Activity Log ရှင်းလင်းပြီးပါပြီ။")
            log_activity("System", "Cleared activity log")
            st.rerun()

def render_agent_settings():
    """Settings for agents"""
    st.markdown("### ⚙️ ဆက်တင်များ")
    
    user_info = st.session_state.users_db[st.session_state.current_user]
    
    with st.form("agent_settings_form"):
        st.markdown("#### 👤 ကိုယ်ရေးကိုယ်တာအချက်အလက်")
        
        current_name = st.text_input(
            "အမည်အပြည့်အစုံ",
            value=user_info['name']
        )
        
        current_email = st.text_input(
            "အီးမေးလ်",
            value=user_info.get('email', '')
        )
        
        new_password = st.text_input(
            "စကားဝှက် အသစ်",
            type="password",
            placeholder="စကားဝှက်ပြောင်းလိုပါကထည့်ပါ",
            help="မထည့်လျှင်လက်ရှိစကားဝှက်အတိုင်းထားမည်"
        )
        
        if st.form_submit_button("💾 အချက်အလက်များသိမ်းဆည်းမည်"):
            update_data = {
                'name': current_name,
                'email': current_email
            }
            
            if new_password:
                update_data['password'] = new_password
            
            success, message = update_user_info(st.session_state.current_user, **update_data)
            
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
