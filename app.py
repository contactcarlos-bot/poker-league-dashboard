import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

st.title("🏆 Dirty Town Poker League Leaderboard")

def get_cloud_history_data():
    """Connects to Google Sheets using Streamlit Secrets and pulls the pre-calculated history."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Authenticate safely using Streamlit's cloud secrets vault
    google_secrets = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_secrets, scope)
    client = gspread.authorize(creds)
    
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    
    # CRITICAL: Read directly from the calculated history tab!
    sheet = workbook.worksheet("Database History")
    return sheet.get_all_records()

try:
    # 1. Fetch data from the cloud history sheet
    records = get_cloud_history_data()
    
    if not records:
        st.warning("No calculated match data found in your 'Database History' tab yet!")
    else:
        # 2. Load records into a clean Pandas DataFrame
        df_history = pd.DataFrame(records)
        
        # 3. Clean and convert numeric types safely
        df_history["Points"] = pd.to_numeric(df_history["Points"], errors="coerce").fillna(0).astype(int)
        
        # 4. Group by Player Name and tally up the grand totals
        leaderboard = df_history.groupby("Player Name").agg(
            Total_Points=("Points", "sum"),
            Games_Played=("Date", "count")
        ).reset_index()
        
        # 5. Sort with the highest point earner at the top
        leaderboard = leaderboard.sort_values(by="Total_Points", ascending=False).reset_index(drop=True)
        
        # Format column names nicely for the users
        leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
        leaderboard.index = leaderboard.index + 1  # Shifts index from 0 to 1 for rank numbering
        
        # 6. Display the beautiful interactive leaderboard table
        st.dataframe(leaderboard, use_container_width=True)
        
        # Optional: Add a little expandable view so players can see match breakdowns
        with st.expander("🔍 View Game-by-Game History Log"):
            st.dataframe(df_history.sort_values(by=["Date", "Position"], ascending=[False, True]), use_container_width=True, index=False)

except Exception as e:
    st.error(f"Could not load league data: {e}")
