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

    Example of JSON font file is below:

        {
            "font_image" : "experiments/bitmap_font/red_gradient_capital_font.png",
            "font_color" : "#FF0000",
            "colorkey" : "#000000",
            "separator_color" : "#7F7F7F",
            "character_order" : ["Aa", "Bb", "Cc", "Dd", "Ee", "Ff", "Gg", "Hh", "Ii", "Jj", "Kk", "Ll", "Mm", "Nn", "Oo", "Pp", "Qq", "Rr", "Ss", "Tt", "Uu", "Vv", "Ww", "Xx", "Yy", "Zz", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "?", " "]
        }
'''
import pygame
from . import BitmapFontProtocol, load_font_data_from_file, load_font_image, color_swap
from pathlib import Path

class BitmapFontFixedHeight(BitmapFontProtocol):
    ''' Class containing character font pictures and necessary information.
    '''

    __slots__ = ['font_height', 'font_img', 'font_color', 'colorkey', 'spacing', 'characters', 'default_char']

    def __init__(self, path: Path, size: int=None, fgcolor: pygame.Color=None, spacing: tuple[int, int]=(1,1), default_char: str='_'):
        ''' Prepare bitmap font from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the font
            :type path: str

            :param size: Size of the font in pixels. Default value is hight of the font_image file.
            :type size: int

            :param fgcolor: Color of the font. Swaps default font_color with required color. If None, the font stays as is (textured fonts).
            :type fgcolor: pygame.Color

            :param spacing: Horizontal and vertical space between the characters in px.
            :type spacing: tuple[int, int]

            :param default_char: Character to be used for the character not present in the font.
            :type default_char: str (char)

            :raise: ValueError - in case there is a problem with font initiation
        '''

        # How many pixels of space between characters
        self.spacing = spacing

        # Get font data from the file
        font_data = load_font_data_from_file(path=path)

        # Get font image based on the font data
        try:
            assert 'font_image' in font_data, f"Missing 'font_image' key."
            self.font_img = load_font_image(path=path, font_image=font_data['font_image'])
        except AssertionError:
            raise ValueError

        # Set color
        try:
            assert ('font_color' in font_data and fgcolor) or not fgcolor, f"Missing 'font_color' key."
            self.font_color = pygame.Color(font_data.get('font_color'))
        except AssertionError:
            raise ValueError

        # Set colorkey to correctly prepare the transparent parts of the font image
        try:
            self.colorkey = pygame.Color(font_data.get('colorkey', '#000000'))
            assert self.font_color != self.colorkey, 'Color cannot be the same as the color key'
        except AssertionError:
            raise ValueError

        # Set colorkey of the image - for proper transparency
        self.font_img.set_colorkey(self.colorkey)

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
        try:
            assert 'separator_color' in font_data, f"Missing 'separator_color' key."
            separator_color = pygame.Color(font_data.get('separator_color'))
        except AssertionError:
            raise ValueError

        # List of characters included in the font file in the correct order
        try:
            assert 'character_order' in font_data, f"Missing 'character_order' key."
            assert isinstance(font_data['character_order'], list) == True, f"'character_order' value must be a list."
            assert len(font_data['character_order']) > 1, f"'character_order' must not be empty list."
            character_order = font_data.get('character_order')
        except AssertionError:
            raise ValueError

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

        # Default_char is not defined in the font file, use the first font character instead
        self.default_char = default_char if default_char in self.characters else character_order[0][0]

        # Change color if required
        if fgcolor is not None:
            self.font_img = color_swap(self.font_img, self.font_color, fgcolor)

        # Scale also the font image
        self.font_img = pygame.transform.scale(self.font_img, (int(self.font_img.get_width() * scale), int(self.font_img.get_height() * scale)))

    def _get_text_width(self, text: str) -> int:
        ''' Returns width in pixels of the given text.
        It is used internally tin render function to determine the final dimensions
        of a font surface.
        '''
        # Use default_char in case that character is not contained in the font
        return sum([self.characters[char]['width'] for char in text]) + (self.spacing[0] * len(text))

    def _get_text_height(self, text: str=None) -> int:
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

    def get_metrics(self, text: str) -> list[tuple[int, int, int, int, int, int]]:
        '''Must be implemented due to compatibility with pygame.freetype.Font.
        Returns dimension of the text (min_x, max_x, min_y, max_y, horizontal_advance_x, horizontal_advance_y).
        In case of BitmapFont min_x = max_x = horizontal_advance_x = width and same for y.
        '''
        res = []
        y = self.font_height + self.spacing[1]
        
        for char in text:
            x = self.characters[char]['width'] + self.spacing[0]
            res.append((x,x,y,y,x,y))
        
        return res

    def get_rect(self, text: str) -> pygame.Rect:
        ''' Return the dimensions of the surface with generated text as a pygame.Rect.
        '''
        return pygame.Rect(
            0, 
            0, 
            max([self._get_text_width(self._substitute_unsuported_chars(row_text)) for row_text in text.split('\n')]), 
            (self._get_text_height() + self.spacing[1]) * len(text.split('\n'))
            )

    def render(self, text: str, fgcolor: pygame.Color=None, align: str='LEFT') -> tuple[pygame.Surface, pygame.Rect]:
        ''' Renders given text in given color and in given
        alignment to the new surface.
        '''

        assert fgcolor != self.colorkey, 'Color cannot be the same as the color key'

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
            if fgcolor is not None:
                final_surface = color_swap(final_surface, self.font_color, fgcolor)

        # Must set colorkey otherwise background will not be transparent
        final_surface.set_colorkey(self.colorkey)

        return (final_surface, pygame.Rect(0, 0, max_width, height))
