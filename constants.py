import os as _os


# settings
screen_size = (800, 600)
scale = 2.5
fps = 30


# pathes
game_folder = _os.path.dirname(__file__)
img_folder = _os.path.join(game_folder, 'images')
img_path = _os.path.join(img_folder, 'sprites.gif')


# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# directions & controls
(UP, RIGHT, DOWN, LEFT, FIRE) = range(5)


# bonuses
(SHIELD, DESTROY_ENEMIES, REPAIR_FORTRESS, POWER_UP, HEALING) = range(5)
