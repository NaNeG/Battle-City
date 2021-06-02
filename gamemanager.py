import pygame as pg
from sessionmanager import SessionManager
from constants import WHITE, WIN, screen_size, BLACK
from tactscounter import TactsCounter

class GameManager:
    def __init__(self, screen):
        self.cur_level = None
        self.cur_level_manager = None
        self.selected_level = 0
        self.screen = screen
        self.font = pg.font.SysFont("verdana", 24)
        self.in_game = False
        self.result = None
        self.level_selecting_delay = TactsCounter(count=5, cycled=False)
        pg.mixer.init(44100, -16, 1, 512)

    def menu_update(self, keystate):
        self.level_selecting_delay.update()
        if self.level_selecting_delay.stopped:
            self.level_selecting_delay.reset()
            for i, k in [(-1, pg.K_LEFT), (1, pg.K_RIGHT)]:
                if keystate[k] and 0 <= self.selected_level + i:
                    self.selected_level += i

            if keystate[pg.K_RETURN]:
                self.result = None
                self.in_game = True
                if self.selected_level != self.cur_level:
                    try:
                        f = open(f'levels/{self.selected_level}.txt')
                    except FileNotFoundError:
                        self.in_game = False
                    else:
                        self.cur_level = self.selected_level
                        txt_map = f.read()
                        f.close()
                        self.cur_level_manager = SessionManager(txt_map, self)

        if self.in_game:
            return

        text = self.font.render(f"< Уровень: {self.selected_level} >", True, WHITE)
        self.screen.blit(text, (screen_size[0]//8, screen_size[1]//8))

        text = self.font.render(
            "Старт" if self.selected_level != self.cur_level
                else "Продолжить",
            True, WHITE)
        self.screen.blit(text, (screen_size[0]//8, screen_size[1]//4))

        if self.result is not None:
            text = self.font.render(
                "Победа" if self.result == WIN else "Поражение",
                True, WHITE)
            self.screen.blit(text, (screen_size[0]//8, 3*screen_size[1]//8))

    def update(self):
        keystate = pg.key.get_pressed()
        self.screen.fill(BLACK)
        if not self.in_game:
            pg.mixer.Channel(3).pause()
            pg.mixer.Channel(7).pause()
            self.menu_update(keystate)
            if self.result is not None:
                self.cur_level = None
                self.cur_level_manager = None
        else:
            pg.mixer.Channel(3).unpause()
            pg.mixer.Channel(7).unpause()
            self.cur_level_manager.update(keystate)
            self.screen.blit(self.cur_level_manager.map_screen, (0, 0))
            self.screen.blit(self.cur_level_manager.info_screen, (0.1, 0.9 * screen_size[1]))
