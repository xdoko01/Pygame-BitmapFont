''' Module for handling bitmap fonts

    Bitmap font is defined by picture and json definition. Picture needs to be in
    non-data-loss format (png/bmp). 

    Charactes are defined in a JSON file by the reference to image containing
    the characters, coords and dimensions of the given character on the image.

        - font_image - Specifies path to the bitmap picture with the font. It can be either path relative to the font's
            JSON file or path relative to the project (CWD directory).

        - colorkey - Specifies the background color of the font image. It is needed for
            keying-out the color in the font image.

        - chars- Specifies dictionary where Key is the character and values are coords and dims on the font_image picture.

    Example of JSON font file is below:

{
    "font_image": "charset_id1.png",
    "colorkey": "#000000",
    "chars": {
        "A": {
            "width": 16,
            "height": 16,
            "x": 16,
            "y": 192
        },
        "a": {
            "width": 16,
            "height": 16,
            "x": 16,
            "y": 192
        },
        "B": {
            "width": 16,
            "height": 16,
            "x": 32,
            "y": 192
        ...
'''
import pygame
from . import BitmapFontProtocol, load_font_data_from_file, load_font_image
from pathlib import Path

class BitmapFontFreeDims(BitmapFontProtocol):
    '''Implementation of bitmap font using reference to the texture with characters in bitmap file and 
    json file specifiing position and dimension of individual font characters.
    '''

    __slots__ = ['font_height', 'font_img', 'colorkey', 'spacing', 'characters', 'default_char']

    def __init__(self, path: Path, size: int=None, spacing: tuple[int, int]=(0,0), default_char: str='_'):
        ''' Prepare bitmap font from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the font
            :type path: str

            :param size: Size is scale factor of the whole font
            :type size: int

            :param spacing: Horizontal and vertical space between the characters in px.
            :type spacing: tuple[int, int]

            :param default_char: Character to be used for the character not present in the font.
            :type default_char: str (char)

            :raise: ValueError - in case there is a problem with font initiation
        '''

        # Get font data from the file
        font_data = load_font_data_from_file(path=path)

        # Get font image based on the font data
        self.font_img = load_font_image(path=path, font_image=font_data['font_image'])

        # Get colorkey to correctly prepare the transparent parts of the font image
        self.colorkey = pygame.Color(font_data.get('colorkey', '#000000'))

        # Set colorkey - for proper transparency
        self.font_img.set_colorkey(self.colorkey)

        # How many pixels of space between characters
        self.spacing = spacing

        # Store the original font height
        font_height = max(font_data['chars'][char]['height'] for char in font_data['chars'])

        # Calculate the scaling factor for the font size
        scale = 1 if size is None else size / font_height

        # Store the scaled font height
        self.font_height = int(font_height * scale)

        # Store the coordinates and dimensions of the scaled characters
        self.characters = dict()
        for char, char_info in font_data['chars'].copy().items():
            self.characters[char] = dict()
            self.characters[char]['x'] = int(char_info['x'] * scale)
            self.characters[char]['y'] = int(char_info['y'] * scale)
            self.characters[char]['width'] = int(char_info['width'] * scale)
            self.characters[char]['height'] = int(char_info['height'] * scale)

        # Default_char is not defined in the font file, use the first font character instead
        self.default_char = default_char if default_char in self.characters else next(iter(self.characters))

        # Scale also the font image
        self.font_img = pygame.transform.scale(self.font_img, (int(self.font_img.get_width() * scale), int(self.font_img.get_height() * scale)))

    def _get_text_width(self, text: str) -> int:
        ''' Returns width in pixels of the given text.
        It is used internally in render function to determine the final dimensions
        of a font surface.
        '''
        return sum([self.characters[char]['width'] for char in text]) + (self.spacing[0] * len(text))

    def _get_text_height(self, text: str=None)-> int:
        ''' Returns height in pixels of the given text
        '''
        return self.font_height

    def _substitute_unsuported_chars(self, text: str) -> str:
        '''Cleans the text from characters that are not supported
        by the font and substitutes them with the default character.
        '''
        return ''.join(list(map(lambda c: c if c in self.characters else self.default_char, text)))

    def _render_row(self, text: str) -> pygame.Surface:
        ''' Returns surface containing text in a row.
        It is used internally to render the final wrapped text surface
        '''

        # Clear the text from not covered characters
        text = self._substitute_unsuported_chars(text)

        # Prepare empty surface
        row_surf = pygame.Surface((self._get_text_width(text), self._get_text_height(text)))

        # Fill the surface with the font background color
        row_surf.fill(self.colorkey)

        # Blit the text onto the surface
        x_offset = 0

        for char in text:
            try:
                # Get the part of the font_img with the right character
                char_data = self.characters[char]
                char_rect = pygame.Rect(char_data['x'], char_data['y'], char_data['width'], char_data['height'])
                row_surf.blit(self.font_img, (x_offset, 0), char_rect) # blit only part of the font_img containing the character
                x_offset += char_data['width'] + self.spacing[0]
            except KeyError:
                # Skip if the character is not defined by the font
                pass

        return row_surf

    def get_rect(self, text: str) -> pygame.Rect:
        ''' Return the dimensions of the surface with generated text as a pygame Rect.
        '''
        return pygame.Rect(
            0,
            0,
            max([self._get_text_width(self._substitute_unsuported_chars(row_text)) for row_text in text.split('\n')]), 
            (self._get_text_height() + self.spacing[1]) * len(text.split('\n'))
        )

    def render(self, text: str, align: str='LEFT') -> tuple[pygame.Surface, pygame.Rect]:
        ''' Renders given text in given color and in given
        alignment to the new surface.
        '''

        # Generate each row on a separate surface
        rows_surfaces = []
        max_width = 0 # Store the width of the longest line

        # Prepare individual surface for every row
        for row_text in text.split('\n'):

            # Generate the row surface
            row_surf = self._render_row(row_text)

            # Update the max row width value
            max_width = max(max_width, row_surf.get_width())

            # Add to the list of row surfaces
            rows_surfaces.append(row_surf)
        
        # Store the height of the whole text surface
        height = (self._get_text_height() + self.spacing[1]) * len(rows_surfaces)

        # Generate the new surface
        final_surface = pygame.Surface((max_width, height))

        # Fill the surface with the font background color
        final_surface.fill(self.colorkey)

        for i, row_surface in enumerate(rows_surfaces):

            # Horizontal alignment
            if align == 'LEFT':
                x_align = 0
            elif align == 'RIGHT':
                #x_align = text_dim[0] - row_surface.get_width()
                x_align = max_width - row_surface.get_width()

            elif align in ['CENTER', 'CENTRE']:
                #x_align = (text_dim[0] - row_surface.get_width()) // 2
                x_align = (max_width - row_surface.get_width()) // 2

            else:
                x_align = 0

            final_surface.blit(row_surface, (x_align, i * (self._get_text_height() + self.spacing[1])))

        # Must set colorkey otherwise background will not be transparent
        final_surface.set_colorkey(self.colorkey)

        return (final_surface, pygame.Rect(0, 0, max_width, height))


