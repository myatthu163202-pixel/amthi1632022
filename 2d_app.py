# 2d_app.py
import streamlit as st
import pandas as pd
from shared_functions import *

# Initialize session state for 2D app
if 'today_entries' not in st.session_state:
    st.session_state.today_entries = {}
if 'user_configs' not in st.session_state:
    st.session_state.user_configs = {}
if 'hidden_sections' not in st.session_state:
    st.session_state.hidden_sections = {}
if 'google_sheets' not in st.session_state:
    st.session_state.google_sheets = {}
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = get_myanmar_time().strftime('%Y-%m-%d')

# Initialize main session state
init_session_state()
if not st.session_state.users_db:
    init_users_database()

# Page config
st.set_page_config(
    page_title="2D Betting System",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
st.markdown(load_css(), unsafe_allow_html=True)

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    render_2d_login_page()
else:
    # Check if user is agent
    if st.session_state.user_role != 'agent':
        st.error("⚠️ ဤစနစ်ကို Agent များသာအသုံးပြုနိုင်ပါသည်။")
        st.stop()
    
    render_2d_app()

# ==================== 2D LOGIN PAGE ====================
def render_2d_login_page():
    """2D app login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">🎰 2D Betting System</h1>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🔐 Agent Login")
            st.write("ကျေးဇူးပြု၍ Agent အကောင့်ဖြင့် ဝင်ရောက်ပါ။")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("2d_login_form"):
                username = st.text_input("👤 **Agent Username**", 
                                       placeholder="agent1")
                
                password = st.text_input("🔒 **Password**", 
                                       type="password",
                                       placeholder="agent123")
                
                login_button = st.form_submit_button("🚀 **Agent Login**", 
                                                   use_container_width=True)
                
                if login_button:
                    if username and password:
                        authenticated, role = authenticate_user(username, password)
                        if authenticated and role == 'agent':
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.current_user = username
                            
                            # Initialize user data
                            if username not in st.session_state.today_entries:
                                st.session_state.today_entries[username] = []
                            if username not in st.session_state.user_configs:
                                st.session_state.user_configs[username] = {
                                    'sheet_url': st.session_state.users_db.get(username, {}).get('sheet_url', ''),
                                    'script_url': ''
                                }
                            
                            st.success(f"✅ **Agent** အနေနဲ့ ဝင်ရောက်ပြီးပါပြီ။")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Agent အကောင့်မှန်ကန်မှုမရှိပါ။")
                    else:
                        st.warning("⚠ ကျေးဇူးပြု၍ username နှင့် password ထည့်ပါ။")
            
            st.info("**Agent Credentials:** username: `agent1`, password: `agent123`")

# ==================== 2D APP ====================
def render_2d_app():
    """Main 2D application"""
    
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
        total_amount = sum(entry['amount'] for entry in today_entries)
        
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
        render_2d_settings()

def render_number_entry():
    """Number entry form"""
    st.markdown('<h1 class="main-title">🎯 Enter 2D/3D Numbers</h1>', unsafe_allow_html=True)
    
    # Check if user has sheet configured
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    if not user_config.get('sheet_url'):
        render_sheet_configuration()
        return
    
    # Hide/show toggle
    col_hide, col_info = st.columns([1, 4])
    with col_hide:
        if st.button("🙈 Hide", key="hide_entry_form"):
            st.session_state.hidden_sections['entry_form'] = True
            st.rerun()
    
    if st.session_state.hidden_sections.get('entry_form', False):
        if st.button("👁️ Show", key="show_entry_form"):
            st.session_state.hidden_sections['entry_form'] = False
            st.rerun()
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
            "✅ **Submit Betting Entry** (Click this button only)",
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
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create entry
                entry = {
                    'id': len(st.session_state.today_entries.get(st.session_state.current_user, [])) + 1,
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
                st.session_state.today_entries[st.session_state.current_user].append(entry)
                
                # For demo, just show success message
                # In real app, this would save to Google Sheets
                st.success(f"✅ Entry submitted successfully! Amount: {amount:,} Ks")
                log_activity("2D Entry", f"Added: {number} for {customer_name}")
                st.balloons()

def render_sheet_configuration():
    """Sheet configuration for first-time users"""
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
                
                # Also update in users_db
                if st.session_state.current_user in st.session_state.users_db:
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                
                st.success("✅ Configuration saved successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Please enter Google Sheets URL")

def render_today_entries():
    """Today's entries display"""
    st.markdown('<h1 class="main-title">📋 Today\'s Betting Entries</h1>', unsafe_allow_html=True)
    
    # Hide/show toggle
    if st.button("🙈 Hide This Section", key="hide_entries"):
        st.session_state.hidden_sections['entries'] = True
        st.rerun()
    
    if st.session_state.hidden_sections.get('entries', False):
        if st.button("👁️ Show This Section", key="show_entries"):
            st.session_state.hidden_sections['entries'] = False
            st.rerun()
        return
    
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
    
    # Entries list
    st.markdown("### 📝 Entries List")
    
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

def render_2d_settings():
    """2D app settings"""
    st.markdown('<h1 class="main-title">⚙️ Agent Settings</h1>', unsafe_allow_html=True)
    
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    user_info = st.session_state.users_db[st.session_state.current_user]
    
    tab1, tab2 = st.tabs(["🔗 Google Sheets", "👤 Profile"])
    
    with tab1:
        render_sheets_settings()
    
    with tab2:
        render_profile_settings()

def render_sheets_settings():
    """Google Sheets settings"""
    user_config = st.session_state.user_configs.get(st.session_state.current_user, {})
    
    with st.form("sheets_settings_form"):
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
                if st.session_state.current_user in st.session_state.users_db:
                    st.session_state.users_db[st.session_state.current_user]['sheet_url'] = sheet_url
                
                st.success("✅ Google Sheets settings saved successfully!")
                log_activity("Update Settings", "Updated Google Sheets URL")
                st.rerun()
            else:
                st.error("❌ Please enter Google Sheets URL")
    
    st.divider()
    
    # Data management
    st.markdown("### 🗃️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Today's Data", use_container_width=True):
            today_entries = st.session_state.today_entries.get(st.session_state.current_user, [])
            if today_entries:
                df = pd.DataFrame(today_entries)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                
                today_date = get_myanmar_time().strftime('%Y-%m-%d')
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"2d_entries_{st.session_state.current_user}_{today_date}.csv",
                    mime="text/csv"
                )
                log_activity("Export Data", f"Exported {len(today_entries)} entries")
            else:
                st.info("No data to export.")
    
    with col2:
        if st.button("🔄 Clear Today's Data", use_container_width=True):
            st.warning("This will clear all today's entries. Continue?")
            if st.checkbox("Confirm Clear"):
                st.session_state.today_entries[st.session_state.current_user] = []
                st.success("✅ Today's data cleared successfully!")
                log_activity("Clear Data", "Cleared all today's entries")
                time.sleep(1)
                st.rerun()

def render_profile_settings():
    """Profile settings"""
    user_info = st.session_state.users_db[st.session_state.current_user]
    
    with st.form("profile_settings_form"):
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

if __name__ == "__main__":
    pass
