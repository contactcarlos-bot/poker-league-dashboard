import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================================================================
# CONFIGURATION & UNIQUE PLAYER REGISTRY
# =========================================================================
GOOGLE_SHEET_NAME = "Dirty Town Poker League Input (Responses)"

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
    return LEAGUE_MATRIX.get(buy_ins, [100])[rank - 1] if rank <= buy_ins else 100

def get_google_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("Missing 'credentials.json' keyfile!")
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

def process_unrecorded_games():
    client = get_google_sheets_client()
    workbook = client.open(GOOGLE_SHEET_NAME)
    
    # Open tabs
    form_sheet = workbook.worksheet("Form Responses 1")
    history_sheet = workbook.worksheet("Database History")
    
    # Initialize headers if sheet is empty
    history_values = history_sheet.get_all_values()
    if not history_values:
        history_sheet.append_row(["Date", "Player Name", "Position", "Points"])
        existing_dates = set()
    else:
        existing_dates = set(row[0] for row in history_values[1:])
        
    form_rows = form_sheet.get_all_values()
    cleaned_form_rows = [row for row in form_rows if any(cell.strip() for cell in row)]
    
    if len(cleaned_form_rows) <= 1:
        print("No live submissions found in Google Forms.")
        return

    new_database_entries = []
    processed_any = False

    # Process live form rows chronologically
    for row in cleaned_form_rows[1:]:
        target_date = str(row[1]).strip() if len(row) >= 3 else str(row[0]).strip()
        raw_standings_text = row[2] if len(row) >= 3 else row[1]
        
        if target_date in existing_dates:
            continue
            
        print(f"Processing missing game date: {target_date}...")
        raw_list = [line.strip() for line in str(raw_standings_text).split('\n') if line.strip()]
        raw_list.reverse()  # Match bottom-up structure
        
        total_players = len(raw_list)
        for index, raw_player_input in enumerate(raw_list):
            position = index + 1
            points = calculate_poker_points(total_players, position)
            lookup_key = raw_player_input.strip().lower()
            player_name = PLAYER_REGISTRY.get(lookup_key, raw_player_input.strip().title())
            
            new_database_entries.append([target_date, player_name, position, int(points)])
            
        existing_dates.add(target_date)
        processed_any = True

    if new_database_entries:
        history_sheet.append_rows(new_database_entries)
        print(f"🎉 Appended {len(new_database_entries)} scoring records safely to Google Cloud!")
    else:
        print("All cloud logs match. Your online database history tab is completely up to date!")

if __name__ == "__main__":
    print("--- RUNNING 100% CLOUD LEAGUE MANAGER ---")
    process_unrecorded_games()
