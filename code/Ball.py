"""The ball: launch behaviour, wall bounces and anti-stall steering."""
import math

import pygame

from code.Const import (BALL_SIZE, BALL_SPEED, BALL_MIN_VERTICAL_RATIO,
                        GAME_WIDTH, GAME_HEIGHT)
from code.Assets import get_ball_sprite


class Ball:
    def __init__(self, speed: int = BALL_SPEED, sprite_row: int = 0):
        self.size = BALL_SIZE
        self.surf = get_ball_sprite(sprite_row)
        self.rect = self.surf.get_rect(
            centerx=GAME_WIDTH // 2,
            centery=GAME_HEIGHT // 2
        )
        self.base_speed = speed
        self.speed_x = 0
        self.speed_y = -speed
        self.active = False  # ball follows paddle until launched

    def _set_velocity_from_angle(self, angle_degrees: float):
        angle = math.radians(angle_degrees)
        self.speed_x = self.base_speed * math.cos(angle)
        self.speed_y = -abs(self.base_speed * math.sin(angle))
        self.enforce_min_vertical_speed()

    def enforce_min_vertical_speed(self):
        if not self.active:
            return

        total_speed = max(self.base_speed, math.hypot(self.speed_x, self.speed_y))
        min_speed_y = self.base_speed * BALL_MIN_VERTICAL_RATIO
        if abs(self.speed_y) >= min_speed_y:
            return

        y_sign = -1 if self.speed_y < 0 else 1
        x_sign = -1 if self.speed_x < 0 else 1
        self.speed_y = min_speed_y * y_sign
        self.speed_x = x_sign * math.sqrt(max(total_speed ** 2 - self.speed_y ** 2, 0))

    def move(self, paddle_rect: pygame.Rect):
        if not self.active:
            # Ball sits on top of the paddle until player presses SPACE
            self.rect.centerx = paddle_rect.centerx
            self.rect.bottom = paddle_rect.top - 2
            pressed_key = pygame.key.get_pressed()
            if pressed_key[pygame.K_SPACE]:
                self.active = True
                self._set_velocity_from_angle(60)
            return

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off left/right walls
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x = abs(self.speed_x)
        elif self.rect.right >= GAME_WIDTH:
            self.rect.right = GAME_WIDTH
            self.speed_x = -abs(self.speed_x)

        # Bounce off top wall
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y = abs(self.speed_y)

        self.enforce_min_vertical_speed()

    def check_paddle_collision(self, paddle_rect: pygame.Rect):
        if not self.active:
            return
        if self.rect.colliderect(paddle_rect) and self.speed_y > 0:
            # Calculate bounce angle based on where ball hit the paddle
            # hit_pos: -1.0 (left edge) to 1.0 (right edge)
            hit_pos = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
            hit_pos = max(-1.0, min(1.0, hit_pos))

            # Angle: from 150° (left) to 30° (right), mapped through hit_pos.
            # This keeps enough vertical movement to avoid endless horizontal loops.
            self._set_velocity_from_angle(90 - hit_pos * 60)

            # Ensure ball is above paddle to prevent sticking
            self.rect.bottom = paddle_rect.top - 1

    def is_out_of_bounds(self) -> bool:
        return self.rect.top > GAME_HEIGHT

    def reset(self):
        self.active = False
        self.rect.centerx = GAME_WIDTH // 2
        self.rect.centery = GAME_HEIGHT // 2

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)
