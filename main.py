import os, pygame as pg
from typing import Iterable, List, Tuple, Union
import enum
from pygame import Rect
from pygame.sprite import Group, LayeredUpdates, Sprite
from map import Map
from tactscounter import TactsCounter

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


(UP, RIGHT, DOWN, LEFT, FIRE) = range(5)


class Movable:
    speed: float
    direction: int
    rect: Rect
    blocked: List[bool]
    collide: callable

    def move(self, speed=None, direction=None):
        if speed is None:
            speed = self.speed

        if direction is None:
            direction = self.direction

        # if not forced and hasattr(self, 'blocked'):
        #     blocked = self.blocked
        # else:
        #     blocked = (False,) * 4

        # if blocked[direction]:
        #     return

        step = jump((0,0), 1, direction)

        for _ in range(speed):
            new_rect = self.rect.move(step)
            move_res = map.jump(self, new_rect)
            if move_res.ok:
                self.rect = new_rect
            else:
                self.collide(*move_res.found_extra)
                self.collide(*move_res.bumped)
                break

    def jump(self, dist=None, direction=None):
        if dist is None:
            dist = self.speed

        if direction is None:
            direction = self.direction

        step = jump((0,0), dist, direction)
        self.rect.move_ip(step)


class Tank(pg.sprite.Sprite, Movable):
    def __init__(self, point, speed, delay, direction=UP):
        super().__init__(active)
        self.images = [
            img_rotations(tank_ylw_img),
            img_rotations(tank_grn_img)
        ]
        self.anim_tacts_counter = TactsCounter(count=2, tact_length=5)
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.center = point
        self.speed = speed
        self.shooting_delayer = TactsCounter(count=delay, cycled=False)
        self.controls = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
        # self.collisions = []
        # self.blocked = [False] * 4
        if len(map.place(self)) > 0:
            Boom(self.rect.center)
            self.kill()
            # raise Exception("Tank placed over other object")

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact][self.direction]

    def update(self):
        super().update()
        # self.get_collided()
        self.shooting_delayer.update()

    def move(self):
        super().move()
        self.anim_tacts_counter.update()
    
    def fire(self):
        if self.shooting_delayer.stopped:
            Bullet(jump(self.rect.center, 10*scale, self.direction), 5, self.direction)
            self.shooting_delayer.reset()

    def collide(self, *others):
        pass
    # def get_collided(self):
    #     self.blocked = [False] * 4
    #     for other in self.collisions:
    #         if not issolid(other):
    #             continue
    #         pressure = pressure_force(self.rect, other.rect)
    #         if pressure is None:
    #             continue
    #         self.blocked[pressure] = True
    #         if all(self.blocked):
    #             break


class Player(Tank):
    def __init__(self, point, speed=4, delay=20, direction=UP):
        Tank.__init__(self, point, speed, delay, direction)

    def update(self):
        super().update()

        for dir in UP, RIGHT, DOWN, LEFT:
            if keystate[self.controls[dir]]:
                self.direction = dir
                self.move()
                break

        if keystate[self.controls[FIRE]]:
            self.fire()


class Bullet(pg.sprite.Sprite, Movable):
    def __init__(self, point, speed, direction):
        super().__init__(active)
        self.direction = direction
        self.image = pg.transform.rotate(
            bullet_img,
            (0, 270, 180, 90)[direction]
        )
        self.rect = self.image.get_rect()
        self.rect.center = point
        self.speed = speed
        self.timer = TactsCounter(count=36, cycled=False)
        # self.collisions = []

        extra = map.place(self)
        if len(extra) > 0:
            self.collide(*extra)
            # self.collisions.extend(extra)

    def update(self):
        self.move()
        if self.timer.stopped:
            map.outdate(self.rect, (self,))
            self.kill()
            return
        # self.collisions = []
        self.timer.update()

    def collide(self, *others):
        if len(others) != 0: # and any(issolid(e) for e in others):
            map.outdate(self.rect, (self,))
            self.kill()
            Boom(self.rect.center)


class Boom(Sprite):
    def __init__(self, point):
        super().__init__(effects)
        effects.move_to_back(self)

        self.images = [exp1_img, exp2_img, exp3_img]
        self.rect = exp1_img.get_rect()
        self.rect.center = point
        self.timer = TactsCounter(count=len(self.images)+1, tact_length=12, cycled=False)
    
    @property
    def image(self):
        return self.images[self.timer.tact % len(self.images)]

    def update(self):
        if self.timer.stopped:
            self.kill()
            return
        self.timer.update()


class Tile(Sprite):
    def __init__(self):
        super().__init__(environment)
        self.image = bricks_img
        self.rect = self.image.get_rect()
        self.rect.center = (500, 300)
        self.walkable = False
        if len(map.place(self)) > 0:
            pass


def img_rotations(img):
    return (img,
            pg.transform.rotate(img, 270),
            pg.transform.rotate(img, 180),
            pg.transform.rotate(img, 90))


def pressure_force(presser: Rect, pressed: Rect):
    if -1 <= presser.left - pressed.right <= 1:
        return LEFT
    if -1 <= presser.right - pressed.left <= 1:
        return RIGHT
    if -1 <= presser.bottom - pressed.top <= 1:
        return DOWN
    if -1 <= presser.top - pressed.bottom <= 1:
        return UP


def issolid(obj: Sprite):
    return obj in active or (obj in environment and not obj.walkable)


def jump(coords: Tuple[int, int], dist, direction):
    x, y = coords
    return [(x,y-dist),(x+dist,y),(x,y+dist),(x-dist,y)][direction]


from constants import *

pg.init()
pg.display.set_caption("Battle City")
screen = pg.display.set_mode(screen_size)

from images import *

clock = pg.time.Clock()

active = LayeredUpdates()
environment = LayeredUpdates()
effects = LayeredUpdates()

map = Map()

player = Player((400, 300), speed=2, direction=RIGHT)
Tile()

game_iteration = 0
while True:
    clock.tick(fps)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):
        break


    environment.update()
    active.update()
    effects.update()

    screen.fill(BLACK)
    environment.draw(screen)
    active.draw(screen)
    effects.draw(screen)

    pg.display.flip()

    game_iteration += 1

pg.quit()
