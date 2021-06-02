from typing import Union
from pygame import Rect
import pygame as pg
from pygame.sprite import Sprite, Group, LayeredUpdates
from map import Map
from objects import Destructable, Tank, Projectile, Tile, Explosion, jump
from images import tank_ylw_img, tank_grn_img, tank_ylw2_img, tank_grn2_img, tank_bsc_img, tank_fst_img, tank_pwr_img, tank_arm_img
from images import green_img, water_img, ice_img, bricks_img, concrete_img, base_img
from bonuses import BonusObj
from tactscounter import TactsCounter
from constants import DESTROY_ENEMIES, DOWN, HEALING, POWER_UP, REPAIR_FORTRESS, SHIELD, UP, scale
from controllers import AI, Player
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

        self.cheat_tacts_counter = TactsCounter(count=45, tact_length=1, cycled=False)
        self.required_keys = [False] * 5
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
        return Projectile(tank.team, jump(tank.rect.center, 1.5*tank.projectile_speed*scale, tank.direction),
                          tank.projectile_speed, tank.direction, tank.damage, self.active, self)

    def create_tank(self, images, team, point, speed, delay, health, direction, projectile_speed, damage, points):
        tank = Tank(images, team, point, speed, delay, health, direction, projectile_speed, damage, points, self.active, self)
        team.teammates.add(tank)
        return tank

    def create_player_tank(self, point, direction, player):
        images = [(tank_ylw_img, tank_ylw2_img), (tank_grn_img, tank_grn2_img)][player - 1]
        tank = self.create_tank(images, team=self.players,
                                point=point, speed=4, delay=20, health=100,
                                direction=direction, projectile_speed=7, damage=400, points=-100)
        player_buttons = [(pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_RCTRL),
                          (pg.K_w, pg.K_d, pg.K_s, pg.K_a, pg.K_LSHIFT)][player - 1]
        self.players.teammates.add(tank)
        player = Player(tank, player_buttons)
        self.players.controllers.add(player)
        return player

    def create_ai_tank(self, images, team, point, speed, delay, health, direction, projectile_speed, damage, points):
        tank = self.create_tank(images, team, point, speed, delay, health, direction, projectile_speed, damage, points)
        team.teammates.add(tank)
        ai = AI(tank)
        team.controllers.add(ai)
        return ai

    def create_basic_enemy_tank(self, point, direction):
        return self.create_ai_tank((tank_bsc_img,), team=self.enemies,
                                   point=point, speed=2, delay=60, health=100,
                                   direction=direction, projectile_speed=3, damage=200, points=100)

    def create_fast_enemy_tank(self, point, direction):
        return self.create_ai_tank((tank_fst_img,), team=self.enemies,
                                   point=point, speed=6, delay=30, health=100,
                                   direction=direction, projectile_speed=8, damage=400, points=200)

    def create_powered_enemy_tank(self, point, direction):
        return self.create_ai_tank((tank_pwr_img,), team=self.enemies,
                                   point=point, speed=4, delay=20, health=100,
                                   direction=direction, projectile_speed=10, damage=600, points=300)

    def create_armor_enemy_tank(self, point, direction):
        return self.create_ai_tank((tank_arm_img,), team=self.enemies,
                                   point=point, speed=4, delay=30, health=400,
                                   direction=direction, projectile_speed=7, damage=400, points=400)

    def create_destructable(self, image, point, health, team=None):
        return Destructable(image, point, health, self.environment, self, False, False, team)

    def create_base(self, point):
        self.players.base = self.create_destructable(base_img, point, 200, self.players)
        return self.players.base

    def create_bricks(self, point):
        return self.create_destructable(bricks_img, point, 100)

    def create_concrete(self, point):
        return self.create_destructable(concrete_img, point, 300)

    def create_green(self, point):
        return Tile(green_img, point, self.effects, self, True, True)

    def create_water(self, point):
        return Tile(water_img, point, self.environment, self, False, True)

    def create_ice(self, point):
        return Tile(ice_img, point, self.environment, self, True, True, 22)

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
            aim.health += 50

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
        if s == '1':
            return self.create_player_tank(point, UP, 1)
        if s == '2':
            return self.create_player_tank(point, UP, 2)
        if s == 'B':
            return self.create_basic_enemy_tank(point, DOWN)
        if s == 'F':
            return self.create_fast_enemy_tank(point, DOWN)
        if s == 'P':
            return self.create_powered_enemy_tank(point, DOWN)
        if s == 'A':
            return self.create_armor_enemy_tank(point, DOWN)
        if s == '0':
            return self.create_base(point)

        a,b,c,d = ((point[0] + s1 * square_size//2,
                    point[1] + s2 * square_size//2)
                    for s1 in (0,1) for s2 in (0,1))
        if s == '#':
            return [self.create_bricks(point) for point in (a,b,c,d)]
        if s == '+':
            return [self.create_concrete(point) for point in (a,b,c,d)]
        if s == '"':
            return [self.create_green(point) for point in (a,b,c,d)]
        if s == '~':
            return [self.create_water(point) for point in (a,b,c,d)]
        if s == '*':
            return [self.create_ice(point) for point in (a,b,c,d)]

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
        sounds["music"] = pg.mixer.Sound("sounds/music.mp3")
        return sounds

    def play_sound(self, sound):
        s = self.sounds[sound]
        music = self.sounds["music"]
        music_channel = pg.mixer.Channel(7)
        channel = pg.mixer.Channel(1)
        if sound == "bg":
            channel = pg.mixer.Channel(2)
        if sound == "start":
            channel = pg.mixer.Channel(3)
        if sound == "explosion":
            channel = pg.mixer.Channel(4)
        if not pg.mixer.Channel(3).get_busy():
            channel.play(s)
        if not music_channel.get_busy() and not pg.mixer.Channel(3).get_busy():
            music_channel.set_volume(0.3)
            music_channel.play(music, loops=-1, fade_ms=1000)

    def update_cheat_code(self, keystate):
        self.cheat_tacts_counter.update()
        for i, k in enumerate([pg.K_c, pg.K_h, pg.K_e, pg.K_a, pg.K_t]):
            if keystate[k] and (i == 0 or self.required_keys[i - 1]) and not self.required_keys[i]:
                self.required_keys[i] = True
                self.cheat_tacts_counter.reset()

        if self.cheat_tacts_counter.stopped:
            self.required_keys = [False] * 5
            self.cheat_tacts_counter.reset()

        if all(self.required_keys):
            self.enemies.kill()


    def update(self, keystate):
        self.update_cheat_code(keystate)
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
