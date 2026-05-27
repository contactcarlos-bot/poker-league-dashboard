import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

# =========================================================================
# 🚨 IMPORTANT LEAGUE ANNOUNCEMENTS (TOP OF PAGE)
# =========================================================================
st.error("🚨 **IMPORTANT NOTICE:** This Friday is the **FINAL GAME** of the regular season! You must have **8 or more games played** to qualify for Saturday's Satellite Game. Check your eligibility status at the bottom of the page.")
st.error("🚨 **IMPORTANT NOTICE:** Tournament of Champions Will Be Played on Saturday, June 6, 2026 (Lunch at 12:15pm- Cards Dealt at 1:00pm)")

# =========================================================================
# 🔄 SEASON SELECTOR SYSTEM
# =========================================================================
# This acts as your control panel. When June 5th hits, just change the default index to 1!
selected_season = st.selectbox(
    "🍂 Select League Season:",
    ["Season XLVII (Current)", "Season XLVIII (Starts June 5)"],
    index=0
)

# Map selections to exact Google Sheet tab names
if "Season XLVIII" in selected_season:
    TARGET_WORKSHEET = "Form Responses S48"
    st.title("🏆 Dirty Town Poker League Leaderboard - Season XLVIII")
else:
    TARGET_WORKSHEET = "Form Responses 1"
    st.title("🏆 Dirty Town Poker League Leaderboard - Season XLVII")

# =========================================================================
# 🎨 CUSTOM CSS: PRECISE METRIC FONT SCALING & BRANDING REMOVAL
# =========================================================================
st.markdown(
    """
    <style>
    /* 🛡️ COMPLETELY VAPORIZES H hamburger menu, DEPLOY, FOOTERS, AND HOSTED BADGES */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* 🎯 TARGETS AND DELETES THE BOTTOM RIGHT 'HOSTED WITH STREAMLIT' FLOATING ACTION BADGE */
    .viewerBadge {display: none !important;}
    div[data-testid="stViewerBadge"] {display: none !important;}
    button[title="View source on GitHub"] {display: none !important;}
    
    /* 🎯 TARGETS PLAYER NAMES: Shrinks text uniquely inside metric values */
    div[data-testid="stMetricValue"] div, 
    div[data-testid="stMetricValue"] span {
        font-size: 1.25rem !important;
        letter-spacing: -0.02em;
        font-weight: 600 !important;
    }
    
    /* Keeps numbers/static values bold and readable */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    
    /* Shrinks the smaller bottom metrics labels (e.g., "1600 pts", "Wins") */
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    
    /* Shrinks the top category header emojis & titles */
    div[data-testid="stMetricLabel"] p {
        font-size: 0.9rem !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 🎨 CUSTOM CSS: PRECISE METRIC FONT SCALING & BRANDING REMOVAL
# =========================================================================
st.markdown(
    """
    <style>
    /* 🛡️ HIDES STREAMLIT BRANDING, PROFILE LINKS, AND GITHUB CODE SHORCUTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* 🎯 TARGETS PLAYER NAMES: Shrinks text uniquely inside metric values */
    div[data-testid="stMetricValue"] div, 
    div[data-testid="stMetricValue"] span {
        font-size: 1.25rem !important;
        letter-spacing: -0.02em;
        font-weight: 600 !important;
    }
    
    /* Keeps numbers/static values bold and readable */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    
    /* Shrinks the smaller bottom metrics labels (e.g., "1600 pts", "Wins") */
    div[data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    
    /* Shrinks the top category header emojis & titles */
    div[data-testid="stMetricLabel"] p {
        font-size: 0.9rem !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# CLOUD CONFIGURATION & PLAYER REGISTRY
# =========================================================================
PLAYER_REGISTRY = {
    "bc": "Brian Cox", "dm": "Dustan Mulkey", "mc": "Mike Craft",
    "jm": "Jeff McCleave", "rm": "Ryan Mulkey", "jal": "John Alvenus",    
    "jq": "Jim Qualizza", "nr": "Nick Rouhani", "sb": "Steve Battard",
    "dl": "David Lee", "tk": "Todd Kinsell", "jh": "Joe Hawkins", "fw": "Frank Watts",
    "cz": "C.J. Zamora", "st": "Sam Townsend", "br": "Bill Roland",
    "jho": "John Hopkins", "cr": "Chris Richerson", "mce": "Mike Cercone",
    "jar": "James Arndt", "qs": "Quinton Staton", "rc": "Rob Christian",
    "mo": "Mike Owen", "jf": "Jermaine Ford", "jo": "Jeremy Otterson",
    "car": "Carlos Recalde", "ba": "Bob Allen", "de": "Don Eyster",
    "sc": "Scotty Cutright", "jmc": "John McClain", "jfa": "Jeff Farrar",
    "mm": "Miguel Miranda", "cm": "Chris Martin", "lv": "Liora Volkovich",
    "th": "Travis Harvey", "dh": "Dustin Harper", "bb": "Bob Bowman",
    "pj": "Phillip Johnson", "tg": "Tom Griffin", "mh": "Mark Hoffman", "dc": "Daniel Cook"
}

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

def get_raw_form_responses(worksheet_name):
    """Connects to Google Sheets and reads the selected season tab."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    client = gspread.authorize(creds)
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    sheet = workbook.worksheet(worksheet_name)
    return sheet.get_all_values()

try:
    raw_rows = get_raw_form_responses(TARGET_WORKSHEET)
    cleaned_rows = [r for r in raw_rows if any(cell.strip() for cell in r)]
    
    if len(cleaned_rows) <= 1:
        st.warning(f"No submissions found in your Google Form for {selected_season} yet!")
        leaderboard = pd.DataFrame(columns=["Player Name", "Total Points", "Games Played", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables", "Avg Points/Game", "Last Game Points"])
        df_history = pd.DataFrame(columns=["Date", "Player Name", "Position", "Points"])
        base_sorted_leaderboard = leaderboard
        last_game_date = None
    else:
        parsed_history_records = []
        
        for row in cleaned_rows[1:]:
            game_date = str(row[1]).strip() if len(row) >= 3 else str(row[0]).strip()
            raw_standings_text = row[2] if len(row) >= 3 else row[1]
            
            raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
            if not raw_list:
                continue
                
            if "-" in game_date and len(game_date.split("-")[0]) == 4:
                is_historical = True
            else:
                is_historical = False
                
            total_players = len(raw_list)
            for index, raw_player_input in enumerate(raw_list):
                if is_historical:
                    position = index + 1
                else:
                    position = total_players - index
                    
                points = calculate_poker_points(total_players, position)
                
                lookup_key = raw_player_input.strip().lower()
                player_name = PLAYER_REGISTRY.get(lookup_key, raw_player_input.strip().title())
                
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
        unique_dates_sorted = sorted(df_history["Date"].unique())
        last_game_date = unique_dates_sorted[-1] if unique_dates_sorted else None
        
        if last_game_date:
            df_last_game = df_history[df_history["Date"] == last_game_date][["Player Name", "Points"]].copy()
            df_last_game.columns = ["Player Name", "Last Game Points"]
        else:
            df_last_game = pd.DataFrame(columns=["Player Name", "Last Game Points"])

        # Track granular finish classes
        df_history["🥇 1st"] = df_history["Position"].apply(lambda x: 1 if x == 1 else 0)
        df_history["🥈 2nd"] = df_history["Position"].apply(lambda x: 1 if x == 2 else 0)
        df_history["🥉 3rd"] = df_history["Position"].apply(lambda x: 1 if x == 3 else 0)
        df_history["FT"] = df_history["Position"].apply(lambda x: 1 if x <= 6 else 0)
        
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
        # SPICED-UP METRICS SHELF (Upgraded to 4 Columns)
        # -----------------------------------------------------------------
        if not base_sorted_leaderboard.empty:
            st.markdown("### 👑 Season Milestones & Management")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            current_leader = base_sorted_leaderboard.iloc[0]["Player Name"]
            max_games = base_sorted_leaderboard["Games Played"].max()
            attendance_kings = base_sorted_leaderboard[base_sorted_leaderboard["Games Played"] == max_games]["Player Name"].tolist()
            
            win_sorted = leaderboard.sort_values(by="🥇 1st", ascending=False)
            win_boss = win_sorted.iloc[0]["Player Name"] if not win_sorted.empty else "N/A"
            win_count = win_sorted.iloc[0]["🥇 1st"] if not win_sorted.empty else 0
            
            with m_col1:
                st.metric("League Leader 🥇", current_leader, f"{base_sorted_leaderboard.iloc[0]['Total Points']} pts")
            with m_col2:
                st.metric("Max Attendance 🏃‍♂️", attendance_kings[0] if attendance_kings else "N/A", f"{max_games} games")
            with m_col3:
                st.metric("Championship Wins 🏆", win_boss, f"{win_count} Wins")
            with m_col4:
                st.metric("Commissioner 👑", "Michael Craft", "League Admin")

    # =========================================================================
    # 🏅 POST-SEASON TOURNAMENT TRACKER
    # =========================================================================
    if "Season XLVII" in selected_season:
        st.markdown("---")
        st.subheader("🏁 Post-Season Championship Series Bracket")
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.info("""
            **🛰️ Saturday Satellite Match**
            * **Status:** Scheduled (May 30 @ 4:00pm)
            * **Current Winner:** *TBD* 
            * **Reward:** Advances directly into TOC as Seed #10
            """)
        with b_col2:
            st.success("""
            **👑 Tournament of Champions**
            * **Status:** Scheduled (June 6 @ 1:00pm)
            * **Season XLVII Champion:** *TBD* 🏆
            * **Runner Up:** *TBD* 🥈
            """)

        # =========================================================================
        # 🃏 NEW: NIGHTLY BOUNTIES & WILDCARDS (HIGH HAND & SPIN THE WHEEL)
        # =========================================================================
        st.markdown("---")
        st.subheader("🎉 Nightly Specials & Special Bounties")
        
        # Pull columns safely if they exist in your raw sheet (assuming columns 4 and 5)
        # Adjusted dynamically based on data framework array boundaries
        high_hand_list = []
        spin_wheel_list = []
        
        for row in cleaned_rows[1:]:
            if len(row) >= 4 and row[3].strip():  # High Hand Column
                high_hand_list.append(row[3].strip().title())
            if len(row) >= 5 and row[4].strip():  # Spin The Wheel Column
                spin_wheel_list.append(row[4].strip().title())
                
        w_col1, w_col2 = st.columns(2)
        
        with w_col1:
            st.markdown("### 🪵 High Hand Elite")
            if high_hand_list:
                df_hh = pd.DataFrame(high_hand_list, columns=["Player Name"]).value_counts().reset_index(name="Total Wins")
                st.dataframe(df_hh, use_container_width=True, hide_index=True)
            else:
                st.info("No High Hand records logged yet for this season.")
                
        with w_col2:
            st.markdown("### 🎡 Ace of Spades Wheel Spins")
            if spin_wheel_list:
                df_sw = pd.DataFrame(spin_wheel_list, columns=["Player Name"]).value_counts().reset_index(name="Total Spins")
                st.dataframe(df_sw, use_container_width=True, hide_index=True)
            else:
                st.info("No Spade Ace wheel draws tracked yet for this season.")
                
    # -----------------------------------------------------------------
    # 🏆 SEASON STANDINGS LEADERBOARD
    # -----------------------------------------------------------------
    if not base_sorted_leaderboard.empty:
        st.markdown("---")
        st.subheader("📋 Overall Season Rankings")
        
        display_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        display_leaderboard.index = display_leaderboard.index + 1
        
        final_table_df = display_leaderboard[["Player Name", "Last Game Points", "Total Points", "Games Played", "🥇 1st", "🥈 2nd", "🥉 3rd", "Final Tables"]]

        # Custom highlighters for green (points won) and red (low attendance)
        def highlight_last_game(val):
            return 'background-color: rgba(46, 204, 113, 0.15); font-weight: bold;' if val > 0 else ''

        def highlight_low_attendance(val):
            return 'background-color: rgba(231, 76, 60, 0.18); font-weight: bold; color: #ff7675;' if val <= 7 else ''

        # Chain both mapping operations onto the styling pipeline
        styled_df = final_table_df.style\
            .map(highlight_last_game, subset=["Last Game Points"])\
            .map(highlight_low_attendance, subset=["Games Played"])
            
        st.dataframe(styled_df, use_container_width=True)
        
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

        # -----------------------------------------------------------------
        # 🔍 INDIVIDUAL LOG REPORTS
        # -----------------------------------------------------------------
        if search_player_placeholder != "-- View All --":
            st.markdown(f"#### 📖 Individual Performance Ledger")
            player_df = df_history[df_history["Player Name"] == search_player_placeholder].copy()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Points", int(player_df["Points"].sum()))
            col2.metric("Games Tracked", int(player_df["Date"].count()))
            
            # Recalculate local final table matches cleanly
            ft_count_local = sum(1 for p in player_df["Position"] if p <= 6)
            col3.metric("Final Tables", ft_count_local)
            st.dataframe(player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], use_container_width=True, hide_index=True)
        else:
            with st.expander("🔍 View All Game-by-Game History Logs"):
                st.dataframe(df_history.sort_values(by=["Date", "Position"], ascending=[False, True])[["Date", "Player Name", "Position", "Points"]], use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # 🃏 SATELLITE GAME QUALIFIED PLAYERS (Only displays for Season XLVII)
    # -----------------------------------------------------------------
    if "Season XLVII" in selected_season and not leaderboard.empty:
        st.markdown("---")
        st.subheader("🃏 Satellite Game Qualified Players")
        st.markdown("*Players with **8 or more games played** who are currently ranked **10th place or lower (11th, 12th, etc.)**.*")

        # Create a copy of the overall sorted rankings to check exact placements
        df_sat_check = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        # Shift index to start at 1 to match official ranking positions
        df_sat_check.index = df_sat_check.index + 1 
        
        # Filter: Games Played >= 8 AND Rank (Index) >= 11 (Targets 11th, 12th, etc.)[cite: 2]
        df_satellite_qualified = df_sat_check[
            (df_sat_check["Games Played"] >= 8) & (df_sat_check.index >= 10)
        ].copy()
        
        if df_satellite_qualified.empty:
            st.info("No players currently meet the qualification criteria for the Satellite Game.")
        else:
            # Insert the actual Season Rank as a clean visible column
            df_satellite_qualified["Season Rank"] = df_satellite_qualified.index
            
            # Reset the dataframe index and shift by 1 to create a clean sequential list numbering (1, 2, 3...)
            df_satellite_qualified = df_satellite_qualified.reset_index(drop=True)
            df_satellite_qualified.index = df_satellite_qualified.index + 1
            df_satellite_qualified["#"] = df_satellite_qualified.index
            
            # Reorder columns to put the list number first
            sat_display_df = df_satellite_qualified[["#", "Season Rank", "Player Name", "Games Played", "Total Points"]]
            
            with st.container():
                st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
                st.dataframe(sat_display_df, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
        # -----------------------------------------------------------------
        # 📉 WEEKLY POSITION TRACKER LINE GRAPH 
        # -----------------------------------------------------------------
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
            
        pivot_df = df_filtered_tracked.pivot_table(index="Date", columns="Player Name", values="Position", aggfunc="first")
        line_data = pivot_df.reset_index().melt("Date", var_name="Player Name", value_name="Position").dropna()
        line_data["Position"] = line_data["Position"].astype(int)
        
        import altair as alt
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
        st.markdown("---")
        st.subheader("📈 Top 10 Performance Standings (Points)")
        points_chart = alt.Chart(base_sorted_leaderboard.head(10)).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Player Name:N", sort="-y", title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Total Points:Q", title=""),
            color=alt.Color("Total Points:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=["Player Name", "Total Points"]
        ).properties(height=260)
        
        with st.container():
            st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
            st.altair_chart(points_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------------------------------------------
        # 🔮 LEAGUE ARCHETYPES BUBBLE CHART (Edge Clipping Fixed)
        # -----------------------------------------------------------------
        st.markdown("---")
        st.subheader("🔮 League Activity vs Efficiency Matrix")
        st.markdown("*Bubble Size represents **Average Points Per Game**. Sharks stay high up on small game samples; Grinders stack points over max attendance.*")
        
        # FIX: Padding limits added to the domain ranges prevents circle clipping on axes borders
        min_games, max_games_track = int(leaderboard["Games Played"].min()), int(leaderboard["Games Played"].max())
        min_pts, max_pts_track = int(leaderboard["Total Points"].min()), int(leaderboard["Total Points"].max())

        bubble_chart = alt.Chart(leaderboard).mark_circle().encode(
            x=alt.X("Games Played:Q", 
                    title="Total Attendance (Games)", 
                    scale=alt.Scale(domain=[max(0, min_games - 1), max_games_track + 1]),
                    axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Total Points:Q", 
                    title="Total Points Accumulated",
                    scale=alt.Scale(domain=[max(0, min_pts - 500), max_pts_track + 1000])),
            size=alt.Size("Avg Points/Game:Q", title="Efficiency", scale=alt.Scale(range=[100, 1000])),
            color=alt.Color("Player Name:N", title="Player", legend=None),
            tooltip=["Player Name", "Games Played", "Total Points", "Avg Points/Game"]
        ).properties(height=340).interactive()
        
        with st.container():
            st.markdown('<div style="background-color: rgba(255,255,255,0.04); padding: 15px; border-radius: 8px;">', unsafe_allow_html=True)
            st.altair_chart(bubble_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 🛡️ LEAGUE INFO FOOTER 
    # -----------------------------------------------------------------
    st.markdown("---")
    st.info("📋 **League Notice:** For schedule changes, blind structure, or dispute resolution, please contact your League Commissioner: **Miguel Craft** 🙉")

except Exception as e:
    st.error(f"Could not load league data: {e}")
