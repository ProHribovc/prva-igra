
import pygame
import random
import math
import sys
import array

pygame.init()

# ZVOK
try:
    pygame.mixer.init()
    SOUND = True
except pygame.error:
    SOUND = False

WIDTH = 960
HEIGHT = 640

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TREASURE HUNTER")

clock = pygame.time.Clock()

# BARVE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 200, 30)
BLUE = (40, 140, 255)
RED = (240, 50, 70)
GREEN = (30, 180, 100)
DARK = (10, 15, 40)
PURPLE = (150, 80, 255)

# PISAVE
font = pygame.font.Font(None, 36)
medium = pygame.font.Font(None, 55)
big = pygame.font.Font(None, 85)

# USTVARJANJE ZVOKOV
def make_sound(frequency, duration):
    if not SOUND:
        return None

    rate = 22050
    samples = array.array("h")

    for i in range(int(rate * duration)):
        t = i / rate
        fade = max(0, 1 - t / duration)
        value = int(
            10000 * fade *
            math.sin(2 * math.pi * frequency * t)
        )
        samples.append(value)

    return pygame.mixer.Sound(buffer=samples.tobytes())

coin_sound = make_sound(1000, 0.15)
hit_sound = make_sound(180, 0.3)
win_sound = make_sound(700, 0.4)

def play(sound):
    if sound is not None:
        sound.play()

# OZADJE
background = pygame.Surface((WIDTH, HEIGHT))

for y in range(HEIGHT):
    ratio = y / HEIGHT
    color = (
        int(8 + 15 * ratio),
        int(12 + 15 * ratio),
        int(40 + 35 * ratio)
    )
    pygame.draw.line(background, color, (0, y), (WIDTH, y))

# ZVEZDE
stars = []

for i in range(100):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3),
        random.random() * 6.28
    ])

# IGRALNI LIK
player = pygame.Rect(100, 300, 46, 54)
speed = 5

# TOCKE IN ZIVLJENJA
score = 0
lives = 3
invincible = 0

# KOVANEC
def new_coin():
    return pygame.Rect(
        random.randint(60, WIDTH - 60),
        random.randint(120, HEIGHT - 70),
        30, 30
    )

coin = new_coin()

# SOVRAZNIKI
def create_enemy(x, y, speed):
    return {
        "rect": pygame.Rect(x, y, 48, 48),
        "speed": speed,
        "phase": random.random() * 6
    }

def reset_game():
    global score, lives, invincible
    global player, coin, enemies, particles
    global state

    score = 0
    lives = 3
    invincible = 0

    player.x = 100
    player.y = 300

    coin = new_coin()

    enemies = [
        create_enemy(300, 170, 3),
        create_enemy(600, 400, -4),
        create_enemy(450, 280, 3)
    ]

    particles = []
    state = "playing"

enemies = [
    create_enemy(300, 170, 3),
    create_enemy(600, 400, -4),
    create_enemy(450, 280, 3)
]

# DELCI
particles = []

def create_particles(x, y, color):
    for i in range(22):
        angle = random.random() * math.pi * 2
        velocity = random.uniform(1, 5)

        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * velocity,
            "vy": math.sin(angle) * velocity,
            "life": 35,
            "color": color,
            "size": random.randint(2, 6)
        })

def update_particles():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.08
        p["life"] -= 1

        if p["life"] <= 0:
            particles.remove(p)

def draw_particles():
    for p in particles:
        size = max(1, int(p["size"] * p["life"] / 35))
        pygame.draw.circle(
            screen,
            p["color"],
            (int(p["x"]), int(p["y"])),
            size
        )

# RISANJE IGRALCA
def draw_player():
    t = pygame.time.get_ticks()
    bounce = math.sin(t * 0.012) * 4

    x = player.x
    y = int(player.y + bounce)

    # Senca
    pygame.draw.ellipse(
        screen, BLACK,
        (x - 3, player.bottom - 3, 52, 12)
    )

    # Sij
    pygame.draw.circle(
        screen, (20, 65, 130),
        (x + 23, y + 25), 34
    )

    # Telo
    pygame.draw.rect(
        screen, BLUE,
        (x, y, 46, 54),
        border_radius=14
    )

    pygame.draw.ellipse(
        screen, (120, 210, 255),
        (x + 9, y + 28, 28, 18)
    )

    # Oci
    pygame.draw.circle(screen, WHITE, (x + 14, y + 17), 8)
    pygame.draw.circle(screen, WHITE, (x + 33, y + 17), 8)

    pygame.draw.circle(screen, BLACK, (x + 16, y + 18), 4)
    pygame.draw.circle(screen, BLACK, (x + 35, y + 18), 4)

    # Usta
    pygame.draw.arc(
        screen, BLACK,
        (x + 13, y + 25, 22, 14),
        0, math.pi, 3
    )

    # Zascita po zadetku
    if invincible > 0 and (t // 100) % 2 == 0:
        pygame.draw.rect(
            screen, WHITE,
            (x - 5, y - 5, 56, 64),
            3, border_radius=18
        )

# RISANJE KOVANCA
def draw_coin():
    t = pygame.time.get_ticks()
    x, y = coin.center

    width = int(7 + abs(math.sin(t * 0.009)) * 13)

    pygame.draw.circle(screen, (120, 75, 0), (x, y), 24)
    pygame.draw.circle(screen, GOLD, (x, y), 19)

    pygame.draw.ellipse(
        screen, (255, 245, 130),
        (x - width // 2, y - 16, width, 32)
    )

    pygame.draw.circle(screen, WHITE, (x, y), 4)

# RISANJE SOVRAZNIKA
def draw_enemy(enemy):
    r = enemy["rect"]

    bounce = math.sin(
        pygame.time.get_ticks() * 0.01 + enemy["phase"]
    ) * 3

    x = r.x
    y = int(r.y + bounce)

    pygame.draw.circle(
        screen, (100, 10, 35),
        (x + 24, y + 24), 31
    )

    pygame.draw.circle(
        screen, RED,
        (x + 24, y + 24), 23
    )

    pygame.draw.circle(screen, WHITE, (x + 15, y + 18), 7)
    pygame.draw.circle(screen, WHITE, (x + 33, y + 18), 7)

    pygame.draw.circle(screen, BLACK, (x + 16, y + 19), 3)
    pygame.draw.circle(screen, BLACK, (x + 34, y + 19), 3)

    pygame.draw.line(
        screen, BLACK,
        (x + 16, y + 36),
        (x + 32, y + 36), 3
    )

# UI
def draw_ui():
    pygame.draw.rect(
        screen, (12, 18, 45),
        (0, 0, WIDTH, 82)
    )

    score_text = font.render(
        "SCORE: " + str(score), True, GOLD
    )

    screen.blit(score_text, (25, 25))

    level = 1 + score // 10

    level_text = font.render(
        "LEVEL: " + str(level), True, WHITE
    )

    screen.blit(level_text, (420, 25))

    for i in range(lives):
        x = 790 + i * 42
        y = 35

        pygame.draw.circle(screen, RED, (x - 7, y), 10)
        pygame.draw.circle(screen, RED, (x + 7, y), 10)

        pygame.draw.polygon(
            screen, RED,
            [(x - 17, y + 3), (x + 17, y + 3), (x, y + 23)]
        )

# MENI
def draw_menu():
    title = big.render("TREASURE HUNTER", True, GOLD)
    subtitle = medium.render("THE ARCADE ADVENTURE", True, WHITE)
    start = font.render("PRESS SPACE TO START", True, BLUE)
    controls = font.render("MOVE: WASD OR ARROW KEYS", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 190))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 285))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 400))
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, 465))

# STANJE IGRE
state = "menu"
running = True

# GLAVNA ZANKA
while running:

    dt = clock.tick(60)
    t = pygame.time.get_ticks()

    screen.blit(background, (0, 0))

    # ZVEZDE
    for star in stars:
        x, y, size, phase = star

        brightness = int(
            150 + 105 * abs(math.sin(t * 0.002 + phase))
        )

        pygame.draw.circle(
            screen,
            (brightness, brightness, 255),
            (x, y),
            size
        )

    # DOGODKI
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if state == "menu" and event.key == pygame.K_SPACE:
                reset_game()

            elif state == "gameover" and event.key == pygame.K_r:
                reset_game()

    # IGRANJE
    if state == "playing":

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += speed

        player.clamp_ip(
            pygame.Rect(0, 82, WIDTH, HEIGHT - 82)
        )

        if invincible > 0:
            invincible = max(0, invincible - dt)

        # SOVRAZNIKI
        for enemy in enemies:

            r = enemy["rect"]
            r.x += enemy["speed"]

            if r.left <= 0 or r.right >= WIDTH:
                enemy["speed"] *= -1

            if player.colliderect(r) and invincible <= 0:

                lives -= 1
                invincible = 1500

                play(hit_sound)

                create_particles(
                    player.centerx,
                    player.centery,
                    RED
                )

                player.x = 100
                player.y = 300

                if lives <= 0:
                    state = "gameover"
                    break

        # KOVANCI
        if state == "playing" and player.colliderect(coin):

            score += 1

            play(coin_sound)

            create_particles(
                coin.centerx,
                coin.centery,
                GOLD
            )

            coin = new_coin()

            if score % 10 == 0:
                play(win_sound)

        if state == "playing":

            draw_coin()

            for enemy in enemies:
                draw_enemy(enemy)

            draw_player()
            draw_ui()

    # DELCI
    update_particles()
    draw_particles()

    # GLAVNI MENI
    if state == "menu":
        draw_menu()

    # KONEC IGRE
    if state == "gameover":

        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        overlay.fill((5, 5, 20, 220))
        screen.blit(overlay, (0, 0))

        title = big.render("GAME OVER", True, RED)

        result = medium.render(
            "YOUR SCORE: " + str(score),
            True, GOLD
        )

        restart = font.render(
            "PRESS R TO RESTART",
            True, WHITE
        )

        screen.blit(
            title,
            (WIDTH // 2 - title.get_width() // 2, 210)
        )

        screen.blit(
            result,
            (WIDTH // 2 - result.get_width() // 2, 315)
        )

        screen.blit(
            restart,
            (WIDTH // 2 - restart.get_width() // 2, 400)
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
