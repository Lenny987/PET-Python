import pygame

'''
function for game over screen
'''


def game_over_screen():
    pygame.init()
    pygame.font.init()
    WIDTH = 800
    HEIGHT = 600
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    fps = 60
    timer = pygame.time.Clock()
    font = pygame.font.Font("data/fonts/Pixeboy-z8XGD.ttf", 70)
    font2 = pygame.font.Font('data/fonts/Pixeboy-z8XGD.ttf', 150)
    pygame.display.set_caption("Pacman")

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
            button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (250, 65))
            pygame.draw.rect(screen, 'black', button_rect, 0, 5)
            pygame.draw.rect(screen, 'white', button_rect, 2, 5)
            screen.blit(button_text, (self.x_pos + 3, self.y_pos + 3))

        def check_click(self):
            mouse_pos = pygame.mouse.get_pos()
            left_click = pygame.mouse.get_pressed()[0]
            button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (250, 65))
            if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
                return True
            else:
                return False

    global game_over
    game_over = True
    BG = Background('data/images/background_images/backgroundpicture.jpg', [0, 0])
    while game_over:
        pygame.display.set_caption("Game Over")
        game_over_message = "Game Over"
        ts = font2.render(game_over_message, False, (255, 255, 255))
        screen.fill([255, 255, 255])
        screen.blit(BG.image, BG.rect)
        timer.tick(fps)
        my_button1 = Button('Record', 275, 530, True, font, screen)
        my_button2 = Button('  Menu', 540, 530, True, font, screen)
        my_button3 = Button('Retry', 10, 530, True, font, screen)
        screen.blit(ts, (110, 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'stop'
            if pygame.mouse.get_pressed()[0]:
                if my_button2.check_click():
                    pygame.quit()
                    return 'menu'
                if my_button3.check_click():
                    pygame.quit()
                    return 'retry'
                if my_button1.check_click():
                    pygame.quit()
                    return 'record'
