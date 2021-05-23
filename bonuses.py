from objects import Tank, Wall
from pygame.sprite import Sprite
from images import star_bonus_img, dark_bonus_img
from tactscounter import TactsCounter


class BonusObj(Sprite):
    def __init__(self, point, type, group, session_manager):
        super().__init__(group)
        self.images = [star_bonus_img, dark_bonus_img]
        self.rect = self.images[0].get_rect()
        self.rect.center = point
        self.anim_tacts_counter = TactsCounter(count=2, tact_length=5)
        self.timer = TactsCounter(count=200, cycled=False)
        self.type = type
        self._sm = session_manager

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact]

    def update(self):
        if self.timer.stopped:
            self.kill()
        inside_bonus = self._sm.count_rect_content(self.rect, lambda x: isinstance(x, Tank))
        best_pretendent = inside_bonus.most_common(1)
        if len(best_pretendent) > 0:
            (best_pretendent, _), = best_pretendent
            self.kill()
            self._sm.set_bonus(best_pretendent, self.type)
        self.anim_tacts_counter.update()
        self.timer.update()


# class Bonus:
#     @staticmethod
#     def tank_healing(tank, session_manager):
#         tank.health = 100

#     @staticmethod
#     def enemies_destroying(tank, session_manager):
#         if tank.team is PLAYERS:
#             session_manager.destroy_team(ENEMIES)

#     def __init__(self, effect_func, session_manager, duration=0):
#         self._func = effect_func
#         self._sm = session_manager
#         self.dur_counter = TactsCounter(count=duration, cycled=False)

#     def update(self):
#         self.dur_counter
