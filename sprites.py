import pygame as pg
from settings import *
from time import sleep
import random 
from os import path

# Takes data from sprite sheet
class Spritesheet:
    # Utility class for pasrsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (52, 52))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.image = self.stand_frames[0]
        self.rect = self.image.get_rect()
        self.x = x *TILESIZE
        self.y = y *TILESIZE
        # Velocity and Physics
        self.vx, self.vy = 0,0
        self.walk_time = WALK_TIME
        self.player_speed = PLAYER_SPEED
        self.dx = 0
        self.dy = 0
        # Player Direction. 0 is down, 2 if up , 1 is left and 3 is right
        self.facing = 0

        # Update/Time Variables
        self.last_update = 0
        self.interact_update = 0
        self.dash_update = 0
        self.attack_update = 0
        self.damage_update = 0
        self.current_frame = 0
        # Flags
        self.walking = False
        self.interact = False
        self.pressed = False
        self.open = False
        self.read = False

        # Player Statistics
        self.health = PLAYER_HEALTH
        self.crystal = 0
        self.level = 1
        self.exp = 0

    # Movement Controls
    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.vx = -self.player_speed - self.dx
            self.facing = 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vx = self.player_speed + self.dx
            self.facing = 3
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.vy = -self.player_speed - self.dy
            self.facing = 0
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vy = self.player_speed + self.dy
            self.facing = 2
        # Diagonal Movement 
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def load_images(self):
        self.stand_frames = [self.game.spritesheet.get_image(0, 0, 32, 32),
                             self.game.spritesheet.get_image(32, 0, 32, 32)]
        self.walk_frames_r = [self.game.spritesheet.get_image(0, 64, 32, 32),
                              self.game.spritesheet.get_image(32, 64, 32, 32),
                            self.game.spritesheet.get_image(64, 64, 32, 32)]
        self.walk_frames_l =[self.game.spritesheet.get_image(0, 32, 32, 32),
                              self.game.spritesheet.get_image(32, 32, 32, 32),
                            self.game.spritesheet.get_image(64, 32, 32, 32)]
        self.walk_frames_u = [self.game.spritesheet.get_image(0, 96, 32, 32),
                              self.game.spritesheet.get_image(32, 96, 32, 32),
                            self.game.spritesheet.get_image(66, 96, 32, 32)]
        self.walk_frames_d = [self.game.spritesheet.get_image(0, 0, 32, 32),
                              self.game.spritesheet.get_image(32, 0, 32, 32),
                            self.game.spritesheet.get_image(66, 0, 32, 32)]

        for frame in self.walk_frames_r:  
           frame.set_colorkey(GREEN)
        for frame in self.walk_frames_l:
           frame.set_colorkey(GREEN)
        for frame in self.stand_frames:  
           frame.set_colorkey(GREEN)
        for frame in self.walk_frames_u:  
           frame.set_colorkey(GREEN)
        for frame in self.walk_frames_d:  
           frame.set_colorkey(GREEN)

    # Collision system for walls and objects
    def collide_with_sprite(self,sprite, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, sprite, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, sprite, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    # The button interaction works but the button press flag is in the wrong place
    def button_press(self):
        now = pg.time.get_ticks()
        hits = pg.sprite.spritecollide(self, self.game.buttons,False)
        if hits and self.interact:
            if now - self.interact_update > BUTT_TIME:
                hits[0].on = not hits[0].on
                self.interact_update = now
                if hits[0].on == True:
                    hits[0].image =  self.game.spritesheet5.get_image(0, 0, 32, 32)
                    hits[0].image.set_colorkey(BLACK)
                    hits[0].image = pg.transform.scale(hits[0].image, (TILESIZE, TILESIZE))
                else:
                    hits[0].image = self.game.spritesheet5.get_image(32, 32, 32, 32)
                    hits[0].image.set_colorkey(BLACK)
                    hits[0].image = pg.transform.scale(hits[0].image, (TILESIZE, TILESIZE))

    # Opening and closing door. Based off the button code
    def open_door(self):
        hits = pg.sprite.spritecollide(self, self.game.doors,False)
        if hits:
            if self.interact:
                hits[0].kill()
            else:
                self.collide_with_sprite(self.game.doors,'x')
                self.collide_with_sprite(self.game.doors, 'y')

    def break_barell(self):
        hits = pg.sprite.spritecollide(self, self.game.barells,False)
        if hits and self.interact: 
            hits[0].image = self.game.spritesheet2.get_image(182, 64, 64, 64)
            hits[0].image.set_colorkey(BLACK)
            if hits[0].broken == False:
                if self.health < PLAYER_HEALTH:
                    self.health += 10
                hits[0].broken = True

    # Chest interaction
    def open_chest(self):
        hits = pg.sprite.spritecollide(self, self.game.chests,False)
        self.collide_with_sprite(self.game.chests,'x')
        self.collide_with_sprite(self.game.chests, 'y')
        if hits and self.interact:
            hits[0].image = self.game.spritesheet2.get_image(256, 704, 64, 64)
            hits[0].image.set_colorkey(BLACK)

    # Damage Interaction
    def damage(self):
        now = pg.time.get_ticks()
        hits = pg.sprite.spritecollide(self, self.game.enemies,False)
        if hits:
            if now - self.damage_update > DAMAGE_TIME:
                self.health -= 10
                self.game.dmg_sound.play()
                self.damage_update = now
        else:
            pass
    def enemy_collide(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies,False)
        if hits:
            hits[0].vx = 0
    # Crystal Pick Up
    def pick_up(self):
        hits = pg.sprite.spritecollide(self, self.game.crystals,False)
        if hits:
            self.crystal += 1
            hits[0].kill()
            self.game.pickup_sound.play()
    # Needs to be cleaned up 
    def level_up(self):
        if self.exp >= 10*(2**self.level):
            self.game.levelup_sound.play()
            self.level += 1
            self.exp = 0

    def update(self):
        self.get_keys()
        self.vx += self.vx*(-0.12)
        self.vy += self.vy*(-0.12)
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt 
        # Wall and object collision 
        self.rect.x = self.x
        self.collide_with_sprite(self.game.walls, 'x')
        self.rect.y = self.y
        self.collide_with_sprite(self.game.walls, 'y')
        # Level up
        self.level_up()
        # Button interaction 
        self.button_press()
        # Door Interaction      
        self.open_door()
         # Chest Interaction
        self.open_chest()
        # Barells Busting 
        self.break_barell()
        # Damage on player
        self.damage()
        # Pick up crystals
        self.pick_up()
        # Animation Function
        self.animate()

    def animate(self):
        now = pg.time.get_ticks()
        # Walking animation
        if self.vx != 0 or self.vy!= 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > self.walk_time:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                if self.vx > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                elif self.vx < 0:
                    self.image = self.walk_frames_l[self.current_frame]
                elif self.vy < 0:
                    self.image = self.walk_frames_u[self.current_frame]
                else:
                    self.image = self.walk_frames_d[self.current_frame]
        # Idle Animation
        if not self.walking:
            if now - self.last_update > IDLE_TIME:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.stand_frames)
                self.image = self.stand_frames[self.current_frame]
        self.mask = pg.mask.from_surface(self.image)


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("img/walls.png")
        self.image = pg.transform.scale(self.image, (TILESIZE+4, TILESIZE+4))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Barell(pg.sprite.Sprite):
    def __init__(self, game, x, y, broken):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.barells
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet2.get_image(128, 64, 64, 64)
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.broken = broken
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Background(pg.sprite.Sprite):
    def __init__(self):
        self._layer = BG_LAYER
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("img/Dungeon.png")
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (51*TILESIZE, 16*TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = [0,0]

class Button(pg.sprite.Sprite):
    def __init__(self, game, x, y, on):
        self._layer = BUTTON_LAYER
        self.groups = game.all_sprites, game.buttons
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.on = on
        self.image = self.game.spritesheet5.get_image(32, 32, 32, 32)
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, open):
        self._layer = DOOR_LAYER
        self.groups = game.all_sprites, game.doors
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.open = open
        self.image = pg.image.load("img/door2.png")
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (32, TILESIZE + 5))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.open = True
        self.rect.x = x * TILESIZE +16
        self.rect.y = y * TILESIZE 

class Chest(pg.sprite.Sprite):
    def __init__(self, game, x, y, open):
        self._layer = CHEST_LAYER
        self.groups = game.all_sprites, game.chests
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.open = open
        self.image = self.game.spritesheet2.get_image(0,704, 64, 64)
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Dialogue(pg.sprite.Sprite):
    def __init__(self):
        self._layer = DIALOGUE_LAYER
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("img/font2.png")
        self.image = pg.transform.scale(self.image, (WIDTH, 200))
        self.rect = self.image.get_rect()
        self.rect.topleft = [0,400]

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, health, id):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.id = id
        self.load_images()
        self.image = self.stand_frames[0]
        self.image.set_colorkey(GREEN)
        self.current_frame = 0
        self.last_update = 0
        self.damage_update = 0
        self.health = 30
        self.walk_time = WALK_TIME
        self.damage_update = 0
        self.walking = False
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.vx = random.randrange(4, 8)
        self.vy = 0
        self.health = health
        self.dead = False

    def collide_with_sprite(self,sprite, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, sprite, False)
            if hits:
                if self.vx > 0:
                    self.vx = -(self.vx)
                    self.rect.x += self.vx
                else:
                    self.vx = -(self.vx)
                    self.rect.x += self.vx 
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, sprite, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def load_images(self):
        self.stand_frames = [self.game.spritesheet3.get_image(0, 0, 48, 71),
                             self.game.spritesheet3.get_image(48, 0, 48, 71)]
        self.walk_frames_r = [self.game.spritesheet3.get_image(0, 142, 48, 71),
                              self.game.spritesheet3.get_image(48, 142, 48, 71),
                            self.game.spritesheet3.get_image(96, 142, 48, 71)]
        self.walk_frames_l =[self.game.spritesheet3.get_image(0, 71, 48, 71),
                              self.game.spritesheet3.get_image(48, 71, 48, 71),
                            self.game.spritesheet3.get_image(96, 71, 48, 71)]

        for frame in self.walk_frames_r:  
           frame.set_colorkey(GREEN)
        for frame in self.walk_frames_l:
           frame.set_colorkey(GREEN)
        for frame in self.stand_frames:  
           frame.set_colorkey(GREEN)

    def animate(self):
        now = pg.time.get_ticks()
        # Walking animation
        if self.vx != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > self.walk_time:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                if self.vx > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                elif self.vx < 0:
                    self.image = self.walk_frames_l[self.current_frame]
        if not self.walking:
            if now - self.last_update > IDLE_TIME:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.stand_frames)
                self.image = self.stand_frames[self.current_frame]
    def damage(self):
        now = pg.time.get_ticks()
        hits = pg.sprite.spritecollide(self, self.game.bullets,False)
        if hits:
            if now - self.damage_update > DAMAGE_TIME:
                self.health -= 10
                self.damage_update = now
        else:
            pass
    def death(self):
        if (self.health <= 0) and (self.dead == False):
            self.game.player.exp += 10
            self.dead = True
            self.kill()

    def update(self):
        self.rect.x += self.vx 
        self.collide_with_sprite(self.game.walls,'x')
        self.collide_with_sprite(self.game.doors,'x')
        self.damage()
        self.animate()
        self.death()


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, x_direction, y_direction):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #self.image = pg.Surface((20, 20))
        #self.image.fill(LIGHTBLUE)
        self.image = pg.image.load("img/Water.png")
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (20, 20))
        self.current_frame = 0
        self.last_update = 0
        self.distance = 0
        self.damage_update = 0
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y 
        self.vx = x_direction
        self.vy = y_direction
        self.death_update = 0
    # Collision Death Sequence
    def collide_with_sprite(self,sprite):
        now = pg.time.get_ticks()
        hits = pg.sprite.spritecollide(self, sprite, False)
        if hits:
            self.game.hit_sound.play()
            self.image = self.game.spritesheet4.get_image(0, 50, 25, 25)
            self.image.set_colorkey(GREEN)
            self.image = pg.transform.scale(self.image, (25, 25))
            if now - self.death_update < 1000:
                self.kill()
            self.death_update = now

    def break_barell(self):
        hits = pg.sprite.spritecollide(self, self.game.barells,False)
        if hits and hits[0].broken == False: 
            hits[0].image = self.game.spritesheet2.get_image(182, 64, 64, 64)
            hits[0].image.set_colorkey(BLACK)
            hits[0].broken = True
            if self.game.player.health < PLAYER_HEALTH:
                self.game.player.health += 10
            self.kill()
        else:
            pass

    def update(self):
        self.rect.x += self.vx 
        self.rect.y += self.vy 
        self.distance += self.vx + self.vy
        self.collide_with_sprite(self.game.walls)
        self.collide_with_sprite(self.game.enemies)
        if self.distance > ATTACK_RANGE:
            self.kill()
        self.break_barell()

class Crystal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.crystals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("img/Red_Crystal.png")
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y 
        self.rect.x = x * TILESIZE + 16
        self.rect.y = y * TILESIZE + 16
        self.vy = 0
        self.dy = 0.4

    def update(self):
        self.vy += self.dy
        if self.vy >= 2 or self.vy <= - 1.0:
            self.dy *= -1
        self.rect.y += self.vy

class MobSpawn(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.spawn
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet5.get_image(64, 32, 32, 32)
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y 
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE 
        self.health = 60
        self.update_time = 0

    def update(self):
        # Spawn
        #Enemy(self.game,self.rect.x, self.rect.y, 30,1)
        #now = pg.time.get_ticks()
        #if now - self.update_time < 100:
            #Enemy(self.game,self.rect.x, self.rect.y, 30,1)
            #self.update_time = now
        pass
class Sign(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = OBJ_LAYER
        self.groups = game.all_sprites, game.signs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet5.get_image(32, 64, 32, 32)
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y 
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE 