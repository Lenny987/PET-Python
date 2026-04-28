import pygame
import time
from datetime import datetime
from field import arr

'''
Class for pacman
'''
class Pacman(pygame.sprite.Sprite):
    def __init__(self, screen):
        super(Pacman, self).__init__()
        self.screen = screen
        self.image = pygame.transform.scale(pygame.image.load('data/images/pacman_images/pacman.png'), (15, 15))

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.x = 14 * 16
        self.rect.y = 24 * 16
        self.direction = 0
        self.pacCol = False
        self.mRight = False
        self.mLeft = False
        self.mUp = False
        self.mDown = False
        self.god_mode = False
        self.energized = False
        self.energized_start_time = 0
        self.PLAYER_IMAGES_CONST = list()
        self.player_images = []
        self.player_god_mode_images = []
        for i in range(1, 5):
            self.player_images.append(pygame.transform.scale(pygame.image.load(f'data/images/pacman_images/{i}.png'), (16, 16)))
            self.player_god_mode_images.append(
                pygame.transform.scale(pygame.image.load(f'data/images/pacman_images/{i}_god_mode.png'), (16, 16)))
        self.PLAYER_IMAGES_CONST = self.player_images.copy()

    def output(self, screen, counter, start):
        if self.god_mode or self.energized:
            self.player_images = self.player_god_mode_images
        else:
            self.player_images = self.PLAYER_IMAGES_CONST
        if self.direction == 0:
            screen.blit(self.player_images[counter // 5], (self.rect.x, self.rect.y))
        elif self.direction == 1:
            screen.blit(pygame.transform.flip(self.player_images[counter // 5], True, False), self.rect)
        elif self.direction == 2:
            screen.blit(pygame.transform.rotate(self.player_images[counter // 5], 90), self.rect)
        elif self.direction == 3:
            screen.blit(pygame.transform.rotate(self.player_images[counter // 5], 270), self.rect)
        
        if time.time() - start > 3:
            self.god_mode = False

        if self.energized_start_time != 0 and (datetime.now() - self.energized_start_time).seconds > 5:
            self.energized = False



    def update_pacman(self, array):
        field = arr
        if array:
            field = array
        try:
            if self.mRight and self.rect.right < self.screen_rect.right and \
                    field[self.rect.y // 16][(self.rect.right + 1) // 16] % 100 == 0 and self.rect.centery % 16 == 7:
                self.rect.centerx += 2
                self.direction = 0
            if self.mLeft and field[self.rect.y // 16][(self.rect.left - 1) // 16] % 100 == 0 and self.rect.centery % 16 == 7:
                self.rect.centerx -= 2
                if self.rect.x < 0:
                    self.rect.x = self.screen_rect.right
                self.direction = 1
            if self.mUp and field[(self.rect.top - 1) // 16][self.rect.x // 16] % 100 == 0 and self.rect.centerx % 16 == 7:
                self.rect.centery -= 2
                self.direction = 2
            if self.mDown and field[(self.rect.bottom + 1) // 16][self.rect.x // 16] % 100 == 0 and self.rect.centerx % 16 == 7:
                self.rect.centery += 2
                self.direction = 3
        except IndexError:
            self.rect.x = self.screen_rect.left



