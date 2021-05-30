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

with open('map.txt', 'r') as f:
    sm.parse_map(f.read(), True)
b = sm.create_bonus((560, 200), SHIELD)

game_iteration = 0
while True:
    clock.tick(fps)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):# or not sm.enemies.alive or not sm.players.alive:
        break

    sm.update(keystate)
    screen.fill(BLACK)
    sm.draw(screen)

    pg.display.flip()

    game_iteration += 1

pg.quit()
