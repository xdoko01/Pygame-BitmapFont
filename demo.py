########################################################
### BitmapFont demo
########################################################

import pygame # for game window
from bitmap_font import BitmapFont # for bitmap font usage
import sys, pathlib

pygame.init()
pygame.display.set_caption('BitmapFont Demo - close the window for exit')
screen = pygame.display.set_mode((500, 500), 0, 32)

# Where to find the JSON fonts
FONT_PATH = pathlib.Path('fonts')

# One way to init font
my_first_font = BitmapFont(path=FONT_PATH / 'small_font.json', color=pygame.Color('grey'))

# Other way to init font (size included)
my_second_font = BitmapFont(path=FONT_PATH / 'small_font.json',  size=16)

# Yet another way ti init font (color included)
my_third_font = BitmapFont(path=FONT_PATH /'small_font.json', size=16, color=pygame.Color('purple'))

# Yet another font - gradient
my_fourth_font = BitmapFont(path=FONT_PATH /'red_gradient_capital_font.json', size=35)

# Yet another font - good neighbours
my_fifth_font = BitmapFont(path=FONT_PATH /'good_neighbours_font.json', size=32, color=pygame.Color('blue'))

while True:

    # Background
    screen.fill((128, 128, 128))

    # Second render method - blit manually
    screen.blit(my_second_font._render_row('Render row text'), (40, 40))

    # Third render method - blit manually multiple lines, alignment left
    screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.'), (60, 60))

    # Third render method - blit manually multiple lines, alignment right
    screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', align='RIGHT'), (260, 60))

    # Third render method - blit manually multiple lines, alignment center
    screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', pygame.Color('#010101'), align='CENTER'), (260, 260))

    # Gradient font
    screen.blit(my_fourth_font.render(f'Render text\nthat is rendered\nonto multiple\nlines'.upper(), pygame.Color('#010101'), align='CENTER'), (160, 260))

    # Good Neighbours font
    screen.blit(my_fifth_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', align='CENTER'), (60, 260))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
