import pygame as pg
from constants import *


pg.init()
pg.display.set_caption("Battle City")
screen = pg.display.set_mode(screen_size)
clock = pg.time.Clock()

from gamemanager import GameManager

gm = GameManager(screen)
while True:
    events = pg.event.get()

    if any(event.type == pg.QUIT for event in events):
        break

    clock.tick(fps)
    gm.update()
    pg.display.flip()

pg.quit()
