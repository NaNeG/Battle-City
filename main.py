import os, pygame as pg
from typing import List
from pygame import Rect
from pygame.sprite import Sprite


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
    def move(self):
        blocked = self.blocked if hasattr(self, 'blocked') else (False,) * 4
        if self.direction == RIGHT and not blocked[RIGHT]:
            self.rect.x += self.speed
        elif self.direction == UP and not blocked[UP]:
            self.rect.y -= self.speed
        elif self.direction == DOWN and not blocked[DOWN]:
            self.rect.y += self.speed
        elif self.direction == LEFT and not blocked[LEFT]:
            self.rect.x -= self.speed


class Tank(pg.sprite.Sprite, Movable):
    def __init__(self, point, speed, delay, direction=UP):
        super().__init__(sprite_group)
        self.images = [
            img_rotations(tank_ylw_img),
            img_rotations(tank_grn_img)
        ]
        coll_finder.add_active(self)
        self.tacts_counter = TactsCounter(count=2, tact_length=5)
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.center = point
        self.speed = speed
        self.shooting_delayer = TactsCounter(count=delay, tact_length=1, cycled=False)
        self.controls = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
        self.collisions = []
        self.blocked = [False] * 4

    @property
    def image(self):
        return self.images[self.tacts_counter.tact][self.direction]

    def update(self):
        super().update()
        self.get_collided()
        self.shooting_delayer.update()

    def move(self):
        super().move()
        self.tacts_counter.update()
    
    def fire(self):
        if self.shooting_delayer.stopped:
            Bullet(self.rect.center, 5, self.direction)
            self.shooting_delayer.reset()

    def get_collided(self):
        self.blocked = [False] * 4
        for other in self.collisions:
            if self.rect.top < other.rect.top:
                self.blocked[DOWN] = True
            if self.rect.bottom > other.rect.bottom:
                self.blocked[UP] = True
            if self.rect.right > other.rect.right:
                self.blocked[LEFT] = True
            if self.rect.left < other.rect.left:
                self.blocked[RIGHT] = True


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
        super().__init__(sprite_group)
        coll_finder.add_active(self)
        self.direction = direction
        self.image = pg.transform.rotate(
            bullet_img,
            (0, 270, 180, 90)[direction]
        )
        self.rect = self.image.get_rect()
        self.rect.center = point
        self.speed = speed
        self.collisions = []

    def update(self):
        self.move()
        if len(self.collisions) != 0:
            print(f'BOOM!')


class Tile(Sprite):
    def __init__(self):
        super().__init__(sprite_group)
        coll_finder.add_passive(self)
        self.image = bricks_img
        self.rect = self.image.get_rect()
        self.rect.center = (500, 300)
        self.walkable = False

    def get_collided(self, others):
        print(f'{type(self)} with {[type(e) for e in others]}')


class CollisionsFinder:
    def __init__(self, active=None, passive=None):
        self.active = active if active is not None else []
        self.passive = passive if passive is not None else []

    def add_active(self, e):
        self.active.append(e)

    def add_passive(self, e):
        self.passive.append(e)

    def collide_all(self):
        for group in self.active, self.passive:
            for e in group:
                if hasattr(e, 'collisions'):
                    e.collisions = []
        
        def collide_two(a, b):
            for a_, b_ in (a, b), (b, a):
                if hasattr(a_, 'collisions'):
                    a_.collisions.append(b_)
        
        for i in range(len(self.active)):
            collisions = (self.active[i].rect
                .collidelistall([e.rect for e in self.active[(i+1):]]))
            for j in collisions:
                collide_two(self.active[i], self.active[(i+1)+j])

            collisions = (self.active[i].rect
                .collidelistall([e.rect for e in self.passive]))
            for j in collisions:
                collide_two(self.active[i], self.passive[j])

    # def collisions(self):
    #     dict = {}
    #     for i in range(len(self.active)):
    #         if i not in dict:
    #             dict[i] = []

    #         collisions = self.active[i].rect.collidelistall([e.rect for e in self.active[i+1:]])
    #         dict[i].extend(((i+1)+j for j in collisions))
    #         for j in collisions:
    #             if (i+1)+j not in dict:
    #                 dict[(i+1)+j] = []
    #             dict[(i+1)+j].append(i)

    #         collisions = self.active[i].rect.collidelistall([e.rect for e in self.passive])
    #         dict[i].extend((j+len(self.active) for j in collisions))
    #         for j in collisions:
    #             if j+len(self.active) not in dict:
    #                 dict[j+len(self.active)] = []
    #             dict[j+len(self.active)].append(i)
        
    #     return dict

    # def collide_all(self):
    #     def _(j):
    #         return (self.active[j]
    #                 if j < len(self.active)
    #                 else self.passive[j-len(self.active)])

    #     for i, coll in self.collisions().items():
    #         if len(coll) != 0:
    #             _(i).get_collided((_(j) for j in coll))

    # def collisions(self):
    #     list = []
    #     for i in range(len(self.active)):
    #         obj = self.active[i]

    #         collisions = obj.rect.collidelistall([e.rect for e in self.active[i+1:]])
    #         for indice in collisions:
    #             list.append((obj, self.active[indice]))

    #         collisions = obj.rect.collidelistall([e.rect for e in self.passive])
    #         for indice in collisions:
    #             list.append((obj, self.passive[indice]))
        
    #     return list

    # def collide_all(self):
    #     for a, b in self.collisions():
    #         a.get_collided((b,))
    #         b.get_collided((a,))


def img_rotations(img):
    return (img,
            pg.transform.rotate(img, 270),
            pg.transform.rotate(img, 180),
            pg.transform.rotate(img, 90))


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

sprite_group = pg.sprite.Group()
coll_finder = CollisionsFinder()

player = Player((400, 300), speed=2, direction=RIGHT)
Tile()

while True:
    clock.tick(30)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):
        break

    sprite_group.update()
    coll_finder.collide_all()

    screen.fill(BLACK)
    sprite_group.draw(screen)

    pg.display.flip()

pg.quit()