import pygame
import random
import sys

pygame.init()


SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird By Aaqid')
game_font = pygame.font.Font('.\\bin\\04B_19.ttf',25)

clock = pygame.time.Clock()
FPS = 120

# GAME VARIABLES
GAME_GRAVITY = 0.1
LIFT = -3
BACKGROUND_VELOCITY = 0.5
FLOOR_VELOCITY = 2
pipe_velocity = 2

game_active = False
score = 0
high_score = 0
can_score = True
reset_score_value = 0


# Read Game Data
highest_score = 0
with open('.\\bin\\data.txt', 'r') as f:
    data = f.read()

    highest_score = int(data)


# bird
bird_downflap = pygame.image.load('assests\\yellowbird-upflap.png').convert_alpha()
bird_midflap = pygame.image.load('assests\\yellowbird-midflap.png').convert_alpha()
bird_upflap = pygame.image.load('assests\\yellowbird-downflap.png').convert_alpha()
flappy_bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
flappy_bird_surface = flappy_bird_frames[bird_index]
flappy_bird_rect = flappy_bird_surface.get_rect(center = (50,300))

# creating a custom event
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP,100)
flappy_bird_dy = 0

# floor
floor_surface = pygame.image.load('.\\assests\\base.png').convert()
floor_x = 0
FLOOR_Y = 412



# pipes
pipe_surface = pygame.image.load('.\\assests\\pipe-green.png')
pipe_list = []

# pipe spawn event
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE,1200)

# background

background_surface = pygame.image.load('.\\assests\\background.png').convert()

background_x = 0
background_y = 0




# game over
game_over_surface = pygame.image.load('.\\assests\\message.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center = (144,275))

# GAME SOUNDS
flap_sound = pygame.mixer.Sound('.\\sound\\sfx_wing.wav')
death_sound = pygame.mixer.Sound('.\\sound\\sfx_die.wav')
score_sound = pygame.mixer.Sound('.\\sound\\sfx_point.wav')
hit_sound = pygame.mixer.Sound('.\\sound\\sfx_hit.wav')
# swoosh_sound = pygame.mixer.Sound('.\\sound\\sfx_swooshing.wav')

score_sound_countdown = 100
SCOREEVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SCOREEVENT,100)

def generate_background():

    global background_x

    screen.blit(background_surface, (background_x, background_y))
    screen.blit(background_surface, (background_x + SCREEN_WIDTH, background_y))

    if background_x <= -SCREEN_WIDTH:
        background_x = 0

    background_x -= BACKGROUND_VELOCITY



def generate_floor():
    global floor_x

    screen.blit(floor_surface, (floor_x, FLOOR_Y))
    screen.blit(floor_surface, (floor_x + SCREEN_WIDTH, FLOOR_Y))

    if floor_x <= -SCREEN_WIDTH:
        floor_x = 0

    floor_x -= FLOOR_VELOCITY

def update_bird_index():
    global bird_index

    if bird_index < 2:
        bird_index += 1
    else:
        bird_index = 0

def rotate_bird():
    rotated_flappy_bird = pygame.transform.rotozoom(flappy_bird_surface,-flappy_bird_dy * 6,1)
    return rotated_flappy_bird

def update_bird():
    new_flappy_bird_surface = flappy_bird_frames[bird_index]
    new_flappy_bird_rect = new_flappy_bird_surface.get_rect(center=(50, flappy_bird_rect.centery))

    return new_flappy_bird_surface, new_flappy_bird_rect


def check_collision(pipes):

    for pipe in pipes:
        if flappy_bird_rect.colliderect(pipe):
            hit_sound.play()
            return False



    if flappy_bird_rect.top <= -100 or flappy_bird_rect.bottom >= 412:
        death_sound.play()
        return False

    return True


def create_pipe():
    pipe_y_pos = random.randint(200,500)
    buttom_pipe = pipe_surface.get_rect(midtop=(SCREEN_WIDTH + 50, pipe_y_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (SCREEN_WIDTH + 50, pipe_y_pos - 250))

    return buttom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_velocity
    visible_pipes = [pipe for pipe in pipes if pipe.right > -25]
    return visible_pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_surface, pipe)
        else:
            flipped_pipe = pygame.transform.flip(pipe_surface,False,True)
            screen.blit(flipped_pipe,pipe)


def update_highest_score(score):
    global highest_score
    highest_score = score
    with open('.\\bin\\data.txt', 'w') as f:
        f.write(str(highest_score))

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255,255,255))
        score_rect = score_surface.get_rect(center = (140,100))
        screen.blit(score_surface, score_rect)

    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255,255,255))
        score_rect = score_surface.get_rect(center = (140,100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255,255,255))
        high_score_rect = high_score_surface.get_rect(center = (140,65))
        screen.blit(high_score_surface, high_score_rect)

        highest_score_surface = game_font.render(f'Highest Score: {int(highest_score)}', True, (100,100,100))
        highest_score_rect = high_score_surface.get_rect(center = (115,475))
        screen.blit(highest_score_surface, highest_score_rect)




def update_score(score, high_score):
	if score > high_score:
		high_score = score
	return high_score

def pipe_score_check():
    global score, can_score, reset_score_value
    score = reset_score_value
    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and can_score:
                score += 1
                reset_score_value += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and game_active:
            flappy_bird_dy = LIFT
            flap_sound.play()

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and not game_active:
                game_active = True

        if event.type == BIRDFLAP:
            update_bird_index()
            flappy_bird_surface,flappy_bird_rect = update_bird()

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())


    generate_background()
    generate_floor()


    if game_active:
        flappy_bird_dy += GAME_GRAVITY
        rotated_bird = rotate_bird()
        flappy_bird_rect.centery += flappy_bird_dy
        screen.blit(rotated_bird, flappy_bird_rect)
        game_active = check_collision(pipe_list)


        # pipe logic
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # scoring
        pipe_score_check()
        score_display('main_game')

    else:
        screen.blit(game_over_surface, game_over_rect)
        flappy_bird_rect = flappy_bird_surface.get_rect(center = (50,300))
        flappy_bird_dy = -6
        pipe_list.clear()
        high_score = update_score(score, high_score)
        score_display('game_over')
        reset_score_value = 0
        if score > highest_score:
            update_highest_score(score)


    pygame.display.update()
    clock.tick(FPS)
