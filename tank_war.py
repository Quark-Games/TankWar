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
BRIGHT_RED = (255, 20, 0)
BRIGHT_GREEN = (0, 255, 0)
GREY = (77, 79, 74)
BROWN = (102, 74, 50)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (153, 204, 255)
LIGHT_BROWN = (74, 52, 38)
LIGHT_YELLOW = (255, 255, 153)
DARK_ORANGE = (204, 102, 0)
LIGHT_ORANGE = (255, 153, 51)

horizon = display_height - 100

gameDisplay = pygame.display.set_mode((display_width, display_height), FULLSCREEN)
pygame.display.set_caption('TANK WAR')
tankicon = pygame.image.load("tank_img.png")
terrianimg = pygame.image.load("tankwar_terrian.png")
cloud_1 = pygame.image.load("cloud_1.png")
cloud_2 = pygame.image.load("cloud_2.png")
pygame.display.set_icon(tankicon)
clock = pygame.time.Clock()

class Buttons:

    def __init__(self, x, y, w, h, ac_color, ic_color, text, size):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ac_color = ac_color
        self.ic_color = ic_color
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.font = pygame.font.SysFont(None, size)

    @property
    def text_objects(self):
        bit_map = self.font.render(self.text, True, BLACK)
        return bit_map, bit_map.get_rect()

    def show_ac(self):
        pygame.draw.rect(gameDisplay, self.ac_color, self.rect)

    def show_ic(self):
        pygame.draw.rect(gameDisplay, self.ic_color, self.rect)

    @property
    def collide(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            return True
        else:
            return False
    @property
    def click(self):
        click = pygame.mouse.get_pressed()
        if click[0] == 1:
            return True

    def write(self):
        smallText = pygame.font.SysFont("comicsansms", 45)
        TitleSurf, TitleRect = self.text_objects
        TitleRect.center = (self.x+(self.w/2), self.y+(self.h/2))
        gameDisplay.blit(TitleSurf, TitleRect)


class Msg:

    def __init__(self, x, y, text, size):
        self.x = x
        self.y = y
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont(None, self.size)

    @property
    def text_objects(self):
        bit_map = self.font.render(self.text, True, BLACK)
        return bit_map, bit_map.get_rect()

    def show(self):
        textSurf, textRect = self.text_objects
        textRect.center = (self.x, self.y)
        gameDisplay.blit(textSurf, textRect)


class Bar:

    width = 140
    height = 20
    thickness = 3
    font = pygame.font.SysFont(None, 30)

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
        if self.current_p <= 0:
            self.current_p = 0
        textSurf = self.text_objects
        #inside rect
        pygame.draw.rect(gameDisplay, self.color,
                        (self.x, self.y, self.current_p * (Bar.width / self.points), Bar.height))
        #outside rect
        pygame.draw.rect(gameDisplay, BLACK,
                        (self.x, self.y, Bar.width, Bar.height),
                         Bar.thickness)
        gameDisplay.blit(textSurf, (self.x, self.y - 20))


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


class Crack:

    img = pygame.image.load("crack.png")
    img2 = pygame.image.load("crack2.png")
    imgs = [img, img2]
    rounds = 100
    family = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.round = Crack.rounds
        Crack.family.append(self)
        self.image = Crack.imgs[random.randint(0, len(Crack.imgs) - 1)]

    def show(self):
        gameDisplay.blit(self.image, (self.x - 13, horizon))

    def renew(self):
        if self.round > 0:
            self.round -= 1
        else:
            del Crack.family[Crack.family.index(self)]


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
            Crack(self.x, self.y)
            Explosion(int(self.x), horizon)
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

    energy = 100

    def __init__(self, x, y, b_color, w_color):
        self.x = x
        self.y = y
        self.b_color = b_color
        self.w_color = w_color
        self.length = Tank.barrel_length
        self.angle = Tank.init_angle
        Tank.family.append(self)
        self.health = Tank.init_health
        self.energy = Tank.energy

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


def rtan(x, y):
    angle = math.degrees(math.atan(y / x))
    if x > 0:
        return angle
    else:
        return angle + 180

def quitgame():
    pygame.quit()
    quit()

def button(obj):
    if obj.collide:
        obj.show_ac()
        if obj.click:
            return True
    else:
        obj.show_ic()
    obj.write()

def setton(obj):
    obj.show_ic()
    obj.write()
    if obj.collide:
        obj.show_ac()
        obj.write()
        return True

def game_renew():
    Bullet.family = []
    Obstacle.rects = []
    Explosion.family = []
    Tank.family = []

def paused():
    contin_b = Buttons(750, 450, 140, 70, BRIGHT_GREEN, GREEN, "CONTINUE", 30)
    restart_b = Buttons(150, 450, 140, 70, BRIGHT_GREEN, GREEN, "RESTART", 30)
    title = Msg(display_width / 2, display_height / 3, "PAUSED", 80)
    title.show()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_RETURN:
                    return None
        if button(contin_b):
            return None
        if button(restart_b):
            game_renew()
            return game_loop()
        pygame.display.update()
        clock.tick(30)

def settings():
    back_b = Buttons(750, 520, 120, 50, BRIGHT_GREEN, GREEN, "BACK", 30)
    play_b = Buttons(150, 520, 120, 50, BRIGHT_GREEN, GREEN, "PLAY", 30)
    title = Msg(display_width / 2, display_height / 6, "SETTINGS", 80)


    l_set_family = []
    r_set_family = []
    texts = ("BARREL LEFT", "BARREL RIGHT", "TANK LEFT",
             "TANK RIGHT", "POWER UP", "POWER DOWN", "FIRE")

    with open("l_key.txt", "r") as file:
        l_keys = file.read().split(",")
    with open("r_key.txt", "r") as file:
        r_keys = file.read().split(",")

    for each in l_keys:
        ind = l_keys.index(each)
        k_name = pygame.key.name(int(l_keys[ind]))
        pos = ind + 1
        if (ind + 1) % 2 == 0:
            pos = ind
        if (ind + 1) % 2 == 0:
            button_x = 250
        # if ind == 6:
        #     button_x = 150
        else:
            button_x = 50
        l_set_family.append(Buttons(button_x,
                          int(display_height / 14) * pos + 110, 150, 60,
                          BRIGHT_GREEN, GREEN,
                          texts[int(ind)] + ": " + k_name, 23))
    for each in r_keys:
        r_ind = r_keys.index(each)
        r_k_name = pygame.key.name(int(r_keys[r_ind]))
        r_pos = r_ind + 1
        # if r_ind == 6:
        #     r_button_x = 650
        if (r_ind + 1) % 2 == 0:
            r_pos = r_ind
        if (r_ind + 1) % 2 == 0:
            r_button_x = 800
        else:
            r_button_x = 600
        r_set_family.append(Buttons(r_button_x,
                          int(display_height / 14) * r_pos + 110, 150, 60,
                          BRIGHT_GREEN, GREEN,
                          texts[int(r_ind)] + ": " + r_k_name, 23))
    print(r_set_family)

    while True:
        gameDisplay.fill(LIGHT_BLUE)
        title.show()

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                with open("l_key.txt", "w") as file:
                    file.write(','.join(map(str, l_keys)))
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    with open("l_key.txt", "w") as file:
                        file.write(','.join(map(str, l_keys)))
                    quitgame()
                if event.key == K_RETURN:
                    return None
        if button(back_b):
            with open("l_key.txt", "w") as file:
                file.write(','.join(map(str, l_keys)))
            return None
        if button(play_b):
            with open("l_key.txt", "w") as file:
                file.write(','.join(map(str, l_keys)))
            return game_loop()

        for each in l_set_family:
            if setton(each):
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        num = l_set_family.index(each)
                        l_keys[num] = event.key
                        each.text = texts[num] + ": " + pygame.key.name(int(l_keys[num]))
        for each in r_set_family:
            if setton(each):
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        num = r_set_family.index(each)
                        r_keys[num] = event.key
                        each.text = texts[num] + ": " + pygame.key.name(int(r_keys[num]))

        with open("l_key.txt", "w") as file:
            file.write(','.join(map(str, l_keys)))
        with open("r_key.txt", "w") as file:
            file.write(','.join(map(str, r_keys)))

        pygame.display.update()
        clock.tick(30)

def game_intro():
    quit_b = Buttons(750, 450, 140, 70, LIGHT_ORANGE, DARK_ORANGE, "QUIT", 30)
    play_b = Buttons(150, 450, 140, 70, LIGHT_ORANGE, DARK_ORANGE, "PLAY", 30)
    title = Msg(display_width / 2, display_height / 3, "TANK WAR", 80)
    bigcloud_x = random.randint(0, display_width - 500)
    bigcloud_y = random.randint(0, int(display_height / 4))
    tinycloud_x = random.randint(500, display_width)
    tinycloud_y = random.randint(0, int(display_height / 4))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_s:
                    settings()
                if event.key == K_RETURN:
                    game_loop()
        gameDisplay.fill(LIGHT_BLUE)
        gameDisplay.blit(terrianimg, (0, 0))
        gameDisplay.blit(cloud_1, (bigcloud_x, bigcloud_y))
        gameDisplay.blit(cloud_2, (tinycloud_x, tinycloud_y))
        title.show()
        if bigcloud_x < -380:
            bigcloud_x = random.randint(0, 500) + display_width
        else:
            bigcloud_x -= 2
        if tinycloud_x < -113:
            tinycloud_x = random.randint(0, 500) + display_width
        else:
            tinycloud_x -= 4
        if button(quit_b):
            return quitgame()
        if button(play_b):
            return game_loop()
        pygame.display.update()
        clock.tick(30)

def end(text):
    quit_b = Buttons(750, 390, 140, 60, LIGHT_YELLOW, YELLOW, "QUIT", 30)
    replay_b = Buttons(150, 390, 140, 60, LIGHT_YELLOW, YELLOW, "START AGAIN", 30)
    title = Msg(display_width / 2, display_height / 3 - 60, "GAME OVER", 80)
    bigcloud_x = random.randint(0, display_width - 500)
    bigcloud_y = random.randint(0, int(display_height / 3))
    tinycloud_x = random.randint(500, display_width)
    tinycloud_y = random.randint(0, int(display_height / 3))
    win_msg = Msg(display_width / 2, display_height / 2 - 60, text, 40)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == K_RETURN:
                    game_renew()
                    game_intro()

        gameDisplay.fill(LIGHT_BLUE)
        gameDisplay.blit(terrianimg, (0, 0))
        gameDisplay.blit(cloud_1, (bigcloud_x, bigcloud_y))
        gameDisplay.blit(cloud_2, (tinycloud_x, tinycloud_y))
        title.show()
        win_msg.show()
        if bigcloud_x < -380:
            bigcloud_x = random.randint(0, 500) + display_width
        else:
            bigcloud_x -= 2
        if tinycloud_x < -113:
            tinycloud_x = random.randint(0, 500) + display_width
        else:
            tinycloud_x -= 4
        if button(quit_b):
            return quitgame()
        if button(replay_b):
            game_renew()
            return game_intro()
        pygame.display.update()
        clock.tick(30)

def game_loop():

    global barrel_angle

    tank_x = 300
    enemy_x = 600
    x_change = 0
    ang_change = 0

    barrel_speed = 4
    barrel_limit = 60

    player_power = 12
    enemy_power = 12

    #create objects
    player_tank = Tank(tank_x, horizon, BLACK, BROWN)
    enemy_tank = Tank(enemy_x, horizon, BLACK, BROWN)
    #create bars
    left_bar = Bar(10, 30, YELLOW, 12, 12, "Power: ")
    right_bar = Bar(850, 30, YELLOW, 12, 12, "Power: ")
    l_healbar = Bar(10, 80, RED, 5, 5, "Health: ")
    r_healbar = Bar(850, 80, RED, 5, 5, "Health: ")
    l_energy = Bar(10, 130, LIGHT_ORANGE, int(Tank.energy / 10),
                   int(Tank.energy / 10), "Energy: ")
    r_energy = Bar(850, 130, LIGHT_ORANGE, int(Tank.energy / 10),
                   int(Tank.energy / 10), "Energy: ")

    #read keys from l_key.txt
    with open("l_key.txt", "r") as file:
        keys = file.read().split(",")
    keys = map(int, keys)
    bl, br, tl, tr, pu, pd, f = keys

    #set obstacle
    Obstacle.set()

    while True:

        key_press = pygame.key.get_pressed()

        gameDisplay.fill(LIGHT_BLUE)

        #tank movement
        if key_press[tl]:
            player_tank.x -= 5
        if key_press[tr]:
            player_tank.x += 5
        if key_press[K_l]:
            enemy_tank.x -= 5
        if key_press[39]:
            enemy_tank.x += 5

        #barrel movement
        if key_press[br]:
            player_tank.angle += 2
        if key_press[bl]:
            player_tank.angle -= 2
        if key_press[K_LEFTBRACKET]:
            enemy_tank.angle += 2
        if key_press[K_o]:
            enemy_tank.angle -= 2

        #power change
        if key_press[pu]:
            if player_power < 12:
                player_power += 1
        if key_press[pd]:
            if player_power > 1:
                player_power -= 1
        if key_press[K_p]:
            if enemy_power < 12:
                enemy_power += 1
        if key_press[K_SEMICOLON]:
            if enemy_power > 1:
                enemy_power -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                if event.key == f:
                    if player_tank.energy > 0:
                        Bullet(player_tank, player_power + 10)
                        Spark(player_tank, YELLOW)
                        player_tank.energy -= 25

                if event.key == K_k:
                    if enemy_tank.energy > 0:
                        Bullet(enemy_tank, enemy_power + 10)
                        Spark(enemy_tank, YELLOW)
                        enemy_tank.energy -= 25

                if event.key == K_SPACE:
                    paused()

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
            #check Health
            if each.health <= 0:
                if each == player_tank:
                    return end("RIGHT SIDE WON")
                else:
                    return end("LEFT SIDE WON")

        #obstacle check
        if player_tank.x + player_tank.tankbase_w >= Obstacle.x:
            player_tank.x = Obstacle.x - player_tank.tankbase_w
        if enemy_tank.x <= Obstacle.x + Obstacle.width * 3:
            enemy_tank.x = Obstacle.x + Obstacle.width * 3

        #show progress bar
        left_bar.current_p = player_power
        right_bar.current_p = enemy_power
        left_bar.show()
        right_bar.show()
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
        #cracks
        for each in Crack.family:
            each.renew()
            each.show()
        #energy
        if player_tank.energy < Tank.energy:
            player_tank.energy += 1
        if enemy_tank.energy < Tank.energy:
            enemy_tank.energy += 1
        #show energy
        l_energy.current_p = int(player_tank.energy / 10)
        l_energy.show()
        r_energy.current_p = int(enemy_tank.energy / 10)
        r_energy.show()
        pygame.display.update()
        clock.tick(30)

try:
    game_intro()

except KeyboardInterrupt:
    quitgame()
