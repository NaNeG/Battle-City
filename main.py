import os, pygame as pg
from typing import Iterable, List
from pygame import Rect
from pygame.sprite import Group, LayeredUpdates, Sprite


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

(UP, RIGHT, DOWN, LEFT, FIRE) = range(5)


class TactsCounter:
    def __init__(self, *, count, tact_length=1, cycled=True):
        self._frame = 0
        self.count = count
        self.tact_length = tact_length
        self.active = True
        self.cycled = cycled

    @property
    def tact(self):
        return self._frame // self.tact_length

    @property
    def stopped(self):
        return not self.cycled and self.tact == self.count - 1

    def update(self):
        if self.active and (self.cycled or self.tact < self.count - 1):
            self._frame = ((self._frame + 1) % 
                           (self.tact_length * self.count))
    
    def reset(self):
        self._frame = 0


class Movable:
    speed: float
    direction: int
    rect: Rect
    blocked: List[bool]

    def move(self, speed=None, direction=None, forced=False):
        if speed is None:
            speed = self.speed

        if direction is None:
            direction = self.direction

        if not forced and hasattr(self, 'blocked'):
            blocked = self.blocked
        else:
            blocked = (False,) * 4

        if (game_iteration * speed) % 60 != 0 or blocked[direction]:
            return

        step = [(0,-1),(1,0),(0,1),(-1,0)][direction]
        self.rect.move_ip(step)

    def jump(self, dist=None, direction=None):
        if dist is None:
            dist = self.speed

        if direction is None:
            direction = self.direction

        step = [(0,-dist),(dist,0),(0,dist),(-dist,0)][direction]
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
        self.collisions = []
        self.blocked = [False] * 4

    @property
    def image(self):
        return self.images[self.anim_tacts_counter.tact][self.direction]

    def update(self):
        super().update()
        self.get_collided()
        self.shooting_delayer.update()

    def move(self):
        super().move()
        self.anim_tacts_counter.update()
    
    def fire(self):
        if self.shooting_delayer.stopped:
            Bullet(self.rect.center, 5, self.direction).jump(9)
            self.shooting_delayer.reset()

    def get_collided(self):
        self.blocked = [False] * 4
        for other in self.collisions:
            if not issolid(other):
                continue
            pressure = pressure_force(self.rect, other.rect)
            if pressure is None:
                continue
            self.blocked[pressure] = True
            if all(self.blocked):
                break


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
        self.timer = TactsCounter(count=12, cycled=False)
        self.collisions = []

    def update(self):
        self.move()
        if len(self.collisions) != 0 and any(issolid(e) for e in self.collisions):
            self.kill()
            Boom(self.rect.center)
        if self.timer.stopped:
            self.kill()
            return
        self.timer.update()

    # @property
    # def blocked(self):
    #     blocked = [False] * 4
    #     for other in self.collisions:
    #         pressure = pressure_force(self.rect, other.rect)
    #         if pressure is None:
    #             continue
    #         blocked[pressure] = True
    #         if all(blocked):
    #             break
    #     return blocked


class Boom(Sprite):
    def __init__(self, point):
        super().__init__(effects)

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


'''class CollisionsManager:
    def collide_all(self):
        for group in active_group, environment_group:
            for e in group:
                if hasattr(e, 'collisions'):
                    e.collisions = ()

            collisions = groupcollide(active_group, group, False, False,
                lambda x, y: x is not y and x.rect.colliderect(y.rect))

            for e in collisions:
                if hasattr(e, 'collisions'):
                    e.collisions = collisions[e]'''
class CollisionsManager:
    # def collide_groups(self, active, passive):
    #     for i in range(len(active)):
    #         collisions = (active.get_sprite(i).rect
    #             .collidelistall([active.get_sprite(j).rect
    #                              for j in range((i+1), len(active))]))
    #         for j in collisions:
    #             self.collide_two(active.get_sprite(i),
    #                              active.get_sprite((i+1)+j))

    #         collisions = (active.get_sprite(i).rect
    #             .collidelistall([e.rect for e in passive]))
    #         for j in collisions:
    #             self.collide_two(active.get_sprite(i),
    #                              passive.get_sprite(j))

    def collide_groups(self, active: Iterable[LayeredUpdates], passive: Iterable[LayeredUpdates]):
        active = [e for group in active for e in group]
        passive = [e for group in passive for e in group]
        for i in range(len(active)):
            collisions = (active[i].rect
                .collidelistall([active[j].rect
                                 for j in range((i+1), len(active))]))
            for j in collisions:
                self.collide_two(active[i], active[(i+1)+j])

            collisions = (active[i].rect
                .collidelistall([e.rect for e in passive]))
            for j in collisions:
                self.collide_two(active[i], passive[j])

    def invalidate_collisions(self, *groups):
        for group in groups:
            for e in group:
                if hasattr(e, 'collisions'):
                    e.collisions = []

    def collide_two(self, a, b):
        for x, y in (a, b), (b, a):
            if hasattr(x, 'collisions'):
                x.collisions.append(y)


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


pg.init()
pg.display.set_caption("Battle City")
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')
clock = pg.time.Clock()
screen = pg.display.set_mode((800, 600))

all_images = pg.image.load(os.path.join(img_folder, 'sprites.gif')).convert_alpha()
tank_ylw_img = pg.Surface.subsurface(all_images, (0,0,13,13))
tank_grn_img = pg.Surface.subsurface(all_images, (16,0,13,13))
tank_wsm_img = pg.Surface.subsurface(all_images, (32,0,13,13))
missing_img = pg.Surface.subsurface(all_images, (48,64,13,13))

bullet_img = pg.Surface.subsurface(all_images, (75,74,3,4))

bricks_img = pg.Surface.subsurface(all_images, (48,64,8,8))
red_bricks_img = pg.Surface.subsurface(all_images, (56,64,8,8))
concrete_img = pg.Surface.subsurface(all_images, (48,72,8,8))
leaves_img = pg.Surface.subsurface(all_images, (56,72,8,8))

exp1_img = pg.Surface.subsurface(all_images, (0,80,32,32))
exp2_img = pg.Surface.subsurface(all_images, (32,80,32,32))
exp3_img = pg.Surface.subsurface(all_images, (64,80,32,32))

active = LayeredUpdates()
environment = LayeredUpdates()
effects = LayeredUpdates()

coll_man = CollisionsManager()

# player = Player((400, 300), speed=42, direction=RIGHT)
# player = Player((400, 300), speed=30, direction=RIGHT)
# player = Player((400, 300), speed=14, direction=RIGHT)
player = Player((400, 300), speed=9, direction=RIGHT)
player = Player((400, 300), speed=5, direction=RIGHT)
player = Player((400, 300), speed=4, direction=RIGHT)
# player = Player((400, 300), speed=3.5, direction=RIGHT)
player = Player((400, 300), speed=3, direction=RIGHT)
# player = Player((400, 300), speed=2.5, direction=RIGHT)
player = Player((400, 300), speed=2, direction=RIGHT)
# player = Player((400, 300), speed=1.5, direction=RIGHT)
player = Player((400, 300), speed=1, direction=RIGHT)
Tile()

#НОК(1,..,6) = 60
game_iteration = 0
while True:
    clock.tick(30*1600)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):
        break

    environment.update()
    active.update()
    effects.update()

    coll_man.invalidate_collisions(active, environment, effects)
    coll_man.collide_groups((active,), (environment, effects))

    screen.fill(BLACK)
    environment.draw(screen)
    active.draw(screen)
    effects.draw(screen)

    pg.display.flip()

    game_iteration += 1

pg.quit()