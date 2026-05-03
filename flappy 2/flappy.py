import pygame, sys, random, os

pygame.init()
pygame.mixer.init()

# ===== SCREEN =====
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Ultra Max")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)

# ===== LOAD =====
bird_frames = [
    pygame.image.load("assets/bird1.png").convert_alpha(),
    pygame.image.load("assets/bird2.png").convert_alpha(),
    pygame.image.load("assets/bird3.png").convert_alpha()
]

pipe_img = pygame.image.load("assets/pipe.png").convert_alpha()
bg_img = pygame.image.load("assets/background.png").convert()

bird_frames = [pygame.transform.scale(b, (40, 30)) for b in bird_frames]
pipe_img = pygame.transform.scale(pipe_img, (70, 400))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# ===== SOUND =====
jump_s = pygame.mixer.Sound("assets/jump.wav")
hit_s = pygame.mixer.Sound("assets/hit.wav")
score_s = pygame.mixer.Sound("assets/score.wav")

# ===== HIGH SCORE =====
if not os.path.exists("highscore.txt"):
    open("highscore.txt", "w").write("0")

best_score = int(open("highscore.txt").read())

# ===== GAME VARS =====
gravity = 0.5
bird_vel = 0
bird_rect = bird_frames[0].get_rect(center=(80, HEIGHT//2))

pipe_pairs = []
SPAWN = pygame.USEREVENT
pygame.time.set_timer(SPAWN, 1300)

score = 0
game_state = "START"

bg_x = 0
frame = 0

PIPE_GAP = 170

# ===== FUNCTIONS =====
def draw_text(text, x, y, color=(255,255,255)):
    screen.blit(font.render(text, True, color), (x, y))

def create_pipe_pair():
    h = random.randint(200, 450)
    bottom = pipe_img.get_rect(midtop=(WIDTH+60, h))
    top = pipe_img.get_rect(midbottom=(WIDTH+60, h-PIPE_GAP))
    return {"bottom": bottom, "top": top, "scored": False}

def move_pipes(pairs):
    for p in pairs:
        p["bottom"].centerx -= 4
        p["top"].centerx -= 4
    return [p for p in pairs if p["bottom"].right > -60]

def draw_pipes(pairs):
    for p in pairs:
        screen.blit(pipe_img, p["bottom"])
        screen.blit(pygame.transform.flip(pipe_img, False, True), p["top"])

def check_collision(pairs):
    for p in pairs:
        if bird_rect.colliderect(p["bottom"]) or bird_rect.colliderect(p["top"]):
            return True
    return bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT

def rotate_bird(bird, vel):
    return pygame.transform.rotate(bird, -vel * 3)

def save_high(score, best):
    if score > best:
        best = score
        with open("highscore.txt", "w") as f:
            f.write(str(best))
    return best

# ===== LOOP =====
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            if game_state == "START":
                game_state = "PLAY"

            elif game_state == "PLAY":
                bird_vel = -8
                jump_s.play()

            elif game_state == "OVER":
                game_state = "PLAY"
                pipe_pairs.clear()
                bird_rect.center = (80, HEIGHT//2)
                bird_vel = 0
                score = 0

        if e.type == SPAWN and game_state == "PLAY":
            pipe_pairs.append(create_pipe_pair())

    # ===== BACKGROUND =====
    bg_x -= 1
    if bg_x <= -WIDTH:
        bg_x = 0
    screen.blit(bg_img, (bg_x, 0))
    screen.blit(bg_img, (bg_x + WIDTH, 0))

    # ===== ANIMATION =====
    frame += 1
    bird = bird_frames[(frame // 6) % 3]

    if game_state == "START":
        draw_text("Press SPACE to Start", 40, HEIGHT//2)

    elif game_state == "PLAY":
        bird_vel += gravity
        bird_rect.centery += int(bird_vel)

        pipe_pairs = move_pipes(pipe_pairs)
        draw_pipes(pipe_pairs)

        # ===== PERFECT SCORING SYSTEM =====
        for p in pipe_pairs:
            if p["bottom"].centerx < bird_rect.centerx and not p["scored"]:
                score += 1
                score_s.play()
                p["scored"] = True

        if check_collision(pipe_pairs):
            hit_s.play()
            game_state = "OVER"
            best_score = save_high(score, best_score)

        draw_text(f"Score: {score}", 10, 10)

    elif game_state == "OVER":
        draw_text("GAME OVER", 100, 230, (255,0,0))
        draw_text(f"Score: {score}", 120, 280)
        draw_text(f"Best: {best_score}", 120, 320)
        draw_text("Press SPACE", 90, 370)

    screen.blit(rotate_bird(bird, bird_vel), bird_rect)

    pygame.display.update()
    clock.tick(60)