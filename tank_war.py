import pygame
from pygame.locals import *
import logging
import math
import random

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
LIGHT_BROWN = (74, 52, 38)

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
        # hit ground
        if self.y > horizon:
            Explosion(int(self.x), int(self.y))
            for each in Tank.family:
                if self.x > each.x and self.x < each.x + each.tankbase_w:
                    each.health -= 1
            del Bullet.family[Bullet.family.index(self)]
        # hit obstacles
        for rect in Obstacle.rects:
            if rect.collidepoint((self.x, self.y)):
                Explosion(int(self.x), int(self.y))
                del Bullet.family[Bullet.family.index(self)]

    def show(self):
        gameDisplay.blit(self.img, (self.x, self.y))


class Tank:

    init_health = 5
    tankbase_h = 15
    tankbase_w = 60
    top_r = tankbase_h
    tank_wheel_r = int(tankbase_h / 2)
    tank_wheel_d = tankbase_h

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
        self.health = Tank.init_health

    @property
    def centerx(self):
        return self.x + int(Tank.tankbase_w / 2)

    @property
    def centery(self):
        return self.y - Tank.tankbase_h - Tank.tank_wheel_r

    @property
    def end_x(self):
        return self.centerx + math.cos(math.radians(self.angle)) * self.length

    @property
    def end_y(self):
        return self.centery + math.sin(math.radians(self.angle)) * self.length

    def show_tank(self):
        #top
        pygame.draw.circle(gameDisplay, self.b_color,
                          (self.centerx, self.centery), Tank.top_r)
        #base
        pygame.draw.rect(gameDisplay, self.b_color,
                        (self.x, self.y - Tank.tankbase_h - Tank.tank_wheel_r,
                         Tank.tankbase_w, Tank.tankbase_h))
        #wheel
        for each in range(1, 5):
            pygame.draw.circle(gameDisplay, self.w_color,
                              (self.x + (Tank.tank_wheel_d * each - Tank.tank_wheel_r),
                               self.y - Tank.tank_wheel_r), Tank.tank_wheel_r)
        #barrel
        pygame.draw.line(gameDisplay,
                         self.b_color,
                         (self.centerx, self.centery),
                         (self.end_x, self.end_y),
                         8)


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
    limit = 20
    ang_range = 25
    dense = 2

    family = []

    def __init__(self, tank, color):
        self.tank = tank
        self.color = color
        self.angle = tank.angle
        self.length = Spark.init_length
        self.change = 1
        Spark.family.append(self)

    @property
    def x(self):
        return self.tank.end_x

    @property
    def y(self):
        return self.tank.end_y

    def show(self):
        for ang in range(self.angle - Spark.ang_range,
                         self.angle + Spark.ang_range + 1,
                         int(Spark.ang_range / self.dense)):
            x = int(self.x + math.sin(math.radians(90 - ang)) * self.length)
            y = int(self.y + math.cos(math.radians(90 - ang)) * self.length)
            pygame.draw.circle(gameDisplay, self.color, (x, y), 2)
        self.length += self.change
        self.change += 1

    def renew(self):
        self.length += 2
        if self.length >= Spark.limit:
            del Spark.family[Spark.family.index(self)]


class Obstacle:

    num = 3
    height = 300
    width = 30
    x = int(display_width / 2 - ((width * num) / 2))
    rects = []

    @classmethod
    def show(cls):
        for rect in Obstacle.rects:
            pygame.draw.rect(gameDisplay, LIGHT_BROWN, rect)

    @classmethod
    def set(cls):
        for i in range(Obstacle.num):
            h = random.randint(100, cls.height)
            y = horizon - h
            x = Obstacle.x + (Obstacle.width * i)
            rect = pygame.Rect(x, y, Obstacle.width, h)
            Obstacle.rects.append(rect)


class Bar:

    width = 140
    height = 20
    thickness = 3
    font = pygame.font.SysFont("comicsansms",30)

    def __init__(self, x, y, color, points, current_p, msg):
        self.x = x
        self.y = y
        self.color = color
        self.points = points
        self.current_p = current_p
        self.msg = msg

    @property
    def text_objects(self):
        bit_map = Bar.font.render(self.msg + str(self.current_p), True, BLACK)
        return bit_map

    def show(self):
        textSurf = self.text_objects
        slice = int(Bar.width / self.points)
        #inside rect
        pygame.draw.rect(gameDisplay, self.color,
                        (self.x, self.y, self.current_p * slice, Bar.height))
        #outside rect
        pygame.draw.rect(gameDisplay, BLACK,
                        (self.x, self.y, Bar.width - slice, Bar.height),
                         Bar.thickness)
        gameDisplay.blit(textSurf, (self.x, self.y - 20))


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

    player_power = 20
    enemy_power = 20

    #create objects
    player_tank = Tank(tank_x, horizon, BLACK, BROWN)
    enemy_tank = Tank(enemy_x, horizon, BLACK, BROWN)
    left_bar = Bar(10, 30, YELLOW, 13, player_power - 9, "Power: ")
    right_bar = Bar(860, 30, YELLOW, 13, enemy_power - 9, "Power: ")
    l_healbar = Bar(10, 80, RED, 6, 5, "Health: ")
    r_healbar = Bar(860, 80, RED, 6, 5, "Health: ")

    Obstacle.set()

    while True:
        key_press = pygame.key.get_pressed()

        gameDisplay.fill(LIGHT_BLUE)

        #tank movement
        if key_press[K_a]:
            player_tank.x -= 5
        if key_press[K_d]:
            player_tank.x += 5
        if key_press[K_l]:
            enemy_tank.x -= 5
        if key_press[39]:
            enemy_tank.x += 5

        #barrel movement
        if key_press[K_e]:
            player_tank.angle += 2
        if key_press[K_q]:
            player_tank.angle -= 2
        if key_press[K_LEFTBRACKET]:
            enemy_tank.angle += 2
        if key_press[K_o]:
            enemy_tank.angle -= 2

        #power change
        if key_press[K_w]:
            if player_power < 22:
                player_power += 1
        if key_press[K_s]:
            if player_power > 10:
                player_power -= 1
        if key_press[K_p]:
            if enemy_power < 22:
                enemy_power += 1
        if key_press[K_SEMICOLON]:
            if enemy_power > 10:
                enemy_power -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_f:
                    Bullet(player_tank, player_power)
                    Spark(player_tank, YELLOW)
                if event.key == K_k:
                    Bullet(enemy_tank, enemy_power)
                    Spark(enemy_tank, YELLOW)

        for each in Tank.family:
            #barrel check
            if each.angle >= 270 + barrel_limit:
                each.angle = 270 + barrel_limit
            if each.angle <= 270 - barrel_limit:
                each.angle = 270 - barrel_limit
            #wall check
            if each.x < 0:
                each.x = 0
            if each.x > display_width - each.tankbase_w:
                each.x = display_width - each.tankbase_w

        #obstacle check
        if player_tank.x + player_tank.tankbase_w >= Obstacle.x:
            player_tank.x = Obstacle.x - player_tank.tankbase_w
        if enemy_tank.x <= Obstacle.x + Obstacle.width * 3:
            enemy_tank.x = Obstacle.x + Obstacle.width * 3


        #show progress bar
        left_bar.current_p = player_power - 9
        right_bar.current_p = enemy_power - 9
        left_bar.show()
        right_bar.show()
        #show health bar
        l_healbar.current_p = player_tank.health
        r_healbar.current_p = enemy_tank.health
        l_healbar.show()
        r_healbar.show()
        #land
        pygame.draw.rect(gameDisplay,
                         GREEN,
                         (0, horizon, display_width, display_height - horizon))
        #obstacles
        Obstacle.show()
        #bullet renew
        for bullet in Bullet.family:
            bullet.renew()
        #show all tank
        for each in Tank.family:
            each.show_tank()
            each.show_tank()
        #show all Bullet
        for bullet in Bullet.family:
            bullet.show()
        #show spark
        for each in Spark.family:
            each.renew()
            each.show()
        #show explosion
        for explosion in Explosion.family:
            explosion.renew()
            explosion.show()

        pygame.display.update()
        clock.tick(30)

try:
    game_loop()
except KeyboardInterrupt:
    quitgame()
