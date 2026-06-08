import streamlit as st

# Set page layout and clean browser tab title
st.set_page_config(
    page_title="Dirty Town Poker League - Maintenance", 
    page_icon="🃏", 
    layout="centered"
)

# =========================================================================
# 🎨 CUSTOM STYLE INJECTION (Premium Cardroom Dark Theme)
# =========================================================================
st.markdown(
    """
    <style>
    /* Hide default Streamlit headers, footers, and menus */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* Center layout elements vertically and style typography */
    .main-box {
        text-align: center;
        padding: 40px 20px;
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 165, 2, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-top: 40px;
    }
    .main-title {
        color: #ffa502 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 5px;
    }
    .subtitle {
        color: #a4b0be;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    .status-badge {
        background-color: rgba(231, 76, 60, 0.15);
        color: #ff7675;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 20px;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    .bulletin-box {
        background-color: rgba(46, 204, 113, 0.06);
        border: 1px solid rgba(46, 204, 113, 0.2);
        padding: 15px;
        border-radius: 8px;
        color: #2ed573;
        font-size: 0.95rem;
        margin-top: 25px;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 🎴 VISUAL LAYOUT RENDERING
# =========================================================================

# Main centered container card
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# Status indicator chip
st.markdown('<span class="status-badge">🛠️ Engine Upgrades In Progress</span>', unsafe_allow_html=True)

# Primary branding header
st.markdown('<h1 class="main-title">🏆 Dirty Town Poker League</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Official Season Analytics & Leaderboard Portal</p>', unsafe_allow_html=True)

st.markdown("---")

# Informative prose
st.write(
    "The data aggregation engine is currently offline for routine sandboxing and layout maintenance "
    "as we transition historical records and configure backend calculations for the upcoming league cycle."
)

# Notice block for the players
st.markdown(
    """
    <div class="bulletin-box">
        <strong>♠️ Season XLVIII Briefing:</strong><br>
        • Master player registry tables have been modernized to full-name matrices.<br>
        • Chronological scoring structures are locked in.<br>
        • Live data synchronization fields will return online shortly.
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# Standard minimalist footer notice
st.markdown("<br><p style='text-align: center; color: #747d8c; font-size: 0.8rem;'>For direct schedule inquiries or structure modifications, contact league administration.</p>", unsafe_allow_html=True)
