"""Game-wide constants, asset paths and per-level configuration.

Layout numbers are authored in a logical design space (``BASE_*``) and scaled
into the render resolution through :func:`s`, so the whole game can be retuned
by changing a single resolution pair.
"""
import os
import sys

import pygame

# Logical design resolution. All gameplay/layout numbers below are authored
# in this coordinate space and then multiplied by SCALE.
BASE_WIDTH = 576
BASE_HEIGHT = 324

# Internal render resolution (what game_surface is actually rendered at).
# Kept at 16:9. Rendering here instead of at BASE_* keeps geometry/text crisp
# when the surface is scaled to the real window. Bump this for sharper output.
GAME_WIDTH = 1280
GAME_HEIGHT = 720

# Initial window size. Matches the internal render resolution so the default
# view maps 1:1 (no scaling, no blur). On resize the game_surface is scaled to
# *cover* (fill) the window, so it never letterboxes.
WINDOW_WIDTH = GAME_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT

# Uniform scale from the logical design space to the render space.
SCALE = GAME_WIDTH / BASE_WIDTH


def s(value):
    """Scale a logical (BASE_*) value into render-space pixels."""
    return round(value * SCALE)


def asset_path(*parts):
    """Return an asset path that works both locally and inside PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, 'assets', *parts)


def window_to_game(window, pos):
    """Map a window pixel position to game-surface coordinates (cover scaling)."""
    win_w, win_h = window.get_size()
    scale = max(win_w / GAME_WIDTH, win_h / GAME_HEIGHT)
    scaled_w = round(GAME_WIDTH * scale)
    scaled_h = round(GAME_HEIGHT * scale)
    ox = (win_w - scaled_w) // 2
    oy = (win_h - scaled_h) // 2
    x, y = pos
    if not (ox <= x < ox + scaled_w and oy <= y < oy + scaled_h):
        return None
    return (
        (x - ox) * GAME_WIDTH / scaled_w,
        (y - oy) * GAME_HEIGHT / scaled_h,
    )


# Pixel-art font used across all screens.
FONT_PATH = asset_path("m5x7.ttf")
FONT_SIZE_STEP = 8

# Cache fonts by size.
_FONT_CACHE = {}


def get_font(size):
    """Return a cached pixel font snapped to a crisp, even size."""
    size = max(FONT_SIZE_STEP, round(size / FONT_SIZE_STEP) * FONT_SIZE_STEP)
    font = _FONT_CACHE.get(size)
    if font is None:
        font = pygame.font.Font(FONT_PATH, size)
        _FONT_CACHE[size] = font
    return font


# Colors
C_WHITE = (255, 255, 255)
C_YELLOW = (255, 255, 128)

# Menu text styling
C_MENU_ACTIVE = (90, 235, 255)   # bright cyan matching the logo/background
C_MENU_IDLE = (255, 255, 255)    # high-contrast white for idle options
C_TEXT_OUTLINE = (10, 8, 22)     # near-black outline for readability

# Points awarded when a brick is destroyed, keyed by its starting HP.
BRICK_SCORE = {
    5: 50,
    4: 40,
    3: 30,
    2: 20,
    1: 10,
}

# Brick color row in bricks.png keyed by HP. Color is a *predictable*
# indicator of strength, escalating from soft warm tones to a hard stone block.
BRICK_HP_COLOR_ROW = {
    1: 2,  # gold
    2: 3,  # orange
    3: 4,  # red
    4: 5,  # maroon
    5: 0,  # stone (toughest)
}

# Paddle
PADDLE_WIDTH = s(80)
PADDLE_HEIGHT = s(10)
PADDLE_SPEED = s(5)
PADDLE_Y_OFFSET = s(30)  # distance from bottom

# Ball
BALL_SIZE = s(8)
BALL_SPEED = s(3)
BALL_MIN_VERTICAL_RATIO = 0.45

# Bricks layout
BRICK_WIDTH = s(48)
BRICK_HEIGHT = s(14)
BRICK_GAP = s(4)
BRICK_TOP_OFFSET = s(50)

# Player
PLAYER_LIVES = 3
HEART_SIZE = 24
HEART_GAP = 8

# Menu
MENU_OPTION = ('NEW GAME', 'SCORES', 'EXIT')

# Score name entry
SCORE_NAME_MAX_LEN = 4
SCORE_NAME_DEFAULT = 'NONE'

# Audio
MUSIC_VOLUME = 0.3

# Level configs
LEVEL_CONFIG = {
    'Level1': {
        'display_name': 'LEVEL 1',
        'music': 'level-1.mp3',
        'background': 'bg-1.png',
        'sprite_row': 2,  # gold: strong contrast against the night city
        'ball_speed': s(3),
        'rows': 5,
        'cols': 10,
        'max_hp': 2,
        'brick_hp_pattern': (
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
            (2, 1, 2, 1, 2, 1, 2, 1, 2, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        ),
    },
    'Level2': {
        'display_name': 'LEVEL 2',
        'music': 'level-2.mp3',
        'background': 'bg-2.png',
        'sprite_row': 4,  # magenta: pops against the purple mountain scene
        'ball_speed': s(3.6),
        'rows': 6,
        'cols': 10,
        'max_hp': 4,
        'brick_hp_pattern': (
            (4, 3, 4, 3, 4, 4, 3, 4, 3, 4),
            (3, 4, 3, 4, 3, 3, 4, 3, 4, 3),
            (3, 3, 2, 3, 3, 3, 2, 3, 3, 3),
            (2, 3, 2, 2, 3, 3, 2, 2, 3, 2),
            (2, 2, 2, 1, 2, 2, 1, 2, 2, 2),
            (1, 1, 2, 1, 1, 1, 2, 1, 1, 1),
        ),
    },
    'Level3': {
        'display_name': 'LEVEL 3',
        'music': 'level-3.mp3',
        'background': 'bg-3.png',
        'sprite_row': 3,  # orange: high contrast in the blue aquatic scene
        'ball_speed': s(4.1),
        'rows': 7,
        'cols': 10,
        'max_hp': 5,
        'brick_hp_pattern': (
            (5, 4, 5, 4, 5, 5, 4, 5, 4, 5),
            (4, 5, 4, 4, 5, 5, 4, 4, 5, 4),
            (4, 4, 3, 4, 4, 4, 3, 4, 4, 4),
            (3, 4, 3, 3, 4, 4, 3, 3, 4, 3),
            (3, 3, 2, 3, 3, 3, 2, 3, 3, 3),
            (2, 2, 3, 2, 2, 2, 3, 2, 2, 2),
            (1, 2, 2, 1, 2, 2, 1, 2, 2, 1),
        ),
    },
}

# Score positions
SCORE_POS = {
    'Title': (GAME_WIDTH / 2, s(50)),
    'EnterName': (GAME_WIDTH / 2, s(80)),
    'Label': (GAME_WIDTH / 2, s(90)),
    'Name': (GAME_WIDTH / 2, s(110)),
    0: (GAME_WIDTH / 2, s(110)),
    1: (GAME_WIDTH / 2, s(130)),
    2: (GAME_WIDTH / 2, s(150)),
    3: (GAME_WIDTH / 2, s(170)),
    4: (GAME_WIDTH / 2, s(190)),
    5: (GAME_WIDTH / 2, s(210)),
    6: (GAME_WIDTH / 2, s(230)),
    7: (GAME_WIDTH / 2, s(250)),
    8: (GAME_WIDTH / 2, s(270)),
    9: (GAME_WIDTH / 2, s(290)),
}
