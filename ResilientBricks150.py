import pygame
import random
import json
import os
import math
import time
import sys, os

def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

INVADER_PATTERN = [
    "001110011100",
    "011111011110",
    "111111111111",
    "111011110111",
    "111111111111",
    "001101101100",
    "001001001000",
]

CONTROL_MODE_VALUES = ["Keyboard", "mouse", "Joypad"]
CONTROL_MODE_DISPLAY = [
    "Keyboard- Arrow keys + '1' to fire.",
    "Mouse control+Left button to fire missile.",
    "Joypad-Left,right buttons. A to fire."
]

GRAVITY = 200
WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 0
Max_BRICK_RESILIENCE = 2
exploding =[False]
boss_intro_timer =[0]
pygame.joystick.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(32)
End_level=15
flash_timer = 0
FLASH_DURATION = 200   # milliseconds


playlist = None
current_track = 0

class WarpTunnel:
    def __init__(self, width, height):
        self.active = False
        self.timer = 0
        self.duration = 3.0  # total warp time
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.fade = 0  # 0 → 255

    def start(self):
        self.active = True
        self.timer = self.duration
        self.fade = 0

    def update(self, dt, stars):
        if not self.active:
            return

        self.timer -= dt

        for star in stars:
            # star = [x, y, speed, color]

            # 1. Exponential acceleration
            star[2] *= 1.05

            # 2. Radial stretch toward centre
            dx = star[0] - self.center_x
            dy = star[1] - self.center_y
            star[0] += dx * 0.04
            star[1] += dy * 0.04

        # Fade to white near the end
        if self.timer < 1.0:
            self.fade = int((1.0 - self.timer) * 255)

        if self.timer <= 0:
            self.active = False

    def draw_overlay(self, screen):
        if not self.active:
            return

        # White fade overlay
        if self.fade > 0:
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill((255, 255, 255))
            overlay.set_alpha(self.fade)
            screen.blit(overlay, (0, 0))

class EndMessage:
    def __init__(self, width, height, duration=5.0):
        self.active = False
        self.timer = 0
        self.duration = 3.0  # how long the message stays visible
        self.alpha = 0
        self.width = width
        self.height = height
        self.duration =duration

        self.font_big = pygame.font.Font(None, 72)
        self.font_small = pygame.font.Font(None, 42)

    def start(self):
        self.active = True
        self.timer = self.duration
        self.alpha = 0

    def update(self, dt):
        if not self.active:
            return

        # Fade in for first 1 second
        if self.timer > self.duration - 1.0:
            self.alpha = min(255, self.alpha + dt * 255)

        # Fade out for last 1 second
        elif self.timer < 1.0:
            self.alpha = max(0, self.alpha - dt * 255)

        self.timer -= dt

        # End message finished
        if self.timer <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        # Render text
        text1 = self.font_big.render("MISSION COMPLETE!", True, (0, 255, 0))
        text2 = self.font_small.render("You have saved the luna arena", True, (200, 200, 255))
        text3 = self.font_small.render("The alien forces have been defeated.", True, (200, 200, 255))

        # Apply alpha
        text1.set_alpha(self.alpha)
        text2.set_alpha(self.alpha)
        text3.set_alpha(self.alpha)

        # Center positions
        rect1 = text1.get_rect(center=(self.width // 2, self.height // 2 - 00))
        rect2 = text2.get_rect(center=(self.width // 2, self.height // 2 + 80))
        rect3 = text3.get_rect(center=(self.width // 2, self.height // 2 + 160))

        # Draw
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        screen.blit(text3, rect3)

class CreditsScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False
        self.finished = False
        self.y = height + 50   # start just below the screen

        self.speed = 40        # scroll speed
        self.font = pygame.font.Font(None, 30)

        self.lines = [
            "*SMASH DELUXE*",
            "",
            "Programming & Design:",
            "Ike Muoma",
            "https://activesynapticsoftware.org/"
            "",
            "Visual imagery arts:",
            "Neil Hawkins",
            "https://www.instagram.com/neilsy420/"
            "",
            "AI assistant:",
            "Microsoft Copilot",
            "",
            "Sound contributions:",
            "",
            "20180831.bouncing.ball.corridor.74.wav by dobroide",
            " -- https://freesound.org/s/439304/ -- License: Attribution 4.0",
            "",
            "smash_far.wav by singintime",
            " -- https://freesound.org/s/170630/ -- License: Attribution 4.0",
            "",
            "hit_002.wav by leviclaassen",
            "-- https://freesound.org/s/107789/ -- License: Attribution 4.0",
            "",
            "Explosion Test by Apenguin73",
            "-- https://freesound.org/s/335152/ -- License: Creative Commons 0",
            "",
            "Launch.wav by ChrisButler99",
            "-- https://freesound.org/s/367987/ -- License: Attribution 4.0"
            "",
            "Arpeggiator End Credits .wav by lharman94",
            "-- https://freesound.org/s/329597/ -- License: Creative Commons 0",
            "",
            "German Techno loop.wav by Satanen",
            "-- https://freesound.org/s/317383/ -- License: Creative Commons 0",
            "",
            "Rechambering Click 2.wav by morganpurkis",
            "-- https://freesound.org/s/379975/ -- License: Creative Commons 0",
            "",
            "power 37 v2.wav by Centurion_of_war",
            "-- https://freesound.org/s/416019/ -- License: Attribution 4.0",
            "",
            "Robot voice - intruder alert.wav by Ionicsmusic",
            "-- https://freesound.org/s/137916/ -- License: Attribution NonCommercial 3.0",
            "",
            "Arcade Laser 014.wav by Debsound",
            "-- https://freesound.org/s/339169/ -- License: Attribution NonCommercial 4.0",
            "timpani1-chiptone.wav by AceOfSpadesProduc100",
            "",
            "large explosion 1 by V-ktor ",
            "-- https://freesound.org/s/482993/ -- License: Creative Commons 0",
            "",
            "poujade_eva_2020_2021_BouncingBall(son1).wav by iut_Paris8",
            "-- https://freesound.org/s/567801/ -- License: Creative Commons 0",
            "",
            "Spacey 1up/Power up by GameAudio",
            "-- https://freesound.org/s/220173/ -- License: Creative Commons 0",
            "",
            "Robot voice - red alert.wav by Ionicsmusic",
            "-- https://freesound.org/s/137948/ -- License: Attribution NonCommercial 3.0"
            "",
            "Permission to panic? by deleted_user_2906614",
            "-- https://freesound.org/s/263621/ -- License: Attribution 3.0",
            "",
            "Transition Whoosh 6.wav by F.M.Audio",
            "-- https://freesound.org/s/616208/ -- License: Attribution 4.0",
            "",
            "Alien landing by BloodPixelHero",
            "-- https://freesound.org/s/591091/ -- License: Attribution 4.0",
            "",
            "Teaser Background Music by Migfus20",
            "-- https://freesound.org/s/560738/ -- License: Attribution 4.0",
            "",
            "Long Decay Explosion (2).wav by JohanDeecke",
            "-- https://freesound.org/s/369530/ -- License: Attribution 3.0",
            "",
            "WarpDrive_02.wav by LittleRobotSoundFactory",
            "-- https://freesound.org/s/270554/ -- License: Attribution 4.0",
            "",
            "Sound Design Elements Whoosh SFX 040 by AudioPapkin ",
            "-- https://freesound.org/s/812675/ -- License: Creative Commons 0",
            "",
            "(c) 2026 Activesynaptic Games.",
            
            "Thank you for playing!"
        ]

    def start(self):
        self.active = True
        self.finished = False
        self.y = self.height + 50

    def update(self, dt):
        if not self.active:
            return

        self.y -= self.speed * dt

        # When credits fully scroll off screen, stop them
        if self.y < -len(self.lines) * 60:
            self.active = False
            self.finished = True

    def draw(self, screen):
        if not self.active:
            return

        y = self.y
        for line in self.lines:
            text = self.font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(self.width // 2, int(y)))
            screen.blit(text, rect)
            y += 60

class Boss:
    def __init__(self, x, y, scale=12):
        self.x = x
        self.y = y
        self.fire_cooldown = 0
        self.burst_offsets = []
        self.burst_timer = 0
        self.flash_timer = 0

        # Add this:
        self.fire_rate = 60
        self.fire_cooldown = 0

        self.dead = False
        self.death_timer = 0

        self.scale = scale
        # Compute width/height from pattern
        self.width = len(INVADER_PATTERN[0]) * scale
        self.height = len(INVADER_PATTERN) * scale

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Compute width/height from pattern
        self.width = len(INVADER_PATTERN[0]) * scale
        self.height = len(INVADER_PATTERN) * scale

        # Horizontal movement
        self.speed = 3
        self.direction = 1

        # Sinusoidal vertical movement
        self.wave_offset = 0
        self.wave_speed = 0.05
        self.wave_amplitude = 40
        self.base_y = y

        # ⭐ Boss health
        self.hp = 20
        self.max_hp = 20

        # Flash when hit
        self.flash_timer = 0

    def hit(self):
        self.hp -= 1
        self.flash_timer = 0.15

    def draw_health_bar(self, screen):
        bar_width = 300
        bar_height = 20
        x = WIDTH // 2 - bar_width // 2
        y = 40

        # Background bar
        pygame.draw.rect(screen, (80, 80, 80), (x, y, bar_width, bar_height))

        # Foreground bar (scaled to HP)
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * ratio, bar_height))

        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    def fire_logic(self, missiles):
        if self.fire_cooldown <= 0:
            self.fire_missile(missiles)
            self.fire_cooldown = self.fire_rate

    def update(self):

        # Horizontal movement
        self.x += self.speed * self.direction

        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.direction *= -1

        # Smooth vertical sine wave
        self.wave_offset += self.wave_speed
        self.y = self.base_y + math.sin(self.wave_offset) * self.wave_amplitude

        self.rect.x = self.x
        self.rect.y = self.y

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def draw(self, screen):
        # Flash white if recently hit
        if self.flash_timer > 0:
            color = (255, 255, 255)  # flash color
        else:
            color = (0, 255, 0)  # normal boss color

        for row_idx, row in enumerate(INVADER_PATTERN):
            for col_idx, pixel in enumerate(row):
                if pixel == "1":
                    pygame.draw.rect(
                        screen,
                        color,
                        (
                            self.x + col_idx * self.scale,
                            self.y + row_idx * self.scale,
                            self.scale,
                            self.scale
                        )
                    )

    def fire_missile(self, missiles, x_offset=0):
        x = self.rect.centerx + x_offset
        y = self.rect.bottom
        missile = BossMissile(x, y)
        missiles.add(missile)

class BossMissile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Missile appearance
        self.image = pygame.Surface((6, 20))
        self.image.fill((255, 50, 50))

        # Position
        self.rect = self.image.get_rect(center=(x, y))

        # Speed (pixels per frame)
        self.speed = 6

    def update(self):
        # Move downward
        self.rect.y += self.speed

        # Remove if off-screen
        if self.rect.top > HEIGHT:
            self.kill()
class StartScreen:
    def __init__(self, screen, starfield):
        self.screen = screen
        self.starfield = starfield
        self.c=0

        self.options = ["Start Game", "Controls Options", "Mission Briefing", "High Scores","Credits", "Quit"]
        self.selected = 0

        self.title_font = pygame.font.Font(None, 90)
        self.menu_font = pygame.font.Font(None, 50)

        self.running = True

        self.copyright_font = pygame.font.Font(None, 30)
        self.copyright_font.set_italic(True)
        self.copyright_text = self.copyright_font.render(
            "Smash Deluxe © 2026 Activesynaptic Games. All Rights Reserved.", True, (0, 255, 0)
        )

        # Start just off the right edge
        self.copyright_x = WIDTH
        self.copyright_y = HEIGHT - 40  # bottom of the screen

    def reset_state(self):
        self.selected = 0
        self.running = True
        self.c = 0

        # Reset copyright scroll
        self.copyright_x = WIDTH

        # If run() uses any of these, reset them too:
        if hasattr(self, "choice_made"):
            self.choice_made = False
        if hasattr(self, "fade"):
            self.fade = 0
        if hasattr(self, "timer"):
            self.timer = 0
        if hasattr(self, "ready"):
            self.ready = False

    def handle_input(self, event):
        pygame.mixer.init()
        gun_rechamber = pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav"))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                gun_rechamber.play()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                gun_rechamber.play()
            elif event.key == pygame.K_RETURN:
                gun_rechamber.play()
                return self.options[self.selected]
        return None

    def update(self, dt):
        self.starfield.update(dt)

        # Move left by 2 pixels per frame
        if self.copyright_x > 10:  # stop at x = 10
            self.copyright_x -= 1

    def draw(self,logocol1,logocol2,logocol3):
        self.screen.fill((0, 0, 0))
        self.starfield.draw(self.screen)

        # Draw the scrolling copyright
        self.screen.blit(self.copyright_text, (self.copyright_x, self.copyright_y))


        # Title
        title = self.title_font.render("*SMASH DELUXE*", True, (logocol1,logocol2,logocol3))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 120))

        # Menu
        y = 210 #This is the y coordinate of the start menu
        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            surf = self.menu_font.render(text, True, color)
            self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, y))
            y += 60

    def run(self):

        pygame.event.clear()
        clock = pygame.time.Clock()

        input_lock = pygame.time.get_ticks() + 200

        while self.running:
            dt = clock.tick(60) / 1000

            for event in pygame.event.get():

                # just skip mouse events, don't exit run()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    continue

                if pygame.time.get_ticks() < input_lock:
                    continue

                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                choice = self.handle_input(event)
                if choice is not None:
                    return choice

            self.update(dt)
            c1 = random.randint(0, 255)
            c2 = random.randint(0, 255)
            c3 = random.randint(0, 255)
            self.draw(c1, c2, c3)
            pygame.display.flip()


class Starfield3D:
    def __init__(self, width, height, num_stars=300):
        self.width = width
        self.height = height
        self.num_stars = num_stars
        self.stars = []

        for _ in range(num_stars):
            self.stars.append(self.new_star())

    def new_star(self):
        # x, y in range -1..1, z in range 0.1..1
        return [
            random.uniform(-1, 1),   # x
            random.uniform(-1, 1),   # y
            random.uniform(0.1, 1)   # z depth
        ]

    def update(self, speed=0.02):
        for star in self.stars:
            star[2] -= speed
            if star[2] <= 0:
                star[:] = self.new_star()

    def draw(self, surface):
        cx = self.width // 2
        cy = self.height // 2

        for x, y, z in self.stars:
            # Perspective projection
            k = 300 / z
            sx = int(cx + x * k)
            sy = int(cy + y * k)

            if 0 <= sx < self.width and 0 <= sy < self.height:
                size = max(1, int((1 - z) * 5))
                shade = max(150, min(255, int((1 - z) * 255)))
                pygame.draw.circle(surface, (shade, shade, shade), (sx, sy), size)

class ScrollingBriefing:
    def __init__(self, text_lines, font, width, height):
        self.lines = text_lines
        self.font = font
        self.width = width
        self.height = height

        self.speed = 40  # slow + readable
        self.start_y = height + 50
        self.y = self.start_y
        self.total_height = len(text_lines) * font.get_linesize()

        self.finished = False

        self.rendered = [font.render(line, True, (255, 0, 0)) for line in text_lines]

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -self.total_height:
            self.finished = True

    def draw(self, screen):
        y_offset = self.y
        for surf in self.rendered:
            x = (self.width - surf.get_width()) // 2
            screen.blit(surf, (x, y_offset))
            y_offset += surf.get_height() + 10

    def is_finished(self):
        last_line_bottom = self.y + len(self.rendered) * (self.font.get_height() + 10)
        return last_line_bottom < 0

class LevelManager:
    def __init__(self, x, y, level=1, font_size=32, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.level = level
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.seed=None

    def next_level(self):
        """Advance to the next level and generate a new seed."""
        self.level = min(self.level + 1, End_level)
        self.seed = random.randint(0, 999999)
        return self.seed

    def get_seed(self):
        """Return the current seed (generate one if missing)."""
        if self.seed is None:
            self.seed = random.randint(0, 999999)
        return self.seed

    def reset(self):
        """Reset to level 1 with a new seed."""
        self.level = 1
        self.seed = random.randint(0, 999999)

    def add(self,increment):
        self.level += 1

    def draw(self, surface):
        display_level = min(self.level, End_level)
        text = self.font.render(f"Level: {display_level}", True, self.color)
        surface.blit(text, (self.x, self.y))

class Score:
    def __init__(self, x, y, font_size=32, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.score = 0
        self.color = color

        # Create a font object
        self.font = pygame.font.Font(None, font_size)

    def add(self, amount):
        self.score += amount

    def draw(self, surface):
        text = self.font.render(f"Score: {self.score}", True, self.color)
        surface.blit(text, (self.x, self.y))

class Lives:
    def __init__(self, x,y,lives=3, font_size=32, color=(255, 0, 255)):
        self.x=x
        self.y=y
        self.lives=lives
        self.start_lives = lives
        self.color = color
        self.font = pygame.font.Font(None, font_size)

    def reset(self):
        self.lives = self.start_lives

    def add(self, amount): #lives can nver exceed 5
        if self.lives<5:
            self.lives += 1

    def dec(self):
        self.lives -= 1

    def draw(self, surface):
        text = self.font.render(f"Lives: {self.lives}", True, self.color)
        surface.blit(text, (self.x, self.y))

class ScrollingStars:
    def __init__(self, width, height, star_count=80):
        self.width = width
        self.height = height
        self.star_count = star_count
        self.stars = []
        self._create_stars()

    def _create_stars(self):
        spacing = self.height / self.star_count

        for i in range(self.star_count):
            y = i * spacing + random.uniform(-spacing / 2, spacing / 2)
            x = random.randint(0, self.width)
            speed = random.uniform(40, 140)

            # Random colour per star (but fixed)
            r = random.randint(100, 255)
            g = random.randint(100, 255)
            b = random.randint(100, 255)

            # star = [x, y, speed, color]
            self.stars.append([x, y, speed, (r, g, b)])

    def update(self, dt):
        for star in self.stars:
            # Move downward
            star[1] += star[2] * dt

            # Wrap to top
            if star[1] > self.height:
                star[1] -= self.height

    def draw(self, surface):
        for x, y, speed, color in self.stars:
            pygame.draw.circle(surface, color, (int(x), int(y)), 2)


class Paddle:
    def __init__(self, x, y, width=120, height=20, speed=7):
        self.color = (255, 255, 0)

        self.powerup_active = False
        self.powerup_start = 0
        self.powerup_duration = 0
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(x, y, width, height)
        self.laser_enabled = False
        self.flash_timer = 0

        self.start_x = x
        self.start_y = y
        self.start_width = width
        self.start_height = height
        self.start_speed = speed

    def reset(self):
        # Reset position
        self.rect.x = self.start_x
        self.rect.y = self.start_y

        # Reset size
        self.width = self.start_width
        self.height = self.start_height
        self.rect.width = self.start_width
        self.rect.height = self.start_height

        # Reset speed
        self.speed = self.start_speed

        # Reset power-up state
        self.powerup_active = False
        self.powerup_start = 0
        self.powerup_duration = 0
        self.laser_enabled = False

    def update_keyboard(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        self.rect.x = max(0, min(WIDTH - self.width, self.rect.x))

    def update_mouse(self):
        mouse_x, _ = pygame.mouse.get_pos()
        self.rect.centerx = mouse_x

        self.rect.x = max(0, min(WIDTH - self.width, self.rect.x))

    def update_joypad(self, joystick):


        if joystick is None:
            return

        hat_x, hat_y = joystick.get_hat(0)

        # Move left
        if hat_x == -1:
            self.rect.x -= 12

        # Move right
        elif hat_x == 1:
            self.rect.x += 12

    def p_update(self, control_mode, joystick=None):
        if control_mode == "Keyboard":
            self.update_keyboard()

        elif control_mode == "mouse":
            self.update_mouse()

        elif control_mode == "Joypad":
            self.update_joypad(joystick)

        # Clamp to screen for ALL control modes
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))


    def draw(self, surface):
        # Draw the paddle itself
        pygame.draw.rect(surface, self.color, self.rect)

        # Draw missile ports if laser is active
        if self.laser_enabled:
            port_width = 6
            port_height = 10
            offset = 8  # distance from paddle edge

            # Left port
            left_port = pygame.Rect(
                self.rect.left + offset,
                self.rect.top - port_height,
                port_width,
                port_height
            )
            # Right port
            right_port = pygame.Rect(
                self.rect.right - offset - port_width,
                self.rect.top - port_height,
                port_width,
                port_height
            )

            if self.flash_timer > 0:
                color = (255, 255, 255)
            else:
                color = (0, 200, 255)  # your normal paddle color

            pygame.draw.rect(surface, (255, 0, 0), left_port)
            pygame.draw.rect(surface, (255, 0, 0), right_port)

class Ball: #Speed of ball can increase at each level
    def __init__(self, x, y, score, difficulty="Normal",radius=10):

        self.x = x
        self.y = y

        self.start_x = x
        self.start_y = y

        self.prev_x = x
        self.prev_y = y

        self.radius = radius
        self.score = score
        # Difficulty multipliers
        difficulty_factor = {
            "Easy": 0.7,
            "Normal": 1.0,
            "Hard": 1.4,
            "Insane": 1.7
        }.get(difficulty, 1.0)

        # Base speed
        base_speed = 6
        speed = base_speed * difficulty_factor

        self.speed_x = speed
        self.speed_y = -speed

        self.base_speed_x = self.speed_x
        self.base_speed_y = self.speed_y


        self.attached = True
        self.paddlehit = False
        self.sidehit = False
        self.tophit = False
        self.speed_multiplier =1.0

        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        self.last_dir_x = 1 if self.speed_x > 0 else -1
        self.last_dir_y = 1 if self.speed_y > 0 else -1

    def check_collision_only(self, paddle_rect):
        if self.rect.colliderect(paddle_rect):
            self.speed_y *= -1
            self.paddlehit = True

    def check_paddle_collision(self, paddle_rect):

        if self.rect.colliderect(paddle_rect) and self.speed_y > 0:
            self.speed_y *= -1
            self.score.add(10)
            sound_paddle = pygame.mixer.Sound(resource_path("sounds/PaddleBounce.wav"))
            sound_paddle.play()
            self.paddlehit = True

    def b_update(self, paddle_rect):

        # ---------------------------------------------------------
        # 1. ATTACHED TO PADDLE
        # ---------------------------------------------------------
        if self.attached:
            self.x = paddle_rect.centerx
            self.y = paddle_rect.top - self.radius
            self.rect.x = self.x - self.radius
            self.rect.y = self.y - self.radius
            return False

        # ---------------------------------------------------------
        # 2. STORE PREVIOUS POSITION
        # ---------------------------------------------------------
        self.prev_x = self.x
        self.prev_y = self.y

        # ---------------------------------------------------------
        # 3. MICRO-STEP SETUP
        # ---------------------------------------------------------
        steps = int(max(abs(self.speed_x), abs(self.speed_y)))
        if steps < 1:
            steps = 1

        dx = (self.speed_x * self.speed_multiplier) / steps
        dy = (self.speed_y * self.speed_multiplier) / steps

        # ---------------------------------------------------------
        # 4. MICRO-STEP LOOP
        # ---------------------------------------------------------
        for _ in range(steps):

            # Move
            self.x += dx
            self.y += dy

            # Sync rect
            self.rect.x = self.x - self.radius
            self.rect.y = self.y - self.radius

            # -----------------------------------------------------
            # LEFT / RIGHT WALL COLLISION
            # -----------------------------------------------------
            if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
                self.speed_x *= -1

                #  clamp vertical speed
                if abs(self.speed_y) < 1.5:
                    self.speed_y = 1.5 if self.speed_y > 0 else -1.5

                # recalc dx for remaining micro-steps
                dx = (self.speed_x * self.speed_multiplier) / steps
                continue

            # -----------------------------------------------------
            # TOP WALL COLLISION
            # -----------------------------------------------------
            if self.y - self.radius <= 0:
                self.speed_y *= -1

                #  clamp vertical speed
                min_v = 1.5 / self.speed_multiplier
                if abs(self.speed_y) < min_v:
                    self.speed_y = min_v if self.speed_y > 0 else -min_v

                # recalc dy for remaining micro-steps
                dy = (self.speed_y * self.speed_multiplier) / steps
                continue

            # -----------------------------------------------------
            # PADDLE COLLISION
            # -----------------------------------------------------
            if self.rect.colliderect(paddle_rect) and self.speed_y > 0:
                self.speed_y *= -1

                #  clamp vertical speed
                if abs(self.speed_y) < 1.5:
                    self.speed_y = 1.5

                # recalc dy
                dy = (self.speed_y * self.speed_multiplier) / steps

                self.score.add(10)
                pygame.mixer.Sound(resource_path("sounds/PaddleBounce.wav")).play()
                continue

            # -----------------------------------------------------
            # BALL FELL OFF SCREEN
            # -----------------------------------------------------
            if self.y > HEIGHT:
                self.attached = True
                return True

        # ---------------------------------------------------------
        # 5. END OF UPDATE — NO EXTRA CLAMP NEEDED
        # ---------------------------------------------------------
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, (0, 200, 255), (self.x, self.y), self.radius)

    def reset(self):
        # Reset position
        self.x = self.prev_x = self.start_x
        self.y = self.prev_y = self.start_y

        # Reset speed
        self.speed_x = self.base_speed_x
        self.speed_y = self.base_speed_y

        # Reset state flags
        self.attached = True
        self.paddlehit = False
        self.sidehit = False
        self.tophit = False

        # Reset rect
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

        # Reset last direction
        self.last_dir_x = 1 if self.speed_x > 0 else -1
        self.last_dir_y = 1 if self.speed_y > 0 else -1


class BrickField:
    def __init__(self, width, height, level, rows=5, cols=10, seed=None, y_offset=0, max_reslience=2):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.seed = seed
        self.y_offset = y_offset
        self.level = level

        self.bricks = []
        self._generate()

    def _generate(self):
        random.seed(self.seed)   # ← deterministic generation

        self.bricks.clear()
        for row in range(self.rows):
            for col in range(self.cols):

                # 20% chance to skip a brick
                if random.random() < 0.2:
                    continue

                x = col * 70
                y = row * 25 +self.y_offset
                rect = pygame.Rect(x, y, 70, 25)

                color = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
                low = min(self.level.level, Max_BRICK_RESILIENCE)
                health = random.randint(low, Max_BRICK_RESILIENCE)

                self.bricks.append(Brick(rect, color, health))

    def draw(self, surface):
        for brick in self.bricks:
            pygame.draw.rect(surface, brick.color, brick.rect)

class Brick:
    def __init__(self, rect, color, health):
        self.rect = rect
        self.color = color
        self.health = health
        self.max_health = health #Store original health of brick

    def hit(self):
        self.health -= 1
        return self.health <= 0  # True if brick should be destroyed

    def update_color(self):
        # Optional: change colour based on remaining health
        if self.health == 3:
            self.color = (255, 0, 0)      # red
        elif self.health == 2:
            self.color = (255, 165, 0)    # orange
        elif self.health == 1:
            self.color = (255, 255, 0)    # yellow

class GameOverScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bg = pygame.image.load(resource_path("gameover_bg.jpg")).convert()

        self.bg = pygame.transform.scale(self.bg, (width, height))

        self.font_big = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 60)

    def draw(self, surface, score):
        surface.blit(self.bg, (0, 0))

        text1 = self.font_big.render("GAME OVER", True, (255, 0, 0))
        text2 = self.font_small.render(f"Final Score: {score}", True, (255, 165, 0))
        text3 = self.font_small.render("Click to continue", True, (255, 255, 0))

        surface.blit(text1, (self.width//2 - text1.get_width()//2, 200))
        surface.blit(text2, (self.width//2 - text2.get_width()//2, 300))
        surface.blit(text3, (self.width//2 - text3.get_width()//2, 400))

class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.speed = 3
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0), self.rect)  # placeholder colour

class PowerUpManager:  # Keep track of all power ups
    def __init__(self):
        self.powerups = []

        # Base weights stored once
        self.base_weights = {
            "life": 0.75,
            "big_paddle": 3,
            "slow_ball": 3,
            "laser": 1,
            "second_bat": 2,
            "multiball": 3,
            "super_multiball": 1.5,
            "nuke": 0.75
        }

        # This will be filled each spawn
        self.weights = self.base_weights.copy()

    def update(self, dt):
        for p in self.powerups:
            p.update()  # PowerUp.update() takes no dt

        # Remove powerups that fall off screen
        self.powerups = [p for p in self.powerups if p.y < HEIGHT]

    def draw(self, screen):
        for p in self.powerups:
            p.draw(screen)

    def spawn(self, x, y, level, difficulty):
        # 20% chance to drop a power-up
        if random.random() < 0.2:

            # 1. Start with base weights
            weights = self.base_weights.copy()

            # 2. Level scaling
            weights["laser"] += level

            # 3. Difficulty scaling
            weights = self.scale_powerup_weights(weights, difficulty)

            # 4. Store final weights
            self.weights = weights

            # 5. Choose powerup
            kinds = list(self.weights.keys())
            values = list(self.weights.values())

            kind = random.choices(kinds, values)[0]

            self.powerups.append(PowerUp(x, y, kind))

    def reset(self):
        self.powerups.clear()

    def scale_powerup_weights(self, weights, difficulty):
        multipliers = {
            "Easy": 1.40,
            "Normal": 1.00,
            "Hard": 0.70,
            "Insane": 0.45
        }

        m = multipliers[difficulty]

        # Scale the provided weights dict
        return {k: v * m for k, v in weights.items()}

class ProjectileManager:
    def __init__(self):
        self.projectiles = []   # list of active Projectile objects

    def fire(self, paddle_rect):
        # Fire two lasers from the paddle edges
        left_x = paddle_rect.left + 10
        right_x = paddle_rect.right - 14
        y = paddle_rect.top - 10

        self.projectiles.append(Projectile(left_x, y))
        self.projectiles.append(Projectile(right_x, y))

    def update(self):
        for p in self.projectiles[:]:
            p.update()
            if p.y < 0:
                self.projectiles.remove(p)

    def draw(self, surface):
        for p in self.projectiles:
            p.draw(surface)

class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = -8
        self.rect = pygame.Rect(self.x, self.y, 4, 12)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)

class ExplosionManager:
    def __init__(self):
        self.explosions = []

    def spawn(self, position, color):
        self.explosions.append(Explosion(position, color))

    def update(self, dt):
        for explosion in self.explosions:
            explosion.update(dt)
            if explosion.finished:
                self.explosions.remove(explosion)

    def draw(self, screen):
        for explosion in self.explosions:
            explosion.draw(screen)

class Explosion:
    def __init__(self, position, color):
        self.particles = create_particles(position, color)
        self.timer = 0
        self.duration = 0.3  # seconds
        self.finished = False

    def update(self, dt):
        self.timer += dt

        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

        if self.timer >= self.duration or len(self.particles) == 0:
            self.finished = True

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class Particle:
    def __init__(self, position, color):
        self.x, self.y = position
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-200, 0)
        self.radius = random.randint(2, 5)
        self.color = color
        self.life = 0.5  # seconds

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Stats: #this is the summary screen datat structure
    def __init__(self):
        self.levels_completed = 0
        self.bricks_destroyed = 0
        self.powerups_collected = 0
        self.balls_lost = 0

class HighScoreTable:
    def __init__(self, filename="highscores.json", max_scores=10):
        self.filename = filename
        self.max_scores = max_scores
        self.data = self.load()

    # ---------------------------------------------------------
    # Load JSON file or create default structure
    # ---------------------------------------------------------
    def load(self):
        if not os.path.exists(self.filename):
            # Create empty structure for all difficulties
            data = {
                "Easy": [],
                "Normal": [],
                "Hard": [],
                "Insane": []
            }
            self.save_data(data)
            return data

        with open(self.filename, "r") as f:
            return json.load(f)

    # ---------------------------------------------------------
    # Save entire JSON structure back to file
    # ---------------------------------------------------------
    def save_data(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------
    # Get the score list for a specific difficulty
    # ---------------------------------------------------------
    def get_scores(self, difficulty):
        if difficulty not in self.data:
            self.data[difficulty] = []
        return self.data[difficulty]

    # ---------------------------------------------------------
    # Check if a score qualifies for the leaderboard
    # ---------------------------------------------------------
    def qualifies(self, score, difficulty):
        scores = self.get_scores(difficulty)

        if len(scores) < self.max_scores:
            return True

        return score > scores[-1]["score"]

    # ---------------------------------------------------------
    # Add a new score and save the updated table
    # ---------------------------------------------------------
    def add_score(self, name, score, difficulty):
        scores = self.get_scores(difficulty)

        scores.append({"name": name, "score": score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        self.data[difficulty] = scores[:self.max_scores]

        self.save_data(self.data)

    # ---------------------------------------------------------
    # Return a formatted list for display
    # ---------------------------------------------------------
    def formatted(self, difficulty):
        scores = self.get_scores(difficulty)
        return [f"{entry['name']}  —  {entry['score']}" for entry in scores]

class NameEntryScreen:
    def __init__(self, font=None, max_length=10):
        self.font = font or pygame.font.Font(None, 48)
        self.max_length = max_length

        # ⭐ Cursor blink state
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 0.5  # seconds

    def run(self, screen, clock, final_score):
        name = ""

        while True:
            dt = clock.tick(60) / 1000.0

            # ⭐ Update cursor blink
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_blink_speed:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(name) > 0:
                        return name.upper()

                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]

                    elif len(name) < self.max_length:
                        if event.unicode.isalpha():
                            name += event.unicode

            # Draw UI
            screen.fill((0, 0, 0))

            title = self.font.render("NEW HIGH SCORE!", True, (255, 255, 0))
            screen.blit(title, (100, 100))

            score_text = self.font.render(f"Score: {final_score}", True, (255, 255, 255))
            screen.blit(score_text, (100, 160))

            # ⭐ Add blinking cursor
            display_name = name + ("|" if self.cursor_visible else "")

            name_text = self.font.render(f"Name: {display_name}", True, (0, 255, 0))
            screen.blit(name_text, (100, 240))

            pygame.display.flip()


class HighScoreScreen:
    def __init__(self, highscores, font):
        self.highscores = highscores
        self.font = font

    def run(self, screen, clock, difficulty):
        bg_image2 = pygame.image.load(resource_path("highscore_background.png")).convert()
        bg_image2 = pygame.transform.scale(bg_image2, (WIDTH, HEIGHT))
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    running = False

            screen.blit(bg_image2, (0, 0))
            title = self.font.render(f"****{difficulty.upper()} Level HIGH SCORES****", True, (0, 255, 0))
            # Title
            x = (screen.get_width() - title.get_width()) // 2
            y = 50

            screen.blit(title, (x, y))

            # Draw entries
            y = 150
            for entry in self.highscores.get_scores(difficulty):
                line = self.font.render(f"{entry['name']}   {entry['score']}", True, (0, 255, 255))
                screen.blit(line, (100, y))
                y += 40
            self.font.set_italic(True)
            backtext = self.font.render(f"Press any key to return to main menu.", True, (255, 255, 255))
            self.font.set_italic(False)

            x= (screen.get_width() - backtext.get_width()) // 2
            y=HEIGHT - 40
            screen.blit(backtext, (x, y))

            pygame.display.flip()
            clock.tick(60)

class SummaryScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bg = pygame.image.load(resource_path("SummaryPageImage_bg.jpg")).convert()
        self.bg = pygame.transform.scale(self.bg, (width, height))
        self.flash_timer = 0
        self.show_prompt = True

        self.font_big = pygame.font.Font(None, 80)
        self.font_small = pygame.font.Font(None, 60)

    def update(self, dt):
        self.flash_timer += dt
        if self.flash_timer >= 0.5:
            self.show_prompt = not self.show_prompt
            self.flash_timer = 0


    def draw(self, surface, stats):
        surface.blit(self.bg, (0, 0))

        title = self.font_big.render("LEVEL SUMMARY", True, (255, 255, 0))
        surface.blit(title, (self.width//2 - title.get_width()//2, 120))

        line1 = self.font_small.render(f"Levels Completed: {stats.levels_completed}", True, (210, 105, 30))
        line2 = self.font_small.render(f"Bricks Destroyed: {stats.bricks_destroyed}", True, (210, 105, 30))
        line3 = self.font_small.render(f"Powerups Collected: {stats.powerups_collected}", True, (210, 105, 30))
        line4 = self.font_small.render(f"Balls Lost: {stats.balls_lost}", True, (210, 105, 30))

        surface.blit(line1, (self.width//2 - line1.get_width()//2, 240))
        surface.blit(line2, (self.width//2 - line2.get_width()//2, 300))
        surface.blit(line3, (self.width//2 - line3.get_width()//2, 360))
        surface.blit(line4, (self.width//2 - line4.get_width()//2, 420))

        if self.show_prompt:
            prompt = self.font_small.render("Press SPACE to continue", True, (255, 200, 0))
            surface.blit(prompt, (self.width // 2 - prompt.get_width() // 2, 520))

# -----------------------------------------
# Screen shake variables
# -----------------------------------------
shake_timer = 5
shake_intensity = 20000

def start_screen_shake(duration=0.5, intensity=15):
    """Begin a screen shake effect."""
    global shake_timer, shake_intensity
    shake_timer = duration
    shake_intensity = intensity

def get_shake_offset(dt):
    """Return the current shake offset (x, y)."""
    global shake_timer, shake_intensity

    if shake_timer > 0:
        shake_timer -= dt

        # Convert intensity to int to avoid randrange errors
        i = int(shake_intensity)

        if i < 1:
            return 0, 0

        ox = random.randint(-i, i)
        oy = random.randint(-i, i)

        # Ease out
        shake_intensity *= 0.9

        return ox, oy

    return 0, 0


# -----------------------------------------
# Nuke Debris Part Class
# -----------------------------------------
class DebrisPart:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # Explosion burst velocity
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(200, 600)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed * -1

        # Chaos wobble
        self.phase_x = random.random() * math.pi * 2
        self.phase_y = random.random() * math.pi * 2
        self.amp_x = random.uniform(20, 60)
        self.amp_y = random.uniform(10, 30)

        # Multi‑coloured debris
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

        self.size = 15
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

        # Bounce physics
        self.bounce_energy = .5
        self.min_bounce_speed = 80
        self.dead = False

    def update(self, dt, t):
        if self.dead:
            return

        # Chaotic wobble for first 2 seconds
        if t < 2.0:
            wobble_x = math.sin(t * 10 + self.phase_x) * self.amp_x
            wobble_y = math.cos(t * 12 + self.phase_y) * self.amp_y
            self.vx += wobble_x * dt
            self.vy += wobble_y * dt

        # Gravity
        self.vy += GRAVITY * dt

        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Rotation
        self.rotation += self.rot_speed * dt

        # Ground collision + bounce
        if self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size

            # Bounce upward with reduced energy
            self.vy = -abs(self.vy) * self.bounce_energy
            self.vx *= 0.7
            self.rot_speed *= 0.5

            # Remove if bounce too weak
            if abs(self.vy) < self.min_bounce_speed:
                self.dead = True

    def draw(self, surface, ox, oy):
        """Draw debris with screen shake offset."""
        if not self.dead:
            pygame.draw.rect(surface, self.color,
                             (self.x + ox, self.y + oy, self.size, self.size))

#Helper functions
#Level 10 Boss xplosion
def explode_boss(boss, debris_list):
    for row_idx, row in enumerate(INVADER_PATTERN):
        for col_idx, pixel in enumerate(row):
            if pixel == "1":
                # Spawn debris at each pixel block
                x = boss.x + col_idx * boss.scale
                y = boss.y + row_idx * boss.scale
                for _ in range(3):  # debris per pixel
                    debris_list.append(DebrisPart(x, y))

#Responsible for limiting ball angle to prevent vertical and horiztal lock
def clamp_ball_angle(ball):
    speed = math.hypot(ball.x, ball.y)

    # Minimum component is 25% of speed
    min_component = 0.25 * speed

    # Prevent vertical lock
    if abs(ball.x) < min_component:
        ball.dx = min_component * (1 if ball.x >= 0 else -1)

    # Prevent horizontal lock
    if abs(ball.y) < min_component:
        ball.dy = min_component * (1 if ball.y >= 0 else -1)

    # Renormalize to original speed
    length = math.hypot(ball.x, ball.y)
    ball.dx = ball.x / length * speed
    ball.dy = ball.y / length * speed

def draw_text(surface, text, size, x, y, color=(255, 255, 255), highlight=False):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if highlight:
        pygame.draw.rect(
            surface,
            (80, 80, 80),
            text_rect.inflate(20, 10),
            border_radius=8
        )

    surface.blit(text_surface, text_rect)
    #Options menu
def options_menu(screen, clock, control_mode, difficulty):

    selected = 0
    options = ["Control Method", "Difficulty", "Back"]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return control_mode, difficulty, False  # quit entire game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav")).play()

                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav")).play()

                elif event.key == pygame.K_RETURN:
                    pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav")).play()
                    choice = options[selected]
                    if choice == "Control Method":
                       index = CONTROL_MODE_VALUES.index(control_mode)
                       index = (index + 1) % len(CONTROL_MODE_VALUES)
                       control_mode = CONTROL_MODE_VALUES[index]
                       pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav")).play()

                    elif choice == "Difficulty":
                        DIFFICULTIES = ["Easy", "Normal", "Hard", "Insane"]
                        index = DIFFICULTIES.index(difficulty)
                        difficulty = DIFFICULTIES[(index + 1) % len(DIFFICULTIES)]
                        pygame.mixer.Sound(resource_path("sounds/Gunrechamber.wav")).play()
                    elif choice == "Back":
                        return control_mode, difficulty, True
        # DRAWING
        screen.fill((0, 0, 0))
        #These next functions are calls to drawing text to the screen
        draw_text(screen,
            "OPTIONS", 60,
            WIDTH // 2,
            80
        )

        draw_text(
            screen,
            "Use up/down arrow keys to toggle and Enter to select. "
            ,40, (WIDTH // 2),400
            ,color=(0,255,0)
        )

        index = CONTROL_MODE_VALUES.index(control_mode)
        display_text = CONTROL_MODE_DISPLAY[index]
        draw_text(
            screen,
            f"Control Method: {display_text}",
            40,
            WIDTH // 2,
            200,
            highlight=(selected == 0),
        )

        draw_text(
            screen,
            f"Difficulty: {difficulty}",
            40,
            WIDTH // 2,
            260,
            highlight=(selected == 1),
        )

        draw_text(
            screen,
            "Back",
            40,
            WIDTH // 2,
            320,
            highlight=(selected == 2),
        )

        draw_text(
            screen,
            "Esc key to abort mission.",
            40,(WIDTH // 2),500,
            color=(255,40,40), highlight=False
        )


        pygame.display.flip()
        clock.tick(60)

def explode_remaining_bricks(brick_field, debris_list):

    for brick in brick_field.bricks:
        bx = brick.rect.x
        by = brick.rect.y

        for _ in range(6):  # debris per brick
            debris_list.append(DebrisPart(bx, by))

    # Clear the actual brick list
    brick_field.bricks.clear()

#Add power-ups
def apply_powerup(kind, paddle, paddle2, balls, lives, active_powerups, score, bricks, debris_list, explosion_timer,difficulty):
    now = pygame.time.get_ticks()

    if kind == "life":
        lives.add(1)

    elif kind == "big_paddle":
        paddle.rect.width = min(paddle.rect.width + 40, 120)
        active_powerups["big_paddle"] = now + 5000

    elif kind == "slow_ball":
        for b in balls:
            b.speed_multiplier = 0.5
        active_powerups["slow_ball"] = now + 5000


    elif kind == "laser":
        paddle.laser_enabled = True
        active_powerups["laser"] = now + 10000

    elif kind == "second_bat":
        paddle2.active=True
        active_powerups["second_bat"] = now + 10000

    elif kind == "multiball":
        main_ball = balls[0]

        if len(balls) < 5:  # Only create extra balls if there are less than 5 balls on screen

            new_ball = Ball(main_ball.x, main_ball.y, score,difficulty)

            # Give it a different direction
            new_ball.speed_x = -main_ball.speed_x
            new_ball.speed_y = main_ball.speed_y

            new_ball.attached = False

            balls.append(new_ball)

    elif kind.lower() == "super_multiball":
        global flash_timer
        flash_timer = FLASH_DURATION

        max_balls = 10
        current = len(balls)
        to_spawn = max_balls - current

        if to_spawn <= 0:
            return

        main = balls[0]

        min_angle = 40
        max_angle = 140

        # Generate evenly spaced angles
        if to_spawn == 1:
            angles = [(min_angle + max_angle) / 2]
        else:
            angles = [
                min_angle + (i / (to_spawn - 1)) * (max_angle - min_angle)
                for i in range(to_spawn)
            ]

        speed = math.hypot(main.speed_x, main.speed_y)

        for angle in angles:
            angle = safe_angle(angle)  #  clamp BEFORE radians
            rad = math.radians(angle)  #  radians AFTER clamp

            new_ball = Ball(main.x, main.y, score, difficulty)
            new_ball.attached = False

            new_ball.speed_x = speed * math.cos(rad)
            new_ball.speed_y = -abs(speed * math.sin(rad))

            balls.append(new_ball)


    elif kind == "nuke":
        global exploding
        sound_nuke = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))
        sound_nuke.play()

        exploding[0] = True
        explosion_timer[0] = 4
        score.add(500)
        explode_remaining_bricks(bricks, debris_list)
        start_screen_shake(duration=0.6, intensity=20)
#Remove powerups
def remove_powerup(kind, paddle, paddle2, balls):

    if kind == "big_paddle":
        paddle.rect.width=120

    elif kind == "slow_ball":
        for b in balls:
            b.speed_multiplier = 1.0

    elif kind == "laser":
        paddle.laser_enabled = False

    elif kind == "second_bat":
        paddle2.active=False

#Helper methods
def reset_game_state(score, ball, paddle, powerup_manager, lives,difficulty):
    score.score = 0
    ball.reset()
    paddle.reset()
    powerup_manager.reset()
    lives.reset()
    game_over = False
    return game_over

#Mission briefing text
def show_mission_briefing(screen):
    big_font = pygame.font.Font(None, 48)
    bg_image = pygame.image.load(resource_path("briefing_background.png")).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    sound_RedAlert = pygame.mixer.Sound(resource_path("sounds/RedAlert.wav"))
    sound_RedAlert.play()

    clock = pygame.time.Clock()

    briefing_text = [
        "*****RED ALERT*****",
        "",
        "",
        "Your mission: break everything. Simple.",
        "",
        "The luna arena orbiting earth is filling up with",""
        " strange carbon anomalies, shaped like bricks.",
        "Your mission? Smash the lot of them.",
        "",
        "Objective:",
        "- Clear every brick.",
        "- Keep the ball alive.",
        "- Grab powerups.",
        "- NUKE powerups, destroys entire levels. ",
        "- Make it to level 15 and kill Big Boss.",
        "",
        "",
        "Good luck, recruit!",
        "",
        "",
        "Press space bar to return to main menu."
    ]

    briefing = ScrollingBriefing(briefing_text, big_font, WIDTH, HEIGHT)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
                #Draw background

        screen.blit(bg_image, (0, 0))

        briefing.update(dt)
        briefing.draw(screen)

        if briefing.is_finished():
            running = False

        pygame.display.flip()


#Waits for user to press space on the summary page
def show_summary_screen(summary_screen, stats, screen,level_manager):
    clock = pygame.time.Clock()
    level_manager.add(1)
    waiting = True

    while waiting:
        dt = clock.tick(60) / 1000.0  # convert ms → seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

        summary_screen.update(dt)
        summary_screen.draw(screen, stats)
        pygame.display.flip()

#music loop
def play_next_track():
    global current_track

    current_track = (current_track + 1) % len(playlist)

    pygame.mixer.music.load(playlist[current_track])
    pygame.mixer.music.play()


def init_music():
    global playlist, current_track

    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)

    playlist = [
        resource_path("sounds/BackgroundMusic01.ogg"),
        resource_path("sounds/GermanTechnoLoop.wav"),
        resource_path("sounds/ingamemusic3.wav")
    ]

    current_track = 0
    pygame.mixer.music.load(playlist[current_track])

    return MUSIC_END


#Particle system for explosion
def create_particles(position, color):
    particles = []
    for i in range(20):
        particles.append(Particle(position, color))
    return particles

#corrects ball angle during super_multi ball powwerup
def safe_angle(angle, dead_zone=15):
    mid = 90
    if mid - dead_zone <= angle <= mid + dead_zone:
        return mid - dead_zone if angle < mid else mid + dead_zone
    return angle

# --- Game Loop ---
#Difficuty variable is passed in from option menu
#This then is transfered to the Max_BRICK_RESILIENCE variable
#This will dictate resilience of bricks according to difficulty level.
def run_game_loop(screen, clock, control_mode, difficulty, stars, joystick):
    print(difficulty)
    # --- GAMEPLAY STATE ---
    # --- difficulty-based boss firing intervals ---
    difficulty_intervals = {
        "Easy": (2.0, 3.5),
        "Normal": (1.0, 2.5),
        "Hard": (0.6, 1.4),
        "Insane": (0.3, 0.8)
    }

    max_resilience_by_difficulty = {
        "Easy": 1,
        "Normal": 2,
        "Hard": 3,
        "Insane": 4
    }

    pygame.mouse.set_visible(False)
    global flash_timer

    running = True
    show_ready = True
    ready_phase = "drop"
    ready_y = -100
    ready_x = WIDTH // 2
    ready_pause_start = pygame.time.get_ticks()


    # --- CREATE GAME OBJECTS ---
    paddle = Paddle((WIDTH - 120) // 2, HEIGHT - 50)
    paddle2 = Paddle((WIDTH - 120) // 2, HEIGHT - 150)
    paddle2.active = False
    score = Score(10, 10)
    level = LevelManager(650, 10, 1)
    lives = Lives(330, 10, 3)

    seed = level.get_seed()
    max_brick_resilience = max_resilience_by_difficulty.get(difficulty, 2)
    bricks = BrickField(WIDTH, HEIGHT, level, rows=6, cols=12, seed=seed, y_offset=100,max_reslience=max_brick_resilience)


    balls = [Ball(WIDTH // 2, HEIGHT // 2, score,difficulty)]
    balls[0].attached = True

    missiles = pygame.sprite.Group()

    powerups = PowerUpManager()
    projectiles = ProjectileManager()
    explosions = ExplosionManager()
    stats = Stats()
    active_powerups = {}

    # --- LOAD SOUNDS ---

    sound_brick = pygame.mixer.Sound(resource_path("sounds/finalBallSmash.wav"))
    sound_laser = pygame.mixer.Sound(resource_path("sounds/laser.wav"))
    sound_ball_side = pygame.mixer.Sound(resource_path("sounds/sideSound.wav"))
    sound_ball_top = pygame.mixer.Sound(resource_path("sounds/TopHit.wav"))
    sound_powerup = pygame.mixer.Sound(resource_path("sounds/powerup.wav"))
    sound_whoosh = pygame.mixer.Sound(resource_path("sounds/whoosh.wav"))
    sound_explosion = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))
    lost_ball = pygame.mixer.Sound(resource_path("sounds/LostBall.wav"))
    sound_RedAlert = pygame.mixer.Sound(resource_path("sounds/RedAlert.wav"))
    boss_hit = pygame.mixer.Sound(resource_path("sounds/bossHit.wav"))
    missile_explosion = pygame.mixer.Sound(resource_path("sounds/MissileExplosion.wav"))
    boss_fire = pygame.mixer.Sound(resource_path("sounds/bossMissile.wav"))
    boss_fire.set_volume(0.2)
    intruder_alert = pygame.mixer.Sound(resource_path("sounds/IntruderAlert.wav"))
    warp_drive = pygame.mixer.Sound(resource_path("sounds/WarpDrive.wav"))

    game_over_screen = GameOverScreen(WIDTH, HEIGHT)
    font = pygame.font.Font(None, 36)
    font_big = pygame.font.Font(None, 48)

    highscores = HighScoreTable() #Instantiate high score table
    name_entry_screen = NameEntryScreen()
    highscore_screen = HighScoreScreen(highscores, font)
    clock = pygame.time.Clock() #This maintains fram rates for Nameentry screen
    warp = WarpTunnel(WIDTH, HEIGHT)
    end_message = EndMessage(WIDTH, HEIGHT, duration=8.0)
    credits = CreditsScreen(WIDTH, HEIGHT)

    #Reset game variables for new game
    score.score = 0
    lives.reset()
    game_over = False
    paddle.reset()
    powerups.reset()
    starfield_3d = None
    game_time = 0
    debris_list=[]
    explosion_timer=[0]
    level.level=1
    sound_RedAlert.play()
    ready_has_run = False
    boss = None
    boss_missiles = pygame.sprite.Group()
    boss_intro_timer[0] = 300
    game_state = "GAMEPLAY"

    level10_sound_timer = [7.0]
    hit_pause_timer = [0.0]
    pygame.mixer.music.stop()
    if level.level != End_level:
        MUSIC_END = init_music()
        current_track = 0

        # ⭐ Clear stale events BEFORE starting music
        pygame.event.clear(MUSIC_END)

        # ⭐ Start track 0 cleanly
        pygame.mixer.music.play()
    else:
        MUSIC_END = None
    # --- MAIN LOOP ---
    while running:
        dt = clock.tick(60) / 1000.0
        game_time += dt  # <-- UPDATE IT EVERY FRAME

        # --- MISSILE HIT PAUSE ---
        if hit_pause_timer[0] > 0:
            hit_pause_timer[0] -= dt
            if hit_pause_timer[0] <= 0:
                pygame.mixer.music.unpause()
                show_ready = True
            return

        if show_ready:
            stars.scroll_speed=107
        else:
            stars.scroll_speed=100

        stars.update(dt)

        debris_list = [d for d in debris_list if not d.dead]
        # -------------------------
        #        GAME OVER
        # -------------------------
        if game_over:

            # Create starfield ONCE
            if starfield_3d is None:
                starfield_3d = Starfield3D(WIDTH, HEIGHT, num_stars=400)
                pygame.mixer.music.fadeout(5000)
                pygame.mouse.set_visible(True)

            # Draw the game over screen
            screen.fill((0, 0, 0))
            starfield_3d.update(dt)
            starfield_3d.draw(screen)
            game_over_screen.draw(screen, score.score)
            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return  # exit game loop completely

                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Player qualifies for high score
                    if highscores.qualifies(score.score, difficulty):
                        name = name_entry_screen.run(screen, clock, score.score)
                        highscores.add_score(name, score.score, difficulty)
                        highscore_screen.run(screen, clock, difficulty)

                    # ALWAYS reset game state before leaving
                    pygame.mixer.music.load(resource_path("sounds/splashscreenmusic.wav"))
                    pygame.mixer.music.play(-1)

                    # Reset the game_over flag BEFORE leaving
                    game_over = False
                    running = False
                    while True:
                        pygame.event.pump()
                        keys = pygame.key.get_pressed()
                        if not any(keys):
                            break

                    return  # <-- CRITICAL: exit run_game_loop completely

            continue  # stay in GAME OVER loop until click

        #---------------------
        # INPUT
        #---------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.mixer.stop()
                    pygame.mixer.music.load(resource_path("sounds/splashscreenmusic.wav"))
                    pygame.mixer.music.play(-1)
                    running = False

            if control_mode == "Keyboard":
                # only detach ball if mouse button pressed and Get Ready message is gone
                if event.type == pygame.KEYDOWN and event.key == pygame.K_1 and not show_ready:
                    if balls[0].attached:
                        balls[0].attached = False
                    elif paddle.laser_enabled:
                        sound_laser.play()

                        projectiles.fire(paddle.rect)

            elif control_mode == "Joypad" and event.type == pygame.JOYBUTTONDOWN and not show_ready:
                if event.button == 0:  # A / Cross
                    if balls[0].attached:
                            balls[0].attached = False
                    elif paddle.laser_enabled:
                        sound_laser.play()
                        projectiles.fire(paddle.rect)

                # ⭐ Mouse firing (left click)
            else:  # mouse mode
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not show_ready:
                    if balls[0].attached:
                        balls[0].attached = False
                    elif paddle.laser_enabled:
                        sound_laser.play()

                        projectiles.fire(paddle.rect)
            if event.type == MUSIC_END:
                play_next_track()
                #UPDATE

        #Boss collision
        # Only run this on the boss level 10
        if level.level == End_level and boss:
            # Boss collision
            for ball in balls:
                if ball.rect.colliderect(boss.rect):
                    boss_hit.play()
                    # Determine collision side
                    overlap_top = abs(ball.rect.bottom - boss.rect.top)
                    overlap_bottom = abs(ball.rect.top - boss.rect.bottom)
                    overlap_left = abs(ball.rect.right - boss.rect.left)
                    overlap_right = abs(ball.rect.left - boss.rect.right)

                    smallest = min(overlap_top, overlap_bottom, overlap_left, overlap_right)

                    # --- Vertical collision (top or bottom) ---
                    if smallest == overlap_top:
                        # ball hit boss from above
                        ball.rect.bottom = boss.rect.top
                        ball.y = ball.rect.centery

                    elif smallest == overlap_bottom:
                        # ball hit boss from below
                        ball.rect.top = boss.rect.bottom
                        ball.y = ball.rect.centery

                    elif smallest == overlap_left:
                        ball.rect.right = boss.rect.left
                        ball.x = ball.rect.centerx

                    elif smallest == overlap_right:
                        ball.rect.left = boss.rect.right
                        ball.x = ball.rect.centerx
                    # --- Prevent vertical/horizontal lock ---
                    min_v = 2.0
                    if abs(ball.speed_y) < min_v:
                        ball.speed_y = min_v if ball.speed_y > 0 else -min_v

                    # Damage the boss

                    boss.hit()

                    # Boss defeated?
                    if boss.hp <= 0:

                        explode_boss(boss, debris_list)
                        boss.dead = True
                        boss_missiles.empty()
                        explosion_timer[0] = 5
                        pygame.mixer.find_channel(True).play(sound_explosion)
                        score.add(1000)
                        balls[0].attached=True
                        game_state = "BOSS_EXPLOSION"
                        boss_explosion_timer = 2.0  # or however long your explosion lasts


                    if ball.speed_y < 0:  # ball moving up
                        ball.y = boss.rect.bottom + ball.radius
                    else:  # ball moving down
                        ball.y = boss.rect.top - ball.radius

                    # Now bounce (always)
                    ball.speed_y *= -1

                    # Stop further collision checks this frame
                    break


        # --- UPDATE PADDLES ---
        paddle.p_update(control_mode, joystick)
        if paddle2.active:
            paddle2.rect.centerx = paddle.rect.centerx

        # --- UPDATE BALLS ---
        lost_balls = []
        for b in balls:
            ball_lost = b.b_update(paddle.rect)
            if ball_lost:
                lost_balls.append(b)

        #  Guarantee only the main ball can ever be attached
        for i, b in enumerate(balls):
            if i != 0:
                b.attached = False

        for b in lost_balls:
            balls.remove(b)

        if len(balls) == 0:
            stats.balls_lost += 1
            lives.dec()
            if lives.lives > 0:
                balls = [Ball(WIDTH // 2, HEIGHT // 2, score, difficulty)]
                balls[0].attached = True
                show_ready = True
                ready_has_run = False
                ready_phase = "drop"
                ready_x = WIDTH // 2
                ready_y = -100
            else:
                game_over = True

        # --- PADDLE2 COLLISION ONLY ---
        if paddle2.active:
            for b in balls:
                b.check_paddle_collision(paddle2.rect)

        # --- BALL SOUND FLAGS (use first ball as reference if exists) ---
        if balls:
            ref = balls[0]
            if ref.sidehit:
                sound_ball_side.play()
                ref.sidehit = False
            if ref.tophit:
                sound_ball_top.play()
                ref.tophit = False
            if ref.paddlehit:
                ref.paddlehit = False

            # --- BRICK COLLISIONS ---
        if level.level !=End_level:
            for b in balls:
                for brick in bricks.bricks[:]:
                    if b.rect.colliderect(brick.rect):
                        sound_brick.play()

                        hit_from_top = b.prev_y + b.radius <= brick.rect.top
                        hit_from_bottom = b.prev_y - b.radius >= brick.rect.bottom
                        hit_from_left = b.prev_x + b.radius <= brick.rect.left
                        hit_from_right = b.prev_x - b.radius >= brick.rect.right

                        if hit_from_top:
                            b.speed_y *= -1
                            # Prevent horizontal lock after top-hit
                            if abs(b.speed_y) < 1:
                                b.speed_y = 1 if b.speed_y >= 0 else -1

                            b.y = brick.rect.top - b.radius
                        elif hit_from_bottom:
                            b.speed_y *= -1
                            #  Prevent horizontal lock after bottom-hit
                            if abs(b.speed_y) < 1:
                                b.speed_y = 1 if b.speed_y >= 0 else -1

                            b.y = brick.rect.bottom + b.radius
                        elif hit_from_left:
                            b.speed_x *= -1
                            b.x = brick.rect.left - b.radius
                        elif hit_from_right:
                            b.speed_x *= -1
                            b.x = brick.rect.right + b.radius

                        b.rect.x = b.x - b.radius
                        b.rect.y = b.y - b.radius
                        clamp_ball_angle(b)

                        if brick.hit():
                            bricks.bricks.remove(brick)
                            stats.bricks_destroyed += 1
                            score.add(50)
                            powerups.spawn(brick.rect.x, brick.rect.y, level.level, difficulty)
                        else:
                            brick.update_color()
                        break

        # --- LEVEL / BOSS ---
        if not exploding[0] and level.level % 4 == 0:
            pygame.mixer.music.pause()
            summary = SummaryScreen(WIDTH, HEIGHT)

            balls.clear()
            balls.append(Ball(WIDTH // 2, HEIGHT // 2, score, difficulty))
            balls[0].attached = True
            show_summary_screen(summary, stats, screen, level)
            # --- CLEANUP any graphics after summary page
            boss_missiles.empty()
            missiles.empty()
            debris_list.clear()
            explosion_timer[0] = 0
            exploding[0] = False
            paddle.missile_active = False
            paddle.can_fire = True
            shake_timer = 0

            # Reset GET READY animation flags
            ready_has_run = False
            show_ready = True
            ready_phase = "drop"
            ready_x = WIDTH // 2
            ready_y = -100
            pygame.mixer.music.unpause()

        if level.level == End_level and boss is None:
            boss = Boss(WIDTH // 2 - 60, 80, scale=20)

        # --- POWERUPS COLLISION ---
        for p in powerups.powerups[:]:
            if p.rect.colliderect(paddle.rect) or (paddle2.active and p.rect.colliderect(paddle2.rect)):
                stats.powerups_collected += 1
                sound_powerup.play()
                apply_powerup(p.kind, paddle, paddle2, balls, lives, active_powerups,
                                score, bricks, debris_list, explosion_timer, difficulty)
                powerups.powerups.remove(p)

        # --- LEVEL CLEAR ---
        if not exploding[0] and len(bricks.bricks) == 0:

            seed = level.next_level()
            stats.levels_completed=level.level
            #Brick resilience must be an input parameter
            bricks = BrickField(WIDTH, HEIGHT, level, rows=6, cols=12, seed=seed, y_offset=100)

        # --- PROJECTILES vs BRICKS ---
        for p in projectiles.projectiles[:]:
            for brick in bricks.bricks[:]:
                if p.rect.colliderect(brick.rect):
                    if brick.hit():
                        bricks.bricks.remove(brick)
                        score.add(50)
                    else:
                        brick.update_color()
                    projectiles.projectiles.remove(p)
                    explosions.spawn(brick.rect.center, brick.color)
                    sound_explosion.play()
                    break

        # --- UPDATE MANAGERS ---
        powerups.update(dt)
        projectiles.update()
        explosions.update(dt)
        missiles.update()
        warp.update(dt, stars.stars)

        if flash_timer > 0:
            flash_timer -= dt * 1000  # convert seconds → milliseconds
            if flash_timer < 0:
                flash_timer = 0

        # --- BOSS MISSILE → PADDLE COLLISION ---
        for missile in boss_missiles:
            if missile.rect.colliderect(paddle.rect) and not show_ready:

                pygame.mixer.find_channel(True).play(missile_explosion)

                # Remove missile

                boss_missiles.remove(missile)

                # Damage player
                lives.dec()

                # Paddle flash + screen shake
                paddle.flash_timer = 5.0
                explosion_timer[0] = 0.25
                shake_intensity = 5

                # ⭐ Reset ball on paddle
                ball.attached = True
                ball.x = paddle.rect.x + paddle.width // 2
                ball.y = paddle.rect.y - ball.radius
                ball.prev_x = ball.x
                ball.prev_y = ball.y
                ball.speed_x = ball.base_speed_x
                ball.speed_y = ball.base_speed_y

                # ⭐ Reset GET READY animation
                ready_has_run = False
                show_ready = True
                ready_phase = 0
                ready_x = WIDTH // 2
                ready_y = HEIGHT // 2

                # Optional: paddle flash
                paddle.flash_timer = 0.15

                # Optional: screen shake
                screen_shake = 5

                # Game over?
                if lives.lives <= 0:
                    game_over = True
                    break

            if paddle.flash_timer > 0:
                paddle.flash_timer -= dt

        # --- ACTIVE POWERUPS TIMER ---
        now = pygame.time.get_ticks()
        for kind, end_time in list(active_powerups.items()):
            if now >= end_time:
                remove_powerup(kind, paddle, paddle2, balls)
                del active_powerups[kind]

        # --- BOSS INTRO TIMER ---
        if level.level == End_level and boss_intro_timer[0] > 0:
            boss_intro_timer[0] -= 1

        # --- GET READY INITIALISATION ---
        if show_ready and not ready_has_run:
            powerups.powerups.clear()
            ready_phase = "drop"
            ready_y = -100
            ready_x = WIDTH // 2
            ready_pause_start = pygame.time.get_ticks()
            balls[0].attached = True
            ready_has_run = True

        # --- GET READY ANIMATION ---
        if show_ready and not game_over:
            if ready_phase == "drop":
                ready_y += 2
                if ready_y >= HEIGHT // 2:
                    ready_y = HEIGHT // 2
                    ready_phase = "pause"
                    ready_pause_start = pygame.time.get_ticks()

            elif ready_phase == "pause":
                if pygame.time.get_ticks() - ready_pause_start > 3000:
                    ready_phase = "exit"

            if ready_phase == "exit":
                ready_x += 50
                sound_whoosh.play()
                if ready_x > WIDTH + 200:
                    show_ready = False
                    balls[0].attached = False
                    ready_phase = "drop"
                    ready_y = -100
                    ready_x = WIDTH // 2

        if level.level == End_level and not show_ready:
            level10_sound_timer[0] -= dt

            if level10_sound_timer[0] <= 0:
                pygame.mixer.find_channel(True).play(intruder_alert)
                level10_sound_timer[0] = 7.0  # restart the 10-second cycle

        # --- UPDATE DEBRIS ---
        debris_list = [d for d in debris_list if not d.dead]
        for d in debris_list:
            d.update(dt, game_time)
        if boss and not boss.dead:
            if boss.fire_cooldown <= 0:
                # Start a staggered burst
                boss.burst_offsets = [-40, -20, 0, 20, 40]   # fire 3 missiles
                boss.burst_timer = 0.1  # 150ms between shots

                # Reset main cooldown
                low, high = difficulty_intervals[difficulty]
                boss.fire_cooldown = random.uniform(low, high)

            # Handle staggered burst firing
            if boss.burst_offsets:
                boss.burst_timer -= dt
                if boss.burst_timer <= 0:
                    off = boss.burst_offsets.pop(0)
                    boss.fire_missile(missiles, x_offset=off)
                    boss.burst_timer = .75  # reset timer for next missile

            # --- FIX: reset burst state when done ---
            elif not boss.burst_offsets:
                boss.burst_timer = 0
            boss.fire_cooldown -= dt

            if boss.flash_timer > 0:
                boss.flash_timer -= dt

        if game_state == "BOSS_EXPLOSION":
            boss_explosion_timer -= dt
            if boss_explosion_timer <= 0:
                end_message.start()

                game_state = "END_MESSAGE"

        if game_state == "END_MESSAGE":
            end_message.update(dt)

            if not end_message.active:  # message finished fading out
                warp.start()
                game_state = "WARP"

        if game_state == "WARP":
            warp_drive.play()
            warp.update(dt, stars.stars)

            if not warp.active and warp.timer <= 0:
                pygame.mixer.music.load(resource_path("sounds/EndCredits.wav"))
                pygame.mixer.music.play(0)
                credits.start()
                game_state = "CREDITS"

        if game_state == "CREDITS":

            credits.update(dt)

            if credits.finished:
                pygame.mixer.music.stop()
                return

        if game_state == "CREDITS":
            balls[0].attached = True
            screen.fill((0, 0, 0))
            credits.draw(screen)
            pygame.display.flip()
            continue
        screen.fill((0, 0, 0))

        # Background
        stars.draw(screen)

        if game_state == "END_MESSAGE":
            end_message.draw(screen)

        for missile in boss_missiles.sprites():
            pygame.draw.rect(screen, (255, 0, 0), missile.rect, 1)

        pygame.draw.rect(screen, (0, 255, 0), paddle.rect, 1)

        # Bricks (with shake)
        if explosion_timer[0] > 0:
            ox, oy = get_shake_offset(dt)
        else:
            ox, oy = (0, 0)

        if level.level !=End_level: #Only draw bricks when level is not 10
            for brick in bricks.bricks:
                pygame.draw.rect(screen, brick.color, brick.rect.move(ox, oy))

        # Paddles
        paddle.draw(screen)
        if paddle2.active:
            paddle2.draw(screen)

        # Balls
        for b in balls:
            if b.attached:
                b.x = paddle.rect.centerx
                b.y = paddle.rect.top - b.radius
                b.rect.center = (b.x, b.y)
            b.draw(screen)

        # Effects
        explosions.draw(screen)
        powerups.draw(screen)
        projectiles.draw(screen)
        missiles.draw(screen)
        warp.draw_overlay(screen)

        # Explosion timer
        if exploding[0]:
            explosion_timer[0] -= dt
            if explosion_timer[0] <= 0:
                exploding[0] = False
        
        # Debris
        for d in debris_list:
            d.draw(screen, ox, oy)

        # HUD
        score.draw(screen)
        level.draw(screen)
        lives.draw(screen)

        # Boss
        if boss:
            pygame.mixer.music.stop()
            if level.level == End_level and boss.dead!=True:
                boss.draw_health_bar(screen)
                boss.update()
                boss.draw(screen)

        if boss and boss.dead:
            if pygame.time.get_ticks() - boss.death_timer > 2000:
                boss = None
                level.level += 1

        # Boss firing update
        if boss:
            if not boss.dead:
                boss.update()
                boss.fire_logic(boss_missiles)
                boss_fire.play()
                boss_missiles.update()

        # Boss intro text
        if level.level == End_level and boss_intro_timer[0] > 0:

            #Deactivate laser powerup
            if "laser" in active_powerups:
                del active_powerups["laser"]

            paddle.laser_enabled = False
            paddle.laser_cooldown = 0
            paddle.laser_ready = False

            line1 = "Well done recruit. Now do battle with"
            line2 = "the evil Big Boss!"
            text1 = font_big.render(line1, True, (255, 0, 0))
            text2 = font_big.render(line2, True, (255, 0, 0))
            rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(text1, rect1)
            screen.blit(text2, rect2)

        # GET READY overlay
        if show_ready and not game_over:
            font_ready = pygame.font.Font(None, 80)
            font_ready.set_italic(True)
            ready_text = font_ready.render("GET READY!", True, (255, 0, 0))
            ready_rect = ready_text.get_rect(center=(ready_x, ready_y))
            screen.blit(ready_text, ready_rect)

        #Mult ball power up screen flash
        if flash_timer > 0:
            alpha = int((flash_timer / FLASH_DURATION) * 255)
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(alpha)
            screen.blit(flash_surface, (0, 0))

        pygame.display.flip()

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(resource_path("sounds/splashscreenmusic.wav"))
    pygame.joystick.init()

    screentransition = pygame.mixer.Sound(resource_path("sounds/screentransition.wav"))
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smash Deluxe")

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.joystick.init()
    powerups = PowerUpManager()

    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    #defualt options
    control_mode="mouse"
    difficulty = "Normal"

    # Shared starfield for menus
    starfield_3d = Starfield3D(WIDTH, HEIGHT, num_stars=400)

    # 2D scrolling stars for gameplay
    stars_2d = ScrollingStars(WIDTH, HEIGHT, star_count=150)
    score =Score(10,10)
    ball = Ball(0, 0, score)
    paddle = Paddle(350, 550)
    powerup_manager = PowerUpManager()

    lives = Lives(330, 10, 3)

    game_over = reset_game_state(score, ball, paddle, powerup_manager, lives, difficulty)

    # Start screen
    while True:
        clock.tick(60)
        screen.fill((0, 0, 0))
        pygame.mixer.music.stop()
        pygame.mixer.music.load(resource_path("sounds/splashscreenmusic.wav"))
        pygame.mixer.music.play(-1)

        start_screen = StartScreen(screen, starfield_3d)
        choice = start_screen.run()

        font = pygame.font.Font(None, 36)


        if choice == "Start Game":

            pygame.mixer.music.fadeout(1000)

            pygame.mixer.music.play(-1)

            run_game_loop(screen, clock, control_mode, difficulty, stars_2d, joystick)

        if choice =="Controls Options":

            control_mode, difficulty, continue_game = options_menu(
                screen, clock, control_mode, difficulty
            )

        elif choice == "Mission Briefing":
            screentransition.play()
            show_mission_briefing(screen)

        elif choice == "High Scores":
            screentransition.play()
            table=HighScoreTable()
            highscore_screen = HighScoreScreen(table,font)
            highscore_screen.run(screen, clock, difficulty)

        elif choice == "Credits":
            screentransition.play()

            credits = CreditsScreen(WIDTH, HEIGHT)
            credits.start()

            while credits.active:
                dt = clock.tick(60) / 1000.0
                credits.update(dt)

                screen.fill((0, 0, 0))
                credits.draw(screen)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        credits.active = False

        elif choice == "Quit":
            pygame.quit()
            return

if __name__ == '__main__':
    main()


