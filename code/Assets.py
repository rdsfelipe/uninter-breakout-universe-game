"""Sprite loader for entities, sliced from the sheets in ``assets/``.

Images are loaded once and the scaled sprites are cached, so creating many
bricks (or recreating levels) never re-reads or re-scales an image. All
sprites are nearest-neighbour scaled to keep the pixel-art crisp.
"""
import pygame

from code.Const import (PADDLE_WIDTH, PADDLE_HEIGHT, BALL_SIZE,
                        BRICK_WIDTH, BRICK_HEIGHT, HEART_SIZE,
                        GAME_WIDTH, GAME_HEIGHT, s, asset_path)

_SHEETS = {}
_CACHE = {}

# bricks.png: middle group has the rounded brick in three damage states.
# Rows set the brick color; columns set the damage state.
_BRICK_ROWS = 6
_BRICK_BASE_X = 112
_BRICK_CELL_SIZE = (32, 16)

# paddles_and_balls.png: each row is a different color palette.
# Use paddle model 1 (left), then stretch it to the gameplay size.
_PADDLE_BASE_X = 0
_PADDLE_CELL_SIZE = (32, 16)
_BALL_BASE_X = 176
_BALL_CELL_SIZE = (14, 16)
_HEART_FILE = 'hearts.png'
_HEART_CELL_SIZE = (16, 16)
_HEART_FILLED_FRAME = 7
_LOGO_WIDTH = s(420)


def _scale_to_width(surface: pygame.Surface, width: int) -> pygame.Surface:
    scale = width / surface.get_width()
    height = round(surface.get_height() * scale)
    return pygame.transform.smoothscale(surface, (width, height))


def _scale_cover(surface: pygame.Surface, width: int, height: int) -> pygame.Surface:
    """Scale a surface to fully cover width x height, cropping any overflow."""
    src_w, src_h = surface.get_size()
    scale = max(width / src_w, height / src_h)
    scaled = pygame.transform.smoothscale(
        surface, (round(src_w * scale), round(src_h * scale)))
    out = pygame.Surface((width, height)).convert()
    out.blit(scaled, scaled.get_rect(center=(width // 2, height // 2)))
    return out


def _load_image(name: str) -> pygame.Surface:
    """Load an image from ``assets/`` once and cache the raw surface."""
    surface = _SHEETS.get(name)
    if surface is None:
        surface = pygame.image.load(asset_path(name)).convert_alpha()
        _SHEETS[name] = surface
    return surface


def _slice(sheet: pygame.Surface, rect: pygame.Rect) -> pygame.Surface:
    """Crop a cell and trim surrounding transparent padding."""
    cell = sheet.subsurface(rect).copy()
    bbox = cell.get_bounding_rect(min_alpha=10)
    return cell.subsurface(bbox).copy()


def _sprite_row(row: int) -> int:
    return max(0, min(5, row))


def get_paddle_sprite(sprite_row: int = 0) -> pygame.Surface:
    sprite_row = _sprite_row(sprite_row)
    key = ('paddle', sprite_row)
    sprite = _CACHE.get(key)
    if sprite is None:
        cell_w, cell_h = _PADDLE_CELL_SIZE
        cell = pygame.Rect(_PADDLE_BASE_X, sprite_row * cell_h, cell_w, cell_h)
        raw = _slice(_load_image('paddles_and_balls.png'), cell)
        sprite = pygame.transform.scale(raw, (PADDLE_WIDTH, PADDLE_HEIGHT))
        _CACHE[key] = sprite
    return sprite


def get_ball_sprite(sprite_row: int = 0) -> pygame.Surface:
    sprite_row = _sprite_row(sprite_row)
    key = ('ball', sprite_row)
    sprite = _CACHE.get(key)
    if sprite is None:
        cell_w, cell_h = _BALL_CELL_SIZE
        cell = pygame.Rect(_BALL_BASE_X, sprite_row * cell_h, cell_w, cell_h)
        raw = _slice(_load_image('paddles_and_balls.png'), cell)
        sprite = pygame.transform.scale(raw, (BALL_SIZE, BALL_SIZE))
        _CACHE[key] = sprite
    return sprite


def get_brick_sprite(max_hp: int, hp: int, color_row: int) -> pygame.Surface:
    color_row = max(0, min(_BRICK_ROWS - 1, color_row))
    key = ('brick', max_hp, hp, color_row)
    sprite = _CACHE.get(key)
    if sprite is None:
        # Spread the 3 damage frames (clean/cracked/broken) across the brick's
        # full HP range so tough blocks don't look broken after a single hit.
        if max_hp > 1 and hp < max_hp:
            fraction = (max_hp - hp) / max_hp
            damage_state = max(0, min(2, int(fraction * 3)))
        else:
            damage_state = 0
        cell_w, cell_h = _BRICK_CELL_SIZE
        cell = pygame.Rect(
            _BRICK_BASE_X + damage_state * cell_w, color_row * cell_h,
            cell_w, cell_h)
        raw = _slice(_load_image('bricks.png'), cell)
        sprite = pygame.transform.scale(raw, (BRICK_WIDTH, BRICK_HEIGHT))
        _CACHE[key] = sprite
    return sprite


def get_heart_sprite() -> pygame.Surface:
    sprite = _CACHE.get('heart')
    if sprite is None:
        cell_w, cell_h = _HEART_CELL_SIZE
        cell = pygame.Rect(_HEART_FILLED_FRAME * cell_w, 0, cell_w, cell_h)
        raw = _load_image(_HEART_FILE).subsurface(cell).copy()
        sprite = pygame.transform.scale(raw, (HEART_SIZE, HEART_SIZE))
        _CACHE['heart'] = sprite
    return sprite


def get_background(name: str) -> pygame.Surface:
    key = ('background', name)
    background = _CACHE.get(key)
    if background is None:
        raw = _load_image(name)
        background = _scale_cover(raw, GAME_WIDTH, GAME_HEIGHT)
        _CACHE[key] = background
    return background


def get_logo_sprite() -> pygame.Surface:
    sprite = _CACHE.get('logo')
    if sprite is None:
        raw = _load_image('logo.png')
        bbox = raw.get_bounding_rect(min_alpha=10)
        raw = raw.subsurface(bbox).copy()
        sprite = _scale_to_width(raw, _LOGO_WIDTH)
        _CACHE['logo'] = sprite
    return sprite
