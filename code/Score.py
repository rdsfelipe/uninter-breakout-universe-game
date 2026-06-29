"""End-of-game screen: name entry, score persistence and the top-10 board."""
import sys
from datetime import datetime

import pygame
from pygame import Surface, Rect, KEYDOWN, K_RETURN, K_BACKSPACE, K_ESCAPE
from pygame.font import Font

from code.Const import (C_YELLOW, SCORE_POS, C_WHITE, GAME_WIDTH,
                        MUSIC_VOLUME, s, get_font, asset_path)
from code.Assets import get_background
from code.DBProxy import DBProxy


class Score:
    def __init__(self, game_surface: Surface):
        self.game_surface = game_surface
        self.surf = get_background('bg-gameover.png')
        self.rect = self.surf.get_rect(left=0, top=0)

    def save(self, player_score: int, scale_callback,
             title: str = 'GAME OVER'):
        pygame.mixer_music.load(asset_path('gameover.mp3'))
        pygame.mixer_music.set_volume(MUSIC_VOLUME)
        pygame.mixer_music.play(-1)
        db_proxy = DBProxy('DBScore')
        name = ''
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            self.game_surface.blit(source=self.surf, dest=self.rect)
            self.score_text(s(48), title, C_YELLOW, SCORE_POS['Title'])
            text = 'Enter your name (4 characters):'
            self.score_text(s(20), text, C_WHITE, SCORE_POS['EnterName'])
            self.score_text(s(20), name or '____', C_WHITE, SCORE_POS['Name'])
            self.score_text(s(16), 'Press ENTER to save',
                            C_WHITE, (GAME_WIDTH / 2, s(135)))

            scale_callback()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif event.key == K_RETURN and len(name) == 4:
                        db_proxy.save(
                            {'name': name, 'score': player_score, 'date': get_formatted_date()})
                        self.show(scale_callback)
                        return
                    elif event.key == K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 4 and event.unicode.isalnum():
                            name += event.unicode.upper()

    def show(self, scale_callback):
        pygame.mixer_music.load(asset_path('gameover.mp3'))
        pygame.mixer_music.set_volume(MUSIC_VOLUME)
        pygame.mixer_music.play(-1)
        clock = pygame.time.Clock()

        db_proxy = DBProxy('DBScore')
        list_score = db_proxy.retrieve_top10()
        db_proxy.close()

        while True:
            clock.tick(60)
            self.game_surface.blit(source=self.surf, dest=self.rect)
            self.score_text(s(48), 'TOP 10 SCORES',
                            C_YELLOW, SCORE_POS['Title'])
            self.score_text(
                s(20), 'NAME     SCORE           DATE      ',
                C_YELLOW, SCORE_POS['Label'])

            for player_score in list_score:
                id_, name, score, date = player_score
                self.score_text(s(20), f'{name}     {score:05d}     {date}', C_YELLOW,
                                SCORE_POS[list_score.index(player_score)])

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

    def score_text(self, text_size: int, text: str, text_color: tuple, text_center_pos: tuple):
        text_font: Font = get_font(text_size)
        text_surf: Surface = text_font.render(
            text, False, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(center=text_center_pos)
        self.game_surface.blit(source=text_surf, dest=text_rect)


def get_formatted_date():
    current_datetime = datetime.now()
    current_time = current_datetime.strftime("%H:%M")
    current_date = current_datetime.strftime("%d/%m/%y")
    return f"{current_time} - {current_date}"
