########################################################
### BitmapFont demo
########################################################

import pygame # for game window
from ..bitmapfont import BitmapFontFixedHeight, BitmapFontFreeDims # for bitmap font usage
import sys, pathlib

pygame.init()
pygame.display.set_caption('BitmapFont Demo - close the window for exit')
screen = pygame.display.set_mode((800, 800))

# Where to find the JSON fonts
FONT_PATH = pathlib.Path('fonts')

# Fixed Height formats fonts examples
my_first_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json', color=pygame.Color('grey'))
my_second_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json',  size=16)
my_third_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json', size=16, color=pygame.Color('purple'))
my_fourth_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'red_gradient_capital_font.json', size=16)
my_fifth_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'good_neighbours_font.json', size=32, color=pygame.Color('blue'))

# Free Dimension fonts examples
my_first_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_id1.json')
my_second_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'simple.json')
my_third_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_id5.json')
my_fourth_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_moon1.json')


while True:

    # Background
    screen.fill((128, 128, 128))

    # Second render method - blit manually
    screen.blit(my_second_fixed_height_font._render_row('Render row text'), (40, 40))

    # Third render method - blit manually multiple lines, alignment left
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + left.')[0], (60, 60))

    # Third render method - blit manually multiple lines, alignment right
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + right.', align='RIGHT')[0], (260, 60))

    # Third render method - blit manually multiple lines, alignment center
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + changed color and centered.', pygame.Color('#010101'), align='CENTER')[0], (260, 260))

    # Gradient font
    screen.blit(my_fourth_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines changed color and centered'.upper(), pygame.Color('#010101'), align='CENTER')[0], (160, 260))

    # Good Neighbours font
    screen.blit(my_fifth_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + centered.', align='CENTER')[0], (60, 260))

    # Quake fonts
    screen.blit(my_first_free_dims_font.render(f'Quake font\nIs the greatest\nanyways! + centered', align='CENTER')[0], (50, 150))
    screen.blit(my_second_free_dims_font.render(f'Quake 2 font Is the greatest anyways!', align='LEFT')[0], (0, 0))
    screen.blit(my_third_free_dims_font.render(f'Quake 3 font Is the greatest anyways!', align='LEFT')[0], (0, 30))
    screen.blit(my_fourth_free_dims_font.render(f'Quake 4 font\nIs the greatest\nanyways!', align='CENTER')[0], (0, 500))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
