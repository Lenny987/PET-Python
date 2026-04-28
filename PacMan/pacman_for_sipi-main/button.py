from constants import FILL_WIDTH
from arrays import arr
import pygame

'''
Class for check click element on the right site
'''


class Cell(object):
    WIDTH = 40

    def __init__(self, x, y, func, screen, func_number):
        self.screen = screen
        self.x = x
        self.y = y
        self.func = func
        pygame.draw.rect(self.screen, (8, 22, 22), (self.x - 5, self.y - 5, self.WIDTH + 10, self.WIDTH + 10), 3)
        self.function_number = func_number + 1
        func(screen, self.WIDTH, (x, y))

        self.draw = False
        self.active = False

    def update(self, event, buttons):
        x_mouse, y_mouse = pygame.mouse.get_pos()
        y_in_ar = y_mouse // 16
        x_in_ar = x_mouse // 16
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and x_mouse >= FILL_WIDTH and x_mouse <= self.x + self.WIDTH and self.y <= y_mouse and \
                    y_mouse <= self.y + self.WIDTH and self.x <= x_mouse and not self.draw:  # левая кнопка мыши
                for b in buttons:
                    if b.draw and b != self:
                        pygame.draw.rect(b.screen, (8, 22, 22), (b.x - 5, b.y - 5, b.WIDTH + 10, b.WIDTH + 10), 3)
                        b.draw = False
                self.draw = True
                pygame.draw.rect(self.screen, (50, 50, 50), (self.x - 5, self.y - 5, self.WIDTH + 10, self.WIDTH + 10),
                                 3)
            elif event.button == 1 and x_mouse < FILL_WIDTH and self.draw and (
                    y_in_ar <= 11 or y_in_ar >= 19 or x_in_ar <= 8 or x_in_ar >= 19) and (
                    y_in_ar >= 2 and y_in_ar <= 30) and (
                    x_in_ar >= 1 and x_in_ar <= 26):
                arr[y_in_ar][x_in_ar] = self.function_number
            elif event.button == 3 and x_mouse < FILL_WIDTH and not self.draw and (
                    y_in_ar <= 11 or y_in_ar >= 19 or x_in_ar <= 8 or x_in_ar >= 19) and (
                    y_in_ar >= 2 and y_in_ar <= 30) and (x_in_ar >= 1 and x_in_ar <= 26):  # левая кнопка мыши
                arr[y_in_ar][x_in_ar] = 0
            elif event.button == 3 and x_mouse >= FILL_WIDTH and self.draw:
                pygame.draw.rect(self.screen, (8, 22, 22), (self.x - 5, self.y - 5, self.WIDTH + 10, self.WIDTH + 10),
                                 3)
                self.draw = False
