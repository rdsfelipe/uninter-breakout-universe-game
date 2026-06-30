"""Top-level game controller: window setup, scaling and screen flow."""
import sys

import pygame

from code.Const import (GAME_WIDTH, GAME_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
                        MENU_OPTION)
from code.Level import Level
from code.Menu import Menu
from code.Score import Score


class Game:
    def __init__(self):
        self._enable_dpi_awareness()
        pygame.init()

        pygame.display.set_caption("Breakout Universe")

        try:
            self.window = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE, vsync=1
            )
        except pygame.error:
            # Some drivers reject vsync on a plain window; fall back without it.
            self.window = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

        # Off-screen surface where the whole game is drawn at fixed resolution.
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    @staticmethod
    def _enable_dpi_awareness():
        """Stop Windows from bitmap-stretching (and blurring) the window on
        high-DPI displays scaled above 100%."""
        if sys.platform != 'win32':
            return
        try:
            import ctypes
            # Per-monitor DPI aware (v2) when available, else system-DPI aware.
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (AttributeError, OSError):
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    def present(self):
        """Scale the game surface to cover (fill) the window and present it."""
        win_w, win_h = self.window.get_size()
        # Fast path: when the window matches the render resolution there is no
        # scaling to do, so blit directly and keep the pixel font perfectly crisp.
        if win_w == GAME_WIDTH and win_h == GAME_HEIGHT:
            self.window.blit(self.game_surface, (0, 0))
            pygame.display.flip()
            return
        # Cover: use the larger scale factor so the frame fills the window,
        # cropping any overflow instead of leaving bars.
        scale = max(win_w / GAME_WIDTH, win_h / GAME_HEIGHT)
        scaled_w = round(GAME_WIDTH * scale)
        scaled_h = round(GAME_HEIGHT * scale)
        scaled = pygame.transform.smoothscale(self.game_surface, (scaled_w, scaled_h))
        self.window.blit(scaled, ((win_w - scaled_w) // 2, (win_h - scaled_h) // 2))
        pygame.display.flip()

    def run(self):
        while True:
            score = Score(self.game_surface)
            menu = Menu(self.game_surface)
            menu_return = menu.run(self.present, self.window)

            if menu_return == MENU_OPTION[0]:  # NEW GAME
                player_score = 0
                game_cancelled = False

                for level_name in ('Level1', 'Level2', 'Level3'):
                    level = Level(self.game_surface, level_name, player_score)
                    won, player_score = level.run(self.present)

                    if not won:
                        game_cancelled = level.quit_requested
                        break

                if game_cancelled:
                    continue
                if won:
                    score.save(player_score, self.present, 'YOU WIN!!')
                else:
                    score.save(player_score, self.present, 'GAME OVER')

            elif menu_return == MENU_OPTION[1]:  # SCORES
                score.show(self.present)

            elif menu_return == MENU_OPTION[2]:  # EXIT
                pygame.quit()
                sys.exit()
