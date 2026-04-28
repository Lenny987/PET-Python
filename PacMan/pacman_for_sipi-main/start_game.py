import sys

import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Button:
    def __init__(self, text, x_pos, y_pos, enabled, font, screen):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled
        self.font = font
        self.draw(screen)

    def draw(self, screen):
        button_text = self.font.render(self.text, True, 'white')
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (190, 65))
        pygame.draw.rect(screen, 'black', button_rect, 0, 5)
        pygame.draw.rect(screen, 'white', button_rect, 2, 5)
        screen.blit(button_text, (self.x_pos + 3, self.y_pos + 3))

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (200, 65))
        if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False


def start():
    pygame.init()
    pygame.font.init()
    WIDTH = 800
    HEIGHT = 600
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    fps = 60
    timer = pygame.time.Clock()
    pygame.display.set_caption("Pacman")
    pygame.display.set_caption("Menu")
    run = True
    font = pygame.font.Font("data/fonts/Pixeboy-z8XGD.ttf", 50)
    font2 = pygame.font.Font("data/fonts/Pixeboy-z8XGD.ttf", 165)
    BG = Background('data/images/background_images/backgroundpicture.jpg', [0, 0])

    while run:
        title = "Pacman"
        ts1 = font2.render(title, False, (255, 255, 255))
        screen.blit(BG.image, BG.rect)

        timer.tick(fps)
        my_button1 = Button('      Exit', 5, 530, True, font, screen)
        my_button2 = Button('   Rating', 207, 530, True, font, screen)
        my_button3 = Button('Settings', 409, 530, True, font, screen)
        my_button4 = Button('    Start', 611, 530, True, font, screen)
        my_button5 = Button('   Editor', 409, 455, True, font, screen)

        screen.blit(ts1, (90, 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if pygame.mouse.get_pressed()[0]:
                if my_button1.check_click():
                    run = False
                    pygame.quit()
                    return 'exit'
                elif my_button4.check_click():
                    run = False
                    pygame.quit()
                    return 'game'
                elif my_button2.check_click():
                    pygame.quit()
                    return 'leaderboard'
                elif my_button3.check_click():
                    pygame.quit()
                    return 'settings'
                elif my_button5.check_click():
                    pygame.quit()
                    return 'editor'


if __name__ == '__main__':
    start()