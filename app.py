# main_app.py (app တစ်ခုတည်း)
import streamlit as st
import pandas as pd
import time
import hashlib
import re
from datetime import datetime
import pytz

# ==================== CONFIGURATION ====================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
PRICE_PER_NUMBER = 50000
ADMIN_USERNAME = "AMTHI"
ADMIN_PASSWORD = "1632022"

# ==================== INITIALIZATION ====================
def init_session_state():
    """Session state initialization"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''
    if 'current_user' not in st.session_state:
        st.session_state.current_user = ''
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    if 'today_entries' not in st.session_state:
        st.session_state.today_entries = {}
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    if 'user_configs' not in st.session_state:
        st.session_state.user_configs = {}
    if 'hidden_sections' not in st.session_state:
        st.session_state.hidden_sections = {}

# Initialize session state
init_session_state()

# Initialize default users if empty
if not st.session_state.users_db:
    # Admin account (hardcoded)
    st.session_state.users_db[ADMIN_USERNAME] = {
        'password': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
        'role': 'admin',
        'name': 'စီမံခန့်ခွဲသူ',
        'email': '',
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sheet_url': ''
    }
    
    # Default agent account
    st.session_state.users_db['agent1'] = {
        'password': hashlib.sha256('agent123'.encode()).hexdigest(),
        'role': 'agent',
        'name': 'အေဂျင့်တစ်',
        'email': 'agent1@company.com',
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sheet_url': '',
        'daily_limit': 1000000
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
    username = username.strip()
    
    # Admin အတွက်သီးသန့်စစ်ဆေးခြင်း
    if username.upper() == ADMIN_USERNAME.upper():
        if password == ADMIN_PASSWORD:
            # Create admin account if not exists
            if ADMIN_USERNAME not in st.session_state.users_db:
                st.session_state.users_db[ADMIN_USERNAME] = {
                    'password': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
                    'role': 'admin',
                    'name': 'စီမံခန့်ခွဲသူ',
                    'email': '',
                    'created_at': datetime.now().strftime("%Y-%m-%d"),
                    'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'sheet_url': ''
                }
            
            st.session_state.users_db[ADMIN_USERNAME]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True, 'admin'
    
    # တခြားအသုံးပြုသူများအတွက်စစ်ဆေးခြင်း
    for stored_username, user_data in st.session_state.users_db.items():
        if stored_username.lower() == username.lower():
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user_data['password'] == hashed_password:
                user_data['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True, user_data['role']
    
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
        'sheet_url': '',
        'daily_limit': 1000000 if role == 'agent' else 0
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

# ==================== CSS STYLING ====================
def load_css():
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

# ==================== LOGIN PAGE ====================
def render_login_page():
    """Login page for all users"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">🎰 2D Betting System</h1>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 အကောင့်ဝင်ရန်")
            st.write("ကျေးဇူးပြု၍ သင့်အကောင့်ဖြင့် ဝင်ရောက်ပါ။")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 **အသုံးပြုသူအမည်**", 
                                       placeholder="AMTHI သို့မဟုတ် agent1")
                
                password = st.text_input("🔒 **စကားဝှက်**", 
                                       type="password",
                                       placeholder="password")
                
                login_button = st.form_submit_button("🚀 **အကောင့်ဝင်ရန်**", 
                                                   use_container_width=True)
                
                if login_button:
                    if username and password:
                        authenticated, role = authenticate_user(username, password)
                        if authenticated:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.current_user = username.upper() if username.upper() == ADMIN_USERNAME.upper() else username
                            
                            # Initialize user data for agents
                            if role == 'agent':
                                if username not in st.session_state.today_entries:
                                    st.session_state.today_entries[username] = []
                                if username not in st.session_state.user_configs:
                                    st.session_state.user_configs[username] = {
                                        'sheet_url': st.session_state.users_db.get(username, {}).get('sheet_url', ''),
                                        'script_url': ''
                                    }
                            
                            log_activity("Login", f"User: {username}")
                            st.success(f"✅ **{role.upper()}** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ အကောင့်မှန်ကန်မှုမရှိပါ။")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ အသုံးပြုသူအမည်နှင့် စကားဝှက်ထည့်ပါ။")
            
            st.info("""
            **Default Credentials:**
            - **Admin:** username: `AMTHI`, password: `1632022`
            - **Agent:** username: `agent1`, password: `agent123`
            """)

# ==================== ADMIN PANEL ====================
def render_admin_panel():
    """Admin panel functions"""
    # Sidebar
    with st.sidebar:
        user_info = st.session_state.users_db[st.session_state.current_user]
        st.markdown(f"""
        <div class="user-card">
            <h3>👑 {user_info['name']}</h3>
            <p><strong>Role:</strong> ADMIN</p>
            <p><strong>User:</strong> {st.session_state.current_user}</p>
            <p><strong>Last Login:</strong><br>{user_info['last_login']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 📋 Admin Menu")
        menu_options = ["🏠 Dashboard", "👥 Agent Management", "📊 Reports", "⚙️ Settings"]
        selected_menu = st.radio("Select Menu", menu_options)
        
        st.divider()
        
        # Quick stats
        total_users = len(st.session_state.users_db)
        agent_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
        st.metric("Total Users", total_users)
        st.metric("Total Agents", agent_count)
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            log_activity("Logout", f"Admin: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main content
    if selected_menu == "🏠 Dashboard":
        render_admin_dashboard()
    elif selected_menu == "👥 Agent Management":
        render_agent_management()
    elif selected_menu == "📊 Reports":
        render_admin_reports()
    elif selected_menu == "⚙️ Settings":
        render_admin_settings()

def render_admin_dashboard():
    """Admin dashboard"""
    st.markdown('<h1 class="main-title">👑 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(st.session_state.users_db)
        st.metric("Total Users", total_users)
    
    with col2:
        admin_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'admin')
        st.metric("Admins", admin_count)
    
    with col3:
        agent_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
        st.metric("Agents", agent_count)
    
    with col4:
        activity_count = len(st.session_state.activity_log)
        st.metric("Activities", activity_count)
    
    st.divider()
    
    # Recent activities
    st.markdown("### 📝 Recent Activities")
    recent_activities = st.session_state.activity_log[-10:] if st.session_state.activity_log else []
    
    if recent_activities:
        for activity in reversed(recent_activities):
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
                    <strong>{activity['action']}</strong>
                    <div style="color: #6B7280; font-size: 12px;">
                        {activity['timestamp']} - {activity['user']}
                        {f"<br>{activity['details']}" if activity['details'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No activities yet.")
    
    st.divider()
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("➕ Add New Agent", use_container_width=True):
            st.session_state.show_add_agent = True
            st.rerun()

def render_agent_management():
    """Agent management"""
    st.markdown('<h1 class="main-title">👥 Agent Management</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Agent", "📋 Agent List", "✏️ Edit Agent"])
    
    with tab1:
        render_add_agent_form()
    
    with tab2:
        render_agent_list()
    
    with tab3:
        render_edit_agent_form()

def render_add_agent_form():
    """Add new agent form"""
    st.markdown('<h3 class="sub-title">Add New Agent</h3>', unsafe_allow_html=True)
    
    with st.form("add_agent_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input(
                "Username *",
                placeholder="agent3",
                help="English letters, numbers and underscore only"
            )
            
            new_password = st.text_input(
                "Password *",
                type="password",
                placeholder="Minimum 6 characters"
            )
        
        with col2:
            new_name = st.text_input(
                "Full Name *",
                placeholder="Agent Three"
            )
            
            new_email = st.text_input(
                "Email",
                placeholder="agent3@company.com"
            )
        
        # Agent settings
        st.markdown("### ⚙️ Agent Settings")
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Optional - Agent's personal Google Sheets"
        )
        
        max_daily_limit = st.number_input(
            "Daily Limit (Ks)",
            min_value=0,
            value=1000000,
            step=100000,
            help="Maximum daily betting amount"
        )
        
        submitted = st.form_submit_button(
            "✅ **Add New Agent**",
            use_container_width=True
        )
        
        if submitted:
            if not all([new_username, new_password, new_name]):
                st.error("Please fill all required fields.")
                return
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            
            success, message = add_new_user(new_username, new_password, 'agent', new_name, new_email)
            
            if success:
                # Add additional agent settings
                if sheet_url:
                    st.session_state.users_db[new_username]['sheet_url'] = sheet_url
                st.session_state.users_db[new_username]['daily_limit'] = max_daily_limit
                
                st.success(f"✅ {message}")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")

def render_agent_list():
    """Display agent list"""
    st.markdown('<h3 class="sub-title">Agent List</h3>', unsafe_allow_html=True)
    
    agents = []
    for username, details in st.session_state.users_db.items():
        if details['role'] == 'agent':
            agents.append({
                'Username': username,
                'Name': details['name'],
                'Email': details.get('email', 'N/A'),
                'Created': details['created_at'],
                'Last Login': details['last_login'],
                'Daily Limit': f"{details.get('daily_limit', 0):,} Ks",
                'Status': 'Active'
            })
    
    if agents:
        df = pd.DataFrame(agents)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No agents found.")

def render_edit_agent_form():
    """Edit agent form"""
    st.markdown('<h3 class="sub-title">Edit Agent</h3>', unsafe_allow_html=True)
    
    # Get agent list
    agent_list = [u for u in st.session_state.users_db.keys() 
                 if st.session_state.users_db[u]['role'] == 'agent']
    
    if not agent_list:
        st.info("No agents available to edit.")
        return
    
    selected_agent = st.selectbox("Select Agent to Edit", agent_list)
    
    if selected_agent:
        agent_info = st.session_state.users_db[selected_agent]
        
        with st.form("edit_agent_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Full Name", value=agent_info['name'])
                edit_email = st.text_input("Email", value=agent_info.get('email', ''))
            
            with col2:
                edit_sheet_url = st.text_input(
                    "Google Sheets URL",
                    value=agent_info.get('sheet_url', '')
                )
                
                edit_daily_limit = st.number_input(
                    "Daily Limit (Ks)",
                    min_value=0,
                    value=agent_info.get('daily_limit', 1000000),
                    step=100000
                )
            
            # Password change (optional)
            st.markdown("### 🔒 Change Password (Optional)")
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Leave empty to keep current password"
            )
            
            col_save, col_reset = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    update_data = {
                        'name': edit_name,
                        'email': edit_email,
                        'sheet_url': edit_sheet_url,
                        'daily_limit': edit_daily_limit
                    }
                    
                    if new_password:
                        update_data['password'] = new_password
                    
                    success, message = update_user_info(selected_agent, **update_data)
                    
                    if success:
                        st.success("✅ Agent updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            with col_reset:
                if st.form_submit_button("🗑️ Delete Agent", use_container_width=True):
                    st.warning(f"Are you sure you want to delete agent: {selected_agent}?")
                    if st.checkbox("Confirm Deletion"):
                        success, message = delete_user_account(selected_agent)
                        if success:
                            st.success(f"✅ {message}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

def render_admin_reports():
    """Admin reports"""
    st.markdown('<h1 class="main-title">📊 Admin Reports</h1>', unsafe_allow_html=True)
    st.info("Reports section will be implemented soon.")

def render_admin_settings():
    """Admin settings"""
    st.markdown('<h1 class="main-title">⚙️ Admin Settings</h1>', unsafe_allow_html=True)
    st.info("Settings section will be implemented soon.")

# ==================== 2D AGENT APP ====================
def render_2d_app():
    """2D Agent application"""
    # Sidebar
    with st.sidebar:
        user_info = st.session_state.users_db[st.session_state.current_user]
        st.markdown(f"""
        <div class="user-card">
            <h3>👤 {user_info['name']}</h3>
            <p><strong>Role:</strong> AGENT</p>
            <p><strong>User:</strong> {st.session_state.current_user}</p>
            <p><strong>Last Login:</strong><br>{user_info['last_login']}</p>
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
        st.markdown("### 🗺️ Navigation")
        menu_options = ["🎯 Enter Numbers", "📋 Today's Entries", "⚙️ Settings"]
        selected_menu = st.radio("Select Menu", menu_options)
        
        st.divider()
        
        # Today's stats
        today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
        total_amount = sum(entry['amount'] for entry in today_entries) if today_entries else 0
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Today's Count", len(today_entries))
        with col_stat2:
            st.metric("Today's Amount", f"{total_amount:,} Ks")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            log_activity("Logout", f"Agent: {st.session_state.current_user}")
            st.session_state.logged_in = False
            st.session_state.user_role = ''
            st.session_state.current_user = ''
            st.rerun()
    
    # Main content
    if selected_menu == "🎯 Enter Numbers":
        render_number_entry()
    elif selected_menu == "📋 Today's Entries":
        render_today_entries()
    elif selected_menu == "⚙️ Settings":
        render_agent_settings()

def render_number_entry():
    """Number entry form for agents"""
    st.markdown('<h1 class="main-title">🎯 Enter 2D/3D Numbers</h1>', unsafe_allow_html=True)
    
    # Check if user has sheet configured
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    
    if not user_config.get('sheet_url'):
        render_sheet_configuration()
        return
    
    with st.form("number_entry_form", clear_on_submit=True):
        st.markdown("### 📝 Enter Betting Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input(
                "Customer Name *",
                placeholder="e.g., Ko Kyaw Kyaw",
                help="Enter customer's name"
            )
            
            number = st.text_input(
                "Number *",
                placeholder="e.g., 55 (2D) or 123 (3D)",
                help="Enter 2D (00-99) or 3D (000-999) number"
            )
            
            winning_number = st.text_input(
                "Winning Number (Optional)",
                placeholder="Result number if known"
            )
        
        with col2:
            quantity = st.number_input(
                "Quantity *",
                min_value=1,
                max_value=100,
                value=1,
                help="Number of times to bet"
            )
            
            # Auto-calculate amount
            amount = 0
            if number and quantity:
                is_valid, _ = validate_number(number)
                if is_valid:
                    amount = calculate_amount(number, quantity)
            
            st.markdown(f"""
            <div style="background-color: #F0F9FF; padding: 1rem; border-radius: 10px;">
                <p><strong>Calculated Amount:</strong></p>
                <h2 style="color: #1E40AF; text-align: center;">{amount:,} Ks</h2>
                <p style="text-align: center; font-size: 0.9rem; color: #6B7280;">
                (Price per number: {PRICE_PER_NUMBER:,} Ks)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            note = st.text_area(
                "Note (Optional)",
                placeholder="Any special notes",
                height=50
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ **Submit Betting Entry**",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            errors = []
            
            is_name_valid, name_error = validate_name(customer_name)
            if not is_name_valid:
                errors.append(name_error)
            
            is_number_valid, number_error = validate_number(number)
            if not is_number_valid:
                errors.append(number_error)
            
            if quantity <= 0:
                errors.append("Quantity must be at least 1")
            
            # Check daily limit
            today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
            today_total = sum(entry['amount'] for entry in today_entries)
            daily_limit = user_info.get('daily_limit', 1000000)
            
            if today_total + amount > daily_limit:
                errors.append(f"Daily limit exceeded! Limit: {daily_limit:,} Ks, Today: {today_total:,} Ks")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create entry
                entry = {
                    'id': len(today_entries) + 1,
                    'time': format_myanmar_time(),
                    'customer': customer_name,
                    'number': number,
                    'quantity': quantity,
                    'amount': amount,
                    'winning_number': winning_number if winning_number else '',
                    'status': 'Pending',
                    'note': note if note else ''
                }
                
                # Add to today's entries
                if st.session_state.current_user not in st.session_state.today_entries:
                    st.session_state.today_entries[st.session_state.current_user] = []
                st.session_state.today_entries[st.session_state.current_user].append(entry)
                
                st.success(f"✅ Entry submitted successfully! Amount: {amount:,} Ks")
                log_activity("2D Entry", f"Added: {number} for {customer_name}")
                st.balloons()
                time.sleep(0.5)
                st.rerun()

def render_sheet_configuration():
    """Sheet configuration for agents"""
    st.markdown("""
    <div class="info-box">
    <h3>📋 Google Sheets Configuration Required</h3>
    <p>To use the 2D Betting System, please configure your Google Sheets URL.</p>
    <p>Contact your administrator to get your Google Sheets URL.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("sheet_config_form"):
        sheet_url = st.text_input(
            "Google Sheets URL *",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Your personal Google Sheets URL"
        )
        
        if st.form_submit_button("💾 Save Configuration", use_container_width=True):
            if sheet_url:
                st.session_state.user_configs[st.session_state.current_user] = {
                    'sheet_url': sheet_url,
                    'script_url': ''
                }
                
                # Update in users_db
                if st.session_state.current_user in st.session_state.users_db:
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                
                st.success("✅ Configuration saved successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Please enter Google Sheets URL")

def render_today_entries():
    """Display today's entries for agents"""
    st.markdown('<h1 class="main-title">📋 Today\'s Betting Entries</h1>', unsafe_allow_html=True)
    
    today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
    
    if not today_entries:
        st.info("No entries for today.")
        return
    
    # Summary stats
    total_quantity = sum(entry['quantity'] for entry in today_entries)
    total_amount = sum(entry['amount'] for entry in today_entries)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries", len(today_entries))
    with col2:
        st.metric("Total Quantity", total_quantity)
    with col3:
        st.metric("Total Amount", f"{total_amount:,} Ks")
    
    st.divider()
    
    # Entries list with edit/delete
    for i, entry in enumerate(today_entries):
        with st.expander(f"#{i+1} - {entry['customer']} ({entry['number']}) - {entry['amount']:,} Ks"):
            col_info, col_actions = st.columns([3, 1])
            
            with col_info:
                st.write(f"**Time:** {entry['time']}")
                st.write(f"**Customer:** {entry['customer']}")
                st.write(f"**Number:** {entry['number']}")
                st.write(f"**Quantity:** {entry['quantity']}")
                st.write(f"**Amount:** {entry['amount']:,} Ks")
                if entry['winning_number']:
                    st.write(f"**Winning Number:** {entry['winning_number']}")
                st.write(f"**Status:** {entry['status']}")
                if entry['note']:
                    st.write(f"**Note:** {entry['note']}")
            
            with col_actions:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.editing_entry = i
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    today_entries.pop(i)
                    st.success("✅ Entry deleted successfully!")
                    log_activity("Delete Entry", f"Deleted entry #{i+1}")
                    time.sleep(1)
                    st.rerun()
    
    # Edit form
    if 'editing_entry' in st.session_state:
        entry_index = st.session_state.editing_entry
        if entry_index < len(today_entries):
            entry = today_entries[entry_index]
            
            st.markdown("---")
            st.markdown("### ✏️ Edit Entry")
            
            with st.form(f"edit_form_{entry_index}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edited_customer = st.text_input("Customer Name", value=entry['customer'])
                    edited_number = st.text_input("Number", value=entry['number'])
                    edited_winning = st.text_input("Winning Number", value=entry.get('winning_number', ''))
                
                with col2:
                    edited_quantity = st.number_input("Quantity", min_value=1, value=entry['quantity'])
                    edited_status = st.selectbox(
                        "Status",
                        ["Pending", "Won", "Lost", "Paid"],
                        index=["Pending", "Won", "Lost", "Paid"].index(entry['status'])
                    )
                    edited_note = st.text_area("Note", value=entry.get('note', ''))
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        today_entries[entry_index]['customer'] = edited_customer
                        today_entries[entry_index]['number'] = edited_number
                        today_entries[entry_index]['quantity'] = edited_quantity
                        today_entries[entry_index]['amount'] = calculate_amount(edited_number, edited_quantity)
                        today_entries[entry_index]['winning_number'] = edited_winning
                        today_entries[entry_index]['status'] = edited_status
                        today_entries[entry_index]['note'] = edited_note
                        
                        del st.session_state.editing_entry
                        st.success("✅ Entry updated successfully!")
                        log_activity("Edit Entry", f"Edited entry #{entry_index+1}")
                        time.sleep(1)
                        st.rerun()
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        del st.session_state.editing_entry
                        st.rerun()
    
    # Clear all entries button
    st.divider()
    if st.button("🗑️ Clear All Today's Entries", type="secondary"):
        st.warning("This will delete ALL today's entries. Are you sure?")
        if st.checkbox("Yes, delete all entries"):
            st.session_state.today_entries[st.session_state.current_user] = []
            st.success("✅ All entries cleared successfully!")
            log_activity("Clear All Entries", "Cleared all today's entries")
            time.sleep(1)
            st.rerun()

def render_agent_settings():
    """Agent settings"""
    st.markdown('<h1 class="main-title">⚙️ Agent Settings</h1>', unsafe_allow_html=True)
    
    user_info = st.session_state.users_db[st.session_state.current_user]
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    tab1, tab2 = st.tabs(["🔗 Google Sheets", "👤 Profile"])
    
    with tab1:
        with st.form("agent_sheets_form"):
            st.markdown("### 🔗 Google Sheets Configuration")
            
            sheet_url = st.text_input(
                "Google Sheets URL",
                value=user_config.get('sheet_url', ''),
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                if sheet_url:
                    st.session_state.user_configs[st.session_state.current_user] = {
                        'sheet_url': sheet_url,
                        'script_url': ''
                    }
                    
                    # Update in users_db
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                    
                    st.success("✅ Google Sheets settings saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter Google Sheets URL")
    
    with tab2:
        with st.form("agent_profile_form"):
            st.markdown("### 👤 Profile Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", value=user_info['name'])
                email = st.text_input("Email", value=user_info.get('email', ''))
            
            with col2:
                new_password = st.text_input(
                    "New Password",
                    type="password",
                    placeholder="Enter new password (optional)"
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm new password"
                )
            
            if st.form_submit_button("💾 Update Profile", use_container_width=True):
                if new_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        update_data = {
                            'name': name,
                            'email': email,
                            'password': new_password
                        }
                else:
                    update_data = {
                        'name': name,
                        'email': email
                    }
                
                success, message = update_user_info(st.session_state.current_user, **update_data)
                
                if success:
                    st.success("✅ Profile updated successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

# ==================== MAIN APP ====================
def main():
    """Main application"""
    st.set_page_config(
        page_title="2D Betting System",
        page_icon="🎰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        render_login_page()
    else:
        # Route based on user role
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
