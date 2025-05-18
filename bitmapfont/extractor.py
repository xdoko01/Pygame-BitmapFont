########################################################
### Extractor - prepare font in the suitable format
###  - take fixed font picture
###    - enter parameters of the whole charset and one character
###  - define which characters to extract
###    - define from - to range or list of tuples to generate
###    - [('Aa', (5,5))]
###  - define the background color and separator
###  - construct the new picture with font and the json descriptive file
###  - alternative descriptive json creation
###    {
###         'A': {x: 150, y:150, dx:16, dy:16},
###         'a': {x: 150, y:150, dx:16, dy:16}
###    }
###
###    TODO: Tab button will go through the grit from top left to bottom down
########################################################
import pygame
from dataclasses import dataclass

@dataclass(frozen=True)
class Vect:
    """Dataclass holding info about vector."""
    x: int
    y: int

def clip(surf, pos: tuple, size: tuple):
    """Get defined surface from the larger surface."""
    handle_surf = surf.copy()
    clip_rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def get_screen_cell_res_px(screen: pygame.Surface, grid_cnt: Vect) -> Vect:
    """Calculate the resolution of a grid cell on the screen."""
    return Vect(screen.get_width() / grid_cnt.x, screen.get_height() / grid_cnt.y)

def get_cell_pos_from_mouse(mouse_pos: Vect, screen_cell_res_px: Vect) -> Vect:
    """Convert mouse position to grid cell position."""
    return Vect(int(mouse_pos.x // screen_cell_res_px.x), int(mouse_pos.y // screen_cell_res_px.y))

def get_img_topleft_cell_pos_from_cell_px(cell_pos: Vect, img_cell_res_px: int) -> Vect:
    """Get the top-left pixel position of a cell in the image."""
    return Vect(cell_pos.x * img_cell_res_px, cell_pos.y * img_cell_res_px)

def get_screen_topleft_cell_pos_from_cell_px(cell_pos: Vect, screen_cell_res_px: int) -> Vect:
    """Get the top-left position of a cell on the screen."""
    return Vect(int(cell_pos.x * screen_cell_res_px.x), int(cell_pos.y * screen_cell_res_px.y))

def get_screen_topleft_cell_pos_from_mouse_px(mouse_pos: Vect, screen_cell_res_px: Vect) -> Vect:
    """Get the top-left pixel position of a cell on the screen on which mouse is located."""
    return Vect(int((mouse_pos.x // screen_cell_res_px.x) * screen_cell_res_px.x), int((mouse_pos.y // screen_cell_res_px.y) * screen_cell_res_px.y))

def get_char_img_from_cell_selection(font_img: pygame.Surface, img_cell_res_px: int, sel_start_cell: Vect, sel_finish_cell: Vect) -> tuple[pygame.Surface, pygame.Rect]:
    """Get the character image from font texture given the start and end cell"""
    selection_most_topleft_cell = Vect(min(sel_start_cell.x, sel_finish_cell.x), min(sel_start_cell.y, sel_finish_cell.y))
    selection_most_botomright_cell = Vect(max(sel_start_cell.x, sel_finish_cell.x), max(sel_start_cell.y, sel_finish_cell.y))

    selection_cell_length = Vect(selection_most_botomright_cell.x - selection_most_topleft_cell.x+1, selection_most_botomright_cell.y - selection_most_topleft_cell.y+1)
    selection_img_topleft_px = get_img_topleft_cell_pos_from_cell_px(selection_most_topleft_cell, img_cell_res_px)

    return (
        clip(font_img, (selection_img_topleft_px.x, selection_img_topleft_px.y), (selection_cell_length.x * img_cell_res_px, selection_cell_length.y * img_cell_res_px)),
        pygame.Rect(selection_img_topleft_px.x, selection_img_topleft_px.y, selection_cell_length.x * img_cell_res_px, selection_cell_length.y * img_cell_res_px)
    )


# Create an ArgumentParser object for processing the input
import argparse
parser = argparse.ArgumentParser(description="Process command-line arguments.")
parser.add_argument("--img", type=str, help="Image with font characters", required=False) 
parser.add_argument("--out", type=str, help="Output JSON file", required=False)
args = parser.parse_args()

# Get from input line
FONT_IMG = args.img if args.img else 'fonts/charset_moon1.png'
FONT_JSON = args.out if args.out else FONT_IMG.split('/')[-1].split('.')[0] + '.jsonx'
IMG_CELL_RES_PX = 16 # resolution of the grid cell on the original image
COLORKEY_PIXEL_LOCATION = (0,0)

POSITION_CELL_COLOR = (255,0,0,128) # Color of cell on which the cursor is located
SELECTION_CELL_COLOR = (0,255,0,128) # Color of cells selected by mouse
SAVED_CELL_COLOR = (128,128,128,128) # Color for already saved cells into the font file

TEXT_COLOR = (255,0,0,128)
TEXT_SIZE = 20

GRID_COLOR = (0,255,0,128)

HELP_TEXT = \
'''Help
1. Select the suitable grid resolution by 'PgUp', 'PgDown'
2. Select the cell with texture by mouse and/or cursor keys
3. Press INSERT to save the texture details into JSON
Tips
 - once saved, the cell is grey
Enjoy!
'''
# Init pygame window
pygame.init()

# Load the image with font with fixed dim
font_img = pygame.image.load(FONT_IMG)

# Set the resolution of the window so that it fits the picture
screen = pygame.display.set_mode(font_img.get_size(), flags=pygame.RESIZABLE)

# Get the aspect ratio of the font image
img_aspect_ratio = font_img.get_width() / font_img.get_height()

# Get the colorkey of the image - get it from the most topleft pixel
colorkey = font_img.get_at(COLORKEY_PIXEL_LOCATION)

# Set the transparency based on the colorkey
font_img.set_colorkey(colorkey)

# Screen size
screen_size = Vect(screen.get_width(), screen.get_height())

# Calculate the resolution of the grid
grid_cnt: int = None # Number of horizontal and vertical grid lines to display
screen_cell_res_px: int = None # Size of the grid cell on screen in px
is_cell_res_changed: bool = True # Remember if the IMG_CELL_RES_PX has been changed

# Semi-transparent surface for position
cell_pos_rect_surface: pygame.Surface = None

# Semi-transparent surface for selection
cell_sel_rect_surface: pygame.Surface = None

# Semi-transparent surface for already saved cells
cell_save_rect_surface: pygame.Surface = None

# Surface for character
char_img: pygame.Surface = None
char_img_dim: pygame.Rect = None

# Create a font object
font = pygame.font.Font(None, TEXT_SIZE)  # None means default font, 74 is the font size

# Show help
show_help: bool = False

# Render the help text
help_text_surf = font.render(HELP_TEXT, True, TEXT_COLOR)

# Cell where mouse is/was located
cell_pos_from_mouse: Vect = None
cell_pos_from_mouse_old: Vect = None

# Remember selection of cells
is_selection: bool = False
sel_start_cell: Vect = None
sel_finish_cell: Vect = None

# Dictionary for saving extracted char images
font_dict: dict = {}

# Remember saved cells
saved: set = set()

while True:

    ###################################
    # Recalculate if change was done
    ###################################

    # Recalculate grid if IMG_CELL_RES_PX resolution has changed
    if is_cell_res_changed:
        
        # Recalculate Grid variables
        grid_cnt = Vect(font_img.get_width() // IMG_CELL_RES_PX, font_img.get_height() // IMG_CELL_RES_PX)
        screen_cell_res_px = get_screen_cell_res_px(screen, grid_cnt)

        # Recalculate the surfaces for marking the cells
        # Semi-transparent surface for position
        cell_pos_rect_surface = pygame.Surface((screen_cell_res_px.x-1, screen_cell_res_px.y-1), pygame.SRCALPHA)  # Create an empty surface with per-pixel alpha
        cell_pos_rect_surface.fill(color=POSITION_CELL_COLOR)

        # Semi-transparent surface for selection
        cell_sel_rect_surface = pygame.Surface((screen_cell_res_px.x-1, screen_cell_res_px.y-1), pygame.SRCALPHA)  # Create an empty surface with per-pixel alpha
        cell_sel_rect_surface.fill(color=SELECTION_CELL_COLOR)

        # Semi-transparent surface for already saved cells
        cell_save_rect_surface = pygame.Surface((screen_cell_res_px.x-1, screen_cell_res_px.y-1), pygame.SRCALPHA)  # Create an empty surface with per-pixel alpha
        cell_save_rect_surface.fill(color=SAVED_CELL_COLOR)

        is_cell_res_changed = False

    # Recalculate the mouse coordinates within the displayable game window
    mouse = Vect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    # Remember the last cell where mouse was positioned
    cell_pos_from_mouse_old = cell_pos_from_mouse

    # Get the grid cell coordinates where the mouse cursor is located
    cell_pos_from_mouse = get_cell_pos_from_mouse(mouse, screen_cell_res_px)

    # if the mouse cell has changed
    if cell_pos_from_mouse != cell_pos_from_mouse_old:

        # Get the topleft position of the selected cell on the screen in px
        screen_topleft_cell_pos_from_mouse_px = get_screen_topleft_cell_pos_from_mouse_px(mouse, screen_cell_res_px)

        # Selection is the cell on which the cursor is - if there is not other selection
        if not is_selection: sel_start_cell, sel_finish_cell = cell_pos_from_mouse, cell_pos_from_mouse

        # Selected image of character and its position and dimensions on the original font image
        char_img, char_img_dim = get_char_img_from_cell_selection(font_img, IMG_CELL_RES_PX, sel_start_cell, sel_finish_cell)

    ###################################
    # Display window elements
    ###################################

    # Clear the screen
    screen.fill(pygame.Color('#000000'))

    # Display image - scaled for the window
    screen.blit(pygame.transform.scale(font_img, (screen.get_size())), (0, 0))

    # Display the grid
    for i in range(grid_cnt.x): pygame.draw.line(screen, pygame.Color(GRID_COLOR), (int(i*screen_cell_res_px.x), 0), (int(i*screen_cell_res_px.x), screen.get_height()), 1)
    for i in range(grid_cnt.y): pygame.draw.line(screen, pygame.Color(GRID_COLOR), (0, int(i*screen_cell_res_px.y)), (screen.get_width(), int(i*screen_cell_res_px.y)), 1)

    # Display the pointer cell selection overlay
    if not is_selection: screen.blit(cell_pos_rect_surface, (screen_topleft_cell_pos_from_mouse_px.x+1, screen_topleft_cell_pos_from_mouse_px.y+1))

    # Show selected picture
    screen.blit(pygame.transform.scale2x(char_img), (0,0))

    # Show selection semi-transparent
    if is_selection:
        for i in range (min(sel_start_cell.x, sel_finish_cell.x), max(sel_start_cell.x, sel_finish_cell.x)+1):
            for j in range (min(sel_start_cell.y, sel_finish_cell.y), max(sel_start_cell.y, sel_finish_cell.y)+1):
                selected_cell = Vect(i,j)
                screen_topleft_cell_pos_from_cell_px = get_screen_topleft_cell_pos_from_cell_px(selected_cell, screen_cell_res_px)
                screen.blit(cell_sel_rect_surface, (screen_topleft_cell_pos_from_cell_px.x, screen_topleft_cell_pos_from_cell_px.y))

    # Show already saved cells
    for c in saved:
        screen_topleft_cell_pos_from_cell_px = get_screen_topleft_cell_pos_from_cell_px(c, screen_cell_res_px)
        screen.blit(cell_save_rect_surface, (screen_topleft_cell_pos_from_cell_px.x, screen_topleft_cell_pos_from_cell_px.y))

    # Show help
    if show_help: screen.blit(help_text_surf, (0, 0))  # Position the text at (250, 250)

    # Display basic info to the window bar
    pygame.display.set_caption(f'Extractor - res: {IMG_CELL_RES_PX}px, cell: {(cell_pos_from_mouse.x, cell_pos_from_mouse.y)}, sel dim: {char_img_dim}')

    ###################################
    # Process the inputs
    ###################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            
            # Please specify where to save the json file with the dictionary
            if font_dict:
                print('Saving resulting dict to file...')
                output = dict()
                # Add reference to the font img
                output['font_image'] = FONT_IMG
                
                # Add the colorkey
                output['colorkey'] = f"#{colorkey.r:02X}{colorkey.g:02X}{colorkey.b:02X}"

                # Add the chars
                output['chars'] = font_dict

                # Save dictionary to JSON file
                import json
                with open(FONT_JSON, 'w') as json_file:
                    json.dump(output, json_file, indent=4)  # indent=4 to format the output nicely
            
            pygame.quit()
            quit()

        if event.type == pygame.VIDEORESIZE:
            # Save the new window dimensions
            new_screen_width, new_screen_height = screen.get_width(), screen.get_height()

            # Make sure that the window keeps the same aspect ratio as a picture
            if screen_size.x != new_screen_width: # change of width
                # Change the screen height so that it matches the aspect ratio of the image
                new_screen_height = (1 / img_aspect_ratio) * new_screen_width

            if screen_size.y != new_screen_height: # change of height
                # Change the screen height so that it matches the aspect ratio of the image
                new_screen_width = img_aspect_ratio * new_screen_height

            print(f"Change of width: {screen_size.x=} -> {new_screen_width=}, {screen_size.y=} -> {new_screen_height=}")

            # Resize the window
            screen = pygame.display.set_mode((new_screen_width, new_screen_height), flags=pygame.RESIZABLE)

            # Remember the new screen dimensions
            screen_size = Vect(new_screen_width, new_screen_height)

            # Recalculate the spaces in the grid and all related variables
            #screen_cell_res_px = get_screen_cell_res_px(screen, grid_cnt)
            is_cell_res_changed = True

            # Recalculate the selection and position surfaces

            # Create semi-transparent surface for position
            #cell_pos_rect_surface = pygame.Surface((screen_cell_res_px.x-1, screen_cell_res_px.y-1), pygame.SRCALPHA)  # Create an empty surface with per-pixel alpha
            #cell_pos_rect_surface.fill(color=(255,0,0,128))
            
            # Create semi-transparent surface for selection
            #cell_sel_rect_surface = pygame.Surface((screen_cell_res_px.x-1, screen_cell_res_px.y-1), pygame.SRCALPHA)  # Create an empty surface with per-pixel alpha
            #cell_sel_rect_surface.fill(color=(0,255,0,128))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # LEFT MOUSE BUTTON
                #print(f'Screen Cursor Pos TopLeft: {(screen_topleft_cell_pos_from_mouse_px.x, screen_topleft_cell_pos_from_mouse_px.y)}')
                #print(f'BotomRight: {(screen_topleft_cell_pos_from_mouse_px.x + screen_cell_res_px.x, screen_topleft_cell_pos_from_mouse_px.y + screen_cell_res_px.y)}')
                #print(f'Image Cell Coords: {cell_pos_from_mouse}')
                #print(f'Image Cell Px Pos TopLeft: {char_img_dim.topleft}')
                #print(f'Image Cell Px Pos BotomRight: {char_img_dim.bottomright}')
                is_selection = not is_selection
                print(f'Selection: {is_selection}')
                if is_selection == True: sel_start_cell = cell_pos_from_mouse

        if event.type == pygame.MOUSEBUTTONUP: 
           pass
           """
           if event.button == 1:
                print(f'Release of the left button on cell -> {cell_pos_from_mouse}')
                print(f'Selection: {selection}')

                # Clip the selection into char_img
                selection_most_topleft_cell = Vect(min(selection_start_cell.x, selection_finish_cell.x), min(selection_start_cell.y, selection_finish_cell.y))
                selection_most_botomright_cell = Vect(max(selection_start_cell.x, selection_finish_cell.x), max(selection_start_cell.y, selection_finish_cell.y))

                selection_cell_length = Vect(selection_most_botomright_cell.x - selection_most_topleft_cell.x+1, selection_most_botomright_cell.y - selection_most_topleft_cell.y+1)
                selection_img_topleft_px = get_img_topleft_cell_pos_from_cell_px(
                    selection_most_topleft_cell, 
                    IMG_CELL_RES_PX
                )

                # Snap the character image
                char_img = clip(font_img, (selection_img_topleft_px.x, selection_img_topleft_px.y), (selection_cell_length.x * IMG_CELL_RES_PX, selection_cell_length.y * IMG_CELL_RES_PX))
                print(f'Char image: {char_img}')
                print(f'Selected cells from:{(min(selection_start_cell.x, selection_finish_cell.x), min(selection_start_cell.y, selection_finish_cell.y))}, to:{(max(selection_start_cell.x, selection_finish_cell.x), max(selection_start_cell.y, selection_finish_cell.y))}')
            """
           
        if event.type == pygame.KEYDOWN: 
            
            # After pressing the INSERT button
            if event.key == pygame.K_INSERT:

                # Here save the image to key
                print(f'Press the button under which the character will be saved...')
                
                #char_entered = False
                key_entered: bool = False
                key: str = ''
                
                while not key_entered: #char_entered:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN: 
                            if event.key == pygame.K_RETURN and key: # non empty key is mandatory
                                # Save the string
                                font_dict[key] = {
                                            'width': char_img_dim.width, #selection_cell_length.x * img_cell_res_px,
                                            'height': char_img_dim.height, #selection_cell_length.y * img_cell_res_px,
                                            'x': char_img_dim.x, #selection_img_topleft_px.x, # x-coord of the topleft corner in the original file
                                            'y': char_img_dim.y #selection_img_topleft_px.y # y-coord of the topleft corner in the original file
                                        }
                                print(f"Saved under key={key}, {font_dict[key]}, {font_dict=}")
                                key_entered = True

                                # Save the cells as already used
                                if is_selection:
                                    for i in range (min(sel_start_cell.x, sel_finish_cell.x), max(sel_start_cell.x, sel_finish_cell.x)+1):
                                        for j in range (min(sel_start_cell.y, sel_finish_cell.y), max(sel_start_cell.y, sel_finish_cell.y)+1):
                                            saved.add(Vect(i,j))
                                else:
                                    saved.add(cell_pos_from_mouse)

                            else:
                                char = event.unicode
                                if char: # Is printable, save it 
                                    key = key + char
                                    print(f'Key: {key=}')

            # Navigate using arrow keys
            elif event.key == pygame.K_LEFT: pygame.mouse.set_pos((max(0, mouse.x - screen_cell_res_px.x), mouse.y))
            elif event.key == pygame.K_RIGHT: pygame.mouse.set_pos((min(screen_size.x, mouse.x + screen_cell_res_px.x), mouse.y))
            elif event.key == pygame.K_UP: pygame.mouse.set_pos((mouse.x, max(0, mouse.y - screen_cell_res_px.y)))
            elif event.key == pygame.K_DOWN: pygame.mouse.set_pos((mouse.x, min(screen_size.y, mouse.y + screen_cell_res_px.y)))

            # Change the resolution of the grid
            elif event.key == pygame.K_PAGEDOWN:
                IMG_CELL_RES_PX = int(IMG_CELL_RES_PX / 2) if IMG_CELL_RES_PX > 2 else IMG_CELL_RES_PX
                is_cell_res_changed = True

            # Change the resolution of the grid
            elif event.key == pygame.K_PAGEUP:
                IMG_CELL_RES_PX = int(IMG_CELL_RES_PX * 2) if IMG_CELL_RES_PX < 256 else IMG_CELL_RES_PX
                is_cell_res_changed = True
            
            # Show/hide help
            elif event.key == pygame.K_F1:
                show_help = not show_help


    # Selection in progress
    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0] == 1: # left button is pressed
        sel_finish_cell = cell_pos_from_mouse


    pygame.display.update()
