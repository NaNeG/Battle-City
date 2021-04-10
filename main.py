import os, pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Tank(pg.sprite.Sprite):
    (UP, RIGHT, DOWN, LEFT) = range(4) # типа как енумы в шарпе
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)

        self.image_up = player_img
        self.image_right = pg.transform.rotate(self.image, 270)
        self.image_down = pg.transform.rotate(self.image, 180)
        self.image_left = pg.transform.rotate(self.image, 90)

        self.speed = 2
        self.direction = self.UP
        self.controls = [pg.K_SPACE, pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]

    def rotate(self):
        if self.direction == self.UP:
            self.image = self.image_up
        elif self.direction == self.RIGHT:
            self.image = self.image_right
        elif self.direction == self.DOWN:
            self.image = self.image_down
        elif self.direction == self.LEFT:
            self.image = self.image_left


class Player(Tank):
    def __init__(self):
        super().__init__()

    def update(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_UP]:
            self.direction = self.UP
            self.rect.y -= self.speed # ось y направлена вниз
        elif keystate[pg.K_RIGHT]:
            self.direction = self.RIGHT
            self.rect.x += self.speed
        elif keystate[pg.K_DOWN]:
            self.direction = self.DOWN
            self.rect.y += self.speed
        elif keystate[pg.K_LEFT]:
            self.direction = self.LEFT
            self.rect.x -= self.speed
        self.rotate()




pg.init()
pg.display.set_caption("Battle City")
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')
clock = pg.time.Clock()
screen = pg.display.set_mode((800, 600))
all_images = pg.image.load(os.path.join(img_folder, 'sprites.gif')).convert()
player_img = pg.Surface.subsurface(all_images, (0,0,13,13))
sprite_group = pg.sprite.Group()
player = Player()
sprite_group.add(player)

running = True
while running:
    clock.tick(30)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    sprite_group.update()

    screen.fill(BLACK)
    sprite_group.draw(screen)

    pg.display.flip()

pg.quit()