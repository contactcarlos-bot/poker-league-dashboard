import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

st.title("🏆 Dirty Town Poker League Leaderboard")

def get_cloud_history_data():
    """Connects to Google Sheets and pulls the pre-calculated history."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check if we are running locally or on the cloud server
    if "gcp_service_account" in st.secrets:
        # Online Server Mode
        google_secrets = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(google_secrets, scope)
    else:
        # Local Desktop Fallback Mode
        if not os.path.exists("credentials.json"):
            st.error("Missing credentials verification file!")
            st.stop()
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
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
        df_history.columns = [str(col).strip().title() for col in df_history.columns]
        
        if "Points" not in df_history.columns:
            st.error("⚠️ The 'Points' column header is missing in your Google Sheet tab.")
        else:
            df_history["Points"] = pd.to_numeric(df_history["Points"], errors="coerce").fillna(0).astype(int)
            
            # Group data to build aggregate totals
            leaderboard = df_history.groupby("Player Name").agg(
                Total_Points=("Points", "sum"),
                Games_Played=("Date", "count")
            ).reset_index()
            
            # Format display columns
            leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
            
            # -----------------------------------------------------------------
            # 🔄 NEW INTERACTIVE SORTING INTERFACE
            # -----------------------------------------------------------------
            st.sidebar.header("📊 Dashboard Settings")
            
            # Dropdown menu to select what metric to sort by
            sort_by = st.sidebar.selectbox(
                "Sort Leaderboard By:",
                options=["Total Points (Highest First)", "Games Played (Most Active)", "Player Name (A-Z)"]
            )
            
            # Apply sorting logic based on selection
            if sort_by == "Total Points (Highest First)":
                leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
            elif sort_by == "Games Played (Most Active)":
                leaderboard = leaderboard.sort_values(by="Games Played", ascending=False).reset_index(drop=True)
            elif sort_by == "Player Name (A-Z)":
                leaderboard = leaderboard.sort_values(by="Player Name", ascending=True).reset_index(drop=True)
            
            # Re-align index ranks so the display order is clear
            leaderboard.index = leaderboard.index + 1
            
            # -----------------------------------------------------------------
            # Render Leaderboard Display Table
            st.dataframe(leaderboard, use_container_width=True)
            
            # Historical expander view below
            with st.expander("🔍 View Game-by-Game History Log"):
                if "Position" in df_history.columns:
                    sorted_log = df_history.sort_values(by=["Date", "Position"], ascending=[False, True])
                else:
                    sorted_log = df_history.sort_values(by="Date", ascending=False)
                st.dataframe(sorted_log, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not load league data: {e}")
