"""End-of-game screen: name entry, score persistence and the top-10 board."""
import sys
from datetime import datetime

import pygame
from pygame import Surface, KEYDOWN, K_RETURN, K_BACKSPACE, K_ESCAPE
from pygame.font import Font

from code.Const import (C_MENU_ACTIVE, C_MENU_IDLE, SCORE_POS, GAME_WIDTH,
                        GAME_HEIGHT, C_TEXT_OUTLINE, MUSIC_VOLUME,
                        SCORE_NAME_MAX_LEN, SCORE_NAME_DEFAULT, s,
                        get_font, asset_path)
from code.Assets import get_background
from code.DBProxy import DBProxy


class Score:
    def __init__(self, game_surface: Surface):
        self.game_surface = game_surface
        self.surf = get_background('bg-gameover.png')
        self.rect = self.surf.get_rect(left=0, top=0)
        self.overlay = Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((*C_TEXT_OUTLINE, 170))

    def _draw_background(self):
        self.game_surface.blit(source=self.surf, dest=self.rect)
        self.game_surface.blit(source=self.overlay, dest=self.rect)

    def save(self, player_score: int, scale_callback,
             title: str = 'GAME OVER'):
        pygame.mixer_music.load(asset_path('gameover.mp3'))
        pygame.mixer_music.set_volume(MUSIC_VOLUME)
        pygame.mixer_music.play(-1)
        pygame.mouse.set_visible(True)
        db_proxy = DBProxy('DBScore')
        name = ''
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            self._draw_background()
            self.score_text(s(48), title, C_MENU_ACTIVE, SCORE_POS['Title'])
            text = f'Enter your name (up to {SCORE_NAME_MAX_LEN} characters):'
            self.score_text(s(20), text, C_MENU_IDLE, SCORE_POS['EnterName'])
            placeholder = name + '_' * (SCORE_NAME_MAX_LEN - len(name))
            self.score_text(s(20), placeholder or '_' * SCORE_NAME_MAX_LEN,
                            C_MENU_IDLE, SCORE_POS['Name'])
            self.score_text(s(16), 'Press ENTER to save',
                            C_MENU_IDLE, (GAME_WIDTH / 2, s(135)))

            scale_callback()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif event.key == K_RETURN:
                        final_name = name or SCORE_NAME_DEFAULT
                        db_proxy.save(
                            {'name': final_name, 'score': player_score,
                             'date': get_formatted_date()})
                        self.show(scale_callback, restart_music=False)
                        return
                    elif event.key == K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if (len(name) < SCORE_NAME_MAX_LEN
                                and event.unicode.isalnum()):
                            name += event.unicode.upper()

    def show(self, scale_callback, restart_music=True):
        if restart_music:
            pygame.mixer_music.load(asset_path('gameover.mp3'))
            pygame.mixer_music.set_volume(MUSIC_VOLUME)
            pygame.mixer_music.play(-1)
        pygame.mouse.set_visible(True)
        clock = pygame.time.Clock()

        db_proxy = DBProxy('DBScore')
        list_score = db_proxy.retrieve_top10()
        db_proxy.close()

        while True:
            clock.tick(60)
            self._draw_background()
            self.score_text(s(48), 'TOP 10 SCORES',
                            C_MENU_ACTIVE, SCORE_POS['Title'])
            self._draw_score_table(list_score)

            scale_callback()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

    def _score_table_layout(self):
        text_size = s(20)
        font = get_font(text_size)
        name_w = font.size('W' * SCORE_NAME_MAX_LEN)[0]
        score_w = font.size('99999')[0]
        date_w = font.size('00:00 - 00/00/00')[0]
        gap = s(24)
        total_w = name_w + gap + score_w + gap + date_w
        left = (GAME_WIDTH - total_w) / 2
        return {
            'name': left + name_w / 2,
            'score': left + name_w + gap + score_w / 2,
            'date': left + name_w + gap + score_w + gap + date_w / 2,
        }

    def _draw_score_table(self, list_score: list):
        columns = self._score_table_layout()

        self.score_text(s(20), 'NAME', C_MENU_ACTIVE,
                        (columns['name'], SCORE_POS['Label'][1]))
        self.score_text(s(20), 'SCORE', C_MENU_ACTIVE,
                        (columns['score'], SCORE_POS['Label'][1]))
        self.score_text(s(20), 'DATE', C_MENU_ACTIVE,
                        (columns['date'], SCORE_POS['Label'][1]))

        for row, player_score in enumerate(list_score):
            _, name, score, date = player_score
            y = SCORE_POS[row][1]
            self.score_text(s(20), str(name).upper(), C_MENU_IDLE,
                            (columns['name'], y))
            self.score_text(s(20), f'{score:05d}', C_MENU_IDLE,
                            (columns['score'], y))
            self.score_text(s(20), date, C_MENU_IDLE,
                            (columns['date'], y))

    def score_text(self, text_size: int, text: str, text_color: tuple, text_center_pos: tuple):
        text_font: Font = get_font(text_size)
        fill_surf: Surface = text_font.render(
            text, False, text_color).convert_alpha()
        outline_surf: Surface = text_font.render(
            text, False, C_TEXT_OUTLINE).convert_alpha()
        cx, cy = text_center_pos

        offset = max(2, s(1.5))
        for dx, dy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset),
                       (-offset, -offset), (offset, -offset),
                       (-offset, offset), (offset, offset)):
            self.game_surface.blit(
                outline_surf, outline_surf.get_rect(center=(cx + dx, cy + dy)))

        self.game_surface.blit(
            fill_surf, fill_surf.get_rect(center=text_center_pos))


def get_formatted_date():
    current_datetime = datetime.now()
    current_time = current_datetime.strftime("%H:%M")
    current_date = current_datetime.strftime("%d/%m/%y")
    return f"{current_time} - {current_date}"
