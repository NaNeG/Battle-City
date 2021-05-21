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


NONE = 0
PLAYERS = 1
ENEMIES = 2


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
    def __init__(self, team, point, speed, delay, health, direction, damage):
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
        self.health = health
        self.team = team
        self.damage = damage

        self.shooting_delayer = TactsCounter(count=delay, cycled=False)
        self.controls = [False] * 5
        if len(map.place(self)) > 0:
            Boom(NONE, self.rect.center, 0)
            self.kill()

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact][self.direction]

    def update(self):
        super().update()
        if self.health <= 0:
            self.kill()
            map.outdate(self.rect, (self,))
            return

        self.shooting_delayer.update()

        for dir in UP, RIGHT, DOWN, LEFT:
            if self.controls[dir]:
                self.direction = dir
                self.move()
                break

        if self.controls[FIRE]:
            self.fire()

    def move(self):
        super().move()
        self.anim_tacts_counter.update()
    
    def fire(self):
        if self.shooting_delayer.stopped:
            Bullet(self.team, jump(self.rect.center, 10*scale, self.direction), 5, self.direction, self.damage)
            self.shooting_delayer.reset()

    def collide(self, *others):
        pass

    def get_harmed(self, *others):
        for e in others:
            self.health -= e.damage


class Player:
    def __init__(self, tank, buttons):
        self.tank = tank
        self.buttons = buttons

    def update(self):
        self.tank.controls = [keystate[e] for e in self.buttons]


class Bullet(pg.sprite.Sprite, Movable):
    def __init__(self, team, point, speed, direction, damage):
        super().__init__(active)
        self.team = team
        self.direction = direction
        self.image = pg.transform.rotate(
            bullet_img,
            (0, 270, 180, 90)[direction]
        )
        self.rect = self.image.get_rect()
        self.rect.center = point
        self.speed = speed
        self.damage = damage
        self.timer = TactsCounter(count=36, cycled=False)

        extra = map.place(self)
        if len(extra) > 0:
            self.collide(*extra)

    def update(self):
        self.move()
        if self.timer.stopped:
            map.outdate(self.rect, (self,))
            self.kill()
            return
        self.timer.update()

    def collide(self, *others):
        if len(others) != 0:
            map.outdate(self.rect, (self,))
            self.kill()
            Boom(self.team, self.rect.center, self.damage)
    
    get_harmed = collide


class Boom(Sprite):
    def __init__(self, team, point, total_damage):
        super().__init__(effects)
        effects.move_to_back(self)

        self.images = [exp1_img, exp2_img, exp3_img]
        self.rects = []
        for e in self.images:
            rect = e.get_rect()
            rect.center = point
            self.rects.append(rect)

        self.team = team
        self.timer = TactsCounter(count=len(self.images)+1, tact_length=12, cycled=False)
        self.total_damage = total_damage

    @property
    def image(self):
        return self.images[self.timer.tact % len(self.images)]

    @property
    def rect(self):
        return self.rects[self.timer.tact % len(self.rects)]

    @property
    def square(self):
        return self.rect.size[0] * self.rect.size[1] / (scale * scale)

    @property
    def damage(self):
        return self.total_damage / (self.timer.count * self.square)

    def update(self):
        if self.timer.stopped:
            self.kill()
            return
        for e, times in map.count_rect_content(self.rect).items():
            if not hasattr(e, 'team') or e.team != self.team:
                e.get_harmed(*(self for _ in range(times)))
        self.timer.update()


class Tile(Sprite):
    def __init__(self):
        super().__init__(environment)
        self.image = bricks_img
        self.rect = self.image.get_rect()
        self.rect.center = (500, 300)
        self.health = 100
        self.walkable = False
        if len(map.place(self)) > 0:
            pass

    def update(self):
        if self.health < 0:
            map.outdate(self.rect, (self,))
            self.kill()

    def get_harmed(self, *others):
        for e in others:
            self.health -= e.damage


def img_rotations(img):
    return (img,
            pg.transform.rotate(img, 270),
            pg.transform.rotate(img, 180),
            pg.transform.rotate(img, 90))


def pressure_dir(presser: Rect, pressed: Rect):
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

player_tank = Tank(PLAYERS, (400, 300), speed=2, delay=20, health=100, direction=RIGHT, damage=50)
player_buttons = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
player = Player(player_tank, player_buttons)

Tile()

Tank(ENEMIES, (440, 300), speed=1, delay=20, health=2000, direction=DOWN, damage=50).controls = [0, 0, 0, 0, 0]
Tank(ENEMIES, (440, 350), speed=1, delay=20, health=302, direction=DOWN, damage=50).controls = [0, 0, 0, 0, 0]

game_iteration = 0
while True:
    clock.tick(fps)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):
        break

    player.update()

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
