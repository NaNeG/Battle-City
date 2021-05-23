from typing import Union
from pygame import Rect
import pygame as pg
from pygame.sprite import Sprite, Group, LayeredUpdates
from map import Map
from objects import Tank, Projectile, Tile, Explosion, jump
from images import green_img, concrete_img
from bonuses import BonusObj
from constants import DESTROY_ENEMIES, HEALING, POWER_UP, REPAIR_FORTRESS, RIGHT, SHIELD, UP, scale
from controllers import AI, Player
from teams import Team


class SessionManager:
    def __init__(self, map: Map):
        self.active = Group()
        self.environment = Group()
        self.effects = LayeredUpdates()

        self.players = Team()
        self.enemies = Team()

        self._map = map

    def jump(self, obj: Sprite, newrect: Rect, oldrect: Rect=None):
        return self._map.jump(obj, newrect, oldrect)

    def place(self, obj: Sprite, rect: Rect=None, onempty=True):
        return self._map.place(obj, rect, onempty)

    def outdate(self, rect: Rect, expected=()):
        return self._map.outdate(rect, expected)

    def count_rect_content(self, rect, filter=lambda x: x is not None):
        return self._map.count_rect_content(rect, filter)

    def create_explosion(self, obj, point, total_damage, duration):
        return Explosion(obj.team if hasattr(obj, 'team') else None, point, total_damage, duration, self.effects, self)

    def shoot(self, tank):
        return Projectile(tank.team, jump(tank.rect.center, 10*scale, tank.direction), 5, tank.direction, tank.damage, self.active, self)

    def create_tank(self, team, point, speed, delay, health, direction, damage):
        tank = Tank(team, point, speed, delay, health, direction, damage, self.active, self)
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

    def create_tile(self, point, health, team=None):
        return Tile(point, health, self.environment, self, team)

    def create_base(self, point, health):
        self.players.base = self.create_tile(point, health, self.players)
        self.players.base.image = concrete_img
        return self.players.base

    def create_effect(self, point, img):
        s = Sprite(self.effects)
        s.image = img
        s.rect = img.get_rect()
        s.rect.topleft = point
        return s

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

        a,b,c,d = ((point[0] + s1 * square_size//2,
                    point[1] + s2 * square_size//2)
                    for s1 in (0,1) for s2 in (0,1))
        if s == 'B':
            return [self.create_tile(point, 100) for point in (a,b,c,d)]
        if s == 'F':
            return [self.create_base(point, 100) for point in (a,b,c,d)]
        if s == 'G':
            return [self.create_effect(point, green_img) for point in (a,b,c,d)]

    def update(self, keystate):
        for t in self.players, self.enemies:
            t.update(keystate)
        for g in self.environment, self.active, self.effects:
            g.update()

    def draw(self, surface):
        for g in self.environment, self.active, self.effects:
            g.draw(surface)

