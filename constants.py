# ============================================
# ==           GLOBAL CONSTANTS             ==
# ============================================
# Some values are used by lots of parts of the
# code and it would be helpful to be able to
# keep track of them universally or to be able
# to change them in one place. They go here.

# Directions

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
UP_LEFT = 10
UP_RIGHT = 11
DOWN_RIGHT = 12
DOWN_LEFT = 13

# Buttons
# (Directions double as buttons for those directions)
JUMP = 4
FIRE = 5
ITEM = 6
PAUSE = 7
TANK_DOOR = 8

# Physics Information
GRAVITY_STRENGTH = 0.2
TERMINAL_VELOCITY = 4

# Screen Information
SCREEN_W = 640
SCREEN_H = 480
STARTING_CAMERA_ZOOM = 1.5

# Map Information

TILESIZE = 32
BLOCK_LAYER = 1 # This is the layerID in Tiled we use for solidity checks with tiles on the map.
BACKGROUND_LAYER = 3
FOREGROUND_LAYER_1 = 4
FOREGROUND_LAYER_2 = 6
OBJECT_LAYER = 5

# Sprite IDs
PLAYER = 0
ENEMY = 100

# Sprite State Flags
# Each Sprite will have their own unique state flags, but we'll make some of them
# universal because they matter for sprite_handler things like collision checks.
DYING = -1
DEAD = -2

# Game States
MAIN_MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

# Player control states
SOLDIER_ACTIVE = 0
TANK_ACTIVE = 1
NONE_ACTIVE = 2

# Graphics information
TRANSPARENT_COLOR = 0