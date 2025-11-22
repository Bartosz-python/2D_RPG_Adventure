"""
src/config/settings.py
Game configuration and constants
"""
import os

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Grid and tile settings
TILE_SIZE = 32
GRID_WIDTH = 40
GRID_HEIGHT = 22

# Player settings
PLAYER_SPEED = 300  # pixels per second
PLAYER_JUMP_VELOCITY = -400
GRAVITY = 1200
PLAYER_MAX_HP = 100
PLAYER_START_X = 100
# Player starts on top of ground (ground is at y=25, player height is 2 tiles, so y=23)
PLAYER_START_Y = 23 * TILE_SIZE  # Position player on top of ground blocks

# Combat settings
CLUB_DAMAGE = 10
SWORD_DAMAGE = 15
WAND_DAMAGE = 12
BOW_DAMAGE = 14
ATTACK_COOLDOWN = 0.5  # seconds
ENEMY_ATTACK_DAMAGE = 5
ENEMY_ATTACK_COOLDOWN = 1.0

# Inventory settings
VISIBLE_SLOTS = 6
HIDDEN_SLOTS = 6
TOTAL_SLOTS = VISIBLE_SLOTS + HIDDEN_SLOTS

# Equipment slots
EQUIPMENT_SLOTS = {
    'helmet': 0,
    'chestplate': 1,
    'leggings': 2,
    'boots': 3,
    'consumable1': 4,
    'consumable2': 5,
    'weapon': 6
}

# Day/Night cycle
DAY_NIGHT_CYCLE_DURATION = 600  # 10 minutes in seconds
EXPLORATION_RESET_DAYS = 7

# Block interaction
BLOCK_DESTROY_TIME = 0.5  # seconds per block

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# UI Colors
UI_BG_COLOR = (40, 40, 40, 200)
UI_BORDER_COLOR = (100, 100, 100)
HP_BAR_COLOR = (220, 20, 60)
HP_BAR_BG = (60, 60, 60)

# Game states
STATE_TUTORIAL = "tutorial"
STATE_WEAPON_SELECTION = "weapon_selection"
STATE_MAIN_MAP = "main_map"
STATE_EXPLORATION = "exploration"
STATE_COMBAT = "combat"

# Asset paths
ASSETS_PATH = "assets/"
SPRITES_PATH = ASSETS_PATH + "sprites/"
SOUNDS_PATH = ASSETS_PATH + "sounds/"
FONTS_PATH = ASSETS_PATH + "fonts/"

# Map types
MAP_MAIN = "main"
MAP_EXPLORATION = "exploration"

# Enemy types
ENEMY_TYPES = {
    'goblin': {'hp': 30, 'damage': 5, 'speed': 80, 'coins': 5},
    'skeleton': {'hp': 50, 'damage': 8, 'speed': 60, 'coins': 10},
    'orc': {'hp': 80, 'damage': 12, 'speed': 50, 'coins': 15}
}

# Item types
ITEM_TYPES = {
    'block': 'block',
    'coin': 'coin',
    'consumable': 'consumable',
    'weapon': 'weapon',
    'armor': 'armor'
}

# Building types
BUILDING_BEDROOM = "bedroom"
BUILDING_SMITH = "smith"
BUILDING_TAILOR = "tailor"
BUILDING_WITCH = "witch"
BUILDING_FIREPLACE = "fireplace"