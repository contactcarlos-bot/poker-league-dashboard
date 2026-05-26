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
            df_history["Points"] = pd.to_numeric(df_history["Points"], errors="coerce").fillna(0).astype(int)
            
            # 1. Calculate Aggregate Standings
            leaderboard = df_history.groupby("Player Name").agg(
                Total_Points=("Points", "sum"),
                Games_Played=("Date", "count")
            ).reset_index()
            leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
            
            # CRITICAL FIX: Define the base sorted leaderboard baseline FIRST
            base_sorted_leaderboard = leaderboard.sort_values(by="Total Points", ascending=False).reset_index(drop=True)
            
            # -----------------------------------------------------------------
            # 📊 SIDEBAR CONFIGURATIONS
            # -----------------------------------------------------------------
            st.sidebar.header("📊 Dashboard Settings")
            
            sort_by = st.sidebar.selectbox(
                "Sort Leaderboard By:",
                options=["Total Points (Highest First)", "Games Played (Most Active)", "Player Name (A-Z)"]
            )
            
            # Apply display Sorting based on sidebar toggle
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
            # 📈 CHARTS SECTION
            # -----------------------------------------------------------------
            st.subheader("📈 Top 10 Performance Standings (Points)")
            
            # Grab top 10 point earners from our base point list
            top_10 = base_sorted_leaderboard.head(10).copy()
            
            import altair as alt
            
            # Points Bar Chart
            points_chart = alt.Chart(top_10).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("Player Name:N", sort="-y", title="Player Name", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Total Points:Q", title="Total Points Accumulated"),
                color=alt.Color("Total Points:Q", scale=alt.Scale(scheme="viridis"), legend=None),
                tooltip=["Player Name", "Total Points"]
            ).properties(height=300)
            
            st.altair_chart(points_chart, use_container_width=True)
            
            # -----------------------------------------------------------------
            # 📉 WEEKLY POSITION TRACKER LINE GRAPH
            # -----------------------------------------------------------------
            st.markdown("---")
            st.subheader("📉 Weekly Finishing Position History")
            st.markdown("*Track how players fluctuate in placement week by week. Higher lines mean closer to 1st place!*")
            
            if "Date" in df_history.columns and "Position" in df_history.columns:
                # Sort dates chronologically so line chart goes left-to-right properly
                df_sorted_dates = df_history.sort_values(by="Date")
                
                # Filter down to the Top 10 players to keep the line graph readable
                top_players_list = list(base_sorted_leaderboard.head(10)["Player Name"])
                df_filtered_tracked = df_sorted_dates[df_sorted_dates["Player Name"].isin(top_players_list)]
                
                pivot_df = df_filtered_tracked.pivot_table(
                    index="Date", 
                    columns="Player Name", 
                    values="Position",
                    aggfunc="first"
                )
                
                line_data = pivot_df.reset_index().melt("Date", var_name="Player Name", value_name="Position")
                line_data = line_data.dropna()
                
                position_line_chart = alt.Chart(line_data).mark_line(point=True).encode(
                    x=alt.X("Date:N", title="Game Date"),
                    y=alt.Y("Position:Q", title="Finishing Place", sort="descending", scale=alt.Scale(domain=[1, int(df_history["Position"].max())])),
                    color=alt.Color("Player Name:N", title="Players"),
                    tooltip=["Date", "Player Name", "Position"]
                ).properties(height=400).interactive()
                
                st.altair_chart(position_line_chart, use_container_width=True)
            
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
                
                player_df = df_history[df_history["Player Name"] == search_player].copy()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Points Earned", int(player_df["Points"].sum()))
                col2.metric("Total Games Tracked", int(player_df["Date"].count()))
                
                st.markdown("**Detailed Game Placements Ledger:**")
                st.dataframe(
                    player_df.sort_values(by="Date", ascending=False)[["Date", "Position", "Points"]], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                with st.expander("🔍 View All Game-by-Game History Logs"):
                    if "Position" in df_history.columns:
                        sorted_log = df_history.sort_values(by=["Date", "Position"], ascending=[False, True])
                    else:
                        sorted_log = df_history.sort_values(by="Date", ascending=False)
                    st.dataframe(sorted_log, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not load league data: {e}")
