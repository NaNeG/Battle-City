import pygame as pg
from constants import *


pg.init()
pg.display.set_caption("Battle City")
screen = pg.display.set_mode(screen_size)

from sessionmanager import SessionManager
from map import Map

clock = pg.time.Clock()
map = Map()

sm = SessionManager(map)
player = sm.create_player_tank((400,300), speed=2, delay=20, health=100, direction=RIGHT, damage=400)
enemy = sm.create_ai_tank(ENEMIES, (440, 330), speed=1, delay=20, health=100, direction=DOWN, damage=400)

sm.create_tile(100)

game_iteration = 0
while True:
    clock.tick(fps)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):
        break

    player.update(keystate)
    enemy.update()

    sm.update()
    screen.fill(BLACK)
    sm.draw(screen)

    pg.display.flip()

    game_iteration += 1

pg.quit()
