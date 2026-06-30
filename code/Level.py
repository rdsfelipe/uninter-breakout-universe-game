"""A single playable level: brick grid, game loop, collisions and HUD."""
import sys

import pygame
from pygame import Surface, Rect
from pygame.font import Font

from code.Const import (C_WHITE, C_YELLOW, GAME_WIDTH, GAME_HEIGHT,
                        PLAYER_LIVES, LEVEL_CONFIG,
                        BRICK_WIDTH, BRICK_HEIGHT, BRICK_GAP, BRICK_TOP_OFFSET,
                        BRICK_HP_COLOR_ROW, HEART_GAP, HEART_SIZE, MUSIC_VOLUME,
                        s, get_font, asset_path)
from code.Assets import get_background, get_heart_sprite
from code.Paddle import Paddle
from code.Ball import Ball
from code.Brick import Brick


class Level:
    def __init__(self, game_surface: Surface, name: str, player_score: int):
        self.game_surface = game_surface
        self.name = name
        self.config = LEVEL_CONFIG[name]
        self.lives = PLAYER_LIVES
        self.score = player_score
        self.quit_requested = False

        # Create entities
        sprite_row = self.config['sprite_row']
        self.paddle = Paddle(sprite_row=sprite_row)
        self.ball = Ball(speed=self.config['ball_speed'], sprite_row=sprite_row)
        self.bricks: list[Brick] = []
        self._create_bricks()

        # Load level-specific background
        self.bg_surf = get_background(self.config['background']).copy()

        # Pre-bake darkened background once instead of building/blitting a
        # full-screen SRCALPHA overlay every frame.
        dark_overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 120))
        self.bg_surf.blit(dark_overlay, (0, 0))

    def _create_bricks(self):
        rows = self.config['rows']
        cols = self.config['cols']
        max_hp = self.config['max_hp']
        hp_pattern = self.config.get('brick_hp_pattern')

        # Center the brick grid horizontally
        total_width = cols * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (GAME_WIDTH - total_width) // 2

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_GAP)
                fallback_hp = max(1, max_hp - row // 2)
                hp = self._pattern_value(hp_pattern, row, col, fallback_hp)
                # Color is tied to HP so strength is predictable at a glance.
                color_row = BRICK_HP_COLOR_ROW.get(hp, BRICK_HP_COLOR_ROW[1])
                self.bricks.append(Brick(x, y, hp, color_row))

    @staticmethod
    def _pattern_value(pattern: tuple | None, row: int, col: int, fallback: int) -> int:
        if not pattern:
            return fallback
        row_pattern = pattern[row % len(pattern)]
        if not row_pattern:
            return fallback
        return row_pattern[col % len(row_pattern)]

    def run(self, scale_callback) -> tuple[bool, int]:
        """Returns (won: bool, score: int)"""
        pygame.mouse.set_visible(False)
        pygame.mixer_music.load(asset_path(self.config["music"]))
        pygame.mixer_music.set_volume(MUSIC_VOLUME)
        pygame.mixer_music.play(-1)
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_requested = True
                        return False, self.score
                    if event.key == pygame.K_n and event.mod & pygame.KMOD_CTRL:
                        return True, self.score
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

            # Update
            self.paddle.move()
            self.ball.move(self.paddle.rect)
            self.ball.check_paddle_collision(self.paddle.rect)
            self._check_brick_collisions()

            # Ball out of bounds - lose life
            if self.ball.is_out_of_bounds():
                self.lives -= 1
                if self.lives <= 0:
                    return False, self.score
                self.ball.reset()
                self.paddle.reset()

            # All bricks destroyed - win
            if len(self.bricks) == 0:
                return True, self.score

            # Draw (background is already pre-darkened)
            self.game_surface.blit(self.bg_surf, (0, 0))

            for brick in self.bricks:
                brick.draw(self.game_surface)
            self.paddle.draw(self.game_surface)
            self.ball.draw(self.game_surface)

            # HUD
            self._draw_hud(clock.get_fps())

            # Scale and display to real window
            scale_callback()

    def _check_brick_collisions(self):
        if not self.ball.active:
            return

        ball_rect = self.ball.rect
        bricks_to_remove = []

        for brick in self.bricks:
            if ball_rect.colliderect(brick.rect):
                # Determine bounce direction based on overlap
                overlap_left = ball_rect.right - brick.rect.left
                overlap_right = brick.rect.right - ball_rect.left
                overlap_top = ball_rect.bottom - brick.rect.top
                overlap_bottom = brick.rect.bottom - ball_rect.top

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_left or min_overlap == overlap_right:
                    self.ball.speed_x = -self.ball.speed_x
                if min_overlap == overlap_top or min_overlap == overlap_bottom:
                    self.ball.speed_y = -self.ball.speed_y

                score_gained = brick.hit()
                self.score += score_gained
                if brick.is_destroyed():
                    bricks_to_remove.append(brick)

                self.ball.enforce_min_vertical_speed()
                break  # Only collide with one brick per frame

        for brick in bricks_to_remove:
            self.bricks.remove(brick)

    def _draw_hud(self, fps: float):
        self._draw_lives()
        self._draw_text(
            s(14), f'Score: {self.score}', C_YELLOW, (s(10), s(20)))
        self._draw_text(
            s(14), self.config['display_name'], C_WHITE,
            (GAME_WIDTH - s(70), s(5)))
        self._draw_text(
            s(10), f'FPS: {fps:.0f}', C_WHITE,
            (GAME_WIDTH - s(60), GAME_HEIGHT - s(15)))

        # Controls hint while the ball is still resting on the paddle.
        if not self.ball.active:
            hint_y = GAME_HEIGHT // 2 + s(24)
            self._draw_text_centered(
                s(16), 'LEFT / RIGHT ARROWS to move', C_WHITE,
                (GAME_WIDTH // 2, hint_y))
            self._draw_text_centered(
                s(16), 'Press SPACE to launch', C_WHITE,
                (GAME_WIDTH // 2, hint_y + s(20)))

    def _draw_text(self, text_size: int, text: str, text_color: tuple,
                   text_pos: tuple):
        text_font: Font = get_font(text_size)
        text_surf: Surface = text_font.render(
            text, False, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(left=text_pos[0], top=text_pos[1])
        self.game_surface.blit(source=text_surf, dest=text_rect)

    def _draw_text_centered(self, text_size: int, text: str, text_color: tuple,
                            text_center_pos: tuple):
        text_font: Font = get_font(text_size)
        text_surf: Surface = text_font.render(
            text, False, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(center=text_center_pos)
        self.game_surface.blit(source=text_surf, dest=text_rect)

    def _draw_lives(self):
        heart = get_heart_sprite()
        y = s(5)
        for i in range(self.lives):
            x = s(10) + i * (HEART_SIZE + HEART_GAP)
            self.game_surface.blit(heart, (x, y))
