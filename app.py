import os
import json
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import altair as alt

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")
# =========================================================================
# 👑 SIDEBAR: LEAGUE ADMIN & INFO
# =========================================================================
with st.sidebar:
    st.markdown("### 🏛️ League Office")
    st.success("**Commissioner:**\nMichael Craft 👑")
    st.info("**Co-Commissioner:**\nTodd Kinsell 💼")
    st.markdown("---")
    st.markdown("If you know you will **not** be able to attend this week's game, please notify Todd as early as possible!")
# =========================================================================
# 🔄 GLOBAL SESSION STATE & VARIABLE RESETS
# =========================================================================
if "temporary_walk_ins" not in st.session_state:
    st.session_state["temporary_walk_ins"] = []

if "active_season_choice" not in st.session_state:
    st.session_state["active_season_choice"] = "Season XLVIII (Current)"

selected_season = st.session_state["active_season_choice"]

# =========================================================================
# 🗓️ EXPLICIT SEASON ROUTING (PREVENTS LOGICAL OVERLAP)
# =========================================================================
if "Season XLVIII (Current)" == selected_season:
    TARGET_WORKSHEET = "Form Responses S48"
    season_total_weeks = 17
    st.title("🏆 Dirty Town Poker League - Season XLVIII")
else:
    TARGET_WORKSHEET = "Form Responses 1"
    season_total_weeks = 17
    st.title("🏆 Dirty Town Poker League - Season XLVII")

# =========================================================================
# 🎨 CUSTOM CSS: PRECISE METRIC FONT SCALING & LAYOUT DESIGN
# =========================================================================
st.markdown(
    """
    <style>
    div[data-testid="stDataFrameCollapsedCell"] div,
    div[data-testid="stDataFrame"] table,
    .stDataFrame div[data-testid="styled-data-frame"] div {
        font-size: 0.78rem !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    h3#high-hand-elite-logs, h3#ace-of-spades-wheel-spins {
        font-size: 1.1rem !important;
        color: #a4b0be !important;
        margin-top: 10px !important;
    }
    
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
@st.cache_data(ttl=600)
def load_player_registry():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in os.environ:
            creds_dict = json.loads(os.environ["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        elif "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        else:
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
        22: [2327, 1716, 1322, 1050, 867, 727, 612, 520, 442, 373, 313, 263, 224, 196, 174, 159, 149, 139, 131, 122, 113, 100], 
        23: [2428, 1813, 1409, 1126, 932, 786, 666, 567, 486, 413, 350, 295, 250, 217, 192, 171, 159, 148, 139, 131, 123, 113, 100],
        24: [2529, 1910, 1496, 1203, 999, 847, 721, 617, 531, 456, 388, 330, 280, 240, 211, 187, 169, 159, 148, 139, 131, 123, 113, 100], 25: [2630, 2008, 1584, 1282, 1066, 908, 777, 668, 577, 499, 429, 366, 312, 267, 232, 206, 184, 169, 158, 148, 140, 132, 123, 113, 100],
        26: [2732, 2106, 1673, 1362, 1136, 971, 835, 720, 624, 543, 470, 404, 347, 297, 256, 226, 202, 181, 168, 158, 148, 140, 132, 123, 113, 100], 
        27: [2833, 2204, 1763, 1443, 1206, 1034, 894, 774, 673, 588, 513, 444, 383, 329, 284, 248, 221, 197, 179, 168, 158, 148, 140, 132, 123, 113, 100],
        28: [2934, 2303, 1853, 1525, 1279, 1098, 953, 829, 724, 634, 556, 485, 420, 363, 314, 273, 241, 216, 194, 178, 168, 158, 148, 141, 132, 123, 113, 100], 
        29: [3035, 2402, 1944, 1608, 1352, 1164, 1014, 886, 775, 681, 600, 527, 459, 399, 346, 300, 263, 235, 211, 191, 178, 168, 157, 149, 141, 132, 124, 113, 100],
        30: [3137, 2500, 2035, 1692, 1427, 1231, 1076, 943, 828, 730, 645, 570, 500, 437, 380, 331, 289, 256, 230, 207, 189, 178, 167, 157, 149, 141, 133, 124, 113, 100]
        }
    # Safely fetch the points array for the current field size (empty list if not found)
    points_array = LEAGUE_MATRIX.get(buy_ins, [])
    
    # If the rank exists within the array, return the specific points
    if 1 <= rank <= len(points_array):
        return points_array[rank - 1]
        
    # Fallback for small test games (<6 players), huge games (>30), or out-of-bounds ranks
    return 100

@st.cache_data(ttl=600)
def get_raw_form_responses(worksheet_name):
    global global_workbook_instance
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in os.environ:
            creds_dict = json.loads(os.environ["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        elif "gcp_service_account" in st.secrets:
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

# =========================================================================
# 💾 DATA COMPILATION & PARSING ENGINE (REGULAR SEASON ONLY)
# =========================================================================
base_sorted_leaderboard = pd.DataFrame()
leaderboard = pd.DataFrame()
df_history = pd.DataFrame()
last_game_date = None
cleaned_rows = []

try:
    raw_rows = get_raw_form_responses(TARGET_WORKSHEET)
    cleaned_rows = [r for r in raw_rows if any(cell.strip() for cell in r)]
except Exception as data_load_error:
    st.error(f"Could not load sheets backend database engine: {data_load_error}")
    cleaned_rows = []

# 🔒 GLOBAL VALUE LOCK ASSIGNMENT FOR SUCCESS BANNER RESOLUTIONS
total_games_played = max(0, len(cleaned_rows) - 1)

# 🛑 BRAND-NEW/EMPTY SEASONS CLEAN RECOVERY BLOCK
if len(cleaned_rows) <= 1:
    st.success(f"🃏 **{selected_season.split(' (')[0].upper()}:** Staged and ready for action. Shuffle up and deal! 🚀")      
    st.markdown("---")
    st.info("📊 Standing grids and data models will populate automatically once Game 1 scores are posted by the Commish!")
    
    st.markdown("---")
    st.subheader("🏁 Post-Season Championship Series Bracket")
    b_col1, b_col2 = st.columns(2)
    b_col1.warning("""
    **🛰️ Post-Season Satellite**
    * **Status:** Staged for Future Season
    """)
    b_col2.warning("""
    **👑 Tournament of Champions (TOC)**
    * **Status:** Staged for Future Season
    """)

    # 🔐 INPUT ADMIN DRAWER AT FOR PRE-SEASON DEPLOYMENTS
    # 🔐 INPUT ADMIN DRAWER AT FOR PRE-SEASON DEPLOYMENTS
    st.markdown("---")
    with st.expander("⚙️ Secure League Admin Portal"):
        # 1. Start memory state for admin login
        if "is_admin" not in st.session_state:
            st.session_state["is_admin"] = False
            
        admin_password = st.text_input("Enter Admin Password:", type="password", key="pre_season_admin_frame")
        
        # 2. Check secure secrets and lock drawer open
        if admin_password != "" and admin_password == os.environ.get("admin_password"):
            st.session_state["is_admin"] = True
            
        if st.session_state["is_admin"]:
            st.success("Access Verified.")
            st.markdown("#### 📋 Input Tonight's Game Ledger")
            game_date_input = st.date_input("Select Game Date:", value=pd.Timestamp.now(), key="empty_season_date")
            field_size = st.number_input("Total Players:", min_value=2, max_value=30, value=30, key="empty_season_size")
            available_players = sorted(PLAYER_REGISTRY)
            
            placements_data = []
            for i in range(int(field_size)):
                place = i + 1
                selectable_list = [p for p in available_players if p not in placements_data]
                selected_player = st.selectbox(f"🏅 Place #{place}:", ["-- Select Player --"] + selectable_list, key=f"empty_admin_place_{place}")
                if selected_player != "-- Select Player --":
                    placements_data.append(selected_player)
            
            high_hand_input = st.text_area("High Hand Elite Logs:", placeholder="Name - Details", key="empty_hh")
            wheel_spin_input = st.text_area("Ace of Spades Wheel Spins:", placeholder="Name - Prize", key="empty_ws")
            
            if st.button("🚀 Post Official Game Results to Google Sheets", key="empty_season_post_btn"):
                if len(placements_data) == field_size:
                    try:
                        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ["gcp_service_account"]), scope) if "gcp_service_account" in os.environ else ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                        client = gspread.authorize(creds)
                        active_workbook = client.open("Dirty Town Poker League Input (Responses)")
                        sheet = active_workbook.worksheet(TARGET_WORKSHEET)
                        
                        formatted_standings = "\n".join(placements_data)
                        row_values = [str(game_date_input), str(game_date_input), formatted_standings, high_hand_input.strip(), wheel_spin_input.strip()]
                        
                        # 3. Bug Fix: Safely append to the absolute bottom of the sheet
                        sheet.append_row(row_values, value_input_option="USER_ENTERED")
                        
                        st.balloons()
                        st.cache_data.clear()
                        st.session_state["is_admin"] = False # Reset drawer for next time
                        st.rerun()
                    except Exception as append_err:
                        st.error(f"Failed to post data: {append_err}")

    # 🔄 HISTORICAL ARCHIVE NAVIGATOR FOR EMPTY SEASONS
    st.markdown("---")
    st.markdown("### 🗂️ League History Archive")
    season_options = ["Season XLVIII (Current)", "Season XLVII (Archived)"]
    season_toggle = st.selectbox(
        "🍂 Toggle Active League Season Dashboard View:",
        season_options,
        index=0,
        key="empty_season_toggle_nav"
    )
    if season_toggle != selected_season:
        st.session_state["active_season_choice"] = season_toggle
        st.rerun()

    st.markdown("---")
    st.info("📋 **League Notice:** For schedule changes, blind structure, or dispute resolution, please contact your League Commissioner: **Michael Stephen Craft** 👑. If you know you will **not** be able to attend this week's game, please notify Co-Commissioner **Todd Kinsell** 💼 as early as possible! 🏃‍♂️")
    st.stop()

# =========================================================================
# 📈 DATA COMPILATION & PARSING (RUNS ONLY IF LIVE ROWS EXIST IN ACTIVE SHEET)
# =========================================================================
parsed_history_records = []
for row in cleaned_rows[1:]:
    game_date = str(row[1]).strip().split()[0] if len(row) >= 3 else str(row[0]).strip().split()[0]
    raw_standings_text = row[2] if len(row) >= 3 else row[1]
    
    raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
    if not raw_list:
        continue
        
    total_players = len(raw_list)
    for index, raw_player_input in enumerate(raw_list):
        position = index + 1
        points = calculate_poker_points(total_players, position)
        
        player_name = str(raw_player_input).strip().replace("\r", "").title()
        if " Mcc" in player_name:
            player_name = player_name.replace(" Mcc", " McC")
        elif player_name.startswith("Mcc"):
            player_name = "McC" + player_name[3:]
        
        parsed_history_records.append({
            "Date": game_date,
            "Player Name": player_name, 
            "Position": int(position), 
            "Points": int(points)
        })

df_history = pd.DataFrame(parsed_history_records)
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

# 🤖 BANNERS SELECTION USING THE GLOBAL SECURITY POOL VARIABLE KEYWAYS
if selected_season == "Season XLVII (Archived)":
    st.success("🃏 **SEASON XLVII COMPLETED:** 17 regular season games are in the archives.\n\n🏆 **Grand Champion:** Dustan Mulkey")
elif selected_season == "Season XLVIII (Current)":
    st.success(f"🃏 **SEASON XLVIII UNDERWAY:** Game {total_games_played} is officially in the books! Check the updated standings below.")
    st.info("📌 **NOTE:** If you know you will not be able to attend this week's game, please notify Co-Commissioner **Todd Kinsell** 💼 as early as possible! 🏃‍♂️")

# =========================================================================
# 📊 METRICS & SEASON GRIDS
# =========================================================================
if not base_sorted_leaderboard.empty:
    st.markdown("### 👑 Season Milestones")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    current_leader = base_sorted_leaderboard.iloc[0]["Player Name"]
    
    win_sorted = leaderboard.sort_values(by="🥇 1st", ascending=False)
    win_boss = win_sorted.iloc[0]["Player Name"] if not win_sorted.empty else "N/A"
    win_count = win_sorted.iloc[0]["🥇 1st"] if not win_sorted.empty else 0
    
    # Calculate the player with the most Final Tables
    ft_sorted = leaderboard.sort_values(by="Final Tables", ascending=False)
    ft_boss = ft_sorted.iloc[0]["Player Name"] if not ft_sorted.empty else "N/A"
    ft_count = ft_sorted.iloc[0]["Final Tables"] if not ft_sorted.empty else 0
    
    with m_col1:
        st.metric("League Leader 🥇", current_leader, f"{base_sorted_leaderboard.iloc[0]['Total Points']} pts")
        
    with m_col2:
        st.metric("Championship Wins 🏆", win_boss, f"{win_count} Wins")
        
    with m_col3:
        st.metric("Final Table Boss 🃏", ft_boss, f"{ft_count} FTs")

    # 🥶 THE FIRST-OUT METRIC 
    if last_game_date:
        last_game_df = df_history[df_history["Date"] == last_game_date]
        first_out_player = last_game_df.iloc[-1]["Player Name"]
        first_out_position = last_game_df.iloc[-1]["Position"]
        
        with m_col4:
            st.metric("First Out 🥶", first_out_player, f"Busted {first_out_position}th")
    else:
        with m_col4:
            st.metric("First Out 🥶", "N/A", "Waiting for Game 1")


# =========================================================================
# 🏆 1. RESTORED ORIGINAL OVERALL SEASON RANKINGS LEADERBOARD
# =========================================================================
st.markdown("---")
st.subheader("📋 Overall Season Rankings")
display_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
display_leaderboard.index = display_leaderboard.index + 1

display_leaderboard["Games Played Format"] = display_leaderboard["Games Played"].apply(lambda x: f"{int(x)} / {season_total_weeks}")

final_table_df = display_leaderboard[[
    "Player Name", "Total Points", "Last Game Points", 
    "Games Played Format", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables", "Games Played"
]]

def highlight_last_game(val):
    return 'background-color: rgba(46, 204, 113, 0.15); font-weight: bold;' if val > 0 else ''

def highlight_low_attendance(row):
    styles = [''] * len(row)
    idx = row.index.get_loc("Games Played Format")
    attendance_threshold = 7 if season_total_weeks == 17 else 8
    if row["Games Played"] <= attendance_threshold:
        styles[idx] = 'background-color: rgba(231, 76, 60, 0.18); font-weight: bold; color: #ff7675;'
    else:
        styles[idx] = 'background-color: rgba(46, 204, 113, 0.12); font-weight: bold; color: #2ed573;'
    return styles

styled_df = final_table_df.style\
    .map(highlight_last_game, subset=["Last Game Points"])\
    .apply(highlight_low_attendance, axis=1)

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
        "Final Tables": st.column_config.NumberColumn("🃏 FT", alignment="center"),
        "Games Played Format": st.column_config.TextColumn("🏃‍♂️ Played", alignment="center"),
        "Games Played": None
    }
)


# =========================================================================
# 🎉 NIGHTLY BOUNTIES & WILDCARDS
# =========================================================================
if len(cleaned_rows) > 1:
    high_hand_records = []
    spin_wheel_records = []
    
    for row in cleaned_rows[1:]:
        g_date = str(row[1]).strip().split()[0] if len(row) >= 3 else str(row[0]).strip().split()[0]
        if len(row) >= 4 and row[3].strip():
            for line in row[3].strip().split('\n'):
                if line.strip():
                    parts = line.split("-", 1) if "-" in line else [line, "Prize Logged"]
                    high_hand_records.append({"Date": g_date, "Player Name": parts[0].strip().title(), "Prize Won": parts[1].strip()})
        if len(row) >= 5 and row[4].strip():
            for line in row[4].strip().split('\n'):
                if line.strip():
                    parts = line.split("-", 1) if "-" in line else [line, "Prize Logged"]
                    spin_wheel_records.append({"Date": g_date, "Player Name": parts[0].strip().title(), "Prize Won": parts[1].strip()})
                    
    # 🗃️ THE EXPANDER UPGRADE
    if high_hand_records or spin_wheel_records:
        st.markdown("---")
        with st.expander("🎉 View Nightly Specials & Special Bounties History"):
            w_col1, w_col2 = st.columns(2)
            with w_col1:
                st.markdown("### 🪵 High Hand Elite Logs")
                if high_hand_records: 
                    st.dataframe(pd.DataFrame(high_hand_records).sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
            with w_col2:
                st.markdown("### 🎡 Ace of Spades Wheel Spins")
                if spin_wheel_records: 
                    st.dataframe(pd.DataFrame(spin_wheel_records).sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
# =========================================================================
# 🏅 POST-SEASON BRACKETS SYSTEM (ALL NAMES INCLUDED)
# =========================================================================
st.markdown("---")
st.subheader("🏁 Post-Season Championship Series Bracket")

if selected_season == "Season XLVII (Archived)":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(255, 165, 0, 0.12) 0%, rgba(0, 0, 0, 0.4) 100%); border: 2px solid #ffa502; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
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
elif selected_season == "Season XLVIII (Current)":
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.info("""
        **🛰️ Upcoming Post-Season Satellite**
        * **Date Scheduled:** Saturday, September 26, 2026 📅
        * **Time:** 4:00 PM EST ⏰
        * **Status:** Open Qualifier Frame
        * **Requirement:** 8+ season games played to qualify
        """)
    with b_col2:
        st.info("""
        **👑 Tournament of Champions (TOC)**
        * **Date Scheduled:** Saturday, October 3, 2026 🏆
        * **Timeline:** • Lunch Served: 12:15 PM 🍔
          • Cards in the Air: 1:00 PM 🃏
        * **Status:** Awaiting Qualified Field
        * **Requirement:** Season Top 9 + Satellite Winner
        """)

# =========================================================================
# ⚙️ LIVE DASHBOARD CONTROLS & REPORT FILTERS
# =========================================================================
if not df_history.empty and last_game_date:
    st.markdown("---")
    st.markdown("### ⚙️ Dashboard Controls")
    search_player = st.selectbox("🔎 Player Report Search:", ["-- View All --"] + sorted(df_history["Player Name"].unique()), key="active_season_controls_search")

    if search_player != "-- View All --":
        player_df = df_history[df_history["Player Name"] == search_player].copy()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Points", int(player_df["Points"].sum()))
        col2.metric("Games Tracked", int(player_df["Date"].count()))
        col3.metric("Final Tables", sum(1 for p in player_df["Position"] if p <= 10))
        st.dataframe(player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], width="stretch", hide_index=True)
    else:
        with st.expander("🔍 View All Game-by-Game History Logs"):
            st.dataframe(df_history.sort_values(by=["Date", "Position"], ascending=[False, True])[["Date", "Player Name", "Position", "Points"]], width="stretch", hide_index=True)

# -----------------------------------------------------------------
# 📉 CHARTING PANELS (🔓 UNLOCKED FOR ALL LOGGED TIMELINES)
# -----------------------------------------------------------------
if not df_history.empty and not leaderboard.empty:
    st.markdown("---")
    st.subheader("📉 Weekly Finishing Position History")
    df_sorted_dates = df_history.sort_values(by="Date")
    df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"].isin(list(base_sorted_leaderboard.head(5)["Player Name"]))]
    if not df_filtered_tracked.empty:
        position_line_chart = alt.Chart(df_filtered_tracked.pivot_table(index="Date", columns="Player Name", values="Position", aggfunc="first").reset_index().melt("Date", var_name="Player Name", value_name="Position").dropna()).mark_line(point=True, strokeWidth=3).encode(x=alt.X("Date:N", title="Game Date"), y=alt.Y("Position:Q", title="Finishing Place", sort="descending", scale=alt.Scale(domain=[1, int(df_history["Position"].max())])), color=alt.Color("Player Name:N"), tooltip=["Date", "Player Name", "Position"]).properties(height=320).interactive()
        st.altair_chart(position_line_chart, use_container_width=True)

    st.markdown("---")
    st.subheader("🔮 League Activity vs Efficiency Matrix")
    st.altair_chart(alt.Chart(leaderboard).mark_circle().encode(x=alt.X("Games Played:Q", title="Total Attendance (Games)", axis=alt.Axis(tickMinStep=1)), y=alt.Y("Total Points:Q", title="Total Points Accumulated"), size=alt.Size("Avg Points/Game:Q", scale=alt.Scale(range=[100, 1000])), color=alt.Color("Total Points:Q", scale=alt.Scale(range=["#2ed573", "#ffa502"]), legend=None), tooltip=["Player Name", "Games Played", "Total Points", "Avg Points/Game"]).properties(height=340).interactive(), use_container_width=True)

# =========================================================================
# 🔐 SECURE ADMIN DIRECT INPUT PANEL
# =========================================================================
st.markdown("---")
with st.expander("⚙️ Secure League Admin Portal"):
    # 1. Start memory state for admin login
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
        
    admin_password = st.text_input("Enter Admin Password:", type="password", key="active_panel_pass_frame")
    
    # 2. Check secure secrets and lock drawer open
    if admin_password != "" and admin_password == os.environ.get("admin_password"):    
        st.session_state["is_admin"] = True
        
    if st.session_state["is_admin"]:
        st.success("Access Verified.")
        st.markdown("#### 🏃‍♂️ Quick-Add New Surprise Player")
        new_guest_name = st.text_input("Type Full Name of New Player:", key="active_panel_guest_box")
        if st.button("➕ Add Player To Tonight's Dropdowns", key="active_panel_guest_btn"):
            if new_guest_name.strip():
                clean_guest = new_guest_name.strip().title()
                if clean_guest not in st.session_state["temporary_walk_ins"] and clean_guest not in PLAYER_REGISTRY:
                    st.session_state["temporary_walk_ins"].append(clean_guest)
                    st.toast(f"🎉 Added {clean_guest}!", icon="🃏")
        
        st.markdown("---")
        st.markdown("#### 📋 Input Tonight's Game Ledger")
        game_date_input = st.date_input("Select Game Date:", value=pd.Timestamp.now(), key="active_panel_date")
        field_size = st.number_input("Total Players:", min_value=2, max_value=30, value=30, key="active_panel_size")
        available_players = sorted(PLAYER_REGISTRY + st.session_state["temporary_walk_ins"])
        
        placements_data = []
        for i in range(int(field_size)):
            place = i + 1
            selectable_list = [p for p in available_players if p not in placements_data]
            selected_player = st.selectbox(f"🏅 Place #{place}:", ["-- Select Player --"] + selectable_list, key=f"active_admin_place_{place}")
            if selected_player != "-- Select Player --": placements_data.append(selected_player)
                
        high_hand_input = st.text_area("High Hand Elite Logs:", placeholder="Name - Details", key="active_panel_hh")
        wheel_spin_input = st.text_area("Ace of Spades Wheel Spins:", placeholder="Name - Prize", key="active_panel_ws")
        
        if st.button("🚀 Post Official Game Results to Google Sheets", key="active_panel_post_btn"):
            if len(placements_data) == field_size and len(set(placements_data)) == field_size:
                try:
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ["gcp_service_account"]), scope) if "gcp_service_account" in os.environ else ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
                    client = gspread.authorize(creds)
                    active_workbook = client.open("Dirty Town Poker League Input (Responses)")
                    reg_sheet = active_workbook.worksheet("Registry")
                    for name in placements_data:
                        if name not in PLAYER_REGISTRY: reg_sheet.append_row([name])
                            
                    sheet = active_workbook.worksheet(TARGET_WORKSHEET)
                    
                    formatted_standings = "\n".join(placements_data)
                    row_values = [str(game_date_input), str(game_date_input), formatted_standings, high_hand_input.strip(), wheel_spin_input.strip()]
                    
                    # 3. Bug Fix: Safely append to the absolute bottom of the sheet
                    sheet.append_row(row_values, value_input_option="USER_ENTERED")
                    
                    st.balloons()
                    st.cache_data.clear()
                    st.session_state["temporary_walk_ins"] = []
                    st.session_state["is_admin"] = False # Reset drawer for next time
                    st.rerun()
                except Exception as append_err: st.error(f"Failed to post data: {append_err}")
            else:
                st.error("Error: Please make sure all placements are completely filled with no duplicate players.")
                
# =========================================================================
# 🔄 LEAGUE HISTORY ARCHIVE NAVIGATION
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ League History Archive")
season_options = ["Season XLVIII (Current)", "Season XLVII (Archived)"]
season_toggle = st.selectbox(
    "🍂 Toggle Active League Season Dashboard View:",
    season_options,
    index=season_options.index(selected_season),
    key="active_season_toggle_nav"
)

if season_toggle != selected_season:
    st.session_state["active_season_choice"] = season_toggle
    st.rerun()

st.markdown("---")
st.info("📋 **League Notice:** For schedule changes, blind structure, or dispute resolution, please contact your League Commissioner: **Michael Stephen Craft** 👑. If you know you will **not** be able to attend this week's game, please notify Co-Commissioner **Todd Kinsell** 💼 as early as possible! <b>")



