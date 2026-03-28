import streamlit as st
import os

st.set_page_config(
    page_title="DataLens",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session state bootstrap ───────────────────────────────────────────────────
from utils.session_utils import initialize_session_state, get_theme, toggle_theme
initialize_session_state()

# ── Hide sidebar chrome and Streamlit branding ───────────────────────────────
current_theme = get_theme()
is_light = current_theme == 'light'

# Theme colors
theme_bg = '#f8f9fa' if is_light else '#0f0f0f'
theme_text = '#212529' if is_light else '#e8e4dc'
theme_card = '#ffffff' if is_light else '#161616'
theme_border = '#dee2e6' if is_light else '#2a2a2a'
theme_accent = '#c9a84c'

st.markdown(f"""
    <style>
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebar"]        {{ display: none !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}
    #MainMenu {{ visibility: hidden; }}
    footer    {{ visibility: hidden; }}
    header    {{ visibility: hidden; }}
    
    /* Theme variables - override CSS file with !important */
    :root {{
        --bg: {theme_bg} !important;
        --text: {theme_text} !important;
        --card: {theme_card} !important;
        --border: {theme_border} !important;
        --accent: {theme_accent} !important;
        --bg-card: {theme_card} !important;
        --bg-card-2: {'#f1f3f5' if is_light else '#1d1d1d'} !important;
        --border-light: {'#ced4da' if is_light else '#333333'} !important;
        --text-muted: {'#6c757d' if is_light else '#7a7670'} !important;
        --text-dim: {'#adb5bd' if is_light else '#4a4845'} !important;
    }}
    
    /* Force text color everywhere in light mode */
    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
    }}
    
    /* Metric and data text - ensure visibility */
    [data-testid="stMetricValue"] {{
        color: var(--text) !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
    }}
    [data-testid="stMetricDelta"] {{
        color: var(--text) !important;
    }}
    
    /* Dataframe and table text */
    .stDataFrame, [data-testid="stTable"] {{
        color: var(--text) !important;
    }}
    .stDataFrame th, .stDataFrame td {{
        color: var(--text) !important;
    }}
    
    /* All text elements */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: var(--text) !important;
    }}
    
    /* Button text colors - aggressive fix for visibility */
    button[kind="primary"], .stButton button[kind="primary"] {{
        color: #212529 !important;
        background-color: var(--accent) !important;
        border: none !important;
    }}
    button[kind="secondary"], .stButton button[kind="secondary"] {{
        color: var(--text) !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
    }}
    
    /* Base button - ensure all buttons have visible text */
    .stButton > button {{
        color: var(--text) !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
    }}
    
    /* Override for button text content */
    .stButton button p, .stButton button span, .stButton button div {{
        color: var(--text) !important;
    }}
    
    /* Primary button text - always dark for contrast on accent */
    .stButton button[kind="primary"] p, 
    .stButton button[kind="primary"] span, 
    .stButton button[kind="primary"] div {{
        color: #212529 !important;
    }}
    
    /* Download buttons and special buttons */
    button[data-testid="baseButton-secondary"] {{
        color: var(--text) !important;
        background-color: var(--bg-card) !important;
    }}
    
    button[data-testid="baseButton-primary"] {{
        color: #212529 !important;
        background-color: var(--accent) !important;
    }}
    
    /* Spacing for Undo button in transformation log */
    .stButton {{
        margin-top: 8px !important;
    }}
    
    /* Footer padding - prevent elements sticking to bottom */
    .main .block-container {{
        padding-bottom: 4rem !important;
    }}
    
    /* Bottom spacing for last elements */
    div.element-container:last-child {{
        margin-bottom: 3rem !important;
    }}
    
    /* Streamlit widget labels */
    .stSelectbox label, .stMultiselect label, .stTextInput label, 
    .stNumberInput label, .stSlider label, .stRadio label {{
        color: var(--text) !important;
    }}
    
    /* Expander and tab text */
    .streamlit-expanderHeader {{
        color: var(--text) !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: var(--text) !important;
    }}
    
    /* Checkbox and radio text */
    .stCheckbox label, .stRadio label {{
        color: var(--text) !important;
    }}
    
    /* Success/info/warning messages */
    .stAlert {{
        color: var(--text) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ── Custom CSS ────────────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ── Page routing (session-based, no query params) ────────────────────────────
nav_items = [
    ("A", "Upload & Overview"),
    ("B", "Cleaning & Prep"),
    ("C", "Visualize"),
    ("D", "Export & Report"),
]

# Navigation callback
def nav_to(page):
    st.session_state['current_page'] = page
    st.rerun()

current_page = st.session_state.get('current_page', 'A')

# Build navigation HTML with buttons instead of links
nav_html = ""
for key, label in nav_items:
    active_class = "active" if current_page == key else ""
    nav_html += f'<button class="nav-btn {active_class}" onclick="handleNav(\'{key}\')">{label}</button>'

# Theme toggle button
theme_icon = "☀" if is_light else "☾"
theme_label = "Light" if is_light else "Dark"

st.markdown(f"""
<div class="navbar">
    <div class="navbar-brand">
        <span class="brand-icon">◈</span>
        <span class="brand-name">DataLens</span>
    </div>
    <div class="navbar-links">
        <div class="nav-container">
        </div>
    </div>
    <div class="navbar-actions">
    </div>
</div>
<div class="navbar-spacer"></div>
""", unsafe_allow_html=True)

# Use columns for navigation buttons to avoid new tabs
nav_cols = st.columns([1, 1, 1, 1, 0.4, 0.4])
with nav_cols[0]:
    if st.button("Upload & Overview", key="nav_btn_A", type="primary" if current_page == "A" else "secondary", use_container_width=True):
        nav_to("A")
with nav_cols[1]:
    if st.button("Cleaning & Prep", key="nav_btn_B", type="primary" if current_page == "B" else "secondary", use_container_width=True):
        nav_to("B")
with nav_cols[2]:
    if st.button("Visualize", key="nav_btn_C", type="primary" if current_page == "C" else "secondary", use_container_width=True):
        nav_to("C")
with nav_cols[3]:
    if st.button("Export & Report", key="nav_btn_D", type="primary" if current_page == "D" else "secondary", use_container_width=True):
        nav_to("D")
with nav_cols[4]:
    if st.button(f"{theme_icon}", key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

# Options dropdown in navbar
with nav_cols[5]:
    with st.popover("Options", use_container_width=True):
        st.subheader("Screen Recorder")
        
        # Screen recording instructions using Streamlit components only
        st.info("Record your demo using your OS built-in screen recorder:")
        
        tab1, tab2, tab3 = st.tabs(["Windows", "Mac", "Linux"])
        
        with tab1:
            st.markdown("""
            **Windows (Game Bar):**
            1. Press **Win + G** to open Game Bar
            2. Click the record button (or **Win + Alt + R**)
            3. Record your demo
            4. Press **Win + Alt + R** to stop
            5. Video saved to `Videos/Captures/`
            """)
            
        with tab2:
            st.markdown("""
            **Mac (Screenshot Toolbar):**
            1. Press **Cmd + Shift + 5**
            2. Click "Record Entire Screen" or "Record Selected Portion"
            3. Click "Record"
            4. Press **Cmd + Shift + 5** then "Stop" to end
            5. Video saved to Desktop
            """)
            
        with tab3:
            st.markdown("""
            **Linux:**
            1. Use **OBS Studio** (free, recommended)
            2. Or use **Kazam** / **SimpleScreenRecorder**
            3. Install via: `sudo apt install obs-studio`
            """)
        
        st.divider()
        
        st.write("**Alternative: Browser Extension**")
        st.markdown("""
        - Chrome: [Screencastify](https://www.screencastify.com/)
        - Firefox: [OBS Studio](https://obsproject.com/)
        """)
        
        st.divider()
        
        # Deployment Section with direct link
        st.subheader("Deploy")
        st.markdown("""
        **Streamlit Cloud:**
        """)
        
        # Direct deployment link
        st.link_button(
            "Deploy to Streamlit Cloud →",
            "https://share.streamlit.io/deploy",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("""
        **Quick Steps:**
        1. Push code to GitHub
        2. Click button above
        3. Connect your repo
        
        **Local:**
        ```
        streamlit run app.py
        ```
        """)
        
        if st.button("Copy Git Commands", key="copy_deploy"):
            deploy_text = """# Deploy to Streamlit Cloud
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/datalens.git
git push -u origin main

# Then click "Deploy to Streamlit Cloud" button"""
            st.code(deploy_text)
            st.success("Commands copied to clipboard!")

st.markdown("<hr style='margin: 0.5rem 0; border-color: var(--border);'>", unsafe_allow_html=True)

# ── Import and show pages ─────────────────────────────────────────────────────
from pages import page_a, page_b, page_c, page_d

page_map = {
    "A": page_a.show,
    "B": page_b.show,
    "C": page_c.show,
    "D": page_d.show,
}

page_fn = page_map.get(current_page, page_a.show)
page_fn()
