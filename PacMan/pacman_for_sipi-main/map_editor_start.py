from arrays import arr
from button import Cell
import pygame
from start_game import Button


def draw_field(screen):
    n = 34
    m = 28
    for i in range(0, n):  # высота
        for j in range(0, m):  # ширина
            if arr[i][j] == 1:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 10))
            elif arr[i][j] % 100 == 0 and 32 > i > 0 and 0 < j < 32:
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 16))
                pygame.draw.rect(screen, (125, 124, 124), (j * 16, i * 16, 16, 16), 1)
            elif arr[i][j] == 2:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 13))
            elif arr[i][j] == 3:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 16, 13))
            elif arr[i][j] == 4:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 13))
            elif arr[i][j] == 5:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 13))
            elif arr[i][j] == 6:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 16, 13))
            elif arr[i][j] == 7:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 13))
            elif arr[i][j] == 8:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 16))
            elif arr[i][j] == 9:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 10, 13))
            elif arr[i][j] == 10:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 10, 13))
            elif arr[i][j] == 11:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 16))
            elif arr[i][j] == 12:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 16))
            elif arr[i][j] == 13:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, i * 16, 8, 13))
            elif arr[i][j] == 14:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 8, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), ((j * 16) + 8, i * 16, 8, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 8, (i * 16) + 3, 8, 13))
            elif arr[i][j] == 15:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), ((j * 16) + 3, (i * 16) + 3, 13, 10))
            elif arr[i][j] == 16:
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 16), 3)
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 13, 10))
            elif arr[i][j] == 17:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 3, 8, 13))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, (i * 16) + 8, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, (i * 16) + 8, 13, 8))
            elif arr[i][j] == 18:
                pygame.draw.circle(screen, (0, 0, 170), ((j * 16) + 8, (i * 16) + 8), 8, 3)
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 16, 8))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 13, 8))
                pygame.draw.rect(screen, (0, 0, 170), (j * 16, i * 16, 8, 16))
                pygame.draw.rect(screen, (0, 0, 0), (j * 16, i * 16, 8, 13))

# 1
def draw_two_lines_horizontal(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)
# 2

def draw_angular_top_left(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)

# 3

def draw_line_top(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)

# 4

def draw_angular_top_right(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y], [x + WIDTH, y + WIDTH], 3)

# 5

def draw_angular_bottom_left(screen, WIDTH, coords):
    # print(coords)
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)

# 6

def draw_line_bottom(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)

# 7

def draw_angular_bottom_right(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y + WIDTH], [x + WIDTH, y], 3)


# 8

def draw_two_parallel_vertical_lines(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y], [x + WIDTH, y + WIDTH], 3)


# 9

def draw_left_bottom_right_lines(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y], [x + WIDTH, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)

# 10

def draw_left_top_right_lines(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y], [x + WIDTH, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)


# 11

def draw_vertical_left_line(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)


# 12
def draw_vertical_right_line(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y + WIDTH], [x + WIDTH, y], 3)

# 13

def draw_rounded_angular_bottom_left(screen, WIDTH, coords):
    x, y = coords
    pi = 3.14
    pygame.draw.arc(screen, (0, 0, 170),
                    (x, y, WIDTH, WIDTH),
                    pi, 3 * pi / 2, 3)

# 14

def draw_rounded_angular_top_left(screen, WIDTH, coords):
    x, y = coords
    pi = 3.14
    pygame.draw.arc(screen, (0, 0, 170),
                    (x, y, WIDTH, WIDTH),
                    -3 * pi / 2, -pi, 3)

# 15
def draw_top_left_bottom_lines(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)

# 16 

def draw_top_right_bottom_lines(screen, WIDTH, coords):
    x, y = coords
    pygame.draw.line(screen, (0, 0, 170), [x + WIDTH, y], [x + WIDTH, y + WIDTH], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y], [x + WIDTH, y], 3)
    pygame.draw.line(screen, (0, 0, 170), [x, y + WIDTH], [x + WIDTH, y + WIDTH], 3)

# 17

def draw_rounded_angular_top_right(screen, WIDTH, coords):
    x, y = coords
    pi = 3.14
    pygame.draw.arc(screen, (0, 0, 170),
                    (x, y, WIDTH, WIDTH),
                    3 * pi / 2, 2 * pi, 3)

# 18

def draw_rounded_angular_bottom_right(screen, WIDTH, coords):
    x, y = coords
    pi = 3.14
    pygame.draw.arc(screen, (0, 0, 170),
                    (x, y, WIDTH, WIDTH),
                    0, pi / 2, 3)




def start():
    # 1 - две прямые горизонтальные
    # 2 - угол (Г образный)
    # 3 - одна прямая сверху
    # 4 - угол вверху справа
    # 5 - угол снизу слева
    # 6 - одна прямая снизу
    # 7 - угол снизу справа
    # 8 - две прямые вертикальные
    # 9 - П образная вещь
    # 10 - перевернутая П образная вещь
    # 11 - прямая вертикальная слева
    # 12 - прямая вертикальная справа
    # 13 - закругленный угол слева снизу
    # 14 - закругленный угол слева сверху
    # 15 - П образная вещь, смотрящая вправа (свободной частью)
    # 16 - П образная вещь, смотрящая влево (свободной частью)
    # 17 - закругленный угол справа сверху
    # 18 - закругленный угол справа снизу
    all_numbered_draws = [draw_two_lines_horizontal, draw_angular_top_left, draw_line_top, draw_angular_top_right,
                          draw_angular_bottom_left, draw_line_bottom,
                          draw_angular_bottom_right, draw_two_parallel_vertical_lines, draw_left_top_right_lines,
                          draw_left_bottom_right_lines, draw_vertical_left_line, draw_vertical_right_line,
                          draw_rounded_angular_bottom_left, draw_rounded_angular_top_left, draw_top_left_bottom_lines,
                          draw_top_right_bottom_lines,
                          draw_rounded_angular_bottom_right, draw_rounded_angular_top_right,
                          ]

    two_lines = [draw_two_lines_horizontal, draw_two_parallel_vertical_lines]

    lines = [draw_line_top, draw_line_bottom, draw_vertical_right_line, draw_vertical_left_line]

    angulars = [draw_angular_bottom_right, draw_angular_bottom_left, draw_angular_top_left, draw_angular_top_right]

    rounded_angulars = [draw_rounded_angular_bottom_left, draw_rounded_angular_bottom_right,
                        draw_rounded_angular_top_left, draw_rounded_angular_top_right]

    p_figures = [draw_top_left_bottom_lines, draw_top_right_bottom_lines, draw_left_bottom_right_lines,
                 draw_left_top_right_lines]

    all_of_draws = [two_lines, lines, angulars, rounded_angulars, p_figures]

    buttons = list()

    SIZE = WIDTH, HEIGHT = 748, 620



    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    x, y = 498, 100
    const_x, const_y = 448, 100
    
    for group in all_of_draws:
        x = const_x
        gap = ((WIDTH - x) - 40 * len(group)) // (len(group) + 1)
        x += gap
        for item in group:
            b = Cell(x, y, item, screen, all_numbered_draws.index(item))
            buttons.append(b)
            x += 40 + gap
        y += 40 + 40
    font = pygame.font.Font("data/fonts/Pixeboy-z8XGD.ttf", 50)
    while True:
        my_button4 = Button('    Play', WIDTH - 190, HEIGHT - 65, True, font, screen)
        my_button1 = Button('    Quit', 0, HEIGHT - 65, True, font, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

            if pygame.mouse.get_pressed()[0]:
                if my_button1.check_click():
                    pygame.quit()
                    return False
                elif my_button4.check_click():
                    pygame.quit()
                    return arr

        for button in buttons:
            button.update(event, buttons)
        draw_field(screen)
        pygame.display.update()