from tactscounter import TactsCounter
from random import choices, randrange, choice, random, randint
from constants import *


class Player:
    def __init__(self, tank, buttons):
        self.tank = tank
        self.buttons = buttons

    def update(self, keystate):
        self.tank.controls = [keystate[e] for e in self.buttons]


class AI:
    _max_weight = 17
    def __init__(self, tank):
        self.tank = tank
        self.dir_timer = TactsCounter(count=13, cycled=False)
        self._dir_weights = [AI._max_weight // 11] * 5
        self.tank.controls[FIRE] = True

    def update(self, controls=None):
        if self.dir_timer.stopped:
            direction, = choices((UP, RIGHT, DOWN, LEFT, None), self._dir_weights)
            self.tank.controls[:4] = (False,) * 4
            if direction is not None:
                self.tank.controls[direction] = True
                self._dir_weights[direction] = (self._dir_weights[direction]) % AI._max_weight + randint(6,AI._max_weight)
            self.dir_timer.reset()
        self.dir_timer.update()


class PatrolAI:
    def __init__(self, tank):
        self.tank = tank
        self.dir_timer = TactsCounter(count=6, cycled=False)
        self.tank.controls[FIRE] = True

    def update(self, controls=None):
        if self.dir_timer.stopped:
            direction = choice((UP, RIGHT, DOWN, LEFT, None))
            self.tank.controls[:4] = (False,) * 4
            if direction is not None:
                self.tank.controls[direction] = True
            self.dir_timer.reset()
        self.dir_timer.update()
