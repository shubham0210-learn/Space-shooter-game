import pygame
import random
pygame.font.init()
pygame.init()


WIDTH = 800
HEIGHT = 780
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("SPACE SHOOTER")

#IMAGES
BG = pygame.transform.scale(pygame.image.load("bg.jpg"),(WIDTH, HEIGHT))
logo = pygame.image.load("logo.jpg")
P1 = pygame.image.load("fighter.png")
V1 = pygame.image.load("blue.png")
V2 = pygame.image.load("red.png")
V3 = pygame.image.load("yellow.png")
V4 = pygame.image.load("boss.png")

RL =  pygame.image.load("rl.png")
BL =  pygame.image.load("bl.png")
YL =  pygame.image.load("yl.png")
GL =  pygame.image.load("gl.png")

super_font =  pygame.font.SysFont('ALGERIAN', 100)
super_font2 =  pygame.font.SysFont('ALGERIAN', 50)
title_font = pygame.font.SysFont("Forte", 50)
title_font2 = pygame.font.SysFont("Forte", 40)

MUSIC = pygame.mixer.music.load("BGM.mp3")
LASER_SOUND = pygame.mixer.Sound("las.wav")
pygame.mixer.music.set_volume(.3)
pygame.mixer.music.play(-1)
pygame.mixer.Sound.set_volume(LASER_SOUND,.1)

#ASSETS

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        WIN.blit(self.img,(self.x+17 ,self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship():
    COOLDOWN = 15

    def __init__(self,x,y,health):
        self.img = None
        self.x = x
        self.y = y
        self.health = health
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, WIN):
        WIN.blit(self.img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw()


    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 1
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



class Player(Ship):
    def __init__(self,x, y, health = 10):
        super().__init__(x, y, health)
        self.img = P1
        self.vel = 5
        self.score = 0
        self.laser_img = GL
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, WIN):
        super().draw(WIN)
        WIN.blit(self.img, (self.x, self.y))
        pygame.draw.rect(WIN, (255, 0, 0),(self.x, self.y + self.get_height() + 10, 50, 10))
        pygame.draw.rect(WIN, (0, 255, 0), (self.x, self.y + self.get_height() + 10, 50 * self.health/10 ,10))

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.score += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)




class Enemy(Ship):
    COLOR_MAP = {
                "red": (V2, RL ),
                "yellow": (V3, YL),
                "blue": (V1, BL)
                }

    def __init__(self,x, y,colour, health = 100):
        super().__init__(x, y,health)
        self.img,self.laser_img = self.COLOR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, WIN):
        super().draw(WIN)
        WIN.blit(self.img, (self.x, self.y))

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 1
                self.lasers.remove(laser)



def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return (obj1.mask.overlap(obj2.mask, (offset_x, offset_y))) != None



def main():
    RUN1 = False
    RUN2 = True
    FPS = 60
    LEVEL = 0
    LIVES = 5
    enemies = []
    enemy_wave = 3
    enemy_vel = 1
    laser_vel = 7
    player = Player(WIDTH/2 - 50 ,HEIGHT-120)
    clock = pygame.time.Clock()



    def redraw_window():
        WIN.blit(BG,(0,0))
        player.draw(WIN)
        lavel_lable = title_font2.render(f"WAVE:{LEVEL}", 1, (0,0,0))
        WIN.blit(lavel_lable, (40,20))
        lives_lable = title_font2.render(f"LIVES:{LIVES}", 1, (0,0,0))
        WIN.blit(lives_lable, (WIDTH - 170,20))
        NAME = super_font2.render(f"SCORE:{player.score}",1,(255,255,255))
        WIN.blit(NAME, (310,20))
        for enemy in enemies:
            enemy.draw(WIN)
        pygame.display.update()


    while RUN2:

        clock.tick(FPS)
        LOST_COUNT = 0
        if LIVES == 0 :
            RUN2 = False
        if player.health <= 0:
            RUN1 = False
            RUN2 = False
            RUN3 = True


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        if len(enemies) == 0:
            LEVEL += 1
            enemy_wave += 2
            enemy_vel += 0.1
            for i in range (enemy_wave):
                enemy = Enemy(random.randrange(100, WIDTH - 100,100), random.randrange(-1500,-500,100),random.choice(["red","yellow","blue"]))
                enemies.append(enemy)
        for enemy in enemies:
            enemy.y += enemy_vel
            if enemy.y + enemy.get_height()/2 > HEIGHT:
                enemies.remove(enemy)
                LIVES -= 1
            if collide(enemy, player):
                player.health -= 1
                enemies.remove(enemy)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()



        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP ] and player.y > 0:
            player.y -= player.vel
        if keys[pygame.K_DOWN] and player.y + player.get_height() < HEIGHT - 30:
            player.y += player.vel
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < WIDTH:
            player.x += player.vel
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player.vel
        if keys[pygame.K_SPACE]:
            LASER_SOUND.play()
            player.shoot()


        player.move_lasers(-laser_vel, enemies)

        redraw_window()

    while RUN3:
        str = "SPACE"
        str2 = "SHOOTER"
        caption = title_font.render("YOU LOST",1, (255,0,0))
        name1 = super_font.render(str, 1, (255, 255, 255))
        name2 = super_font.render(str2, 1, (255, 255, 255))
        title = title_font.render("PRESS ANY KEY TO PLAY AGAIN", 1, (0, 0, 0))
        WIN.blit(BG, (0, 0))
        WIN.blit(title, (50, 500))
        WIN.blit(name1, (250, 50))
        WIN.blit(name2, (200, 150))
        WIN.blit(caption, (300,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                main()


def menu():
    RUN1 = True
    while RUN1:
        str = "SPACE"
        str2 = "SHOOTER"
        name1 = super_font.render(str,1,(255,255,255))
        name2 = super_font.render(str2,1,(255,255,255))
        title = title_font.render("PRESS ANY KEY TO BEGIN",1,(0,0,0))
        WIN.blit(BG,(0,0))
        WIN.blit(title, (100,350))
        WIN.blit(name1,(250,50))
        WIN.blit(name2, (200,150))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                main()


    pygame.quit()

menu()




