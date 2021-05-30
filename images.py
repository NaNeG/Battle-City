import os, pygame as pg
from pygame.surface import Surface
from pygame.transform import scale as reshape, rotate, flip
from constants import BLACK, img_path, scale

def get_img(x, y, w, h, scale=1):
    orig = pg.Surface.subsurface(all_images, (x,y,w,h))
    return reshape(orig, (round(w * scale), round(h * scale)))


def colorize(img: Surface, color):
    colorImage = Surface(img.get_size()).convert_alpha()
    colorImage.fill(color)
    new_img = img.copy()
    new_img.blit(colorImage, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return new_img


all_images = pg.image.load(img_path).convert_alpha()

tank_ylw_img = get_img(0,0,13,13, scale)
tank_grn_img = get_img(16,0,13,13, scale)
tank_wsm_img = get_img(32,0,13,13, scale)

missing_img = get_img(48,64,13,13, scale)

bullet_img = get_img(75,74,3,4, scale)

bricks_img = get_img(48,64,8,8, scale)
red_bricks_img = get_img(56,64,8,8, scale)
concrete_img = get_img(48,72,8,8, scale)
green_img = get_img(56,72,8,8, scale)
water_img = get_img(64,64,8,8, scale)

base_img = get_img(0,16,16,14, scale)

exp1_img = get_img(10,92,11,10, scale)
exp2_img = get_img(40,91,15,13, scale)
exp3_img = get_img(64,81,32,29, scale)

grenade_bonus_img = get_img(0,32,16,15, scale)
shell_bonus_img = get_img(16,32,16,15, scale)
shovel_bonus_img = get_img(32,32,16,15, scale)
star_bonus_img = get_img(48,32,16,15, scale)
tank_bonus_img = get_img(64,32,16,15, scale)
timer_bonus_img = get_img(80,32,16,15, scale)
dark_bonus_img = colorize(grenade_bonus_img, (255,255,255,120))

base_bonus = get_img(0,16,16,14, scale)


def img_rotations(img):
    return (img,
            rotate(img, 270),
            flip(rotate(img, 180), True, False),
            flip(rotate(img, 90), False, True))

def darken(img, deg=120):
    return colorize(img, (255,255,255,deg))
