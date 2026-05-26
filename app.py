import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Dirty Town Poker League", page_icon="🏆", layout="centered")

st.title("🏆 Dirty Town Poker League Leaderboard")

def get_cloud_history_data():
    """Connects to Google Sheets and pulls pre-calculated history."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check if we are running locally or on the Streamlit cloud server
    if "gcp_service_account" in st.secrets:
        google_secrets = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(google_secrets, scope)
    else:
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
            # Safely parse numeric scores
            df_history["Points"] = pd.to_numeric(df_history["Points"], errors="coerce").fillna(0).astype(int)
            
            # 1. Calculate Aggregate Standings
            leaderboard = df_history.groupby("Player Name").agg(
                Total_Points=("Points", "sum"),
                Games_Played=("Date", "count")
            ).reset_index()
            leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
            
            # -----------------------------------------------------------------
            # 📊 SIDEBAR CONFIGURATIONS (Sorting & Personal Reports)
            # -----------------------------------------------------------------
            st.sidebar.header("📊 Dashboard Settings")
            
            # Sort selector
            sort_by = st.sidebar.selectbox(
                "Sort Leaderboard By:",
                options=["Total Points (Highest First)", "Games Played (Most Active)", "Player Name (A-Z)"]
            )
            
            # Apply Sorting
            if sort_by == "Total Points (Highest First)":
                leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
            elif sort_by == "Games Played (Most Active)":
                leaderboard = leaderboard.sort_values(by="Games Played", ascending=False).reset_index(drop=True)
            elif sort_by == "Player Name (A-Z)":
                leaderboard = leaderboard.sort_values(by="Player Name", ascending=True).reset_index(drop=True)
            
            leaderboard.index = leaderboard.index + 1
            
            # 🕵️‍♂️ Individual Player Lookup Section
            st.sidebar.markdown("---")
            st.sidebar.header("🔎 Player Report Search")
            all_unique_players = sorted(df_history["Player Name"].unique())
            search_player = st.sidebar.selectbox("Select a Player to view history:", ["-- View All --"] + all_unique_players)
            
           # -----------------------------------------------------------------
            # 📈 CHARTS SECTION (Displays Top 10 by default)
            # -----------------------------------------------------------------
            st.subheader("📈 Top 10 Performance Standings")
            
            # Grab the top 10 point earners directly from our already-sorted table
            top_10 = leaderboard.head(10).copy()
            
            # Create a professional Plotly Bar Chart that hard-locks the sort order
            import plotly.express as px
            
            fig = px.bar(
                top_10,
                x="Player Name",
                y="Total Points",
                text="Total Points",  # Puts the exact score number right on top of each bar
                color="Total Points", # Adds a beautiful color gradient (darker = more points)
                color_continuous_scale="Viridis" 
            )
            
            
            # CRITICAL LINE: Forces Plotly to respect our exact dataframe sorting layout (1st place to 10th place)
            fig.update_xaxes(categoryorder="total descending")
            
            # Adjust spacing so it looks great on both laptop screens and mobile phones
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=400,
                coloraxis_showscale=False # Hides the messy color side-bar legend
            )
            
            # Render the advanced chart onto the website
            st.plotly_chart(fig, use_container_width=True)
            
            # -----------------------------------------------------------------
            # 🏆 MAIN LEADERBOARD DISPLAY
            # -----------------------------------------------------------------
            st.subheader("📋 Overall Season Rankings")
            st.dataframe(leaderboard, use_container_width=True)
            
            # -----------------------------------------------------------------
            # 🔍 GAME LOGS & SEARCH RESULTS SECTION
            # -----------------------------------------------------------------
            if search_player != "-- View All --":
                st.markdown(f"---")
                st.subheader(f"📖 Individual Report: {search_player}")
                
                # Filter down to just this player's matches
                player_df = df_history[df_history["Player Name"] == search_player].copy()
                
                # Quick overview numbers for the player
                col1, col2 = st.columns(2)
                col1.metric("Total Points Earned", int(player_df["Points"].sum()))
                col2.metric("Total Games Tracked", int(player_df["Date"].count()))
                
                # Show their placements log
                st.markdown("**Detailed Game Placements Ledger:**")
                st.dataframe(
                    player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                # Default view showing the general game history bucket
                with st.expander("🔍 View All Game-by-Game History Logs"):
                    if "Position" in df_history.columns:
                        sorted_log = df_history.sort_values(by=["Date", "Position"], ascending=[False, True])
                    else:
                        sorted_log = df_history.sort_values(by="Date", ascending=False)
                    st.dataframe(sorted_log, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not load league data: {e}")
