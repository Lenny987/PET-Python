import pygame

"""
Class for super grain
"""


class Super_Grain(pygame.sprite.Sprite):
    def __init__(self, screen):
        super(Super_Grain, self).__init__()
        self.screen = screen
        self.image = pygame.image.load('data/images/super_grain_images/super_grain.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

    def draw(self):
        self.screen.blit(self.image, self.rect)