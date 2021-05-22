from constants import ENEMIES, PLAYERS
from pygame.sprite import Sprite
from images import star_bonus_img, dark_bonus_img
from tactscounter import TactsCounter


class Bonus(Sprite):
    @staticmethod
    def tank_healing(tank, session_manager):
        tank.health = 100

    @staticmethod
    def enemies_destroying(tank, session_manager):
        if tank.team is PLAYERS:
            session_manager.destroy_team(ENEMIES)

    def __init__(self, use_func):
        self.images = [star_bonus_img, dark_bonus_img]
        self.anim_tacts_counter = TactsCounter(count=2, tact_length=5)
        self.timer = TactsCounter(count=12, cycled=False)
        self.use = use_func

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact]
    
    def update(self):
        if self.timer.stopped:
            self.kill()
