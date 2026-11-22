"""
Global configuration, game constants, balance tuning, and color palettes.
"""

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Grid dimensions
GRID_SIZE = 40  # 40x40 pixel cells
GRID_COLS = 24  # 24 * 40 = 960px width for battlefield
GRID_ROWS = 18  # 18 * 40 = 720px height for battlefield
SIDEBAR_WIDTH = WINDOW_WIDTH - (GRID_COLS * GRID_SIZE)  # 1280 - 960 = 320px for HUD & Shop

# Economy & Starting Rules
STARTING_CASH = 650
STARTING_LIVES = 20

# Military Tactical Color Palette
COLOR_BG = (18, 22, 25)              # Deep charcoal/night camouflage
COLOR_GRID_LINE = (28, 35, 40)       # Subdued grid lines
COLOR_PATH = (45, 50, 52)            # Dark asphalt combat path
COLOR_PATH_BORDER = (75, 82, 85)     # Road curbs/barriers
COLOR_SIDEBAR_BG = (24, 29, 34)      # Command console background
COLOR_PANEL_HEADER = (35, 44, 52)    # UI Panel banner
COLOR_ACCENT_GREEN = (60, 180, 100)  # Military radar green
COLOR_ACCENT_AMBER = (220, 150, 40)  # Warning amber
COLOR_ACCENT_RED = (210, 50, 45)     # Combat danger red
COLOR_ACCENT_BLUE = (50, 140, 220)   # High-tech electric blue
COLOR_TEXT_LIGHT = (235, 240, 245)
COLOR_TEXT_MUTED = (140, 150, 160)

# Tower Archetypes Specifications
TOWER_SPECS = {
    "vulcan": {
        "name": "Vulcan Gatling",
        "description": "Rapid-fire 20mm rotary cannon. Shreds light armor.",
        "cost": 150,
        "damage": 12,
        "range": 130,
        "fire_rate": 0.12,  # seconds between shots (~8.3 shots/sec)
        "bullet_speed": 750,
        "type": "kinetic",
        "color": (210, 140, 40),
        "upgrade_cost": 120,
    },
    "missile": {
        "name": "Patriot Battery",
        "description": "Guided rockets with explosive area-of-effect splash.",
        "cost": 250,
        "damage": 65,
        "splash_radius": 75,
        "range": 220,
        "fire_rate": 1.4,
        "bullet_speed": 340,
        "type": "explosive",
        "color": (210, 60, 50),
        "upgrade_cost": 200,
    },
    "sniper": {
        "name": "Anti-Materiel",
        "description": "Extreme range, armor-piercing kinetic rail rounds.",
        "cost": 300,
        "damage": 160,
        "range": 350,
        "fire_rate": 2.2,
        "bullet_speed": 1200,
        "type": "piercing",
        "color": (60, 180, 120),
        "upgrade_cost": 240,
    },
    "tesla": {
        "name": "EMP Shock Coil",
        "description": "Electrical pulse disabling vehicle systems and slowing movement.",
        "cost": 220,
        "damage": 22,
        "range": 120,
        "fire_rate": 0.85,
        "bullet_speed": 0,  # Instant beam
        "type": "electric",
        "slow_factor": 0.45,  # 55% speed reduction
        "slow_duration": 2.2, # seconds
        "color": (50, 160, 240),
        "upgrade_cost": 180,
    }
}

# Enemy Archetypes Specifications
ENEMY_SPECS = {
    "scout": {
        "name": "Scout Drone",
        "max_hp": 60,
        "speed": 140,
        "bounty": 15,
        "penalty": 1,
        "size": 12,
        "color": (160, 210, 80),
    },
    "technical": {
        "name": "Armed Technical",
        "max_hp": 160,
        "speed": 105,
        "bounty": 25,
        "penalty": 1,
        "size": 16,
        "color": (220, 180, 60),
    },
    "apc": {
        "name": "Armored APC",
        "max_hp": 400,
        "speed": 75,
        "bounty": 45,
        "penalty": 2,
        "size": 19,
        "color": (120, 130, 140),
    },
    "tank": {
        "name": "Main Battle Tank",
        "max_hp": 1000,
        "speed": 50,
        "bounty": 90,
        "penalty": 3,
        "size": 22,
        "color": (80, 100, 70),
    },
    "boss": {
        "name": "Mobile Dreadnought",
        "max_hp": 3200,
        "speed": 35,
        "bounty": 300,
        "penalty": 10,
        "size": 28,
        "color": (180, 40, 40),
    },
}
