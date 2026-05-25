import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="Dirty Town Poker League",
    page_icon="♠️",
    layout="wide"
)

DB_FILE = "poker_league_data.xlsx"

# Title & Header
st.title("♠️ Dirty Town Poker League Portal")
st.markdown("Welcome to the official live standings and analytics dashboard.")
st.divider()

# Check if the database exists
if not os.path.exists(DB_FILE):
    st.error(f"Database file '{DB_FILE}' not found. Please run your data scripts first to generate league data!")
else:
    # Load data from the Excel sheets
    leaderboard_df = pd.read_excel(DB_FILE, sheet_name="Leaderboard")
    history_df = pd.read_excel(DB_FILE, sheet_name="Game History")
    
    # -------------------------------------------------------------------------
    # TAB 1: MASTER LEADERBOARD
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["🏆 Current Standings", "📊 Player Profile Lookup", "📜 Season Game History"])
    
    with tab1:
        st.header("Season Leaderboard")
        
        # Add medals to the top 3 visually!
        display_df = leaderboard_df.copy()
        display_df.index = display_df.index + 1  # Rank starts at 1
        
        # Format columns for a clean presentation
        st.dataframe(
            display_df, 
            column_config={
                "Player Name": st.column_config.TextColumn("Player Name"),
                "Total Points": st.column_config.NumberColumn("Total Points", format="%d pts"),
                "Games Played": st.column_config.NumberColumn("Games Played")
            },
            use_container_width=True
        )
        
    # -------------------------------------------------------------------------
    # TAB 2: ADVANCED PLAYER ANALYTICS
    # -------------------------------------------------------------------------
    with tab2:
        st.header("Player Performance Analytics")
        
        # Dropdown to select a player
        all_players = sorted(history_df["Player Name"].unique())
        selected_player = st.selectbox("Select a Player to Analyze:", all_players)
        
        if selected_player:
            # Filter history for just this player
            player_history = history_df[history_df["Player Name"] == selected_player].copy()
            
            # Filter out baseline setups for clean metrics
            game_history_clean = player_history[player_history["Date"] != "HISTORICAL_BASELINE"]
            
            # Calculate metrics
            total_points = player_history["Points"].sum()
            total_games = len(game_history_clean)
            
            # Layout metrics in columns
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Points Accumulated", f"{total_points:,} pts")
            col2.metric("Games Played This Season", total_games)
            
            if total_games > 0:
                avg_finish = round(game_history_clean["Position"].mean(), 1)
                col3.metric("Average Finishing Position", f"#{avg_finish}")
            else:
                col3.metric("Average Finishing Position", "N/A")
                
            st.markdown("### Match-by-Match History")
            st.dataframe(player_history, hide_index=True, use_container_width=True)
            
            # Interactive Line Chart showing points progression over time
            if not game_history_clean.empty:
                st.markdown("### Points Progression Chart")
                # Sort chronologically for the chart
                chart_data = game_history_clean.copy()
                chart_data = chart_data.reset_index()
                chart_data["Cumulative Points"] = chart_data["Points"].cumsum()
                
                st.line_chart(data=chart_data, x="Date", y="Cumulative Points", use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: RAW GAME HISTORY LOGS
    # -------------------------------------------------------------------------
    with tab3:
        st.header("Complete Match Logs")
        st.markdown("Every placement recorded in the system this season:")
        
        # Let users filter history by specific game dates
        all_dates = ["All Games"] + list(history_df["Date"].unique())
        selected_date = st.selectbox("Filter logs by Game Date:", all_dates)
        
        if selected_date == "All Games":
            st.dataframe(history_df, hide_index=True, use_container_width=True)
        else:
            filtered_history = history_df[history_df["Date"] == selected_date]
            st.dataframe(filtered_history, hide_index=True, use_container_width=True)