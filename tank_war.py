import pygame
from pygame.locals import *
import logging
import math
import random
import math

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

pygame.init()

display_width = 1000
display_height = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GREY = (77, 79, 74)
BROWN = (102, 74, 50)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (153, 204, 255)

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
    gravity = 0.35
    air_resist = 0.994
    family = []

    def __init__(self, tank, power):
        self.x = tank.centerx - 4
        self.y = tank.centery - 10
        self.angle = tank.angle
        self.speed_x = math.cos(math.radians(self.angle)) * power
        self.speed_y = math.sin(math.radians(self.angle)) * power
        Bullet.family.append(self)

    @property
    def img(self):
        return pygame.transform.rotate(Bullet.init_img, -self.angle)

    def renew(self):
        self.speed_x *= Bullet.air_resist
        self.speed_y += Bullet.gravity
        self.angle = rtan(self.speed_x, self.speed_y) % 360
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y > horizon:
            Explosion(int(self.x), int(self.y))
            del Bullet.family[Bullet.family.index(self)]

    def show(self):
        gameDisplay.blit(self.img, (self.x, self.y))


class Tank:
    barrel_length = 30
    init_angle = 270
    family = []
    def __init__(self, x, y, b_color, w_color):
        self.x = x
        self.y = y
        self.b_color = b_color
        self.w_color = w_color
        self.length = Tank.barrel_length
        self.angle = Tank.init_angle
        Tank.family.append(self)
    @property
    def centerx(self):
        return self.x + int(tankbase_w / 2)

    @property
    def centery(self):
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
        end_x = self.centerx + math.cos(math.radians(self.angle)) * self.length
        end_y = self.centery + math.sin(math.radians(self.angle)) * self.length
        pygame.draw.line(gameDisplay, self.b_color, (self.centerx, self.centery), (end_x, end_y), 8)


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


class Explosion:
    init_radius = 3
    max_radius = 50
    dot_limit = 150
    dis_limit = 50

    family = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = Explosion.init_radius
        self.dormant = False
        self.dots = []
        self.gene = 0
        Explosion.family.append(self)

    def reproduce(self):
        for each in range(10):
            self.gene += 1
            dot_x = random.randint(self.x - self.radius, self.x + self.radius)
            dot_y = random.randint(self.y - self.radius, self.y + self.radius)
            dot_radius = random.randint(3, 5)
            self.dots.append({'color': (BLACK),
                              'x': dot_x,
                              'y': dot_y,
                              'r': dot_radius})

    def renew(self):
        # generate a new dot
        if (not self.dormant) and self.gene <= Explosion.dot_limit:
            self.reproduce()
        else:
            self.dormant = True
        # renew all other dots
        for dot in self.dots:
            dis = math.sqrt((dot['x'] - self.x)**2 + (dot['y'] - self.y)**2)
            dot['x'] = self.x + (dot['x'] - self.x) * 1.1
            dot['y'] = self.y + (dot['y'] - self.y) * 1.1
            dot['r'] *= 0.5
            if dot['r'] < 0.5 or dis > Explosion.dis_limit:
                self.dots.remove(dot)
            if dis <= 5:
                dot['color'] = RED
            elif dis <= 10:
                dot['color'] = YELLOW
            else:
                rgb = int((dis - 5) / (Explosion.max_radius - 5) * 255)
                if rgb < 0:
                    rgb = 0
                if rgb > 255:
                    rgb = 255
                dot['color'] = (rgb, rgb, rgb)
        if not self.dots and self.dormant:
            Explosion.family.remove(self)
            del self


    def show(self):
        for dot in self.dots:
            pygame.draw.circle(gameDisplay,
                               dot['color'],
                               (int(dot['x']), int(dot['y'])),
                               int(dot['r']))
        self.radius += 1


class Spark:

    init_length = 1
    limit = 30
    ang_range = 25
    dense = 10
    family = []

    def __init__(self, tank, color):
        self.x = tank.centerx
        self.y = tank.centerx
        self.color = color
        self.limit = Spark.limit
        self.angle = tank.angle
        self.ang_range = Spark.ang_range
        self.length = Spark.init_length
        self.change = 1
        self.dense = Spark.dense
        Spark.family.append(self)

    def show(self):
        ang_l = self.angle - self.ang_range
        ang_r = self.angle + self.ang_range
        range = self.ang_range * 2
        for each in (1, self.dense):
            spark_ang = ang_l + (range / self.dense) * each
            spark_x = int(self.y + math.sin(math.radians(360 - spark_ang)) * self.length)
            spark_y = int(self.y + math.cos(math.radians(360 - spark_ang)) * self.length)
            # if self.length <= self.limit:
            pygame.draw.circle(gameDisplay, self.color, (spark_x, spark_y), 1)
        self.length += self.change
        self.change += 1

    def renew(self):
        self.length += 2


def rtan(x, y):
    angle = math.degrees(math.atan(y / x))
    if x > 0:
        return angle
    else:
        return angle + 180

def quitgame():
    pygame.quit()
    quit()

def game_loop():
    global barrel_angle

    tank_x = 300
    enemy_x = 600
    x_change = 0
    ang_change = 0

    barrel_speed = 4
    barrel_limit = 60

    player_tank = Tank(tank_x, horizon, BLACK, BROWN)
    enemy_tank = Tank(enemy_x, horizon, BLACK, BROWN)
    shoot = False

    while True:
        key_press = pygame.key.get_pressed()

        if key_press[K_a]:
            player_tank.x -= 5
        if key_press[K_d]:
            player_tank.x += 5
        if key_press[K_LEFT]:
            enemy_tank.x -= 5
        if key_press[K_RIGHT]:
            enemy_tank.x += 5

        if key_press[K_e]:
            player_tank.angle += 2
        if key_press[K_q]:
            player_tank.angle -= 2
        if key_press[K_DOWN]:
            enemy_tank.angle += 2
        if key_press[K_UP]:
            enemy_tank.angle -= 2

        gameDisplay.fill(LIGHT_BLUE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_s:
                    Bullet(player_tank, 20)
                    Spark(player_tank, YELLOW)
                if event.key == K_RALT:
                    Bullet(enemy_tank, 20)
                    Spark(enemy_tank, YELLOW)

        # logging.debug("bullet angle -> {}".format(bullet.angle))
        # logging.debug("bullet loc -> {},{}".format(bullet.x, bullet.y))

        for each in Tank.family:
            #barrel check
            if each.angle >= 270 + barrel_limit:
                each.angle = 270 + barrel_limit
            if each.angle <= 270 - barrel_limit:
                each.angle = 270 - barrel_limit
            #wall check
            if each.x < 0:
                each.x = 0
            if each.x > display_width - tankbase_w:
                each.x = display_width - tankbase_w

        for bullet in Bullet.family:
            if bullet.x > player_tank.x and bullet.x < player_tank.x + tankbase_w:
                print("hit")
        for bullet in Bullet.family:
            bullet.renew()

        player_tank.show_tank()
        enemy_tank.show_tank()

        for each in Spark.family:
            each.renew()
            each.show()

        for bullet in Bullet.family:
            bullet.show()

        for explosion in Explosion.family:
            explosion.renew()
            explosion.show()

        print(clock.get_fps())

        pygame.display.update()
        clock.tick(30)

game_loop()
