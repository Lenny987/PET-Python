import pygame
import time
import sys
from datetime import datetime
from grain import Grain
from super_grain import Super_Grain
from field import arr
import random
from ghosts import Red, Blue, Orange, Pink

'''
Function for check events in pacman game
'''


def events(pacman, run):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.USEREVENT:
            pacman.pacCol = True
        elif event.type == pygame.KEYDOWN:
            pacman.pacCol = False
            if event.key == pygame.K_d:
                pacman.mRight = True
            elif event.key == pygame.K_a:
                pacman.mLeft = True
            elif event.key == pygame.K_w:
                pacman.mUp = True
            elif event.key == pygame.K_s:
                pacman.mDown = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                pacman.mRight = False
            elif event.key == pygame.K_a:
                pacman.mLeft = False
            elif event.key == pygame.K_w:
                pacman.mUp = False
            elif event.key == pygame.K_s:
                pacman.mDown = False
    return run


'''
Main draw(update screen)
'''


def update(bg_color, screen, pacman, grains, super_grains, sc, counter, ghosts, start, arr):
    screen.fill(bg_color)
    draw_field(screen, arr)
    sc.image_score()  
    sc.image_high_score() 
    sc.update_pacmans()
    sc.show_score()
    sc.image_pacmans()

    for ghost in ghosts:
        ghost.output()
    pacman.output(screen, counter, start)
    grains.draw(screen)
    super_grains.draw(screen)
    pygame.display.flip()


'''
Function for check contact ghost and pacman
'''


def collision_pacman_ghost(stats, pacman, ghosts, start, run, screen, volume):
    collision = pygame.sprite.spritecollideany(pacman, ghosts)
    if collision and pacman.energized:
        for ghost in ghosts:
            if pygame.sprite.collide_mask(pacman, ghost):
                ghost.__init__(screen)
                # ghost.collide_with_energazed = True
                stats.score += 200
                eat = pygame.mixer.Sound("data/musics/eat_ghosts.mp3")
                eat.set_volume(0.01 * volume)
                eat.play()
    elif collision and not pacman.god_mode and stats.pacmans_left > 0:
        stats.pacmans_left -= 1
        reducing_lives = pygame.mixer.Sound("data/musics/reducing_lives_pacman.mp3")
        reducing_lives.set_volume(0.01 * volume)
        reducing_lives.play()
        start = time.time()
        pacman.god_mode = True
    elif stats.pacmans_left == 0:
        pygame.quit()
        run = False
        return None, run
    return start, run


def update_grains(stats, grains, pacman, sc, volume):
    eat = pygame.mixer.Sound("data/musics/eat_grain.mp3")
    eat.set_volume(0.01 * volume)
    grains.update()
    collision = pygame.sprite.spritecollideany(pacman, grains)
    if collision:
        collision.kill()
        stats.score += 10
        sc.image_score()
        check_high_score(stats, sc)
        eat.play()


def update_super_grains(stats, super_grains, pacman, sc, volume):
    eat = pygame.mixer.Sound("data/musics/eat_super_grain.wav")
    eat.set_volume(0.01 * volume)
    super_grains.update()
    collision = pygame.sprite.spritecollideany(pacman, super_grains)
    if collision:
        pacman.energized = True
        pacman.energized_start_time = datetime.now()
        eat.play()
        collision.kill()
        stats.score += 50
        sc.image_score()
        check_high_score(stats, sc)


'''
Function for check high score
'''


def check_high_score(stats, sc):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sc.image_high_score()
        with open('highscore.txt', 'w') as f:
            f.write(str(stats.high_score))


def check_counter(counter):
    if counter < 19:
        return counter + 1
    return 0


'''
2 Function for draw field
'''


def draw_field(screen, array):
    w, h = pygame.display.get_surface().get_size()
    n = h // 16
    m = w // 16
    field = arr
    if array:
        field = array
    for i in range(0, n):
        for j in range(0, m):
            if field[i][j] == 1:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 10))
            elif field[i][j] == 0:
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 16))
            elif field[i][j] == 2:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 13))
            elif field[i][j] == 3:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 13))
            elif field[i][j] == 4:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 13))
            elif field[i][j] == 5:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 13))
            elif field[i][j] == 6:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 13))
            elif field[i][j] == 7:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 13))
            elif field[i][j] == 8:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 16))
            elif field[i][j] == 9:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 10, 13))
            elif field[i][j] == 10:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 13))
            elif field[i][j] == 11:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 16))
            elif field[i][j] == 12:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 16))
            elif field[i][j] == 13:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, i * 16, 8, 13))
            elif field[i][j] == 14:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 8, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, (i * 16) + 3, 8, 13))
            elif field[i][j] == 15:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 10))
            elif field[i][j] == 16:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 10))
            elif field[i][j] == 17:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 8, 13))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 8, 13, 8))
            elif field[i][j] == 18:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 8, 13))


def first_draw_field(screen, grains, super_grains, array):
    w, h = pygame.display.get_surface().get_size()
    n = h // 16
    m = w // 16
    field = arr
    if array:
        field = array
    for i in range(0, n):
        for j in range(0, m):
            if field[i][j] == 1:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 10))
            elif field[i][j] == 0:
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 16))
            elif field[i][j] == 2:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 13))
            elif field[i][j] == 3:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 13))
            elif field[i][j] == 4:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 13))
            elif field[i][j] == 5:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 13))
            elif field[i][j] == 6:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 13))
            elif field[i][j] == 7:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 13))
            elif field[i][j] == 8:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 16))
            elif field[i][j] == 9:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 10, 13))
            elif field[i][j] == 10:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 13))
            elif field[i][j] == 11:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 16))
            elif field[i][j] == 12:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 16))
            elif field[i][j] == 13:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, i * 16, 8, 13))
            elif field[i][j] == 14:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 8, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, (i * 16) + 3, 8, 13))
            elif field[i][j] == 15:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 10))
            elif field[i][j] == 16:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 10))
            elif field[i][j] == 17:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 8, 13))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 8, 13, 8))
            elif field[i][j] == 18:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 8, 13))
            elif field[i][j] == 100:
                grain = Grain(screen)
                grain.x = j * 16
                grain.y = i * 16
                grain.rect.x = grain.x
                grain.rect.y = grain.y
                grains.add(grain)
            elif field[i][j] == 200:
                super_grain = Super_Grain(screen)
                super_grain.x = j * 16
                super_grain.y = i * 16
                super_grain.rect.x = super_grain.x
                super_grain.rect.y = super_grain.y
                super_grains.add(super_grain)

# Функция init ghosts создает заданное количество рандомных призраков, Surface(screen) на котором они будут отрисованы и 
# группу (Group) спрайтов призраков, куда при инициализации каждый добавляется
def init_ghosts(screen, ghosts, quanity): 
    for i in range(quanity):
        number = random.randint(1, 4)
        if number == 1:
            Red(screen, ghosts)
        if number == 2:
            Blue(screen, ghosts)
        if number == 3:
            Orange(screen, ghosts)
        if number == 4:
            Pink(screen, ghosts)
