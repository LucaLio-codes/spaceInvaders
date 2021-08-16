import math

import pygame
import util.helpers as help
import random
from PIL import Image, ImageFilter


class MyGroup(pygame.sprite.Group):

    def __init__(self, *args):
        super(MyGroup, self).__init__(args)

    def blur(self):
        for s in self.sprites():
            s.blur()


class MySprite(pygame.sprite.Sprite):

    def __init__(self):
        super(MySprite, self).__init__()

    def blur(self):
        tmp = Image.frombuffer("RGBA", self.image.get_size(), self.image.get_buffer()).filter(ImageFilter.GaussianBlur(radius=1))
        self.image = pygame.image.frombuffer(tmp.tobytes(), self.image.get_size(), "RGBA")


class Tank(MySprite):

    def __init__(self, scale, pos=(-1, -1)):
        super(Tank, self).__init__()

        self.scale = scale
        self.image = pygame.image.load("data/tank.png")
        self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), scale))
        self.rect = self.image.get_rect()
        self.sprite_height, self.sprite_width = self.rect.size
        self.window_width,self.window_height = pygame.display.get_window_size()
        if pos == (-1, -1):
            self.rect.y, self.rect.x = self.window_height - self.sprite_height, self.window_width/ 2 - self.sprite_width/2
        else:
            self.rect.y, self.rect.x = pos

    def update(self, *args) -> None:
        if args and args[0]:
            direction = args[0]
            tmp = self.rect.x + direction
            if tmp <= 0:
                self.rect.x = 0
            elif tmp > self.window_width - self.sprite_width:
                self.rect.x = self.window_width -self.sprite_width
            else:
                self.rect.x = tmp

    def kill(self) -> None:
            self.image = pygame.image.load("data/tank_broken.png")
            self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), self.scale))
        #super(Tank, self).kill()


    def get_pos(self):
        return self.rect.y, self.rect.x + self.sprite_width/2


class BulletTank (MySprite):

    def __init__(self, pos, scale):
        super(BulletTank, self).__init__()
        self.image = pygame.image.load("data/bullet_tank.png")
        self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), scale))
        self. rect = self.image.get_rect()
        self.hp = 2
        self.rect.y, self.rect.x = pos

    def update(self, *args, **kwargs) -> None:
        self.rect.y -= 1
        if self.rect.y <= 0:
            self.kill()

    def kill(self) -> None:
        if self.hp == 0:
            super(BulletTank, self).kill()
        else:
            self.hp -= 1


class BulletAlien (MySprite):

    def __init__(self, pos, scale):
        super(BulletAlien, self).__init__()
        self.image = pygame.image.load("data/bullet_alien_1.png")
        self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), scale))
        self.image2 = pygame.image.load("data/bullet_alien_2.png")
        self.image2 = pygame.transform.scale(self.image2, help.apply_scale(self.image2.get_size(), scale))
        self. rect = self.image.get_rect()
        self.hp = 3

        self.rect.y, self.rect.x = pos

    def update(self, *args, **kwargs) -> None:
        self.image, self.image2 = self.image2, self.image
        self.rect.y += 1
        if self.rect.y <= 0:
            self.kill()

    def kill(self) -> None:
        if self.hp == 0:
            super(BulletAlien, self).kill()
        else:
            self.hp -= 1


class Alien (MySprite):

    speed = 0

    def __init__(self, pos, scale, alien_type):
        super(Alien, self).__init__()
        self.alien_type = alien_type
        if alien_type == 4 or alien_type==3:
            self.alien_type = 2
        elif alien_type == 2:
            self.alien_type = 1
        self.able_to_shoot = True
        self.image = pygame.image.load("data/alien_%d_1.png" % (self.alien_type+1))
        self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), scale))
        self.rect = self.image.get_rect()
        self.image2 = pygame.image.load("data/alien_%d_2.png" % (self.alien_type+1))
        self.image2 = pygame.transform.scale(self.image2, help.apply_scale(self.image2.get_size(), scale))
        self.scale = scale
        self.sprite_height, self.sprite_width = self.rect.size
        self.hp = 2
        self.rect.y, self.rect.x = pos

    def update(self, *args, **kwargs) -> None:
        if args:
            x, y = args[0]
            self.image, self.image2 = self.image2, self.image
            self.rect.x, self.rect.y = self.rect.x + x, self.rect.y + y
            aliens = args[1]
            aliens.remove(self)
            self.rect.y += self.sprite_height
            if not pygame.sprite.spritecollideany(self, aliens) and random.randint(1, 50) < 10 and self.able_to_shoot:
                event = pygame.event.Event(pygame.USEREVENT + 3, {
                    "x": self.rect.centerx,
                    "y": self.rect.centery
                })
                pygame.time.set_timer(event, 250, 1)
            self.rect.y -= self.sprite_height
            aliens.add(self)


    def kill(self) -> None:
        if self.hp == 0:
            Alien.speed += 2
            event = pygame.event.Event(pygame.USEREVENT + 2, {"alien_type":self.alien_type})
            pygame.event.post(event)
            for g in self.groups():
                g.add(Explosion((self.rect.x, self.rect.y), self.scale))
            super(Alien, self).kill()
        else:
            self.hp -= 1


class HorizontalBoundary(MySprite):

    def __init__(self, pos):
        super(HorizontalBoundary, self).__init__()
        _,y = pygame.display.get_window_size()
        position = (pos, 0)
        size = (1, y)
        r = pygame.rect.Rect(position, size)
        self.rect = r
        self.image = pygame.Surface(size)
        self.image.fill((255,0,0))


class VerticalBoundary(MySprite):

    def __init__(self, pos):
        super(VerticalBoundary, self).__init__()
        _,y = pygame.display.get_window_size()
        position = (0, pos)
        size = (y, 1)
        r = pygame.rect.Rect(position, size)
        self.rect = r
        self.image = pygame.Surface(size)
        self.image.fill((255, 0, 0))


class Explosion(MySprite):

    def __init__(self, pos, scale):
        super(Explosion, self).__init__()
        self.image = pygame.image.load("data/explosion.png")
        self.image = pygame.transform.scale(self.image, help.apply_scale(self.image.get_size(), scale))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self, *args, **kwargs) -> None:
        self.kill()


class BunkerTile(MySprite):

    def __init__(self, pos, scale):
        super(BunkerTile, self).__init__()
        color = 92, 171, 94
        self.image = pygame.Surface((scale,scale))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos



class HUDText(MySprite):

    def __init__(self, text, pos, color, size=20):
        super(HUDText, self).__init__()

        self.color = color
        self.font = pygame.font.Font("data/EarlyGameBoy.TTF", size)
        self.image = self.font.render(text, False, color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self, *args, **kwargs) -> None:
        if args:
            self.image = self.font.render(str(args[0]), False, self.color)


class SplashAlien(Alien):

    def __init__(self, scale):
        rdm_type = random.randint(0, 4)
        self.bounds_x, self.bounds_y = pygame.display.get_window_size()
        right = random.randint(0, 1)
        pos_y = random.randint(0,self.bounds_y)
        pos_x = 0
        self.direction = -1

        if right:
          pos_x = self.bounds_x

        super(SplashAlien, self).__init__((pos_y, pos_x), scale, rdm_type)
        self.able_to_shoot = 0
        if not right:
            self.direction = 1
            self.rect.x -= self.sprite_width

    def update(self, *args, **kwargs) -> None:
        super(SplashAlien, self).update((self.direction, 0), MyGroup())
        if self.rect.x > self.bounds_x + 2*self.sprite_width or self.rect.x < -2*self.sprite_width:
            self.kill()


class SplashText(MySprite):

    def __init__(self, text, pos, color, size):
        super(SplashText, self).__init__()

        self.color = color
        self.font = pygame.font.Font("data/crazy.TTF", size)
        self.image = self.font.render(text, False, color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.rect.x -= self.rect.width / 2

    def update(self, *args, **kwargs) -> None:
        if args:
            self.image = self.font.render(str(args[0]), False, self.color)