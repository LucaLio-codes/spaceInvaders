import json

import pygame
import sys
import util.helpers as help
from util.sprites import Tank, BulletTank, Alien, HorizontalBoundary, VerticalBoundary, BunkerTile, BulletAlien, \
    MyGroup, HUDText, SplashAlien, SplashText
import math


SCALE = 3
RESOLUTION = 224, 256
BLACK = 0, 0, 0
FRAMERATE = 240
STARTSPEED = 1500
GREEN = 92, 171, 94
WHITE = 255, 255, 255
LEVEL = 0


class Main:

    def __init__(self):

        # State
        self.lives_count = 9
        self.pre_game = True
        self.paused = False
        self.score = 0
        self.direction = 1
        with open("data/scores.json") as f:
            self.json_dict = json.load(f)

        # Setup Pygame
        pygame.init()
        dims = help.apply_scale(RESOLUTION, SCALE)
        self.window_width, self.window_height = dims
        self.screen = pygame.display.set_mode(dims)
        self.clock = pygame.time.Clock()

        # Move Event for Aliens
        event = pygame.event.Event(pygame.USEREVENT + 1)
        pygame.time.set_timer(event.type, STARTSPEED)

        # Create Sprites
        self.tank = Tank(SCALE)
        self.tank_sprite = MyGroup(self.tank)

        # Live HUD
        live_tank1 = Tank(SCALE, (5, dims[0] - (dims[0] /5) + self.tank.sprite_width + 1/2 * self.tank.sprite_width ))
        live_tank2 = Tank(SCALE, (5, live_tank1.rect.x + 2 * self.tank.sprite_width))
        live_tank3 = Tank(SCALE, (5, live_tank2.rect.x + 2 * self.tank.sprite_width))
        self.lives = [live_tank1, live_tank2, live_tank3]
        self.dynamic_hud = MyGroup(live_tank1, live_tank2, live_tank3)

        # Bounds
        left_boundary = HorizontalBoundary(-1)
        right_boundary = HorizontalBoundary(dims[0])
        self.lower_boundary = VerticalBoundary(dims[0])
        self.bounds = MyGroup(left_boundary, right_boundary)

        # HUD
        score_text = HUDText("Score:" , (0,0), WHITE)
        lives_text = HUDText("Lives:",(dims[0] - dims[0] / 3, 0), WHITE)
        score = HUDText("0", (score_text.rect.width + 5, 0), GREEN)
        self.static_hud = MyGroup(score_text,lives_text)
        self.score_hud = MyGroup(score)

        # Groups for Bullets
        self.bullets = MyGroup()
        self.alien_bullets = MyGroup()

        # Aliens
        self.aliens = MyGroup()
        self.dummy = Alien((0, 0), SCALE, 0)
        temp = []
        x_offset = self.dummy.sprite_width/2
        y_offset = 50
        for i in range(5):
            for j in range(15):
                y = y_offset + i * self.dummy.sprite_height * 1.5
                x = x_offset + j * self.dummy.sprite_width * 1.5
                temp.append(Alien((y, x), SCALE, i))
        temp.reverse()
        self.aliens.add(temp)

        # Bunkers
        self.bunkers = MyGroup()
        for p in range(1,5):
            for j in range(-4,6):
                for i in range(-9, 11):
                    x = p * math.floor(self.window_width/5) + i*SCALE
                    y = self.window_height - self.dummy.sprite_height * 2 + j * SCALE
                    dummytile = BunkerTile((x, y), SCALE)
                    self.bunkers.add(dummytile)

        # Splashscreen
        self.splashAliens = MyGroup()
        title = SplashText("Space Invaders", (dims[0]/2, dims[1]/8),GREEN, 50)
        high_score = HUDText("High Score:", (0, 0), WHITE)
        name_from_json = self.json_dict["high_name"]
        score_from_json = str(self.json_dict["high_score"])
        high_score_name = HUDText(name_from_json, (dims[0] - high_score.rect.width / 2,0), GREEN)
        high_score_score = HUDText(score_from_json, (high_score.rect.width + 5 * SCALE , 0), GREEN)
        space_to_begin = SplashText("Press Space to Begin", (dims[0]/2, dims[1]/8 + title.rect.height), WHITE, 30)
        main_controls_1 = HUDText("Space: Shoot", (0 + 5 * SCALE, dims[1] - (3 * 15 + 5 * SCALE)), WHITE, 15)
        main_controls_2 = HUDText("Left, Right: move", (0 + 5 * SCALE, dims[1] - (2 * 15 + 5 * SCALE)), WHITE, 15)
        main_controls_3 = HUDText("A, D: move", (0 + 5 * SCALE, dims[1] - (15 + 5 * SCALE)), WHITE, 15)
        self.splashText = MyGroup(title, high_score, high_score_name, high_score_score, space_to_begin, main_controls_1,
                                  main_controls_2, main_controls_3)

        # New High Score Screen
        high_score_text = SplashText("NEW HIGH SCORE! Enter Name:",
                                     (dims[0]/2, dims[1]/8 + title.rect.height),
                                     WHITE,
                                     27)
        hs_controls_1 = HUDText("UP, DOWN: Scroll Character", (0 + 5*SCALE, dims[1] - (3 * 15 + 5 * SCALE)), WHITE, 15)
        hs_controls_2 = HUDText("Space: Confirm", (0 + 5*SCALE, dims[1] - (2 * 15 + 5 * SCALE)), WHITE, 15)
        hs_controls_3 = HUDText("Backspace: Undo", (0 + 5*SCALE, dims[1] - (15 + 5 * SCALE)), WHITE, 15)
        dummy_char = SplashText("_", (dims[0]/2, dims[1]/2),GREEN, 50)
        self.input = [
            SplashText("_", (dims[0]/2 - 2 * (dummy_char.rect.width + 5 * SCALE), dims[1]/2),GREEN, 50),
            SplashText("_", (dims[0]/2 - dummy_char.rect.width + 5 * SCALE, dims[1]/2),GREEN, 50),
            SplashText("_", (dims[0]/2 + 2.5 * (dummy_char.rect.width + 5 * SCALE), dims[1]/2),GREEN, 50),
            SplashText("_", (dims[0]/2 + dummy_char.rect.width + 5 * SCALE, dims[1]/2),GREEN, 50),
        ]
        # TODO Indicator to see which char is beeing edited
        self.newHigh = MyGroup(high_score_text, high_score, high_score_name, high_score_score, hs_controls_1,
                               hs_controls_2, hs_controls_3, title, self.input)


    def main_loop(self):
        while True:
            new_high = False
            game_over = False
            self.handle_events(False)

            # Splashscreen
            while self.pre_game:
                self.handle_events()
                self.render(0)
                if not self.splashAliens.sprites():
                    self.splashAliens.add(SplashAlien(SCALE))
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.pre_game = False
                self.splashAliens.update()
                self.clock.tick(FRAMERATE)

            # Game
            while not game_over and not self.paused:
                self.handle_events()
                self.render(1)
                updated = False
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.tank_sprite.update(-1, self.aliens)
                    updated = True
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.tank_sprite.update(1, self.aliens)
                    updated = True
                if not updated:
                    self.tank_sprite.update(0, self.aliens)
                pygame.sprite.groupcollide(self.bullets, self.bunkers, True, True)
                pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
                pygame.sprite.groupcollide(self.alien_bullets, self.bunkers, True, True)
                hit = pygame.sprite.spritecollideany(self.tank, self.alien_bullets)
                if hit:
                    self.lives_count -= 1
                    event = pygame.event.Event(pygame.USEREVENT + 4, {"lives": self.lives_count})
                    pygame.event.post(event)
                    hit.kill()
                if self.lives_count == 0 or pygame.sprite.spritecollideany(self.lower_boundary, self.aliens):
                    print(self.lives_count)
                    self.tank.kill()
                    event = pygame.event.Event(pygame.USEREVENT + 1)
                    pygame.time.set_timer(event, 0)
                    self.tank_sprite.blur()
                    self.bunkers.blur()
                    self.aliens.blur()
                    self.bullets.blur()
                    self.alien_bullets.blur()
                    self.render(1)
                    game_over = True
                    if self.score > self.json_dict["min"]:
                        new_high = True
                    pygame.time.wait(1000)
                    break

                self.bullets.update()
                self.alien_bullets.update()
                self.score_hud.update()
                self.clock.tick(FRAMERATE)
            # Game-Over Screen
            while game_over:
                if new_high:
                    self.handle_events(True)
                    self.render(3)
                else:
                    self.handle_events()
                    self.render(2)
                if not self.splashAliens.sprites():
                    self.splashAliens.add(SplashAlien(SCALE))
                self.splashAliens.update()
                self.clock.tick(FRAMERATE)

    def handle_events(self, text=False):

        for e in pygame.event.get():
            # Quit
            if e.type == pygame.QUIT:
                sys.exit()
            # Debug kill Aliens
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                hit = [s for s in self.aliens if s.rect.collidepoint(pos)]
                for h in hit:
                    h.kill()
                    h.kill()
                    h.kill()
            # Key Events
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if text:
                        # TODO confirm char/ next char
                        pass
                    else:
                        self.bullets.add(BulletTank(self.tank.get_pos(), SCALE))
                if e.key == pygame.K_UP:
                    # TODO scroll Char up
                    pass
                if e.key == pygame.K_DOWN:
                    # TODO scroll Char up
                    pass
                if e.key == pygame.K_k:
                    self.lives_count = 0
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
            # Move Event
            elif e.type == pygame.USEREVENT + 1:
                move = 30 * self.direction, 0
                self.aliens.update(move, self.aliens)
                if pygame.sprite.groupcollide(self.aliens, self.bounds, dokilla=False, dokillb=False):
                    self.direction *= -1
                    move = 30 * self.direction, self.dummy.sprite_height
                    self.aliens.update(move, self.aliens)
                    self.aliens.update((0, 0), self.aliens ) # to fix animation (im lazy)
            # Alien killed
            elif e.type == pygame.USEREVENT + 2:
                if Alien.speed % 10 == 0:
                    event = pygame.event.Event(pygame.USEREVENT + 1)
                    pygame.time.set_timer(event, STARTSPEED - math.floor(Alien.speed * 10))
                score = 0
                if e.alien_type == 1:
                    score = 300
                elif e.alien_type == 2:
                    score = 200
                elif e.alien_type == 3:
                    score = 100
                self.score += score
                self.score_hud.update(self.score)
            # Alien Shot
            elif e.type == pygame.USEREVENT + 3:
                self.alien_bullets.add(BulletAlien((e.y - 30, e.x), SCALE))
            # Live Lost
            elif e.type == pygame.USEREVENT + 4:
                if e.lives == 6:
                    self.lives[2].kill()
                elif e.lives == 3:
                    self.lives[1].kill()
                elif e.lives < 1:
                    self.lives[0].kill()

    def render(self, sequence):
        self.screen.fill(BLACK)
        if sequence == 0 or sequence == 2:
            self.splashAliens.draw(self.screen)
            self.splashText.draw(self.screen)
        elif sequence == 1:
            self.tank_sprite.draw(self.screen)
            self.aliens.draw(self.screen)
            self.bunkers.draw(self.screen)
            self.bullets.draw(self.screen)
            self.alien_bullets.draw(self.screen)
            self.static_hud.draw(self.screen)
            self.dynamic_hud.draw(self.screen)
            self.score_hud.draw(self.screen)
            self.bounds.draw(self.screen)
        elif sequence == 3:
            self.splashAliens.draw(self.screen)
            self.newHigh.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    dut = Main()
    dut.main_loop()
