import pygame
from pygame.locals import *
import logging
import math

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

pygame.init()

display_width = 800
display_height = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GREY = (77, 79, 74)
BROWN = (102, 74, 50)

tankbase_h = 15
tankbase_w = 60
top_r = tankbase_h
tank_wheel_r = int(tankbase_h / 2)
tank_wheel_d = tankbase_h

tank_w = tankbase_w
tank_h = tankbase_h * 2 + tank_wheel_r

barrel_angle = 270
barrel_length = 2 * tankbase_h

horizon = display_height - 100

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('TANK WAR')
clock = pygame.time.Clock()

class Bullet:
    init_img = pygame.image.load("bullet.png")
    gravity = 0.3
    air_resist = 0.99

    def __init__(self, x, y, angle, power):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed_x = math.cos(math.radians(angle)) * power
        self.speed_y = math.sin(math.radians(angle)) * power

    @property
    def x_graph(self):
        return self.x

    @property
    def y_graph(self):
        return display_height - self.y

    @property
    def angle_graph(self):
        angle = self.angle - 90
        return angle % 360

    @property
    def img(self):
        image = Bullet.init_img
        return pygame.transform.rotate(image, self.angle_graph)

    def renew(self):
        self.speed_x *= Bullet.air_resist
        self.speed_y -= Bullet.gravity
        self.angle = math.degrees(math.atan(self.speed_y / self.speed_x))
        self.x += self.speed_x
        self.y += self.speed_y

    def show(self):
        gameDisplay.blit(self.img, (self.x_graph, self.y_graph))

class Tank:
    def __init__(self, x, y, b_color, w_color, length, angle):
        self.x = x
        self.y = y
        self.b_color = b_color
        self.w_color = w_color
        self.length = length
        self.angle = angle

    @property
    def bulletx(self):
        return self.x + int(tankbase_w / 2)

    @property
    def bullety(self):
        return self.y + tankbase_h

    def show_tank(self):
        #top
        pygame.draw.circle(gameDisplay, self.b_color,
                          (self.x + 2 * top_r, self.y + top_r), top_r)
        #base
        pygame.draw.rect(gameDisplay, self.b_color,
                        (self.x, self.y + tankbase_h, tankbase_w, tankbase_h))
        #wheel
        for each in range(1, 5):
            pygame.draw.circle(gameDisplay, self.w_color,
                              (self.x + (tank_wheel_d * each - tank_wheel_r),
                               self.y + tankbase_h * 2), tank_wheel_r)
        #barrel
        end_y = self.bullety + math.sin(math.radians(self.angle)) * self.length
        end_x = self.bulletx + math.cos(math.radians(self.angle)) * self.length
        pygame.draw.line(gameDisplay, self.b_color, (self.bulletx, self.bullety), (end_x, end_y), 5)

class Buttons:
    def __init__(self, x, y, w, h, ac_color, ic_color, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ac_color = ac_color
        self.ic_color = ic_color
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def show_ac(self):
        pygame.draw.rect(gameDisplay, self.ac_color, self.rect)

    def show_ic(self):
        pygame.draw.rect(gameDisplay, self.ic_color, self.rect)

    def collide(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            return True
        else:
            return False

    def click(self):
        click = pygame.mouse.get_pressed()
        if click[0] == 1:
            return True

    def write(self):
        smallText = pygame.font.SysFont("comicsansms", 45)
        TitleSurf, TitleRect = text_objects(self.text,smallText)
        TitleRect.center = (self.x+(self.w/2), self.y+(self.h/2))
        gameDisplay.blit(TitleSurf, TitleRect)

def quitgame():
    pygame.quit()
    quit()

def game_loop():
    global barrel_angle

    tank_x = 400
    x_change = 0
    ang_change = 0

    barrel_speed = 4
    barrel_limit = 60

    player_tank = Tank(tank_x, horizon, BLACK, BROWN, barrel_length, barrel_angle)

    shoot = False

    while True:
        key_press = pygame.key.get_pressed()

        if key_press[K_a]:
            player_tank.x -= 5
        if key_press[K_d]:
            player_tank.x += 5
        if key_press[K_e]:
            player_tank.angle += 5
        if key_press[K_q]:
            player_tank.angle -= 5

        gameDisplay.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_SPACE:
                    shoot = True

        barrel_angle += ang_change

        # logging.debug("bullet angle -> {}".format(bullet.angle))
        # logging.debug("bullet loc -> {},{}".format(bullet.x, bullet.y))

        #barrel check
        if player_tank.angle >= 270 + barrel_limit:
            player_tank.angle = 270 + barrel_limit
        if player_tank.angle <= 270 - barrel_limit:
            player_tank.angle = 270 - barrel_limit

        #wall check
        if player_tank.x < 0:
            player_tank.x = 0
        if player_tank.x > display_width - tankbase_w:
            player_tank.x = display_width - tankbase_w
        #shoot
        if shoot:
            bullet = Bullet(player_tank.bulletx, player_tank.bullety, player_tank.angle, 10)
            shoot = False
            bullet.show()
            bullet.renew()

        player_tank.show_tank()

        pygame.display.update()
        clock.tick(30)

game_loop()
