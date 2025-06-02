########################################################
### BitmapFont demo
########################################################

#from ..bitmapfont import BitmapFontFixedHeight, BitmapFontFreeDims # for bitmap font usage
# If running directly from the repo for testing, you might need to adjust sys.path:
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pgbitmapfont import BitmapFontFreeDims, BitmapFontFixedHeight, BitmapFont # Or from bitmapfont.bitmapfont import BitmapFont

import pygame # for game window
import pathlib

pygame.init()
pygame.display.set_caption('Pygame-BitmapFont Demo - close the window for exit')
screen = pygame.display.set_mode((800, 800))

# Where to find the JSON fonts
FONT_PATH = pathlib.Path('examples/fonts')

# Fixed Height formats fonts examples
my_first_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json', fgcolor=pygame.Color('grey'))
my_second_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json',  size=16)
my_third_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'small_font.json', size=8, fgcolor=pygame.Color('brown'))
my_fourth_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'red_gradient_capital_font.json', size=16, spacing=(2,5))
my_fifth_fixed_height_font = BitmapFontFixedHeight(path=FONT_PATH / 'good_neighbours_font.json', size=32, fgcolor=pygame.Color('orange'))

# Free Dimension fonts examples
my_first_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_id1.json')
my_second_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'simple.json', fgcolor=(255,255,255))
my_third_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_id5.json')
my_fourth_free_dims_font = BitmapFontFreeDims(path=FONT_PATH / 'charset_moon1.json')

bm_font1 = BitmapFont(path=FONT_PATH / 'small_font.json', fgcolor=pygame.Color('green'), size=32, spacing=(1,1))
bm_font2 = BitmapFont(path=FONT_PATH / 'charset_id1.json', size=40)


while True:

    # Background
    screen.fill((128, 128, 128))

    #BitmapFonts - created by Factory BitmapFont class
    screen.blit(bm_font1.render(f'bm_font1\nsized to 32px\naligned right', align='RIGHT')[0], (570, 370))
    screen.blit(bm_font2.render(f'bm_font2\nsized to 64px\naligned to center', align='CENTER')[0], (10, 650))
    
    # Third render method - blit manually multiple lines, alignment left
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + left.')[0], (410, 160))

    # Third render method - blit manually multiple lines, alignment right
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + right.', align='RIGHT')[0], (710, 160))

    # Third render method - blit manually multiple lines, alignment center
    screen.blit(my_third_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + changed color and centered.', pygame.Color('#010101'), align='CENTER')[0], (510, 160))

    # Gradient font
    screen.blit(my_fourth_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines changed color and centered'.upper(), pygame.Color('#010101'), align='CENTER')[0], (420, 260))

    # Good Neighbours font
    screen.blit(my_fifth_fixed_height_font.render(f'Render text\nthat is rendered\nonto multiple\nlines + centered.', align='CENTER')[0], (20, 300))

    # Quake fonts
    screen.blit(my_first_free_dims_font.render(f'Quake font\nIs the greatest\nanyways! + centered', align='CENTER')[0], (50, 150))
    screen.blit(my_second_free_dims_font.render(f'Quake 2 font Is the greatest anyways!', align='LEFT')[0], (10, 10))
    screen.blit(my_third_free_dims_font.render(f'Quake 3 font Is the greatest anyways!', align='LEFT')[0], (10, 30))
    screen.blit(my_fourth_free_dims_font.render(f'Quake 4 font\nIs the greatest\nanyways!', align='CENTER')[0], (10, 500))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
