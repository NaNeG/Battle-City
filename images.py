import os, pygame as pg
from pygame.transform import scale as reshape, rotate

def get_img(x, y, w, h, scale=1):
    orig = pg.Surface.subsurface(all_images, (x,y,w,h))
    return reshape(orig, (round(w * scale), round(h * scale)))

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')
img_path = os.path.join(img_folder, 'sprites.gif')

all_images = pg.image.load(img_path).convert_alpha()

from constants import scale

tank_ylw_img = get_img(0,0,13,13, scale)
tank_grn_img = get_img(16,0,13,13, scale)
tank_wsm_img = get_img(32,0,13,13, scale)

missing_img = get_img(48,64,13,13, scale)

bullet_img = get_img(75,74,3,4, scale)

bricks_img = get_img(48,64,8,8, scale)
red_bricks_img = get_img(56,64,8,8, scale)
concrete_img = get_img(48,72,8,8, scale)
leaves_img = get_img(56,72,8,8, scale)

exp1_img = get_img(0,80,32,32, scale)
exp2_img = get_img(32,80,32,32, scale)
exp3_img = get_img(64,80,32,32, scale)


def img_rotations(img):
    return (img,
            rotate(img, 270),
            rotate(img, 180),
            rotate(img, 90))