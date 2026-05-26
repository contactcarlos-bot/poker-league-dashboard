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
    
    google_secrets = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_secrets, scope)
    client = gspread.authorize(creds)
    
    workbook = client.open("Dirty Town Poker League Input (Responses)")
    sheet = workbook.worksheet("Database History")
    return sheet.get_all_records()

try:
    records = get_cloud_history_data()
    
    if not records:
        st.warning("No calculated match data found in your 'Database History' tab yet!")
    else:
        df_history = pd.DataFrame(records)
        
        # Force all column names to standard capitalization to avoid mismatch crashes
        df_history.columns = [str(col).strip().title() for col in df_history.columns]
        
        # Safe-check if 'Points' column is missing after standardization
        if "Points" not in df_history.columns:
            st.error("⚠️ The 'Points' column header is missing in your Google Sheet tab.")
            st.info("Please make sure row 1 of your 'Database History' tab has: Date | Player Name | Position | Points")
        else:
            # Clean and convert numeric types safely
            df_history["Points"] = pd.to_numeric(df_history["Points"], errors="coerce").fillna(0).astype(int)
            
            # Group by Player Name and tally up the grand totals
            leaderboard = df_history.groupby("Player Name").agg(
                Total_Points=("Points", "sum"),
                Games_Played=("Date", "count")
            ).reset_index()
            
            # Sort with the highest point earner at the top
            leaderboard = leaderboard.sort_values(by="Total_Points", ascending=False).reset_index(drop=True)
            
            # Format column names nicely for the users
            leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
            leaderboard.index = leaderboard.index + 1  # Shifts index to start from 1 instead of 0
            
            # Render the beautiful interactive leaderboard table
            st.dataframe(leaderboard, use_container_width=True)
            
            # Add an expandable view for match breakdowns
            with st.expander("🔍 View Game-by-Game History Log"):
                if "Position" in df_history.columns:
                    sorted_log = df_history.sort_values(by=["Date", "Position"], ascending=[False, True])
                else:
                    sorted_log = df_history.sort_values(by="Date", ascending=False)
                
                # FIXED LINE: Changed 'index=False' to 'hide_index=True' to comply with Streamlit rules
                st.dataframe(sorted_log, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not load league data: {e}")
