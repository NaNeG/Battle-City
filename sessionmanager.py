from typing import Union
from pygame import Rect
import pygame as pg
from pygame.sprite import Sprite, Group, LayeredUpdates
from map import Map
from objects import Tank, Projectile, Tile, Explosion, jump
from constants import ENEMIES, PLAYERS, RIGHT, scale
from controllers import AI, Player


class SessionManager:
    def __init__(self, map: Map):
        self.active = Group()
        self.environment = Group()
        self.effects = LayeredUpdates()
        self._map = map

    def jump(self, obj: Sprite, newrect: Rect, oldrect: Rect=None):
        return self._map.jump(obj, newrect, oldrect)

    def place(self, obj: Sprite, rect: Rect=None, onempty=True):
        return self._map.place(obj, rect, onempty)

    def outdate(self, rect: Rect, expected=()):
        return self._map.outdate(rect, expected)

    def count_rect_content(self, rect, excluding=(None,)):
        return self._map.count_rect_content(rect, excluding)

    def create_explosion(self, obj, point, total_damage, duration):
        return Explosion(obj.team if hasattr(obj, 'team') else None, point, total_damage, duration, self.effects, self)

    def shoot(self, tank):
        return Projectile(tank.team, jump(tank.rect.center, 10*scale, tank.direction), 5, tank.direction, tank.damage, self.active, self)

    def create_tank(self, team, point, speed, delay, health, direction, damage):
        return Tank(team, point, speed, delay, health, direction, damage, self.active, self)

    def create_player_tank(self, point, speed, delay, health, direction, damage):
        tank = self.create_tank(PLAYERS, point, speed, delay, health, direction, damage)
        player_buttons = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_SPACE]
        return Player(tank, player_buttons)

    def create_ai_tank(self, team, point, speed, delay, health, direction, damage):
        tank = self.create_tank(team, point, speed, delay, health, direction, damage)
        return AI(tank)

    def create_tile(self, health):
        return Tile(health, self.environment, self)

    def update(self):
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
