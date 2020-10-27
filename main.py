import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from time import *
import random


def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
        self.running = True

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map = Map(path.join(game_folder, 'map.txt'))
        self.spritesheet = Spritesheet(path.join("img", SPRITESHEET))
        # Use for next spritesheet 2
        self.spritesheet2 = Spritesheet(path.join("img", SPRITESHEET2))
        self.spritesheet3 = Spritesheet(path.join("img", SPRITESHEET3))
        self.spritesheet4 = Spritesheet(path.join("img", SPRITESHEET4))
        self.spritesheet5 = Spritesheet(path.join("img", SPRITESHEET5))
        # Load Sounds
        self.snd_dir = path.join(game_folder, 'snd')
        self.hit_sound = pg.mixer.Sound(path.join(self.snd_dir,'Hit_Hurt.wav' ))
        self.pickup_sound = pg.mixer.Sound(path.join(self.snd_dir,'Pickup_Crystals.wav' ))
        self.levelup_sound = pg.mixer.Sound(path.join(self.snd_dir,'Level_Up.wav' ))
        self.dmg_sound = pg.mixer.Sound(path.join(self.snd_dir,'Damage.wav' ))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.barells = pg.sprite.Group()
        self.buttons = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.chests = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.dialogue_boxes = pg.sprite.Group()
        self.crystals = pg.sprite.Group()
        self.spawn = pg.sprite.Group() 
        self.signs = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'O':
                    Barell(self, col, row, False)
                if tile == 'B':
                    Button(self, col, row, False)
                if tile == 'D':
                    Door(self, col, row, False)
                if tile == 'C':
                    Chest(self, col, row, False)
                if tile == 'E':
                    Enemy(self, col, row, 30,1)
                if tile == 'R':
                    Crystal(self, col, row)
                if tile == 'S':
                    MobSpawn(self, col, row)
                if tile == 'T':
                    Sign(self, col, row)

        self.camera = Camera(self.map.width, self.map.height)
        self.bg = Background()
        self.bg_image = pg.image.load("img/Dungeon.png")
        self.dial = Dialogue()
        self.dial.image.set_colorkey(GREEN)
        # Time variables
        self.delay_time = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'CleytonRX.ogg'))
        self.run()

    def run(self):
        # Game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops = -1)
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            if self.player.health < 0:
                self.show_go_screen()
        pg.mixer.music.fadeout(FADE)
    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        now = pg.time.get_ticks()
        self.screen.blit(self.bg_image, [0,0])
        self.screen.blit(self.bg.image, self.camera.apply(self.bg))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.sign_post()
        # Top Left Corner
        dg_h = pg.image.load("img/font2.png")
        dg_h = pg.transform.scale(dg_h, (200, 80))
        self.screen.blit(dg_h,[0, 0])
        self.draw_text("Health: ", 18, TXT_COLOR, 55, 5)
        self.draw_text("Crystals: " + str(self.player.crystal), 18, TXT_COLOR, 55, 25)
        self.draw_text("LEVEL: " + str(self.player.level), 18, TXT_COLOR, 55, 45)
        # Health Bar
        draw_player_health(self.screen, 90, 5, self.player.health / PLAYER_HEALTH)
        pg.display.flip()

    # Generic Dialogue Function
    def sign_post(self):
        if self.player.read == True and self.num == 0:
            self.screen.blit(self.dial.image,[0, HEIGHT*2/3])
            self.draw_text("Games are more fun with friends", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 40)
            self.draw_text("We are working to make this game a multiplayer.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 80)
            self.draw_text("We'll get there eventually.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 120)
            self.draw_text("-- Struggling Game Developer", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 150)
        elif self.player.read == True and self.num == 1:
            self.screen.blit(self.dial.image,[0, HEIGHT*2/3])
            self.draw_text("The game code is made by John. Concept is by Horacio", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 40)
            self.draw_text( "and Todd made some sprites or whatever.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 80)
            self.draw_text("Just joking, his sprites are amazing.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 120)
            self.draw_text("-- John", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 150)
        elif self.player.read == True and self.num == 2:
            self.screen.blit(self.dial.image,[0, HEIGHT*2/3])
            self.draw_text("You can pick up crystals to move on to the next level", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 40)
            self.draw_text( "Use WASD or the arrow keys to move.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 80)
            self.draw_text("X is for attack and Z is for interact.", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 120)
            self.draw_text("-- Random Passerby", 22, TXT_COLOR, WIDTH/2, HEIGHT*2/3 + 150)
        else:
            self.dial.kill()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def events(self):
        # catch all events here
        now = pg.time.get_ticks()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_z:
                    self.player.interact = True
                if event.key == pg.K_SPACE:
                    pg.key.set_repeat(3000)
                    if now - self.player.dash_update > 1000:
                        self.player.dy = DASH_SPEED
                        self.player.dx = DASH_SPEED
                        self.walk_time = WALK_TIME/2
                        self.player.dash_update = now
                if event.key == pg.K_c:
                    self.num = random.randrange(0,3)
                    self.player.read = not self.player.read
                if now - self.player.dash_update > 1000:
                    if event.key == pg.K_x:
                        pg.key.set_repeat(1000)
                        if not( (self.player.facing % 2) == 0):
                            Bullet(self, self.player.rect.x + 10 * (self.player.facing -2), self.player.rect.y, 2* (self.player.facing -2), 0)
                        else:
                            Bullet(self, self.player.rect.x + 10 * (self.player.facing -1), self.player.rect.y, 0, 2* (self.player.facing -1))
                    self.player.attack_update
                if event.key == pg.K_p:
                    self.paused()
            if event.type == pg.KEYUP:
                if event.key == pg.K_z:
                    self.player.interact = False
                if event.key == pg.K_SPACE:
                    self.player.dy = 0
                    self.player.dx = 0
                    self.walk_time = WALK_TIME

    def paused(self):
        self.pause = True
        while self.pause:
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.pause = False
                    break
                
            self.screen.blit(self.dial.image,[0, HEIGHT/3])
            self.draw_text("PAUSED", 48, TXT_COLOR, WIDTH/2, HEIGHT/2 - 40)
            self.draw_text("Press R to resume the game", 22, TXT_COLOR, WIDTH/2, HEIGHT/2 + 20)
            pg.display.flip()

    def show_start_screen(self):
        # Game start screen
        background_image = pg.image.load("img/bg_dg.png")
        background_image = pg.transform.scale(background_image, (WIDTH, HEIGHT))
        self.screen.blit(background_image, [0,0])
        dg = pg.image.load("img/font2.png")
        dg = pg.transform.scale(dg, (WIDTH, 260))
        self.screen.blit(dg,[0, HEIGHT/3 - 30])
        self.draw_text(TITLE, 48, TXT_COLOR, WIDTH / 2, HEIGHT/ 2 - 100)
        self.draw_text("WASD for or arrow keys for movement", 22, TXT_COLOR, WIDTH / 2, HEIGHT/ 2 - 20)
        self.draw_text("Z for interact, X for attack and C for read", 22, TXT_COLOR, WIDTH / 2, HEIGHT/ 2 + 20)
        self.draw_text("Press any key to begin", 22, TXT_COLOR, WIDTH/ 2, HEIGHT / 2 + 70 )
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # Game over screen
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, TXT_COLOR, WIDTH / 2, HEIGHT/ 4)
        self.draw_text("Press a key to play again", 22, TXT_COLOR, WIDTH/ 2, HEIGHT * 3 / 4)

        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

# create the game object
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
pg.quit