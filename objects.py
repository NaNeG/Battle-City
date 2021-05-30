from images import *
from typing import Callable, List, Set, Tuple, Type
from pygame import Rect
from pygame.sprite import LayeredUpdates, Sprite
from tactscounter import TactsCounter
from constants import *


__all__ = ['Movable', 'Tank', 'Projectile', 'Explosion', 'jump']


Wall = object()


class Movable:
    speed: float
    direction: int
    rect: Rect
    collide: Callable
    can_walk_on: Callable
    _sm: 'SessionManager'

    def move(self, speed=None, direction=None, can_walk_on=None):
        if speed is None:
            speed = self.speed

        if direction is None:
            direction = self.direction

        if can_walk_on is None:
            can_walk_on = self.can_walk_on

        step = jump((0,0), 1, direction)

        for _ in range(speed):
            new_rect = self.rect.move(step)
            success, found_objects = self._sm.move(self, new_rect, self.rect, can_walk_on)
            for e in found_objects:
                if hasattr(e, 'collide'):
                    e.collide(self)
            self.collide(*found_objects)
            if success:
                self.rect = new_rect
            else:
                break

    def jump(self, dist=None, direction=None):
        if dist is None:
            dist = self.speed

        if direction is None:
            direction = self.direction

        step = jump((0,0), dist, direction)
        self.rect.move_ip(step)


class Tank(Sprite, Movable):
    def __init__(self, images, team, point, speed, delay, health, direction, damage, group, session_manager):
        super().__init__(group)
        self.images = [img_rotations(img) for img in images]
        self.anim_tacts_counter = TactsCounter(count=len(self.images), tact_length=5)

        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.topleft = point
        self.speed = speed
        self.health = health
        self.team = team
        self.damage = damage
        self._sm = session_manager

        self.shooting_delayer = TactsCounter(count=delay, cycled=False)
        self.controls = [False] * 5
        self._sm.place(self)

    def can_walk_on(self, x):
        return isinstance(x, Tile) and x.is_walkable

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact][self.direction]

    def update(self):
        super().update()
        if self.health <= 0:
            self.kill()
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
            self._sm.shoot(self)
            self.shooting_delayer.reset()

    def collide(self, *others):
        pass

    def get_harmed(self, *others):
        for e in others:
            self.health -= e.damage

    def kill(self):
        self.health = 0
        super().kill()
        self._sm.outdate(self)
        self._sm.create_explosion(None, self.rect.center, 0, 6)


class Projectile(Sprite, Movable):
    def __init__(self, team, point, speed, direction, damage, group, session_manager):
        super().__init__(group)
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
        self.health = 15
        self._sm = session_manager

        session_manager.place(self)

    def can_walk_on(self, x):
        return isinstance(x, Tile) and x.is_flyable

    def update(self):
        if self.health <= 0:
            self.kill()
            return
        self.move()

    def get_harmed(self, *others):
        for e in others:
            if self.health <= 0:
                break
            if issolid(e):
                self.health = 0
            elif not self.can_walk_on(e):
                self.health -= e.damage

    collide = get_harmed

    def kill(self):
        self.health = 0
        self._sm.outdate(self)
        self._sm.create_explosion(self, self.rect.center, self.damage, 12)
        super().kill()


class Explosion(Sprite):
    def __init__(self, team, point, total_damage, duration, group: LayeredUpdates, session_manager):
        super().__init__(group)
        group.move_to_back(self)

        self.images = [exp1_img, exp2_img, exp3_img]
        self.rects = []
        for e in self.images:
            rect = e.get_rect()
            rect.center = point
            self.rects.append(rect)

        self.team = team
        self.timer = TactsCounter(count=len(self.images)+1, tact_length=duration // (len(self.images)+1), cycled=False)
        self.total_damage = total_damage
        self.duration = duration
        self._sm = session_manager

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
        return self.total_damage / (self.duration * self.square)

    def update(self):
        if self.timer.stopped:
            self.kill()
            return
        for e, times in self._sm.count_rect_content(self.rect, lambda x: x not in (None, Wall)).items():
            if hasattr(e, 'get_harmed') and (not hasattr(e, 'team') or e.team != self.team):
                e.get_harmed(*(self for _ in range(times)))
        self.timer.update()


class Tile(Sprite):
    def __init__(self, image, point, group, session_manager, is_walkable=False, is_flyable=False):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = point
        self._sm = session_manager
        self._sm.place(self)
        self.is_walkable = is_walkable
        self.is_flyable = is_flyable

    def kill(self):
        self._sm.outdate(self)
        super().kill()

    def collide(self, *others):
        pass


class Destructable(Tile):
    def __init__(self, image, point, health, group, session_manager, is_walkable=False, is_flyable=False, team=None):
        super().__init__(image, point, group, session_manager, is_walkable, is_flyable)
        self.health = health
        self.team = team

    def update(self):
        if self.health <= 0:
            self.kill()

    def get_harmed(self, *others):
        for e in others:
            self.health -= e.damage

    def kill(self):
        super().kill()
        self.health = 0


def issolid(obj: Sprite):
    return isinstance(obj, (Tank, Projectile, Destructable)) or obj is Wall


def jump(coords: Tuple[int, int], dist, direction):
    x, y = coords
    return [(x,y-dist),(x+dist,y),(x,y+dist),(x-dist,y)][direction]


def pressure_dir(presser: Rect, pressed: Rect):
    if -1 <= presser.left - pressed.right <= 1:
        return LEFT
    if -1 <= presser.right - pressed.left <= 1:
        return RIGHT
    if -1 <= presser.bottom - pressed.top <= 1:
        return DOWN
    if -1 <= presser.top - pressed.bottom <= 1:
        return UP
