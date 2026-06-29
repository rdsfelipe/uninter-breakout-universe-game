"""Main menu screen: animated background, logo and option navigation."""
import sys

import pygame.image
from pygame import Surface
from pygame.font import Font

from code.Const import (GAME_WIDTH, MENU_OPTION, MUSIC_VOLUME,
                        C_MENU_ACTIVE, C_MENU_IDLE,
                        C_TEXT_OUTLINE, s, get_font, asset_path)
from code.Assets import get_background, get_logo_sprite


class Menu:
    def __init__(self, game_surface: Surface):
        self.game_surface = game_surface
        self.surf = get_background('menu-bg.png')
        self.rect = self.surf.get_rect(left=0, top=0)
        self.logo_surf = get_logo_sprite()
        self.logo_rect = self.logo_surf.get_rect(
            center=(GAME_WIDTH / 2, s(85)))

    def run(self, scale_callback):
        menu_option = 0
        pygame.mixer_music.load(asset_path('menu.mp3'))
        pygame.mixer_music.set_volume(MUSIC_VOLUME)
        pygame.mixer_music.play(-1)
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)

            # DRAW
            self.game_surface.blit(source=self.surf, dest=self.rect)
            self.game_surface.blit(source=self.logo_surf, dest=self.logo_rect)

            for i in range(len(MENU_OPTION)):
                active = i == menu_option
                center = (GAME_WIDTH / 2, s(205 + 34 * i))
                if active:
                    self.menu_text(
                        s(24), MENU_OPTION[i], C_MENU_ACTIVE, center)
                else:
                    self.menu_text(s(22), MENU_OPTION[i], C_MENU_IDLE, center)

            # Scale and display to real window
            scale_callback()

            # Check for all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        if menu_option < len(MENU_OPTION) - 1:
                            menu_option += 1
                        else:
                            menu_option = 0
                    if event.key == pygame.K_UP:
                        if menu_option > 0:
                            menu_option -= 1
                        else:
                            menu_option = len(MENU_OPTION) - 1
                    if event.key == pygame.K_RETURN:
                        return MENU_OPTION[menu_option]
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

    def menu_text(self, text_size: int, text: str, text_color: tuple, text_center_pos: tuple):
        text_font: Font = get_font(text_size)
        fill_surf: Surface = text_font.render(
            text, False, text_color).convert_alpha()
        outline_surf: Surface = text_font.render(
            text, False, C_TEXT_OUTLINE).convert_alpha()
        cx, cy = text_center_pos

        # Draw an 8-direction outline behind the text for crisp, readable
        # letters that pop against the busy background.
        offset = max(2, s(1.5))
        for dx, dy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset),
                       (-offset, -offset), (offset, -offset),
                       (-offset, offset), (offset, offset)):
            self.game_surface.blit(
                outline_surf, outline_surf.get_rect(center=(cx + dx, cy + dy)))

        self.game_surface.blit(
            fill_surf, fill_surf.get_rect(center=text_center_pos))
