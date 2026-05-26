import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

st.title("🏆 Dirty Town Poker League Leaderboard")

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

def get_raw_form_responses():
    """Connects to Google Sheets and reads the raw form submissions log."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    client = gspread.authorize(creds)
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    sheet = workbook.worksheet("Form Responses 1")
    return sheet.get_all_values()

try:
    raw_rows = get_raw_form_responses()
    cleaned_rows = [r for r in raw_rows if any(cell.strip() for cell in r)]
    
    if len(cleaned_rows) <= 1:
        st.warning("No submissions found in your Google Form yet!")
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
        # DYNAMIC 'LAST GAME' ENGINE
        # -----------------------------------------------------------------
        unique_dates_sorted = sorted(df_history["Date"].unique())
        last_game_date = unique_dates_sorted[-1] if unique_dates_sorted else None
        
        if last_game_date:
            df_last_game = df_history[df_history["Date"] == last_game_date][["Player Name", "Points"]].copy()
            df_last_game.columns = ["Player Name", "Last Game Points"]
        else:
            df_last_game = pd.DataFrame(columns=["Player Name", "Last Game Points"])

        leaderboard = df_history.groupby("Player Name").agg(
            Total_Points=("Points", "sum"), Games_Played=("Date", "count")
        ).reset_index()
        
        leaderboard = pd.merge(leaderboard, df_last_game, on="Player Name", how="left")
        leaderboard["Last Game Points"] = leaderboard["Last Game Points"].fillna(0).astype(int)
        
        leaderboard.columns = ["Player Name", "Total Points", "Games Played", "Last Game Points"]
        base_sorted_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        
        # -----------------------------------------------------------------
        # 🔎 RELOCATED CONTROLS (Main Page Dropdowns)
        # -----------------------------------------------------------------
        st.markdown("### ⚙️ Dashboard Controls")
        control_col1, control_col2 = st.columns(2)
        
        with control_col1:
            sort_by = st.selectbox(
                "Sort Leaderboard Table By:", 
                ["Total Points (Highest First)", "Last Game Points (Newest Slates)", "Games Played (Most Active)", "Player Name (A-Z)"]
            )
            
        with control_col2:
            all_unique_players = sorted(df_history["Player Name"].unique())
            search_player = st.selectbox("🔎 Player Report Search:", ["-- View All --"] + all_unique_players)
            
        if sort_by == "Total Points (Highest First)":
            leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
        elif sort_by == "Last Game Points (Newest Slates)":
            leaderboard = leaderboard.sort_values(by="Last Game Points", ascending=False).reset_index(drop=True)
        elif sort_by == "Games Played (Most Active)":
            leaderboard = leaderboard.sort_values(by="Games Played", ascending=False).reset_index(drop=True)
        elif sort_by == "Player Name (A-Z)":
            leaderboard = leaderboard.sort_values(by="Player Name", ascending=True).reset_index(drop=True)
        leaderboard.index = leaderboard.index + 1
        
        # -----------------------------------------------------------------
        # 📈 VISUAL CHARTS
        # -----------------------------------------------------------------
        st.markdown("---")
        st.subheader("📈 Top 10 Performance Standings (Points)")
        import altair as alt
        points_chart = alt.Chart(base_sorted_leaderboard.head(10)).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Player Name:N", sort="-y", title="Player Name", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Total Points:Q", title="Total Points Accumulated"),
            color=alt.Color("Total Points:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=["Player Name", "Total Points"]
        ).properties(height=260)
        st.altair_chart(points_chart, use_container_width=True)
        
        st.markdown("---")
        if last_game_date:
            st.subheader(f"📉 Weekly Finishing Position History (Last Game: {last_game_date})")
        else:
            st.subheader("📉 Weekly Finishing Position History")
            
        df_sorted_dates = df_history.sort_values(by="Date")
        if search_player != "-- View All --":
            st.markdown(f"*Tracking finishing trends over time for **{search_player}**.*")
            df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"] == search_player]
        else:
            st.markdown("*Displaying season trajectory lines of the current **Top 5 Leaders**.*")
            df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"].isin(list(base_sorted_leaderboard.head(5)["Player Name"]))]
            
        pivot_df = df_filtered_tracked.pivot_table(index="Date", columns="Player Name", values="Position", aggfunc="first")
        line_data = pivot_df.reset_index().melt("Date", var_name="Player Name", value_name="Position").dropna()
        line_data["Position"] = line_data["Position"].astype(int)
        
        position_line_chart = alt.Chart(line_data).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Date:N", title="Game Date"),
            y=alt.Y("Position:Q", title="Finishing Place", sort="descending", scale=alt.Scale(domain=[1, int(df_history["Position"].max())]), axis=alt.Axis(tickMinStep=1)),
            color=alt.Color("Player Name:N", title="Players"),
            tooltip=["Date", "Player Name", "Position"]
        ).properties(height=320).interactive()
        st.altair_chart(position_line_chart, use_container_width=True)
        
        # -----------------------------------------------------------------
        # 🏆 SEASON STANDINGS LEADERBOARD
        # -----------------------------------------------------------------
        st.markdown("---")
        st.subheader("📋 Overall Season Rankings")
        st.dataframe(leaderboard[["Player Name", "Last Game Points", "Total Points", "Games Played"]], use_container_width=True)
        
        # -----------------------------------------------------------------
        # 🔍 DETAILED INDIVIDUAL SEARCH PERFORMANCE REPORT
        # -----------------------------------------------------------------
        if search_player != "-- View All --":
            st.markdown("---")
            st.subheader(f"📖 Individual Report: {search_player}")
            player_df = df_history[df_history["Player Name"] == search_player].copy()
            col1, col2 = st.columns(2)
            col1.metric("Total Points Earned", int(player_df["Points"].sum()))
            col2.metric("Total Games Tracked", int(player_df["Date"].count()))
            st.dataframe(player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], use_container_width=True, hide_index=True)
        else:
            with st.expander("🔍 View All Game-by-Game History Logs"):
                st.dataframe(df_history.sort_values(by=["Date", "Position"], ascending=[False, True]), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not load league data: {e}")
