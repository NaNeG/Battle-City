from typing import Union
from pygame import Rect
import pygame as pg
from pygame.sprite import Sprite, Group, LayeredUpdates
from map import Map
from objects import Destructable, Tank, Projectile, Tile, Explosion, jump
from images import green_img, concrete_img, tank_ylw_img, tank_grn_img, bricks_img, base_img, water_img
from bonuses import BonusObj
from constants import DESTROY_ENEMIES, HEALING, POWER_UP, REPAIR_FORTRESS, SHIELD, UP, scale
from controllers import AI, DrPlayer, Player
from teams import Team


class SessionManager:
    def __init__(self, map: Map):
        self.active = Group()
        self.environment = Group()
        self.effects = LayeredUpdates()

        self.players = Team()
        self.enemies = Team()
        self.sounds = self.load_sounds()
        self.play_sound("start")

        self._map = map

    # def jump(self, obj: Sprite, newrect: Rect, oldrect: Rect=None):
    #     return self._map.jump(obj, newrect, oldrect)

    def move(self, obj: Sprite, newrect: Rect, oldrect: Rect=None, validator=lambda obj: False):
        if oldrect is None:
            oldrect = obj.rect
        found_objects = (self._map.get_rect_content(oldrect, lambda x: x is not obj) |
                         self._map.get_rect_content(newrect, lambda x: x is not obj))
        success = all(validator(obj) for obj in found_objects)
        if success:
            self._map.jump(obj, newrect, oldrect)
        return success, found_objects

    def place(self, obj: Sprite, rect: Rect=None):
        return self._map.place(obj, rect)

    def outdate(self, obj: Sprite, rect: Rect=None):
        return self._map.outdate(obj, rect)

    def count_rect_content(self, rect, selector=lambda obj: True):
        return self._map.count_rect_content(rect, selector)

    def create_explosion(self, obj, point, total_damage, duration):
        return Explosion(obj.team if hasattr(obj, 'team') else None, point, total_damage, duration, self.effects, self)

    def shoot(self, tank):
        return Projectile(tank.team, jump(tank.rect.center, 10*scale, tank.direction), 5, tank.direction, tank.damage, self.active, self)

    def create_tank(self, team, point, speed, delay, health, direction, damage):
        images = tank_ylw_img, tank_grn_img
        tank = Tank(images, team, point, speed, delay, health, direction, damage, self.active, self)
        team.teammates.add(tank)
        return tank

    def create_player_tank(self, point, speed, delay, health, direction, damage):
        tank = self.create_tank(self.players, point, speed, delay, health, direction, damage)
        player_buttons = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
        self.players.teammates.add(tank)
        player = Player(tank, player_buttons)
        self.players.controllers.add(player)
        return player

    def create_ai_tank(self, team, point, speed, delay, health, direction, damage):
        tank = self.create_tank(team, point, speed, delay, health, direction, damage)
        team.teammates.add(tank)
        ai = AI(tank)
        team.controllers.add(ai)
        return ai

    def create_destructable(self, image, point, health, team=None):
        return Destructable(image, point, health, self.environment, self, False, False, team)

    def create_base(self, point, health):
        self.players.base = self.create_destructable(base_img, point, health, self.players)
        return self.players.base

    def create_green(self, point):
        return Tile(green_img, point, self.effects, self, True, True)

    def create_water(self, point):
        return Tile(water_img, point, self.environment, self, False, True)

    def create_ice(self, point):
        return Tile(water_img, point, self.environment, self, True, True, 40)

    def create_bonus(self, point, type):
        return BonusObj(point, type, self.effects, self)

    def set_bonus(self, aim, bonus):
        if bonus == SHIELD:
            aim.health = 99999
        if bonus == DESTROY_ENEMIES:
            if aim.team == self.players:
                self.enemies.kill()
        if bonus == REPAIR_FORTRESS:
            if aim.team == self.players and self.players.base is not None:
                self.players.base.health = 100
        if bonus == POWER_UP:
            pass
        if bonus == HEALING:
            pass

    def parse_map(self, str_map, above_existing=False):
        if not above_existing:
            self._map.clear_cells()
        square_size = 16 * scale
        str_map = str_map.split('\n')

        y = 0
        for row in str_map:
            x = 0
            for e in row:
                self.create_by_sign(e, (x*square_size, y*square_size))
                x += 1
            y += 1

    def create_by_sign(self, s, point):
        square_size = 16 * scale
        if s == 'P':
            return self.create_player_tank(point, speed=2, delay=20, health=100, direction=UP, damage=400)
        if s == 'E':
            return self.create_ai_tank(self.enemies, point, speed=2, delay=20, health=100, direction=UP, damage=400)
        if s == 'F':
            return self.create_base(point, 100)

        a,b,c,d = ((point[0] + s1 * square_size//2,
                    point[1] + s2 * square_size//2)
                    for s1 in (0,1) for s2 in (0,1))
        if s == 'B':
            return [self.create_destructable(bricks_img, point, 100) for point in (a,b,c,d)]
        if s == 'G':
            return [self.create_green(point) for point in (a,b,c,d)]
        if s == 'W':
            return [self.create_water(point) for point in (a,b,c,d)]

    def load_sounds(self):
        sounds = {}
        sounds["start"] = pg.mixer.Sound("sounds/sounds_gamestart.ogg")
        sounds["end"] = pg.mixer.Sound("sounds/sounds_gameover.ogg")
        sounds["score"] = pg.mixer.Sound("sounds/sounds_score.ogg")
        sounds["bg"] = pg.mixer.Sound("sounds/sounds_background.ogg")
        sounds["fire"] = pg.mixer.Sound("sounds/sounds_fire.ogg")
        sounds["bonus"] = pg.mixer.Sound("sounds/sounds_bonus.ogg")
        sounds["explosion"] = pg.mixer.Sound("sounds/sounds_explosion.ogg")
        sounds["brick"] = pg.mixer.Sound("sounds/sounds_brick.ogg")
        sounds["steel"] = pg.mixer.Sound("sounds/sounds_steel.ogg")
        return sounds

    def play_sound(self, sound):
        s = self.sounds[sound]
        channel = pg.mixer.Channel(1)
        if sound == "bg":
            channel = pg.mixer.Channel(2)
        if sound == "start":
            channel = pg.mixer.Channel(3)
        if sound == "explosion":
            channel = pg.mixer.Channel(4)
        if not pg.mixer.Channel(3).get_busy():
            channel.play(s)

    def update(self, keystate):
        for t in self.players, self.enemies:
            t.update(keystate)
        for g in self.environment, self.active, self.effects:
            g.update()

    def draw(self, surface):
        for g in self.environment, self.active, self.effects:
            g.draw(surface)


# class MoveResult:
#     def __init__(self, obj, found_invalid_objects=set(), found_valid_objects=set()):
#         self.obj = obj
#         self.ok = len(found_invalid_objects) == 0
#         self.invalid_objects = found_invalid_objects
#         self.valid_objects = found_valid_objects

#     @classmethod
#     def demarcate(cls, obj, found_objects, validator):
#         return cls(obj, {e for e in found_objects if not validator(e)}, {e for e in found_objects if validator(e)})

    # def __ior__(self, other):
    #     if self.obj != other.obj:
    #         raise ValueError
    #     self.invalid_objects |= other.invalid_objects
    #     self.valid_objects |= other.valid_objects
    #     self.ok |= other.ok
    #     return self
