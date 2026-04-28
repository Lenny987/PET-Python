import pygame.font
from pacman import Pacman
from pygame.sprite import Group


class Scores():
    """вывод игровой информации"""
    def __init__(self, screen, stats):
        """инициализируем подсчет очков"""
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.stats = stats
        self.text_color = (0, 0, 255)
        self.font = pygame.font.SysFont('Arial Black', 13)
        self.pacmans = Group()
        self.lifes = stats.pacmans_left
        for i in range(self.stats.pacmans_left):
            pacman = Pacman(self.screen)
            pacman.rect.x = 15 + i * pacman.rect.width
            pacman.rect.bottom = self.screen_rect.bottom - 10
            self.pacmans.add(pacman)


    def image_score(self):
        """преобразование текста счета в графическое изображение"""
        self.score_img = self.font.render(str(self.stats.score), True, self.text_color, (0, 0, 0))
        self.score_img.set_colorkey((0, 0, 0))
        self.score_rect = self.score_img.get_rect()
        self.score_rect.left = self.screen_rect.left + 80
        self.score_rect.top = self.screen_rect.top

        self.txt = self.font.render('Ваш счет:', True, (0, 0, 255))
        self.txt.set_colorkey((0, 0, 0))
        self.txt_rect = self.txt.get_rect()
        self.txt_rect.left = self.screen_rect.left
        self.txt_rect.top = self.screen_rect.top


    def image_high_score(self):
        """преобразование рекорда в изображение"""
        self.high_score_image = self.font.render(str(self.stats.high_score), True, self.text_color, (0, 0, 0))
        self.high_score_image.set_colorkey((0, 0, 0))
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.right = self.screen_rect.right
        self.high_score_rect.top = self.screen_rect.top

        self.record_txt = self.font.render('Лучший счет:', True, (0, 0, 255))
        self.record_txt.set_colorkey((0, 0, 0))
        self.record_txt_rect = self.record_txt.get_rect()
        self.record_txt_rect.right = self.screen_rect.right - 40
        self.record_txt_rect.top = self.screen_rect.top

    def show_score(self):
        """вывод счета на экран"""
        self.screen.blit(self.score_img, self.score_rect)
        self.screen.blit(self.txt, self.txt_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.record_txt, self.record_txt_rect)
        self.pacmans.draw(self.screen)

    def image_pacmans(self):
        self.pacmans.draw(self.screen)
    
    def update_pacmans(self):
        if self.stats.pacmans_left < self.lifes:
            self.lifes = self.stats.pacmans_left
            list(self.pacmans)[-1].kill()