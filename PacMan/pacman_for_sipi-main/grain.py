import pygame

"""
Class for grain
"""
class Grain(pygame.sprite.Sprite):
    def __init__(self, screen):
        super(Grain, self).__init__()
        self.screen = screen
        self.image = pygame.image.load('data/images/grain_images/grain.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

    def draw(self):
        self.screen.blit(self.image, self.rect)