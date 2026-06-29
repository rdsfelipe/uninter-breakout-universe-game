"""The player paddle: keyboard movement clamped to the play field."""
import pygame

from code.Const import (PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED,
                        PADDLE_Y_OFFSET, GAME_WIDTH, GAME_HEIGHT)
from code.Assets import get_paddle_sprite


class Paddle:
    def __init__(self, sprite_row: int = 0):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.surf = get_paddle_sprite(sprite_row)
        self.rect = self.surf.get_rect(
            centerx=GAME_WIDTH // 2,
            bottom=GAME_HEIGHT - PADDLE_Y_OFFSET
        )

    def move(self):
        pressed_key = pygame.key.get_pressed()
        if pressed_key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        if pressed_key[pygame.K_RIGHT] and self.rect.right < GAME_WIDTH:
            self.rect.x += PADDLE_SPEED

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)

    def reset(self):
        self.rect.centerx = GAME_WIDTH // 2
