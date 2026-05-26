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
        16:
