''' Module for handling bitmap fonts

    Bitmap font is defined by picture and json definition. Picture needs to be in
    non-data-loss format (png/bmp). All characters are on one row and are delimited
    by pixel on the first row that is in specified color (separator_color). The JSON
    definition of the font specifies information needed for font initiation and
    rendering, i.e.

        - font_image - Specifies path to the bitmap picture with the font. It can be either path relative to the font's
            JSON file or path relative to the project (CWD directory).

        - font_color - Specifies the color of the font. It is used when the user
            wants to change the color of the font (substitute font_color by other
            color). The value is only used in case that color attribute is present when instance
            of the font is created. Otherwise, the font images are used as they are.

        - colorkey - Specifies the background color of the font. It is needed for
            keying-out the color in the font image.

        - separator_color - Specifies the color of the pixel that is used to separate
            individual font characters in the font_image file.

        - character_order - Specifies list of characters in the same order that those
            are present in the font_image file. It is used to map the correct images to correct
            letters. character_order values can have several characters. In example below, value "Aa" means
            that the first character image in font_image file will be assign to letter "A" and
            also to letter "a". This is useful in case font is missing for example lower case
            characters.

        - spacing - Specifies space between text characters in pixels (horizontal/vertical)

    Example of JSON font file is below:

        {
            "font_image" : "experiments/bitmap_font/red_gradient_capital_font.png",
            "font_color" : "#FF0000",
            "colorkey" : "#000000",
            "separator_color" : "#7F7F7F",
            "character_order" : ["Aa", "Bb", "Cc", "Dd", "Ee", "Ff", "Gg", "Hh", "Ii", "Jj", "Kk", "Ll", "Mm", "Nn", "Oo", "Pp", "Qq", "Rr", "Ss", "Tt", "Uu", "Vv", "Ww", "Xx", "Yy", "Zz", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "?", " "],
            "spacing" : [1, 1]
        }
'''

__all__ = ['BitmapFont', 'BitmapFont2']

import pygame # For picture manipulation
import json # For reading the JSON font definition
import re # For removing C-style comments before processing JSON
from pathlib import Path

########################################################
### Module functions
########################################################

def clip(surf, x, y, x_size, y_size):
    ''' Get defined surface from the larger surface
    '''
    handle_surf = surf.copy()
    clip_rect = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())

    return image.copy()

def color_swap(surf, old_color, new_color):
    ''' Swap one color to other color in the image
    '''

    # Create new empty surface and fill it with the new color
    img_copy = pygame.Surface(surf.get_size())
    img_copy.fill(new_color)

    # Set transparency on the old surface on the old color
    surf.set_colorkey(old_color)

    # Blit the old image to the new surface - as old color is transparent, colors are swaped
    img_copy.blit(surf, (0, 0))

    return img_copy

def load_font_data_from_file(path: Path) -> dict:
    """Load the data from json to dictionary."""

    # Open the font json file
    try:
        with open(path, 'r') as font_file:
            json_font_data = font_file.read()
            font_data = json.loads(re.sub("//.*", "", json_font_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
    except FileNotFoundError:
        print(f"Bitmap font definition file '{path}' was not found.")
        raise ValueError
    
    return font_data

def load_font_image(path: Path, font_image: str) -> pygame.Surface:
    """Load the texture image from the file."""

    # Evaluate the font image path
    font_image_path = Path(path.parent, font_image).resolve() # Try to evaluate as relative to font file path

    if not font_image_path.is_file():
        font_image_path = Path(font_image) # If not successful evaluate as relative to py project path

    assert font_image_path.is_file() == True, f'Cannot find font image file at "{font_image_path}"'

    return pygame.image.load(font_image_path).convert()

########################################################
### Module classes
########################################################
class BitmapFont2():
    '''Implementation of bitmap font using reference to the texture with characters in bitmap file and 
    json file specifiing position and dimension of individual font characters.
    '''

    __slots__ = ['font_height', 'font_img', 'colorkey', 'spacing', 'characters']

    def __init__(self, path: str, size: int=None, spacing: tuple[int, int]=(0,0)):
        ''' Prepare bitmap font from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the font
            :type path: str

            :param size: Size is scale factor of the whole font
            :type size: int

            :param spacing: Horizontal and vertical space between the characters in px.
            :type spacing: tuple[int, int]

            :raise: ValueError - in case there is a problem with font initiation
        '''

        # Get font data from the file
        font_data = load_font_data_from_file(path=Path(path))

        # Get font image based on the font data
        self.font_img = load_font_image(path=Path(path), font_image=font_data['font_image'])

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

    def _render_row(self, text: str) -> pygame.Surface:
        ''' Returns surface containing text in a row.
        It is used internally to render the final wrapped text surface
        '''

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

    def get_text_dim(self, text: str) -> tuple[int, int]:
        ''' Return the dimensions of the surface with generated text
        '''
        return (max([self._get_text_width(row_text) for row_text in text.split('\n')]), (self._get_text_height() + self.spacing[1]) * len(text.split('\n')))

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

        return (final_surface, pygame.Rect(width=max_width, height=height))


class BitmapFont():
    ''' Class containing character font pictures and necessary information.
    '''

    __slots__ = ['font_height', 'font_img', 'font_color', 'colorkey', 'spacing', 'characters']

    def __init__(self, path: str, size: int=None, color: pygame.Color=None, spacing: tuple[int, int]=(1,1)):
        ''' Prepare bitmap font from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the font
            :type path: str

            :param size: Size of the font in pixels. Default value is hight of the font_image file.
            :type size: int

            :param color: Color of the font. Swaps default font_color with required color. If None, the font stays as is (textured fonts).
            :type color: pygame.Color

            :param spacing: Horizontal and vertical space between the characters in px.
            :type spacing: tuple[int, int]

            :raise: ValueError - in case there is a problem with font initiation
        '''

        # Get font data from the file
        font_data = load_font_data_from_file(path=Path(path))

        # Get font image based on the font data
        self.font_img = load_font_image(path=Path(path), font_image=font_data['font_image'])

        # Set color
        self.font_color = pygame.Color(font_data.get('font_color'))

        # Set colorkey to correctly prepare the transparent parts of the font image
        try:
            self.colorkey = pygame.Color(font_data.get('colorkey', '#000000'))
            assert self.font_color != self.colorkey, 'Color cannot be the same as the color key'
        except AssertionError:
            raise ValueError
        
        # Set colorkey of the image - for proper transparency
        self.font_img.set_colorkey(self.colorkey)

        # How many pixels of space between characters
        self.spacing = spacing

        # Store the original font height
        font_height = self.font_img.get_height()

        # Calculate the scaling factor for the font size
        scale = 1 if size is None else size / font_height

        # Store the scaled font height
        self.font_height = int(font_height * scale)

        #####
        # Store the coordinates and dimensions of the scaled characters
        #####

        # Get the color that is separating the individual characters in the char image
        separator_color = pygame.Color(font_data.get('separator_color'))

        # List of characters included in the font file in the correct order
        character_order = font_data.get('character_order')

        # Store the char img coordinates and dimensions in the original img file
        self.characters = dict()

        # Keep track of witdh of the current character and number of characters
        current_char_width = 0
        character_count = 0

        # Iterate the font image column by column
        for x in range(self.font_img.get_width()):

            # Read the column color and check if encountered the separation bar/pixel - start of the character was found
            if self.font_img.get_at((x, 0)) == separator_color:

                # Get the coords and dim of the found character - for every character in the string, i.e "Aa" means 2 records, one for 'A' and second for 'a'
                for char in character_order[character_count]:
                    # Create a new record in the dictionary
                    self.characters[char] = dict()
                    self.characters[char]['x'] = int((x - current_char_width) * scale)
                    self.characters[char]['y'] = int(0)
                    self.characters[char]['width'] = int(current_char_width * scale)
                    self.characters[char]['height'] = int(font_height * scale)

                character_count += 1
                current_char_width = 0 # reset the counter of char width

            else:
                current_char_width += 1 # count aditional pixel for char width

        # Change color if required
        if color is not None:
            self.font_img = color_swap(self.font_img, self.font_color, color)

        # Scale also the font image
        self.font_img = pygame.transform.scale(self.font_img, (int(self.font_img.get_width() * scale), int(self.font_img.get_height() * scale)))

    def _get_text_width(self, text: str) -> int:
        ''' Returns width in pixels of the given text.
        It is used internally tin render function to determine the final dimensions
        of a font surface.
        '''
        return sum([self.characters.get[char]['width'] for char in text]) + (self.spacing[0] * len(text))

    def _get_text_height(self, text: str=None) -> int:
        ''' Returns height in pixels of the given text
        '''
        return self.font_height

    def _render_row(self, text: str) -> pygame.Surface:
        ''' Returns surface containing text in a row.
        It is used internally to render the final wrapped text surface
        '''

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

    def get_text_dim(self, text: str) -> tuple[int, int]:
        ''' Return the dimensions of the surface with generated text
        '''
        return (max([self._get_text_width(row_text) for row_text in text.split('\n')]), (self._get_text_height() + self.spacing[1]) * len(text.split('\n')))

    def render(self, text: str, color: pygame.Color=None, align: str='LEFT') -> tuple[pygame.Surface, pygame.Rect]:
        ''' Renders given text in given color and in given
        alignment to the new surface.
        '''

        assert color != self.colorkey, 'Color cannot be the same as the color key'

        # Generate each row on a separate surface
        rows_surfaces = []
        max_width = 0

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

            # Change color as required
            if color is not None:
                final_surface = color_swap(final_surface, self.font_color, color)

        # Must set colorkey otherwise background will not be transparent
        final_surface.set_colorkey(self.colorkey)

        return (final_surface, pygame.Rect(width=max_width,height=height))
