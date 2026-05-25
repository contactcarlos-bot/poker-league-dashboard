import os
import math
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================================================================
# CONFIGURATION & UNIQUE PLAYER REGISTRY
# =========================================================================
GOOGLE_SHEET_NAME = "Dirty Town Poker League Input (Responses)"
DB_FILE = "poker_league_data.xlsx"

PLAYER_REGISTRY = {
    # Original Base Field
    "bc": "Brian Cox",
    "dm": "Dustan Mulkey",
    "mc": "Mike Craft",
    "jm": "Jeff McCleave",
    "rm": "Ryan Mulkey",
    "jal": "John Alvenus",    # Unique key 'jal' prevents crossover errors
    "jq": "Jim Qualizza",
    "nr": "Nick Rouhani",
    "sb": "Steve Battard",
    "dl": "David Lee",
    "tk": "Todd Kinsell",
    "jh": "Joe Hawkins",
    "fw": "Frank Watts",
    
    # Active League Expansion
    "cz": "C.J. Zamora",
    "st": "Sam Townsend",
    "br": "Bill Roland",
    "jho": "John Hopkins",
    "cr": "Chris Richerson",
    "mce": "Mike Cercone",
    "jar": "James Arndt",     # Unique key 'jar' prevents crossover errors
    "qs": "Quinton Staton",
    "rc": "Rob Christian",
    "mo": "Mike Owen",
    "jf": "Jermaine Ford",
    "jo": "Jeremy Otterson",
    "car": "Carlos Recalde",
    "ba": "Bob Allen",
    "de": "Don Eyster",
    "sc": "Scotty Cutright",
    "jmc": "John McClain",
    "jfa": "Jeff Farrar",
    "mm": "Miguel Miranda",
    "cm": "Chris Martin",
    "lv": "Liora Volkovich",
    "th": "Travis Harvey",
    "dh": "Dustin Harper",
    "bb": "Bob Bowman",
    "pj": "Phillip Johnson",
    "tg": "Tom Griffin",
    "mh": "Mark Hoffman",
    "dc": "Daniel Cook",
}

def calculate_poker_points(total_players, rank):
    """
    Looks up exact points from your updated LEAGUE_MATRIX.
    """
    buy_ins = int(total_players)
    rank = int(rank)
    
    LEAGUE_MATRIX = {
        6:  [371, 226, 156, 121, 110, 100],
        7:  [460, 282, 195, 143, 119, 110, 100],
        8:  [558, 343, 240, 174, 135, 118, 110, 100],
        9:  [664, 410, 290, 213, 160, 132, 118, 110, 100],
        10: [777, 483, 344, 256, 193, 151, 129, 119, 111, 100],
        11: [897, 560, 402, 303, 231, 178, 146, 128, 119, 111, 100],
        12: [1020, 642, 465, 353, 273, 212, 168, 142, 128, 119, 111, 100],
        13: [1146, 728, 531, 406, 318, 249, 197, 161, 140, 128, 120, 111, 100],
        14: [1272, 820, 601, 463, 365, 290, 230, 185, 156, 138, 128, 120, 111, 100],
        15: [1398, 915, 674, 524, 416, 334, 268, 215, 177, 153, 137, 128, 120, 111, 100],
        16: [1523, 1015, 750, 587, 469, 380, 308, 249, 203, 171, 150, 137, 128, 120, 111, 100],
        17: [1649, 1120, 830, 652, 525, 428, 351, 286, 233, 194, 166, 149, 137, 128, 121, 111, 100],
        18: [1775, 1228, 912, 721, 584, 479, 396, 326, 268, 221, 187, 163, 147, 137, 129, 121, 112, 100],
        19: [1900, 1340, 998, 792, 645, 532, 442, 368, 305, 252, 211, 181, 161, 147, 137, 129, 121, 112, 100],
        20: [2028, 1456, 1101, 866, 710, 588, 491, 413, 345, 287, 239, 203, 178, 158, 147, 137, 129, 121, 112, 100],
        21: [2124, 1547, 1182, 934, 770, 642, 539, 456, 385, 322, 270, 227, 197, 174, 157, 147, 137, 129, 121, 112, 100],
        22: [2327, 1716, 1322, 1050, 867, 727, 612, 520, 442, 373, 313, 263, 224, 196, 174, 159, 149, 139, 131, 122, 113, 100],
        23: [2428, 1813, 1409, 1126, 932, 786, 666, 567, 486, 413, 350, 295, 250, 217, 192, 171, 159, 148, 139, 131, 123, 113, 100],
        24: [2529, 1910, 1496, 1203, 999, 847, 721, 617, 531, 456, 388, 330, 280, 240, 211, 187, 169, 159, 148, 139, 131, 123, 113, 100],
        25: [2630, 2008, 1584, 1282, 1066, 908, 777, 668, 577, 499, 429, 366, 312, 267, 232, 206, 184, 169, 158, 148, 140, 132, 123, 113, 100],
        26: [2732, 2106, 1673, 1362, 1136, 971, 835, 720, 624, 543, 470, 404, 347, 297, 256, 226, 202, 181, 168, 158, 148, 140, 132, 123, 113, 100],
        27: [2833, 2204, 1763, 1443, 1206, 1034, 894, 774, 673, 588, 513, 444, 383, 329, 284, 248, 221, 197, 179, 168, 158, 148, 140, 132, 123, 113, 100],
        28: [2934, 2303, 1853, 1525, 1279, 1098, 953, 829, 724, 634, 556, 485, 420, 363, 314, 273, 241, 216, 194, 178, 168, 158, 148, 141, 132, 123, 113, 100],
        29: [3035, 2402, 1944, 1608, 1352, 1164, 1014, 886, 775, 681, 600, 527, 459, 399, 346, 300, 263, 235, 211, 191, 178, 168, 157, 149, 141, 132, 124, 113, 100],
        30: [3137, 2500, 2035, 1692, 1427, 1231, 1076, 943, 828, 730, 645, 570, 500, 437, 380, 331, 289, 256, 230, 207, 189, 178, 167, 157, 149, 141, 133, 124, 113, 100]
    }
    
    if buy_ins not in LEAGUE_MATRIX:
        return 100
        
    points_list = LEAGUE_MATRIX[buy_ins]
    list_index = rank - 1
    
    if list_index >= len(points_list) or list_index < 0:
        return 100  
        
    return points_list[list_index]

def get_latest_results_from_google():
    """Connects to Google Sheets and pulls raw cell strings from the last row."""
    print("Connecting to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("Missing 'credentials.json' file! Please add it to run live syncing.")
        
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    workbook = client.open(GOOGLE_SHEET_NAME)
    sheet = workbook.sheet1
    all_rows = sheet.get_all_values()
    
    cleaned_rows = [row for row in all_rows if any(cell.strip() for cell in row)]
    if len(cleaned_rows) <= 1:
        raise ValueError("Google sheet contains no response records yet.")
        
    latest_row = cleaned_rows[-1]
    
    if len(latest_row) >= 3:
        target_date = str(latest_row[1]).strip()
        raw_standings_text = latest_row[2]
    else:
        target_date = str(latest_row[0]).strip()
        raw_standings_text = latest_row[1]
    
    raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
    return target_date, raw_list

def initialize_league():
    """Creates local data sheets structure if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        leaderboard_df = pd.DataFrame(columns=["Player Name", "Total Points", "Games Played"])
        history_df = pd.DataFrame(columns=["Date", "Player Name", "Position", "Points"])
        with pd.ExcelWriter(DB_FILE, engine="openpyxl") as writer:
            leaderboard_df.to_excel(writer, sheet_name="Leaderboard", index=False)
            history_df.to_excel(writer, sheet_name="Game History", index=False)
        print(f"Created clean database: {DB_FILE}")

def record_weekly_game(date, standings, is_historical=False):
    """Processes standings, logs to excel safely, and updates scoreboard."""
    initialize_league()
    
    # Copy standings list to prevent original data mutate issues
    local_standings = list(standings)
    
    # Standard forms are logged bottom-up (last place to 1st). 
    # If your copy-pasted PDF list is already 1st down to Last, do not reverse it.
    if not is_historical:
        local_standings.reverse()
        
    total_players = len(local_standings)
    
    try:
        history_df = pd.read_excel(DB_FILE, sheet_name="Game History")
    except Exception:
        history_df = pd.DataFrame(columns=["Date", "Player Name", "Position", "Points"])
        
    # Overwrite protection line
    history_df = history_df[history_df["Date"] != date]

    new_entries = []
    
    for index, raw_player_input in enumerate(local_standings):
        position = index + 1
        points = calculate_poker_points(total_players, position)
        
        lookup_key = raw_player_input.strip().lower()
        player_name = PLAYER_REGISTRY.get(lookup_key, raw_player_input.strip().title())
        
        new_entries.append({
            "Date": date,
            "Player Name": player_name,
            "Position": position,
            "Points": int(points)
        })
        
    new_game_df = pd.DataFrame(new_entries)
    updated_history = pd.concat([history_df, new_game_df], ignore_index=True)
    updated_history["Points"] = pd.to_numeric(updated_history["Points"], errors='coerce').fillna(0).astype(int)
    
    # Re-calculate clean leader totals
    leaderboard = updated_history.groupby("Player Name").agg(
        Total_Points=("Points", "sum"),
        Games_Played=("Date", "count")
    ).reset_index()
    
    leaderboard = leaderboard.sort_values(by="Total_Points", ascending=False)
    leaderboard.columns = ["Player Name", "Total Points", "Games Played"]
    
    # Save sheets
    with pd.ExcelWriter(DB_FILE, engine="openpyxl", mode="w") as writer:
        leaderboard.to_excel(writer, sheet_name="Leaderboard", index=False)
        updated_history.to_excel(writer, sheet_name="Game History", index=False)
        
    print(f"Successfully processed game date: {date} ({total_players} players)")

# =========================================================================
# THE HISTORICAL PDF BACKLOG DICTIONARY
# =========================================================================
# INSTRUCTIONS: I have pre-filled Week 1 and Week 2 with the clean arrays you extracted.
# Paste your remaining 14 weeks of data below following the exact same format!
# =========================================================================
HISTORICAL_GAMES = {
    "02-06-26": ['Brian Cox', 'Sam Townsend', 'Mike Craft', 'Nick Rouhani', 'Don Eyster', 'Dustan Mulkey', 'Steve Battard', 'Quinton Staton', 'Joe Hawkins', 'Todd Kinsell', 'John Alvenus', 'Jim Qualizza', 'Jeff Farrar', 'Bob Bowman', 'Jermaine Ford', 'David Lee', 'Frank Watts', 'John Hopkins', 'Mike Cercone', 'Rob Christian', 'Jeff McCleave', 'Mike Owen', 'Bill Roland', 'Bob Allen', 'Ryan Mulkey', 'Chris Richerson', 'James Arndt', 'Liora Volkovich'],
    "02-13-26": ['John Alvenus', 'Sam Townsend', 'John Hopkins', 'Steve Battard', 'Jeremy Otterson', 'David Lee', 'Mike Craft', 'Mike Cercone', 'Jeff Farrar', 'Brian Cox', 'Rob Christian', 'Bob Allen', 'Carlos Recalde', 'C.J. Zamora', 'Ryan Mulkey', 'James Arndt', 'Jermaine Ford', 'Don Eyster', 'Chris Martin', 'Dustan Mulkey', 'Todd Kinsell', 'Jeff McCleave', 'Frank Watts', 'Chris Richerson', 'Miguel Miranda', 'Nick Rouhani'],
    "02-20-26": ['C.J. Zamora', 'Joe Hawkins', 'Jeff McCleave', 'Jim Qualizza', 'Steve Battard', 'Dustan Mulkey', 'Nick Rouhani', 'Jeremy Otterson', 'Chris Richerson', 'John Alvenus', 'Rob Christian', 'Sam Townsend', 'John Hopkins', 'Bob Allen', 'Dustin Harper', 'Jeff Farrar', 'Liora Volkovich', 'Jermaine Ford', 'Mike Craft', 'Ryan Mulkey', 'James Arndt', 'Mike Cercone', 'Brian Cox', 'Frank Watts', 'Todd Kinsell', 'Quinton Staton', 'David Lee', 'Carlos Recalde', 'Mike Owen'],
    "02-27-26": ['Nick Rouhani', 'John Alvenus', 'Frank Watts', 'Mike Cercone', 'Ryan Mulkey', 'Jeff McCleave', 'Mike Owen', 'Jeremy Otterson', 'Joe Hawkins', 'Mike Craft', 'Chris Richerson', 'Rob Christian', 'Todd Kinsell', 'Quinton Staton', 'John Hopkins', 'Jermaine Ford', 'Scotty Cutright', 'Carlos Recalde', 'Bob Allen', 'Jeff Farrar', 'James Arndt', 'Dustan Mulkey', 'Jim Qualizza', 'Chris Martin', 'Sam Townsend', 'Liora Volkovich', 'C.J. Zamora', 'Brian Cox', 'Steve Battard', 'David Lee'],
    "03-06-26": ['Dustan Mulkey', 'Todd Kinsell', 'Chris Richerson', 'Tom Griffin', 'Dustin Harper', 'Brian Cox', 'David Lee', 'Don Eyster', 'Joe Hawkins', 'C.J. Zamora', 'Steve Battard', 'Scotty Cutright', 'Liora Volkovich', 'Jeff McCleave', 'Bob Allen', 'Jermaine Ford', 'Phillip Johnson', 'Mike Cercone', 'Jim Qualizza', 'John Alvenus', 'Mike Craft', 'Sam Townsend', 'James Arndt', 'Quinton Staton', 'Nick Rouhani', 'Ryan Mulkey', 'John Hopkins', 'Travis Harvey', 'Rob Christian', 'Bill Roland'],
    "03-13-26": ['James Arndt', 'Nick Rouhani', 'Dustan Mulkey', 'Chris Richerson', 'Don Eyster', 'John Hopkins', 'Brian Cox', 'Steve Battard', 'Scotty Cutright', 'Jeff Farrar', 'Mike Cercone', 'Rob Christian', 'Mark Hoffman', 'Chris Martin', 'Todd Kinsell', 'Liora Volkovich', 'Jeremy Otterson', 'Jeff McCleave', 'Carlos Recalde', 'Sam Townsend', 'Mike Craft', 'Ryan Mulkey', 'Mike Owen', 'Quinton Staton', 'Daniel Cook', 'Frank Watts', 'Jermaine Ford', 'John Alvenus', 'Bob Allen', 'David Lee'],
    "03-20-26": ['Frank Watts', 'Miguel Miranda', 'Ryan Mulkey', 'Todd Kinsell', 'Dustan Mulkey', 'Dustin Harper', 'Mike Owen', 'Brian Cox', 'David Lee', 'John Hopkins', 'Chris Richerson', 'Jeff Farrar', 'Jeff McCleave', 'Jermaine Ford', 'Bob Allen', 'James Arndt', 'Jim Qualizza', 'Scotty Cutright', 'Mike Craft', 'Sam Townsend', 'Carlos Recalde', 'John Alvenus', 'Rob Christian', 'Phillip Johnson', 'Chris Martin', 'Mike Cercone', 'Steve Battard', 'Quinton Staton', 'Jeremy Otterson', 'Nick Rouhani'],
    "03-27-26": ['Bob Allen', 'Jermaine Ford', 'Jeff McCleave', 'Nick Rouhani', 'Ryan Mulkey', 'Mike Craft', 'Chris Richerson', 'Rob Christian', 'Carlos Recalde', 'Mike Cercone', 'John Alvenus', 'Jeff Farrar', 'Bill Roland', 'Brian Cox', 'C.J. Zamora', 'Don Eyster', 'Bob Bowman', 'Todd Kinsell', 'Steve Battard', 'Mike Owen', 'Dustan Mulkey', 'Sam Townsend', 'James Arndt', 'Jim Qualizza', 'Jeremy Otterson', 'Liora Volkovich', 'Scotty Cutright', 'David Lee', 'Quinton Staton', 'John Hopkins'],
    "04-03-26": ['Bill Roland', 'James Arndt', 'David Lee', 'Steve Battard', 'John Alvenus', 'Brian Cox', 'Jeff McCleave', 'Jim Qualizza', 'Todd Kinsell', 'Sam Townsend', 'Chris Martin', 'Mike Cercone', 'Scotty Cutright', 'Dustan Mulkey', 'John Hopkins', 'Jeff Farrar', 'Ryan Mulkey', 'Chris Richerson', 'Don Eyster', 'C.J. Zamora', 'Jeremy Otterson', 'Jermaine Ford', 'Nick Rouhani', 'Mike Owen', 'Mike Craft', 'Frank Watts', 'Quinton Staton', 'Bob Allen', 'Rob Christian'],
    "04-10-26": ['Brian Cox', 'Jim Qualizza', 'Frank Watts', 'David Lee', 'Chris Martin', 'Jeff McCleave', 'Ryan Mulkey', 'Dustan Mulkey', 'Carlos Recalde', 'C.J. Zamora', 'Jermaine Ford', 'John Hopkins', 'Mike Craft', 'Mike Owen', 'Todd Kinsell', 'Bob Bowman', 'John Alvenus', 'Scotty Cutright', 'Rob Christian', 'Nick Rouhani', 'Sam Townsend', 'Bill Roland', 'Phillip Johnson', 'James Arndt', 'Travis Harvey', 'Bob Allen', 'Joe Hawkins', 'Mike Cercone', 'Steve Battard', 'Chris Richerson'],
    "04-17-26": ['Joe Hawkins', 'Carlos Recalde', 'Mike Craft', 'Todd Kinsell', 'Sam Townsend', 'Steve Battard', 'Bob Bowman', 'Bill Roland', 'Phillip Johnson', 'Jim Qualizza', 'James Arndt', 'Scotty Cutright', 'Mike Owen', 'Dustan Mulkey', 'David Lee', 'Brian Cox', 'Quinton Staton', 'Jeff McCleave', 'Jeff Farrar', 'John McClain', 'John Alvenus', 'C.J. Zamora', 'Chris Richerson', 'Bob Allen', 'Nick Rouhani', 'Mike Cercone', 'Ryan Mulkey', 'Jeremy Otterson', 'Rob Christian', 'Jermaine Ford'],
    "04-24-26": ['Dustan Mulkey', 'John McClain', 'C.J. Zamora', 'Mike Craft', 'Steve Battard', 'John Hopkins', 'Brian Cox', 'Mike Cercone', 'Jim Qualizza', 'Scotty Cutright', 'Jeff McCleave', 'Jermaine Ford', 'Ryan Mulkey', 'Quinton Staton', 'Joe Hawkins', 'Sam Townsend', 'Don Eyster', 'Nick Rouhani', 'John Alvenus', 'Carlos Recalde', 'Todd Kinsell', 'Jeremy Otterson', 'Chris Richerson', 'Mike Owen', 'James Arndt', 'Jeff Farrar', 'Miguel Miranda', 'David Lee', 'Bob Allen', 'Rob Christian'],
    "05-01-26": ['Travis Harvey', 'Ryan Mulkey', 'Jim Qualizza', 'Jeff McCleave', 'David Lee', 'Brian Cox', 'Bill Roland', 'Phillip Johnson', 'John Hopkins', 'Quinton Staton', 'Jeff Farrar', 'Chris Martin', 'Todd Kinsell', 'Mike Cercone', 'Dustan Mulkey', 'Mike Owen', 'C.J. Zamora', 'Jeremy Otterson', 'Carlos Recalde', 'Bob Allen', 'Frank Watts', 'Chris Richerson', 'James Arndt', 'Scotty Cutright', 'John Alvenus', 'Don Eyster', 'Steve Battard', 'Mike Craft', 'Nick Rouhani', 'Rob Christian'],
    "05-08-26": ['Ryan Mulkey', 'Jeremy Otterson', 'Mike Owen', 'Mike Craft', 'Quinton Staton', 'John Alvenus', 'Scotty Cutright', 'Liora Volkovich', 'David Lee', 'Jim Qualizza', 'Joe Hawkins', 'C.J. Zamora', 'Chris Richerson', 'Chris Martin', 'Carlos Recalde', 'Travis Harvey', 'Frank Watts', 'John Hopkins', 'John McClain', 'Brian Cox', 'Rob Christian', 'Mike Cercone', 'Steve Battard', 'Jermaine Ford', 'Jeff McCleave', 'Nick Rouhani', 'James Arndt', 'Bob Bowman', 'Bob Allen', 'Dustan Mulkey'],
    "05-15-26": ['Quinton Staton', 'John McClain', 'Jeff McCleave', 'Miguel Miranda', 'Don Eyster', 'Jim Qualizza', 'Frank Watts', 'Joe Hawkins', 'Bill Roland', 'Bob Bowman', 'Mike Owen', 'Brian Cox', 'John Hopkins', 'Mike Craft', 'Rob Christian', 'Nick Rouhani', 'Bob Allen', 'Sam Townsend', 'C.J. Zamora', 'Jeff Farrar', 'David Lee', 'Todd Kinsell', 'John Alvenus', 'Jeremy Otterson', 'James Arndt', 'Ryan Mulkey', 'Scotty Cutright', 'Chris Richerson', 'Dustan Mulkey', 'Steve Battard'],
    "05-22-26": ['Rob Christian', 'Mike Craft', 'Bill Roland', 'Mike Cercone', 'Liora Volkovich', 'Brian Cox', 'John Alvenus', 'Jermaine Ford', 'Dustan Mulkey', 'Carlos Recalde', 'Steve Battard', 'C.J. Zamora', 'Nick Rouhani', 'Jim Qualizza', 'Sam Townsend', 'Chris Martin', 'Bob Allen', 'Ryan Mulkey', 'Quinton Staton', 'Jeff McCleave', 'David Lee', 'Todd Kinsell', 'John Hopkins', 'Jeff Farrar', 'Scotty Cutright', 'Jeremy Otterson', 'Mike Owen', 'James Arndt', 'Chris Richerson', 'Joe Hawkins'],
}

# =========================================================================
# RUN COORDINATOR CONTROL HUB
# =========================================================================
if __name__ == "__main__":
    initialize_league()
    
    # 1. Check local Excel storage for recorded matches
    try:
        current_history_df = pd.read_excel(DB_FILE, sheet_name="Game History")
        loaded_dates = set(current_history_df["Date"].astype(str).unique())
    except Exception:
        loaded_dates = set()
        
    print("--- STARTING LEAGUE DATA WORKFLOW ---")
    
    # 2. Automatically process any historical backlog missing from Excel
    backlog_count = 0
    for game_date, player_list in HISTORICAL_GAMES.items():
        if game_date not in loaded_dates and len(player_list) > 0:
            if backlog_count == 0:
                print("\n[BACKLOG] Found unimported PDF records. Processing entries...")
            record_weekly_game(date=game_date, standings=player_list, is_historical=True)
            backlog_count += 1
            
    if backlog_count > 0:
        print(f"[BACKLOG] Completed. {backlog_count} historical games successfully tracked.")
    else:
        print("[BACKLOG] Up to date. No new historical logs to import.")
        
    # 3. Synchronize Live Submissions from Google Forms
    print("\n--- SYNCING LIVE WEEKLY SHEET ---")
    try:
        live_date, live_standings = get_latest_results_from_google()
        
        # Pull fresh dates list right after backlog processing
        current_history_df = pd.read_excel(DB_FILE, sheet_name="Game History")
        loaded_dates = set(current_history_df["Date"].astype(str).unique())
        
        if live_date in loaded_dates:
            print(f"Live row date ({live_date}) is already recorded in the database. Scoreboard is current!")
        else:
            print(f"New game night discovered from Google Form: {live_date}!")
            record_weekly_game(date=live_date, standings=live_standings, is_historical=False)
            
    except Exception as e:
        print(f"Skipping live sheet check: {e}")
        print("Note: If you don't have credentials.json ready yet, historical batching still worked fine.")

    # 4. Print Master Scoreboard Summary Line
    print("\n--- FINAL MASTER LEAGUE SCOREBOARD STANDINGS ---")
    final_leaderboard = pd.read_excel(DB_FILE, sheet_name="Leaderboard")
    print(final_leaderboard.to_string(index=False))
