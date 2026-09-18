"""
Mountain_Roy - Settings & Configuration
"""

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Map settings
MAP_WIDTH = 128
MAP_HEIGHT = 128
TILE_SIZE = 32

# Colors
COLORS = {
    "grass": (34, 139, 34),
    "forest": (0, 100, 0),
    "water": (65, 105, 225),
    "mountain": (105, 105, 105),
    "path": (139, 115, 85),
    "gold": (255, 215, 0),
    "wood": (139, 69, 19),
    "food": (220, 20, 60),
    
    # Units
    "player_unit": (100, 149, 237),
    "enemy_unit": (178, 34, 34),
    "hero": (255, 215, 0),
    "selected": (0, 255, 0),
    
    # UI
    "ui_bg": (50, 50, 50),
    "ui_text": (255, 255, 255),
    "ui_border": (100, 100, 100),
}

# Faction names
FACTION_NAMES = {
    "guardians": "Les Gardiens d'Aube",
    "legion": "La Légion des Cendres",
}
