import pygame
import controls
import time
from pygame.sprite import Group
from pacman import Pacman
from scores import Scores
from stats import Stats


SIZE = WIDTH, HEIGHT = 448, 544
FPS = 60

'''
function to run original pacman
'''
def run_game(arr=False):
    pygame.init()
    f = open('settings.txt', 'r')
    data = [line.strip() for line in f]
    f.close()
    pygame.mixer.music.load('data/musics/show.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.01 * int(data[1]))
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("pacman")
    bg_color = (0, 0, 0)
    counter = 0
    grains = Group()
    super_grains = Group()
    ghosts = Group()
    pacman = Pacman(screen)
    controls.init_ghosts(screen, ghosts, int(data[0]))
    # orange = Orange(screen)
    # pink = Pink(screen)
    # ghosts.add(red)
    # ghosts.add(blue)
    # ghosts.add(orange)
    # ghosts.add(pink)

    stats = Stats()
    sc = Scores(screen, stats)
    controls.first_draw_field(screen, grains, super_grains, arr)
    # start_time = datetime.now()
    start = time.time()
    run = True
    while run:
        counter = controls.check_counter(counter)
        run = controls.events(pacman, run)
        if not run:
            return stats.score
        pacman.update_pacman(arr)
        ghosts.update(pacman, arr)
        start, run = controls.collision_pacman_ghost(stats, pacman, ghosts, start, run, screen, int(data[1]))
        if not run:
            return stats.score
        controls.update(bg_color, screen, pacman, grains, super_grains, sc, counter, ghosts, start, arr)
        controls.update_grains(stats, grains, pacman, sc, int(data[1]))
        controls.update_super_grains(stats, super_grains, pacman, sc, int(data[1]))
        if len(list(grains)) == 0 and len(list(super_grains)) == 0:
            pygame.quit()
            return stats.score
        clock.tick(FPS)