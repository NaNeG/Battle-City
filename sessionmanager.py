from typing import Union
from pygame import Rect
import pygame as pg
from pygame.sprite import Sprite, Group, LayeredUpdates
from map import Map
from objects import Tank, Projectile, Tile, Explosion, jump
from constants import DESTROY_ENEMIES, ENEMIES, EXTRA_LIFE, PLAYERS, POWER_UP, REPAIR_FORTRESS, RIGHT, SHIELD, scale
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
        team.add(tank)
        return tank

    def create_player_tank(self, point, speed, delay, health, direction, damage):
        tank = self.create_tank(self.players, point, speed, delay, health, direction, damage)
        player_buttons = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
        self.players.add(tank)
        return Player(tank, player_buttons)

    def create_ai_tank(self, team, point, speed, delay, health, direction, damage):
        tank = self.create_tank(team, point, speed, delay, health, direction, damage)
        team.add(tank)
        return AI(tank)

    def create_tile(self, health, team=None):
        return Tile(health, self.environment, self, team)

    def create_base(self, health):
        self.players.base = self.create_tile(health, self.players)
        return self.players.base

    def set_bonus(self, aim, bonus):
        if bonus == SHIELD:
            pass
        if bonus == DESTROY_ENEMIES:
            if aim.team == self.players:
                self.enemies.kill()
        if bonus == REPAIR_FORTRESS:
            pass
        if bonus == POWER_UP:
            pass
        if bonus == EXTRA_LIFE:
            pass

    def update(self, keystate):
        # for t in self.players, self.enemies:
        #     t.update()
        for g in self.environment, self.active, self.effects:
            g.update()

    def draw(self, surface):
        for g in self.environment, self.active, self.effects:
            g.draw(surface)

    # def parse_map(self, str_map, above_existing=False):
    #     if not above_existing:
    #         pass
    #     square_size = 13
    #     str_map = str_map.split('\n')

    #     for x in range(self._map.size[0]):
    #         for y in range(self._map.size[1]):
