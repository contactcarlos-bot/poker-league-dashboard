import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import altair as alt

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

# =========================================================================
# 🔄 GLOBAL SESSION STATE INITS
# =========================================================================
if "temporary_walk_ins" not in st.session_state:
    st.session_state["temporary_walk_ins"] = []

# =========================================================================
# 🪓 JAVASCRIPT INJECTION: BREAKS IFRAME TO REMOVE FLOATING TOOLBARS
# =========================================================================
from streamlit.components.v1 import html
html(
    """
    <script>
    const parentDoc = window.parent.document;
    document.addEventListener("DOMContentLoaded", function() {
        parentDoc.querySelectorAll('[href*="streamlit.io"]').forEach(el => {
            const container = el.closest('div');
            if (container) container.style.display = 'none';
        });
        const viewerBadges = parentDoc.querySelectorAll('.viewerBadge, [data-testid="stViewerBadge"]');
        viewerBadges.forEach(badge => badge.style.display = 'none');
    });
    </script>
    """,
    height=0, width=0
)

# =========================================================================
# 🚨 IMPORTANT LEAGUE ANNOUNCEMENTS (TOP OF PAGE)
# =========================================================================
#st.success("🎉 **Note:** Please contact Todd in advance if you know you will not be able to attend a game. ")

# =========================================================================
# 🔄 DEFAULT SEASON INITIALIZATION (TOP OF PAGE)
# =========================================================================
if "active_season_choice" not in st.session_state:
    # Keep Season XLVIII as the default load-out choice for now
    st.session_state["active_season_choice"] = "Season XLVIII (Current)"

selected_season = st.session_state["active_season_choice"]

# Map choices to your Google Sheet tabs (Including the future Season XLIX)
if "Season XLIX" in selected_season:
    TARGET_WORKSHEET = "Form Responses S49"
    st.title("🏆 Dirty Town Poker League - Season XLIX")
elif "Season XLVIII" in selected_season:
    TARGET_WORKSHEET = "Form Responses S48"
    st.title("🏆 Dirty Town Poker League - Season XLVIII")
else:
    TARGET_WORKSHEET = "Form Responses 1"
    st.title("🏆 Dirty Town Poker League - Season XLVII")

# =========================================================================
# 🎨 CUSTOM CSS: PRECISE METRIC FONT SCALING & BRANDING REMOVAL
# =========================================================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* 🎡 Shrink text sizes inside the High Hand and Wheel Spin log tables */
    div[data-testid="stDataFrameCollapsedCell"] div,
    div[data-testid="stDataFrame"] table,
    .stDataFrame div[data-testid="styled-data-frame"] div {
        font-size: 0.78rem !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Make the subsection titles slightly sleeker to match */
    h3#high-hand-elite-logs, h3#ace-of-spades-wheel-spins {
        font-size: 1.1rem !important;
        color: #a4b0be !important;
        margin-top: 10px !important;
    }
    
    .stDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    .viewerBadge {display: none !important;}
    div[data-testid="stViewerBadge"] {display: none !important;}
    button[title="View source on GitHub"] {display: none !important;}
    
    div[data-testid="stDataFrame"] td, 
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] div {
        font-size: 0.88rem !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    div[data-testid="stMetricValue"] div, 
    div[data-testid="stMetricValue"] span {
        font-size: 1.3rem !important;
        letter-spacing: -0.01em;
        font-weight: 700 !important;
        color: #f1f2f6 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #a4b0be !important;
    }
    
    div[data-testid="stNotification"] {
        border-radius: 8px !important;
        border: 1px solid rgba(231, 76, 60, 0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 🔄 DYNAMIC REGISTRY LOADER
# =========================================================================
@st.cache_data(ttl=60)
def load_player_registry():
    """Loads the official player roster list directly from the Google Sheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        except Exception:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
        client = gspread.authorize(creds)
        workbook = client.open("Dirty Town Poker League Input (Responses)")
        reg_sheet = workbook.worksheet("Registry")
        records = reg_sheet.get_all_records()
        return [str(row["Full Name"]).strip() for row in records if row.get("Full Name")]
    except Exception:
        return ["Brian Cox", "Dustan Mulkey", "Mike Craft", "Jeff McCleave"]

PLAYER_REGISTRY = load_player_registry()

def calculate_poker_points(total_players, rank):
    """Looks up exact matrix points based on field size and rank placement."""
    buy_ins = int(total_players)
    rank = int(rank)
    LEAGUE_MATRIX = {
        6:  [371, 226, 156, 121, 110, 100], 7:  [460, 282, 195, 143, 119, 110, 100], 
        8:  [558, 343, 240, 174, 135, 118, 110, 100], 9:  [664, 410, 290, 213, 160, 132, 118, 110, 100],
        10: [777, 483, 344, 256, 193, 151, 129, 119, 111, 100], 11: [897, 560, 402, 303, 231, 178, 146, 128, 119, 111, 100],
        12: [1020, 642, 465, 353, 273, 212, 168, 142, 128, 119, 111, 100], 13: [1146, 728, 531, 406, 318, 249, 197, 161, 140, 128, 120, 111, 100],
        14: [1272, 820, 601, 463, 365, 290, 230, 185, 156, 138, 128, 120, 111, 100], 15: [1398, 915, 674, 524, 416, 334, 268, 215, 177, 153, 137, 128, 120, 111, 100],
        16: [1523, 1015, 750, 587, 469, 380, 308, 249, 203, 171, 150, 137, 128, 120, 111, 100], 17: [1649, 1120, 830, 652, 525, 428, 351, 286, 233, 194, 166, 149, 137, 128, 121, 111, 100],
        18: [1775, 1228, 912, 721, 584, 479, 396, 326, 268, 221, 187, 163, 147, 137, 129, 121, 112, 100], 19: [1900, 1340, 998, 792, 645, 532, 442, 368, 305, 252, 211, 181, 161, 147, 137, 129, 121, 112, 100],
        20: [2028, 1456, 1101, 866, 710, 588, 491, 413, 345, 287, 239, 203, 178, 158, 147, 137, 129, 121, 112, 100], 21: [2124, 1547, 1182, 934, 770, 642, 539, 456, 385, 322, 270, 227, 197, 174, 157, 147, 137, 129, 121, 112, 100],
        22: [2327, 1716, 1322, 1050, 867, 727, 612, 520, 442, 373, 313, 263, 224, 196, 174, 159, 149, 139, 131, 122, 113, 100], 23: [2428, 1813, 1409, 1126, 932, 786, 666, 567, 486, 413, 350, 295, 250, 217, 192, 171, 159, 148, 139, 131, 123, 113, 100],
        24: [2529, 1910, 1496, 1203, 999, 847, 721, 617, 531, 456, 388, 330, 280, 240, 211, 187, 169, 159, 148, 139, 131, 123, 113, 100], 25: [2630, 2008, 1584, 1282, 1066, 908, 777, 668, 577, 499, 429, 366, 312, 267, 232, 206, 184, 169, 158, 148, 140, 132, 123, 113, 100],
        26: [2732, 2106, 1673, 1362, 1136, 971, 835, 720, 624, 543, 470, 404, 347, 297, 256, 226, 202, 181, 168, 158, 148, 140, 132, 123, 113, 100], 27: [2833, 2204, 1763, 1443, 1206, 1034, 894, 774, 673, 588, 513, 444, 383, 329, 284, 248, 221, 197, 179, 168, 158, 148, 140, 132, 123, 113, 100],
        28: [2934, 2303, 1853, 1525, 1279, 1098, 953, 829, 724, 634, 556, 485, 420, 363, 314, 273, 241, 216, 194, 178, 168, 158, 148, 141, 132, 123, 113, 100], 29: [3035, 2402, 1944, 1608, 1352, 1164, 1014, 886, 775, 681, 600, 527, 459, 399, 346, 300, 263, 235, 211, 191, 178, 168, 157, 149, 141, 132, 124, 113, 100],
        30: [3137, 2500, 2035, 1692, 1427, 1231, 1076, 943, 828, 730, 645, 570, 500, 437, 380, 331, 289, 256, 230, 207, 189, 178, 167, 157, 149, 141, 133, 124, 113, 100]
    }
    return LEAGUE_MATRIX.get(buy_ins, [100])[rank - 1] if rank <= buy_ins else 100

global_workbook_instance = None

@st.cache_data(ttl=600)
def get_raw_form_responses(worksheet_name):
    global global_workbook_instance
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    except Exception:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    client = gspread.authorize(creds)
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    global_workbook_instance = workbook  
    sheet = workbook.worksheet(worksheet_name)
    return sheet.get_all_values()

if st.button("🔄 Sync Live Data Response Updates"):
    st.cache_data.clear()
    st.rerun()

base_sorted_leaderboard = pd.DataFrame()
leaderboard = pd.DataFrame()
df_history = pd.DataFrame()
last_game_date = None
cleaned_rows = []

# =========================================================================
# 💾 DATA COMPILATION & PARSING ENGINE (REGULAR SEASON ONLY)
# =========================================================================
try:
    raw_rows = get_raw_form_responses(TARGET_WORKSHEET)
    cleaned_rows = [r for r in raw_rows if any(cell.strip() for cell in r)]
    
    if len(cleaned_rows) <= 1:
        st.warning(f"No submissions found in your Google Form for {selected_season} yet!")
        leaderboard = pd.DataFrame(columns=["Player Name", "Total Points", "Games Played", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables", "Avg Points/Game", "Last Game Points"])
        df_history = pd.DataFrame(columns=["Date", "Player Name", "Position", "Points"])
        base_sorted_leaderboard = leaderboard
    else:
        parsed_history_records = []
        
        for row in cleaned_rows[1:]:
            game_date = str(row[1]).strip() if len(row) >= 3 else str(row[0]).strip()
            raw_standings_text = row[2] if len(row) >= 3 else row[1]
            
            raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
            if not raw_list:
                continue
                
            total_players = len(raw_list)
            for index, raw_player_input in enumerate(raw_list):
                # 🃏 Winner is on top row (index 0 -> position 1)
                position = index + 1
                points = calculate_poker_points(total_players, position)
                
                player_name = str(raw_player_input).strip().replace("\r", "").title()
                if " Mcc" in player_name:
                    player_name = player_name.replace(" Mcc", " McC")
                elif player_name.startswith("Mcc"):
                    player_name = "McC" + player_name[3:]
                
                parsed_history_records.append({
                    "Date": game_date.split()[0],
                    "Player Name": player_name, 
                    "Position": int(position), 
                    "Points": int(points)
                })
        
        df_history = pd.DataFrame(parsed_history_records)
        
        # -----------------------------------------------------------------
        # PODIUM & STATISTICS AGGREGATION ENGINE
        # -----------------------------------------------------------------
        df_history['True_Date'] = pd.to_datetime(df_history['Date'], errors='coerce')
        unique_dates_sorted = sorted(df_history["True_Date"].dropna().unique())
        
        if unique_dates_sorted:
            last_game_date_raw = unique_dates_sorted[-1]
            last_game_date = last_game_date_raw.strftime('%Y-%m-%d')
            
            df_last_game = df_history[df_history["True_Date"] == last_game_date_raw][["Player Name", "Points"]].copy()
            df_last_game.columns = ["Player Name", "Last Game Points"]
        else:
            df_last_game = pd.DataFrame(columns=["Player Name", "Last Game Points"])

        df_history["🥇 1st"] = df_history["Position"].apply(lambda x: 1 if x == 1 else 0)
        df_history["🥈 2nd"] = df_history["Position"].apply(lambda x: 1 if x == 2 else 0)
        df_history["🥉 3rd"] = df_history["Position"].apply(lambda x: 1 if x == 3 else 0)
        df_history["FT"] = df_history["Position"].apply(lambda x: 1 if x <= 10 else 0)
        
        leaderboard = df_history.groupby("Player Name").agg(
            Total_Points=("Points", "sum"),
            Games_Played=("Date", "count"),
            Wins=("🥇 1st", "sum"),
            Seconds=("🥈 2nd", "sum"),
            Thirds=("🥉 3rd", "sum"),
            Final_Tables=("FT", "sum")
        ).reset_index()
        
        leaderboard["Avg Points/Game"] = (leaderboard["Total_Points"] / leaderboard["Games_Played"]).round(1)
        
        leaderboard = pd.merge(leaderboard, df_last_game, on="Player Name", how="left")
        leaderboard["Last Game Points"] = leaderboard["Last Game Points"].fillna(0).astype(int)
        
        leaderboard.columns = ["Player Name", "Total Points", "Games Played", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables", "Avg Points/Game", "Last Game Points"]
        base_sorted_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        
        # -----------------------------------------------------------------
        # METRICS SHELF
        # -----------------------------------------------------------------
        if not base_sorted_leaderboard.empty:
            st.markdown("### 👑 Season Milestones & Management")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            current_leader = base_sorted_leaderboard.iloc[0]["Player Name"]
            
            win_sorted = leaderboard.sort_values(by="🥇 1st", ascending=False)
            win_boss = win_sorted.iloc[0]["Player Name"] if not win_sorted.empty else "N/A"
            win_count = win_sorted.iloc[0]["🥇 1st"] if not win_sorted.empty else 0
            
            with m_col1:
                st.metric("League Leader 🥇", current_leader, f"{base_sorted_leaderboard.iloc[0]['Total Points']} pts")
            with m_col2:
                st.metric("Championship Wins 🏆", win_boss, f"{win_count} Wins")
            with m_col3:
                st.metric("Commissioner 📋", "Michael Craft", "League Admin")
            with m_col4:
                # 🃏 ADDED: Vice-Commissioner role sitting at the end column
                st.metric("Co-Commissioner 💼", "Todd Kinsell", "League Admin")

except Exception as data_load_error:
    st.error(f"Could not load sheets backend database engine: {data_load_error}")

# =========================================================================
# 🏆 1. OVERALL SEASON RANKINGS LEADERBOARD (PRIMARY FOCUS)
# =========================================================================
if not base_sorted_leaderboard.empty:
    st.markdown("---")
    st.subheader("📋 Overall Season Rankings")
    
    display_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
    display_leaderboard.index = display_leaderboard.index + 1
    
    # 🔄 SWAPPED COLUMN ORDER: Placed 'Last Game Points' directly after 'Total Points'
    final_table_df = display_leaderboard[[
        "Player Name", "Total Points", "Last Game Points", 
        "Games Played", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables"
    ]]

    def highlight_last_game(val):
        return 'background-color: rgba(46, 204, 113, 0.15); font-weight: bold;' if val > 0 else ''

    def highlight_low_attendance(val):
        return 'background-color: rgba(231, 76, 60, 0.18); font-weight: bold; color: #ff7675;' if val <= 7 else ''

    styled_df = final_table_df.style\
        .map(highlight_last_game, subset=["Last Game Points"])\
        .map(highlight_low_attendance, subset=["Games Played"])
        
    st.dataframe(
        styled_df, 
        use_container_width=True,
        hide_index=False,
        column_config={
            "Player Name": st.column_config.TextColumn("♠️ Player"),
            "Total Points": st.column_config.NumberColumn("🔥 Total Points", format="%d pts"),
            "Last Game Points": st.column_config.NumberColumn("💥 Last Game", format="+%d"),
            "🥇 1st": st.column_config.NumberColumn(alignment="center"),
            "🥈 2nd": st.column_config.NumberColumn(alignment="center"),
            "🥉 3rd": st.column_config.NumberColumn(alignment="center"),
            "Final Tables": st.column_config.NumberColumn("🃏 FT", alignment="center"),  # 🪓 ABBREVIATED TO FT
            "Games Played": st.column_config.NumberColumn("🏃‍♂️ Played", alignment="center")
        }
    )

# =========================================================================
# 🏅 2. POST-SEASON CHAMPIONSHIP SERIES BRACKET
# =========================================================================
st.markdown("---")
st.subheader("🏁 Post-Season Championship Series Bracket")

# 1️⃣ ARCHIVED SEASON XLVII VIEW
if "Season XLVII (Archived)" in selected_season:
    # 👑 CUSTOM CHAMPION PODIUM DISPLAY
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(255, 165, 0, 0.12) 0%, rgba(0, 0, 0, 0.4) 100%);
            border: 2px solid #ffa502;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        ">
            <span style="font-size: 2.5rem;">👑</span>
            <h2 style="color: #ffa502; margin: 5px 0 0 0; font-weight: 800; letter-spacing: 0.03em;">SEASON XLVII GRAND CHAMPION</h2>
            <p style="color: #f1f2f6; font-size: 1.6rem; font-weight: 700; margin: 10px 0 5px 0;">🥇 Dustan Mulkey</p>
            <p style="color: #a4b0be; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">Tournament of Champions Victor</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.success("""
        **🛰️ Saturday Satellite Match**
        * **Date Completed:** May 30, 2026 🏁
        * **Winner:** **Rob Christian** 🎫
        * **Result:** Formally locked down TOC Seed #10
        """)
    with b_col2:
        st.success("""
        **👑 Tournament of Champions Standings**
        * **Date Completed:** June 6, 2026 🏆
        * **Grand Champion 🎉:** Dustan Mulkey
        * **2nd Place 🥈:** Ryan Mulkey
        * **3rd Place 🥉:** Jeff McCleave
        * **4th Place:** Nick Rouhani
        * **5th Place:** Mike Craft
        * **6th Place:** Brian Cox
        * **7th Place:** John Alvenus
        * **8th Place:** Rob Christian
        * **9th Place:** Jim Qualizza
        * **10th Place:** David Lee
        """)

# 2️⃣ UPCOMING FUTURE SEASON XLIX VIEW
elif "Season XLIX" in selected_season:
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.warning("""
        **🛰️ Post-Season Satellite**
        * **Date Scheduled:** To Be Determined (TBD) 📅
        * **Time:** TBD ⏰
        * **Status:** Staged for Future Season
        """)
    with b_col2:
        st.warning("""
        **👑 Tournament of Champions (TOC)**
        * **Date Scheduled:** To Be Determined (TBD) 🏆
        * **Timeline:** Schedule details will lock in once the Season XLIX calendar is officially released. 🍔🃏
        * **Status:** Staged for Future Season
        """)

# 3️⃣ CURRENT ACTIVE SEASON XLVIII VIEW (DEFAULT FALLBACK)
else:
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.info("""
        **🛰️ Upcoming Post-Season Satellite**
        * **Date Scheduled:** Saturday, September 26, 2026 📅
        * **Time:** 4:00 PM EST ⏰
        * **Status:** Open Qualifier Frame
        * **Requirement:** 8+ season games played
        """)
    with b_col2:
        st.info("""
        **👑 Tournament of Champions (TOC)**
        * **Date Scheduled:** Saturday, October 3, 2026 🏆
        * **Timeline:** • Lunch Served: 12:15 PM 🍔
          • Cards in the Air: 1:00 PM 🃏
        * **Status:** Awaiting Qualified Field
        """)

# =========================================================================
# 🎉 NIGHTLY BOUNTIES & WILDCARDS
# =========================================================================
if len(cleaned_rows) > 1:
    st.markdown("---")
    st.subheader("🎉 Nightly Specials & Special Bounties")
    
    high_hand_records = []
    spin_wheel_records = []
    
    for row in cleaned_rows[1:]:
        game_date = str(row[1]).strip().split()[0] if len(row) >= 3 else str(row[0]).strip().split()[0]
        
        if len(row) >= 4 and row[3].strip():
            raw_text = row[3].strip()
            for line in raw_text.split('\n'):
                if not line.strip(): continue
                if "-" in line:
                    parts = line.split("-", 1)
                    input_name = parts[0].strip().title()
                    prize_text = parts[1].strip()
                else:
                    input_name = line.strip().title()
                    prize_text = "Prize Logged"
                high_hand_records.append({"Date": game_date, "Player Name": input_name, "Prize Won": prize_text})
            
        if len(row) >= 5 and row[4].strip():
            raw_text = row[4].strip()
            for line in raw_text.split('\n'):
                if not line.strip(): continue
                if "-" in line:
                    parts = line.split("-", 1)
                    input_name = parts[0].strip().title()
                    prize_text = parts[1].strip()
                else:
                    input_name = line.strip().title()
                    prize_text = "Prize Logged"
                spin_wheel_records.append({"Date": game_date, "Player Name": input_name, "Prize Won": prize_text})
            
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        st.markdown("### 🪵 High Hand Elite Logs")
        if high_hand_records:
            df_hh = pd.DataFrame(high_hand_records).sort_values(by="Date", ascending=False)
            st.dataframe(df_hh, use_container_width=True, hide_index=True)
        else:
            st.info("No High Hand records logged yet for this season.")
            
    with w_col2:
        st.markdown("### 🎡 Ace of Spades Wheel Spins")
        if spin_wheel_records:
            df_sw = pd.DataFrame(spin_wheel_records).sort_values(by="Date", ascending=False)
            st.dataframe(df_sw, use_container_width=True, hide_index=True)
        else:
            st.info("No Spade Ace wheel draws tracked yet for this season.")

# -----------------------------------------------------------------
# ⚙️ DASHBOARD CONTROLS
# -----------------------------------------------------------------
if not df_history.empty and last_game_date:
    st.markdown("---")
    st.markdown("### ⚙️ Dashboard Controls")
    
    search_player_placeholder = "-- View All --"
    if "search_player_value" in st.session_state:
        search_player_placeholder = st.session_state["search_player_value"]

    all_unique_players = sorted(df_history["Player Name"].unique())
    search_player = st.selectbox(
        "🔎 Player Report Search:", 
        ["-- View All --"] + all_unique_players,
        index=(["-- View All --"] + all_unique_players).index(search_player_placeholder)
    )
    if search_player != search_player_placeholder:
        st.session_state["search_player_value"] = search_player
        st.rerun()

    if search_player_placeholder != "-- View All --":
        st.markdown(f"#### 📖 Individual Performance Ledger")
        player_df = df_history[df_history["Player Name"] == search_player_placeholder].copy()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Points", int(player_df["Points"].sum()))
        col2.metric("Games Tracked", int(player_df["Date"].count()))
        
        ft_count_local = sum(1 for p in player_df["Position"] if p <= 10)
        col3.metric("Final Tables", ft_count_local)
        st.dataframe(player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], use_container_width=True, hide_index=True)
    else:
        with st.expander("🔍 View All Game-by-Game History Logs"):
            st.dataframe(df_history.sort_values(by=["Date", "Position"], ascending=[False, True])[["Date", "Player Name", "Position", "Points"]], use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# 📉 WEEKLY POSITION TRACKER LINE GRAPH 
# -----------------------------------------------------------------
if "Season XLVII" in selected_season and not leaderboard.empty:
    st.markdown("---")
    if last_game_date:
        st.subheader(f"📉 Weekly Finishing Position History (Last Game: {last_game_date})")
    else:
        st.subheader("📉 Weekly Finishing Position History")
        
    df_sorted_dates = df_history.sort_values(by="Date")
    if search_player_placeholder != "-- View All --":
        st.markdown(f"*Tracking finishing trends over time for **{search_player_placeholder}**.*")
        df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"] == search_player_placeholder]
    else:
        st.markdown("*Displaying season trajectory lines of the current **Top 5 Leaders**.*")
        df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"].isin(list(base_sorted_leaderboard.head(5)["Player Name"]))]
        
    if not df_filtered_tracked.empty:
        pivot_df = df_filtered_tracked.pivot_table(index="Date", columns="Player Name", values="Position", aggfunc="first")
        line_data = pivot_df.reset_index().melt("Date", var_name="Player Name", value_name="Position").dropna()
        line_data["Position"] = line_data["Position"].astype(int)
        
        position_line_chart = alt.Chart(line_data).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Date:N", title="Game Date"),
            y=alt.Y("Position:Q", title="Finishing Place", sort="descending", scale=alt.Scale(domain=[1, int(df_history["Position"].max())]), axis=alt.Axis(tickMinStep=1)),
            color=alt.Color("Player Name:N", title="Players"),
            tooltip=["Date", "Player Name", "Position"]
        ).properties(height=320).interactive()
        
        with st.container():
            st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
            st.altair_chart(position_line_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 📈 VISUAL BAR CHART
    # -----------------------------------------------------------------
    #st.markdown("---")
    #st.subheader("📈 Top 10 Performance Standings (Points)")
    #points_chart = alt.Chart(base_sorted_leaderboard.head(10)).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
    #    x=alt.X("Player Name:N", sort="-y", title="", axis=alt.Axis(labelAngle=-45)),
    #    y=alt.Y("Total Points:Q", title=""),
    #    color=alt.Color("Total Points:Q", scale=alt.Scale(range=["#2ed573", "#ffa502"]), legend=None),
    #    tooltip=["Player Name", "Total Points"]
    #).properties(height=260)
    
    #with st.container():
    #    st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
    #    st.altair_chart(points_chart, use_container_width=True)
    #    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 🔮 LEAGUE ARCHETYPES BUBBLE CHART
    # -----------------------------------------------------------------
    st.markdown("---")
    st.subheader("🔮 League Activity vs Efficiency Matrix")
    
    min_games, max_games_track = int(leaderboard["Games Played"].min()), int(leaderboard["Games Played"].max())
    min_pts, max_pts_track = int(leaderboard["Total Points"].min()), int(leaderboard["Total Points"].max())

    bubble_chart = alt.Chart(leaderboard).mark_circle().encode(
        x=alt.X("Games Played:Q", title="Total Attendance (Games)", scale=alt.Scale(domain=[max(0, min_games - 1), max_games_track + 1]), axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("Total Points:Q", title="Total Points Accumulated", scale=alt.Scale(domain=[max(0, min_pts - 500), max_pts_track + 1000])),
        size=alt.Size("Avg Points/Game:Q", title="Efficiency", scale=alt.Scale(range=[100, 1000])),
        color=alt.Color("Total Points:Q", scale=alt.Scale(range=["#2ed573", "#ffa502"]), legend=None),
        tooltip=["Player Name", "Games Played", "Total Points", "Avg Points/Game"]
    ).properties(height=340).interactive()
    
    with st.container():
        st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
        st.altair_chart(bubble_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# 🔐 SECURE ADMIN DIRECT INPUT PANEL (BYPASSES GOOGLE FORMS)
# =========================================================================
st.markdown("---")
with st.expander("⚙️ Secure League Admin Portal"):
    admin_password = st.text_input("Enter Admin Password:", type="password")
    
    if admin_password == "your_secret_password": 
        st.success("Access Verified.")
        
        st.markdown("#### 🏃‍♂️ Quick-Add New Surprise Player")
        new_guest_name = st.text_input("Type Full Name of New Player:", placeholder="e.g., John Doe")
        
        if st.button("➕ Add Player to Tonight's Dropdowns"):
            if new_guest_name.strip():
                clean_guest = new_guest_name.strip().title()
                if clean_guest not in st.session_state["temporary_walk_ins"] and clean_guest not in PLAYER_REGISTRY:
                    st.session_state["temporary_walk_ins"].append(clean_guest)
                    st.toast(f"🎉 {clean_guest} injected into drop-down lists!", icon="🃏")
        
        st.markdown("---")
        st.markdown("#### 📋 Input Tonight's Game Ledger")
        
        game_date_input = st.date_input("Select Game Date:", value=pd.Timestamp.now())
        field_size = st.number_input("Total Players in Tonight's Field:", min_value=2, max_value=30, value=30)
        
        available_players = sorted(PLAYER_REGISTRY + st.session_state["temporary_walk_ins"])
        
        placements_data = []
        for i in range(int(field_size)):
            place = i + 1
            selectable_list = [p for p in available_players if p not in placements_data]
            selected_player = st.selectbox(
                f"🏅 Finished in Place #{place}:", 
                ["-- Select Player --"] + selectable_list,
                key=f"direct_entry_place_{place}"
            )
            if selected_player != "-- Select Player --":
                placements_data.append(selected_player)
                
        st.markdown("---")
        st.markdown("#### 🎁 Nightly Bounties & Side-Bet Logs")
        
        high_hand_input = st.text_area(
            "High Hand Elite Logs:", 
            placeholder="e.g., Brian Cox - A/K's $130\n(Type line-by-line if there are multiple)",
            height=68
        )
        
        wheel_spin_input = st.text_area(
            "Ace of Spades Wheel Spins:", 
            placeholder="e.g., Steve Battard - Sit! by the fridge.",
            height=68
        )
        
        if st.button("🚀 Post Official Game Results to Google Sheets"):
            if len(placements_data) == field_size and len(set(placements_data)) == field_size:
                try:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    try:
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
                    except Exception:
                        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                    
                    client = gspread.authorize(creds)
                    active_workbook = client.open("Dirty Town Poker League Input (Responses)")
                    
                    reg_sheet = active_workbook.worksheet("Registry")
                    for name in placements_data:
                        if name not in PLAYER_REGISTRY:
                            reg_sheet.append_row([name])
                    
                    formatted_standings = "\n".join(placements_data)
                    sheet = active_workbook.worksheet(TARGET_WORKSHEET)
                    
                    # 🎯 Find the absolute last structural row currently occupied
                    next_open_row = len(sheet.get_all_values()) + 1
                    
                    # 🛡️ Force write explicitly to the next clean row index (e.g., Row 5, Row 6)
                    row_values = [
                        str(game_date_input), 
                        str(game_date_input), 
                        formatted_standings, 
                        high_hand_input.strip(), 
                        wheel_spin_input.strip()
                    ]
                    
                    sheet.insert_row(row_values, index=next_open_row, value_input_option="USER_ENTERED")
                    
                    st.balloons()
                    st.success("Game posted and new players permanently registered!")
                    st.cache_data.clear()
                    st.session_state["temporary_walk_ins"] = [] 
                    st.rerun()
                except Exception as append_err:
                    st.error(f"Failed to post data: {append_err}")
            else:
                st.error("Error: Please make sure all placements are completely filled with no duplicate players.")

# =========================================================================
# 🔄 ARCHIVE NAVIGATION SYSTEM (BOTTOM OF PAGE)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ League History Archive")

# Array of available dashboard frames
season_options = [
    "Season XLVIII (Current)", 
    "Season XLIX (Upcoming)", 
    "Season XLVII (Archived)"
]

# Safeguard the index calculation based on session state selection
try:
    current_index = season_options.index(st.session_state["active_season_choice"])
except ValueError:
    current_index = 0

season_toggle = st.selectbox(
    "🍂 Toggle Active League Season Dashboard View:",
    season_options,
    index=current_index
)

if season_toggle != st.session_state["active_season_choice"]:
    st.session_state["active_season_choice"] = season_toggle
    st.rerun()

# -----------------------------------------------------------------
# 🛡️ LEAGUE INFO FOOTER 
# -----------------------------------------------------------------
st.markdown("---")
st.info(
    "📋 **League Notice:** For schedule changes, blind structure, or dispute resolution, "
    "please contact your League Commissioner: **Michael Stephen Craft** 🙉. "
    "If you know you will **not** be able to attend this week's game, please notify "
    " **Todd Kinsell** as early as possible! 🏃‍♂️"
)
