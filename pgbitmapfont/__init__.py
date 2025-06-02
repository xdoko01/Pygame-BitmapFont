''' Module for handling bitmap fonts

    Bitmap font is defined by picture and json definition. Picture needs to be in
    non-data-loss format (png/bmp).

    For the definition of the JSON files see individual fonts in separate Python 
    files.

    For creation of the font from the image, you can use the Extractor tool from
    the 'tools' folder.

    All bitmap fonts must implement the BitmapFont prototype in order to be used
    interchangibly.
'''
########################################################
### Prototype class
########################################################
import pygame
from typing import Protocol
from pathlib import Path


class BitmapFontProtocol(Protocol):
    """Interface all bitmap fonts must implement"""
    def __init__(self, path: Path, size: int):
        pass

    def get_metrics(self, text: str) -> list[tuple[int, int, int, int, int, int]]:
        pass

    def get_rect(self, text: str) -> pygame.Rect:
        pass

    def render(self, text: str, fgcolor: pygame.Color) -> tuple[pygame.Surface, pygame.Rect]:
        pass

########################################################
### Internal Package functions
########################################################
import json # For reading the JSON font definition
import re # For removing C-style comments before processing JSON

def clip(surf: pygame.Surface, x: int, y: int, x_size: int, y_size: int) -> pygame.Surface:
    """Get defined surface from the larger surface."""

    handle_surf = surf.copy()
    clip_rect = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())

    return image.copy()

def color_swap(surf: pygame.Surface, old_color: pygame.Color, new_color: pygame.Color) -> pygame.Surface:
    """Swap one color to other color in the image."""

    # Create new empty surface and fill it with the new color
    img_copy = pygame.Surface(surf.get_size())
    img_copy.fill(new_color)

    # Set transparency on the old surface on the old color
    surf.set_colorkey(old_color)

    # Blit the old image to the new surface - as old color is transparent, colors are swaped
    img_copy.blit(surf, (0, 0))

    return img_copy

def load_font_data_from_file(path: str) -> dict:
    """Load the data from json to dictionary."""

    # Open the font json file
    try:
        with open(path, 'r') as font_file:
            json_font_data = font_file.read()
            font_data = json.loads(re.sub("//.*", "", json_font_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
            return font_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Bitmap font definition file '{path}' was not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in font data file: {path}")
    except Exception as e:
        raise Exception(f"Error loading font data: {e}")


def load_font_image(path: str, font_image: str) -> pygame.Surface:
    """Load the texture image from the file."""

    # Evaluate the font image path
    font_image_path = Path(path.parent, font_image).resolve() # Try to evaluate as relative to font file path

    if not font_image_path.is_file():
        font_image_path = Path(font_image) # If not successful evaluate as relative to py project path

    assert font_image_path.is_file() == True, f"Cannot find font image file at '{font_image_path}'."

    return pygame.image.load(font_image_path).convert()

########################################################
### Public Package classes
########################################################
__all__ = ['BitmapFontFixedHeight', 'BitmapFontFreeDims', 'BitmapFont']

from .bitmapfont_fixed_height import BitmapFontFixedHeight
from .bitmapfont_free_dims import BitmapFontFreeDims

class BitmapFont:
    """
    A factory class that automatically detects the bitmap font format
    and creates an instance of the appropriate font rendering class.
    """
    def __new__(cls, path: Path, size: int=None, spacing: tuple[int, int]=(0,0), fgcolor: pygame.Color=None, default_char: str='_', **kwargs):

        font_data = load_font_data_from_file(path=path)

        if 'character_order' in font_data:
            instance = super().__new__(BitmapFontFixedHeight)
            instance.__init__(path=path, size=size, spacing=spacing, fgcolor=fgcolor, default_char=default_char)
            return instance
        else:
            instance = super().__new__(BitmapFontFreeDims)
            instance.__init__(path=path, size=size, spacing=spacing, fgcolor=fgcolor, default_char=default_char)
            return instance
