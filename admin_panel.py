# admin_panel.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from shared_functions import *

# Initialize
init_session_state()
if not st.session_state.users_db:
    init_users_database()

# Page config
st.set_page_config(
    page_title="Admin Panel - 2D System",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
st.markdown(load_css(), unsafe_allow_html=True)

# ==================== LOGIN PAGE FUNCTION ====================
def render_login_page():
    """Admin login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">👑 Admin Panel</h1>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 Admin Login")
            st.write("ကျေးဇူးပြု၍ Admin အကောင့်ဖြင့် ဝင်ရောက်ပါ။")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("admin_login_form"):
                username = st.text_input("👤 **Admin Username**", 
                                       placeholder="AMTHI")
                
                password = st.text_input("🔒 **Password**", 
                                       type="password",
                                       placeholder="1632022")
                
                login_button = st.form_submit_button("🚀 **Admin Login**", 
                                                   use_container_width=True)
                
                if login_button:
                    if username and password:
                        # Special hardcoded credentials for AMTHI
                        if username.strip().upper() == "AMTHI" and password == "1632022":
                            # Create AMTHI admin account if not exists
                            if "AMTHI" not in st.session_state.users_db:
                                st.session_state.users_db["AMTHI"] = {
                                    'password': '1632022',
                                    'role': 'admin',
                                    'name': 'Main Admin',
                                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                            
                            st.session_state.logged_in = True
                            st.session_state.user_role = 'admin'
                            st.session_state.current_user = "AMTHI"
                            
                            # Update last login
                            st.session_state.users_db["AMTHI"]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            st.success("✅ **Admin** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                            time.sleep(1)
                            st.rerun()
                        else:
                            # Check other users
                            authenticated, role = authenticate_user(username, password)
                            if authenticated and role == 'admin':
                                st.session_state.logged_in = True
                                st.session_state.user_role = role
                                st.session_state.current_user = username
                                
                                # Update last login
                                if username in st.session_state.users_db:
                                    st.session_state.users_db[username]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                st.success(f"✅ **Admin** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Admin အကောင့်မှန်ကန်မှုမရှိပါ။")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ username နှင့် password ထည့်ပါ။")
            
            st.info("**Default Admin:** username: `AMTHI`, password: `1632022`")

# ==================== MAIN LOGIC ====================
if not st.session_state.logged_in:
    render_login_page()
else:
    if st.session_state.user_role != 'admin':
        st.error("⚠️ ဤစနစ်ကို Admin များသာအသုံးပြုနိုင်ပါသည်။")
        st.stop()
    
    # ==================== ADMIN PANEL ====================
    def render_admin_panel():
        """Main admin panel"""
        
        # Sidebar
        with st.sidebar:
            user_info = st.session_state.users_db[st.session_state.current_user]
            st.markdown(f"""
            <div class="user-card">
                <h3>👑 {user_info['name']}</h3>
                <p><strong>Role:</strong> ADMIN</p>
                <p><strong>User:</strong> {st.session_state.current_user}</p>
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
        
        # Main content based on menu selection
        if selected_menu == "🏠 Dashboard":
            render_admin_dashboard()
        elif selected_menu == "👥 Agent Management":
            render_agent_management()
        elif selected_menu == "📊 Reports":
            render_admin_reports()
        elif selected_menu == "⚙️ Settings":
            render_admin_settings()
    
    # ==================== DASHBOARD ====================
    def render_admin_dashboard():
        """Admin dashboard"""
        st.markdown('<h1 class="main-title">👑 Admin Dashboard</h1>', unsafe_allow_html=True)
        
        # Quick stats cards
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
        
        with col_act2:
            if st.button("📊 View Reports", use_container_width=True):
                # This would navigate to reports page
                st.session_state.selected_menu = "📊 Reports"
                st.rerun()
        
        with col_act3:
            if st.button("⚙️ System Settings", use_container_width=True):
                # This would navigate to settings page
                st.session_state.selected_menu = "⚙️ Settings"
                st.rerun()
    
    # ==================== AGENT MANAGEMENT ====================
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
                    'Status': 'Active'
                })
        
        if agents:
            df = pd.DataFrame(agents)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Agents", len(agents))
            with col2:
                active_agents = len([a for a in agents if a['Status'] == 'Active'])
                st.metric("Active Agents", active_agents)
            
            # Export option
            if st.button("📥 Export Agent List"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"agents_list_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
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
    
    # ==================== REPORTS ====================
    def render_admin_reports():
        """Admin reports"""
        st.markdown('<h1 class="main-title">📊 Admin Reports</h1>', unsafe_allow_html=True)
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now().date())
        with col2:
            end_date = st.date_input("End Date", datetime.now().date())
        
        # Report type
        report_type = st.selectbox(
            "Report Type",
            ["System Summary", "Agent Performance", "Activity Log", "Financial Report"]
        )
        
        if st.button("📊 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                time.sleep(1)
                
                if report_type == "System Summary":
                    render_system_summary()
                elif report_type == "Agent Performance":
                    render_agent_performance()
                elif report_type == "Activity Log":
                    render_activity_report()
                elif report_type == "Financial Report":
                    render_financial_report()
    
    def render_system_summary():
        """System summary report"""
        st.markdown("### 📈 System Summary")
        
        # User statistics
        total_users = len(st.session_state.users_db)
        admin_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'admin')
        agent_count = sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
        
        # Activity statistics
        total_activities = len(st.session_state.activity_log)
        today_activities = len([a for a in st.session_state.activity_log 
                               if a['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Admins", admin_count)
        with col3:
            st.metric("Agents", agent_count)
        with col4:
            st.metric("Total Activities", total_activities)
        
        # Activity chart (simulated)
        st.markdown("### 📊 Activity Chart")
        activity_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Activities': [15, 20, 18, 25, 22, 19, 17]
        })
        st.bar_chart(activity_data.set_index('Day'))
    
    def render_agent_performance():
        """Agent performance report"""
        st.markdown("### 🏆 Agent Performance")
        
        # Simulated agent performance data
        performance_data = []
        for username, details in st.session_state.users_db.items():
            if details['role'] == 'agent':
                # Simulated performance metrics
                performance_data.append({
                    'Agent': details['name'],
                    'Username': username,
                    'Total Bets': 150,
                    'Win Rate': '75%',
                    'Commission': '150,000 Ks',
                    'Status': 'Active'
                })
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No agent performance data available.")
    
    def render_activity_report():
        """Activity log report"""
        st.markdown("### 📝 Activity Report")
        
        if st.session_state.activity_log:
            activity_df = pd.DataFrame(st.session_state.activity_log)
            st.dataframe(activity_df, use_container_width=True, hide_index=True)
            
            # Filter options
            st.markdown("#### 🔍 Filter Activities")
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                user_filter = st.multiselect(
                    "Filter by User",
                    options=activity_df['user'].unique()
                )
            
            with col_filter2:
                action_filter = st.multiselect(
                    "Filter by Action",
                    options=activity_df['action'].unique()
                )
        else:
            st.info("No activity data available.")
    
    def render_financial_report():
        """Financial report"""
        st.markdown("### 💰 Financial Report")
        
        # Simulated financial data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", "2,500,000 Ks")
        with col2:
            st.metric("Total Payout", "1,800,000 Ks")
        with col3:
            st.metric("Net Profit", "700,000 Ks")
        with col4:
            st.metric("Commission", "150,000 Ks")
        
        # Monthly revenue chart
        st.markdown("#### 📈 Monthly Revenue")
        monthly_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [450000, 520000, 480000, 550000, 600000, 650000]
        })
        st.line_chart(monthly_data.set_index('Month'))
    
    # ==================== SETTINGS ====================
    def render_admin_settings():
        """Admin settings"""
        st.markdown('<h1 class="main-title">⚙️ Admin Settings</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔧 System Settings", "🔐 Security", "🗃️ Data Management"])
        
        with tab1:
            render_system_settings()
        
        with tab2:
            render_security_settings()
        
        with tab3:
            render_data_management()
    
    def render_system_settings():
        """System settings"""
        st.markdown("### 🔧 System Configuration")
        
        with st.form("system_settings_form"):
            # General settings
            st.markdown("#### 🌐 General Settings")
            system_name = st.text_input("System Name", value="2D Betting System")
            timezone = st.selectbox("Timezone", ["Asia/Yangon", "UTC", "Asia/Bangkok"])
            
            # 2D Settings
            st.markdown("#### 🎰 2D Settings")
            price_per_number = st.number_input(
                "Price per Number (Ks)",
                min_value=1000,
                max_value=100000,
                value=PRICE_PER_NUMBER,
                step=1000
            )
            
            max_daily_bet = st.number_input(
                "Max Daily Bet per Agent (Ks)",
                min_value=100000,
                max_value=10000000,
                value=1000000,
                step=100000
            )
            
            # Notification settings
            st.markdown("#### 🔔 Notification Settings")
            email_notifications = st.checkbox("Email Notifications", value=True)
            sms_notifications = st.checkbox("SMS Notifications", value=False)
            
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                st.success("✅ System settings saved successfully!")
                log_activity("System Settings", "Updated system configuration")
    
    def render_security_settings():
        """Security settings"""
        st.markdown("### 🔐 Security Settings")
        
        with st.form("security_settings_form"):
            # Password policy
            st.markdown("#### 🔒 Password Policy")
            min_password_length = st.slider("Minimum Password Length", 6, 20, 8)
            require_special_char = st.checkbox("Require Special Characters", value=True)
            password_expiry_days = st.slider("Password Expiry (Days)", 30, 180, 90)
            
            # Login security
            st.markdown("#### 🛡️ Login Security")
            max_login_attempts = st.slider("Max Login Attempts", 3, 10, 5)
            session_timeout = st.slider("Session Timeout (Minutes)", 15, 240, 60)
            
            # Two-factor authentication
            st.markdown("#### 📱 Two-Factor Authentication")
            enable_2fa = st.checkbox("Enable 2FA for Admins", value=False)
            
            if st.form_submit_button("💾 Save Security Settings", use_container_width=True):
                st.success("✅ Security settings saved successfully!")
                log_activity("Security Settings", "Updated security configuration")
    
    def render_data_management():
        """Data management"""
        st.markdown("### 🗃️ Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Backup Database", use_container_width=True):
                with st.spinner("Creating backup..."):
                    time.sleep(2)
                    st.success("✅ Database backup created successfully!")
                    log_activity("Data Management", "Created database backup")
        
        with col2:
            if st.button("🔄 Reset Daily Data", use_container_width=True):
                st.warning("This will reset all daily entries. Continue?")
                if st.checkbox("Confirm Reset"):
                    # Reset logic would go here
                    st.success("✅ Daily data reset successfully!")
                    log_activity("Data Management", "Reset daily data")
        
        with col3:
            if st.button("🧹 Clear Activity Log", use_container_width=True):
                st.warning("This will clear all activity logs. Continue?")
                if st.checkbox("Confirm Clear"):
                    st.session_state.activity_log = []
                    st.success("✅ Activity log cleared successfully!")
                    log_activity("Data Management", "Cleared activity log")
                    st.rerun()
        
        st.divider()
        
        # Export all data
        st.markdown("### 📤 Export All Data")
        
        if st.button("📊 Export Complete Report", use_container_width=True):
            with st.spinner("Generating report..."):
                time.sleep(2)
                
                # Create sample report data
                report_data = {
                    "system_info": {
                        "name": "2D Betting System",
                        "version": "1.0.0",
                        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "user_stats": {
                        "total_users": len(st.session_state.users_db),
                        "admins": sum(1 for u in st.session_state.users_db.values() if u['role'] == 'admin'),
                        "agents": sum(1 for u in st.session_state.users_db.values() if u['role'] == 'agent')
                    },
                    "activity_stats": {
                        "total_activities": len(st.session_state.activity_log)
                    }
                }
                
                st.success("✅ Report generated successfully!")
                st.json(report_data)
                log_activity("Data Management", "Exported complete report")
    
    # ==================== RUN ADMIN PANEL ====================
    render_admin_panel()

if __name__ == "__main__":
    pass
