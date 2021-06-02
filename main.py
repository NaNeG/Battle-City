import pygame as pg
from constants import *


pg.init()
pg.display.set_caption("Battle City")
screen = pg.display.set_mode(screen_size)

from sessionmanager import SessionManager
from map import Map

clock = pg.time.Clock()
map = Map()

pg.mixer.init(44100, -16, 1, 512)

sm = SessionManager(map)

with open('map.txt', 'r') as f:
    sm.parse_map(f.read(), True)

def pause():
    paused = True
    while paused:
        keystate = pg.key.get_pressed()

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                quit()

        if keystate[pg.K_RETURN]:
            paused = False

        font = pg.font.SysFont("verdana", 24)
        text = font.render("Нажмите ENTER чтобы продолжить", 1, WHITE)
        screen.blit(text, (5, 5))
        pg.display.flip()

while True:
    clock.tick(fps)
    keystate = pg.key.get_pressed()

    events = pg.event.get()
    if any(event.type == pg.QUIT for event in events):# or not sm.enemies.alive or not sm.players.alive:
        break

    if keystate[pg.K_ESCAPE]:
        pause()

    sm.update(keystate)
    screen.fill(BLACK)
    sm.draw(screen)

    pg.display.flip()

pg.quit()
