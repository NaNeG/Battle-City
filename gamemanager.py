import pygame as pg
from sessionmanager import SessionManager
from constants import WHITE, screen_size, BLACK
from tactscounter import TactsCounter

class GameManager:
    def __init__(self, screen):
        self.cur_level = None
        self.cur_level_manager = None
        self.selected_level = 0
        self.screen = screen
        self.font = pg.font.SysFont("verdana", 24)
        self.in_game = False
        self.level_selecting_delay = TactsCounter(count=5, cycled=False)
        pg.mixer.init(44100, -16, 1, 512)
        # self.play_sound("start")

    def menu_update(self, keystate):
        self.level_selecting_delay.update()
        if self.level_selecting_delay.stopped:
            self.level_selecting_delay.reset()
            for i, k in [(-1, pg.K_LEFT), (1, pg.K_RIGHT)]:
                if keystate[k] and 0 <= self.selected_level + i:
                    self.selected_level += i

            if keystate[pg.K_RETURN]:
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

    def update(self):
        keystate = pg.key.get_pressed()
        # events = pg.event.get()
        self.screen.fill(BLACK)
        if not self.in_game:
            self.menu_update(keystate)
        else:
            self.cur_level_manager.update(keystate)
            self.screen.blit(self.cur_level_manager.map_screen, (0, 0))
            self.screen.blit(self.cur_level_manager.info_screen, (0.1, 0.9 * screen_size[1]))
