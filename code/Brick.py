"""A destructible brick with HP-driven scoring and damage sprites."""
import pygame

from code.Const import BRICK_SCORE
from code.Assets import get_brick_sprite


class Brick:
    def __init__(self, x: int, y: int, hp: int, color_row: int):
        self.hp = hp
        self.max_hp = hp
        self.color_row = color_row
        self.score_value = BRICK_SCORE.get(hp, 10)
        self.surf = get_brick_sprite(self.max_hp, self.hp, self.color_row)
        self.rect = self.surf.get_rect(left=x, top=y)

    def hit(self) -> int:
        """Reduces HP. Returns score if destroyed, 0 otherwise."""
        self.hp -= 1
        if self.hp <= 0:
            return self.score_value
        # Keep the original color and advance through the damaged sprites.
        self.surf = get_brick_sprite(self.max_hp, self.hp, self.color_row)
        return 0

    def is_destroyed(self) -> bool:
        return self.hp <= 0

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)
