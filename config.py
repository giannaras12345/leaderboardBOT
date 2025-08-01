import os

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Channel where leaderboards will be posted

# RTanks Configuration
RTANKS_BASE_URL = "https://ratings.ranked-rtanks.online"
SCRAPE_INTERVAL = 3600  # seconds (1 hour)

# Pagination Configuration
PLAYERS_PER_PAGE = 10
MAX_PLAYERS = 100
TOTAL_PAGES = MAX_PLAYERS // PLAYERS_PER_PAGE

# Categories Configuration - Based on the actual website structure
LEADERBOARD_CATEGORIES = {
    "experience": {
        "name": "Experience Leaderboard",
        "section_index": 0,
        "description": "Top-100 players by earned experience"
    },
    "crystals": {
        "name": "Crystals Leaderboard", 
        "section_index": 1,
        "description": "Top-100 players by earned crystals"
    },
    "golds": {
        "name": "Golds Leaderboard",
        "section_index": 2, 
        "description": "Top-100 players by caught golds"
    },
    "kills": {
        "name": "Kills Leaderboard",
        "section_index": 3,
        "description": "Top-100 players by kills"
    }
}

# Embed Configuration
EMBED_COLOR = 0x00ff41  # Green color matching RTanks theme
EMBED_TIMEOUT = 3600  # 1 hour
