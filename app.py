import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Copy your LEAGUE_MATRIX and PLAYER_REGISTRY maps exactly from your tracking script
PLAYER_REGISTRY = {
    "bc": "Brian Cox", "dm": "Dustan Mulkey", "mc": "Mike Craft", # ... include your full registry here
}

LEAGUE_MATRIX = {
    8:  [558, 343, 240, 174, 135, 118, 110, 100],
    # ... include your full matrix here
}

st.title("🏆 Dirty Town Poker League Leaderboard")

def get_live_data_from_google():
    """Connects to Google Sheets using Streamlit Secrets instead of a local json file"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Authenticate safely using Streamlit's cloud secrets vault
    google_secrets = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_secrets, scope)
    client = gspread.authorize(creds)
    
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    sheet = workbook.sheet1
    all_rows = sheet.get_all_values()
    
    # Exclude empty space rows
    return [row for row in all_rows if any(cell.strip() for cell in row)]

try:
    cleaned_rows = get_live_data_from_google()
    
    if len(cleaned_rows) <= 1:
        st.warning("No matches recorded in the database yet!")
    else:
        all_game_entries = []
        
        # Parse every row submitted to calculate overall standings on-the-fly
        for row in cleaned_rows[1:]:
            if len(row) >= 3:
                target_date = str(row[1]).strip()
                raw_standings_text = row[2]
            else:
                target_date = str(row[0]).strip()
                raw_standings_text = row[1]
                
            # Form lines are logged bottom-up (last place to 1st). Reverse them to calculate 1st down.
            raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
            raw_list.reverse()
            total_players = len(raw_list)
            
            for index, raw_player_input in enumerate(raw_list):
                position = index + 1
                
                # Fetch matrix points
                points_list = LEAGUE_MATRIX.get(total_players, [100])
                points = points_list[position - 1] if (position - 1) < len(points_list) else 100
                
                lookup_key = raw_player_input.strip().lower()
                player_name = PLAYER_REGISTRY.get(lookup_key, raw_player_input.strip().title())
                
                all_game_entries.append({
                    "Player Name": player_name,
                    "Points": int(points),
                    "Date": target_date
                })
        
        # Group and build master leaderboard dataframe
        df_history = pd.DataFrame(all_game_entries)
        leaderboard = df_history.groupby("Player Name").agg(
            Total_Points=("Points", "sum"),
            Games_Played=("Date", "count")
        ).reset_index()
        
        leaderboard = leaderboard.sort_values(by="Total_Points", ascending=False).reset_index(drop=True)
        leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
        leaderboard.index = leaderboard.index + 1  # Standard rank display format
        
        # Render the dashboard out to your web users
        st.dataframe(leaderboard, use_container_width=True)

except Exception as e:
    st.error(f"Could not load data: {e}")
    st.info("Ensure your Google Service Account keys are configured in your Streamlit Advanced Secrets dashboard.")
