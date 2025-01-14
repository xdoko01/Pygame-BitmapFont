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
###    TODO: dynamic cell resolution 
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


# Create an ArgumentParser object for processing the input
import argparse
parser = argparse.ArgumentParser(description="Process command-line arguments.")
parser.add_argument("--img", type=str, help="Image with font characters", required=False) 
parser.add_argument("--out", type=str, help="Output JSON file", required=False)
args = parser.parse_args()

# Get from input line
FONT_IMG = args.img if args.img else 'tools/charset_id1.png'
FONT_JSON = args.out if args.out else FONT_IMG.split('/')[-1].split('.')[0] + 'json'
IMG_CELL_RES_PX = 16 # resolution of the grid cell on the original image

POSITION_CELL_COLOR = (255,0,0,128) # Color of cell on which the cursor is located
SELECTION_CELL_COLOR = (0,255,0,128) # Color of cells selected by mouse
SAVED_CELL_COLOR = (128,128,128,128) # Color for already saved cells into the font file

TEXT_COLOR = (255,0,0,128)
TEXT_SIZE = 20

GRID_COLOR = (0,255,0,128)

HELP_TEXT = \
'''Help
1. Select the suitable grid resolution by '[', ']'
2. Select the cell with texture
3. Press ENTER to save the texture details into JSON
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
char_img = None

# Create a font object
font = pygame.font.Font(None, TEXT_SIZE)  # None means default font, 74 is the font size

# Show help
show_help = False

# Render the help text
help_text_surf = font.render(HELP_TEXT, True, TEXT_COLOR)

# Remember selection of cells
selection: set = set()

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

    # Get the topleft position of the selected cell on the screen in px
    screen_topleft_cell_pos_from_mouse_px = get_screen_topleft_cell_pos_from_mouse_px(mouse, screen_cell_res_px)

    # Get the grid cell coordinates where the mouse cursor is located
    cell_pos_from_mouse = get_cell_pos_from_mouse(mouse, screen_cell_res_px)
    
    # Get the image px coordinates of the topleft and bottomright corner of the cell where the mouse is located
    img_topleft_cell_pos_from_cell_px = get_img_topleft_cell_pos_from_cell_px(cell_pos_from_mouse, IMG_CELL_RES_PX)
    img_bottomright_cell_pos_from_cell_px = Vect(img_topleft_cell_pos_from_cell_px.x + IMG_CELL_RES_PX, img_topleft_cell_pos_from_cell_px.y + IMG_CELL_RES_PX)

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

    # Display the selected cell
    screen.blit(cell_pos_rect_surface, (screen_topleft_cell_pos_from_mouse_px.x+1, screen_topleft_cell_pos_from_mouse_px.y+1))

    # Display basic info to the window bar
    pygame.display.set_caption(f'Extractor - res: {IMG_CELL_RES_PX}px, cell: {(cell_pos_from_mouse.x, cell_pos_from_mouse.y)}, topleft img: {img_topleft_cell_pos_from_cell_px}')

    ###################################
    # Process the inputs
    ###################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            
            # Please specify where to save the json file with the dictionary
            if font_dict:
                print('Saving resulting dict to file...')
                # Save dictionary to JSON file
                import json
                with open(FONT_JSON, 'w') as json_file:
                    json.dump(font_dict, json_file, indent=4)  # indent=4 to format the output nicely
            
            pygame.quit()

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
                print(f'Screen Cursor Pos TopLeft: {(screen_topleft_cell_pos_from_mouse_px.x, screen_topleft_cell_pos_from_mouse_px.y)}')
                print(f'BotomRight: {(screen_topleft_cell_pos_from_mouse_px.x + screen_cell_res_px.x, screen_topleft_cell_pos_from_mouse_px.y + screen_cell_res_px.y)}')
                
                #img_char_coords_cell_x, img_char_coords_cell_y = int(mouse.x // screen_cell_res_px.x), int(mouse.y // screen_cell_res_px.y)
                #img_char_coords_px_x, img_char_coords_px_y = screen_cell_res_px.x*IMG_CELL_RES_PX, screen_cell_res_px.y*IMG_CELL_RES_PX
                print(f'Image Cell Coords: {cell_pos_from_mouse}')
                print(f'Image Cell Px Pos TopLeft: {(img_topleft_cell_pos_from_cell_px.x, img_topleft_cell_pos_from_cell_px.y)}')
                print(f'Image Cell Px Pos BotomRight: {(img_bottomright_cell_pos_from_cell_px.x, img_bottomright_cell_pos_from_cell_px.y)}')

                # Snap the character image
                #char_img = clip(font_img, img_topleft_cell_pos_from_cell_px, (IMG_CELL_RES_PX, IMG_CELL_RES_PX))
                #print(f'Char image: {char_img}')

                # Reset the selection and remember the selection start point
                selection = set()
                selection_start_cell = cell_pos_from_mouse
                selection.add(selection_start_cell)

        if event.type == pygame.MOUSEBUTTONUP: 
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

        if event.type == pygame.KEYDOWN: 
            
            if event.key == pygame.K_LEFTBRACKET:
                IMG_CELL_RES_PX = int(IMG_CELL_RES_PX / 2) if IMG_CELL_RES_PX > 2 else IMG_CELL_RES_PX
                is_cell_res_changed = True

            if event.key == pygame.K_RIGHTBRACKET:
                IMG_CELL_RES_PX = int(IMG_CELL_RES_PX * 2) if IMG_CELL_RES_PX < 256 else IMG_CELL_RES_PX
                is_cell_res_changed = True


            if event.key == pygame.K_F1:
                # SHow/hide help
                show_help = not show_help

            if event.key == pygame.K_RETURN:
                dict_key = input(f"Return pressed. Under what key do you want to save {char_img}?")
                print(f"Dict_key: {dict_key=}")
                if dict_key:
                    for c in dict_key: # Save the same info for all characters in the input string - for example, create 2 records for As input dict_key
                        font_dict[c] = {
                            'width': selection_cell_length.x * IMG_CELL_RES_PX,
                            'height': selection_cell_length.y * IMG_CELL_RES_PX,
                            'x': selection_img_topleft_px.x, # x-coord of the topleft corner in the original file
                            'y': selection_img_topleft_px.y # y-coord of the topleft corner in the original file
                        }
                        print(f'Added to dictionary: {font_dict[c]}.')
                    print(f'Font dict: {font_dict}.')
                    # Mark graphically as saved
                    saved = saved.union(selection)
                    print(f'Selected cells: {selection}, Already saved cells: {saved}')

    # If the left mouse button is pressed, blit the transparent rectancles on all selection
    # If it is not pressed, blit just rectancle where the cursor is located
    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0] == 1: # left button is pressed
        selection_finish_cell = cell_pos_from_mouse

        #img_char_coords_cell_x, img_char_coords_cell_y = int(mouse.x // screen_cell_res_px.x), int(mouse.y // screen_cell_res_px.y)
        #select_finish_x_cell, select_finish_y_cell = img_char_coords_cell_x, img_char_coords_cell_y

        # Take min on x and count to max on x
        for i in range (min(selection_start_cell.x, selection_finish_cell.x), max(selection_start_cell.x, selection_finish_cell.x)+1):
            for j in range (min(selection_start_cell.y, selection_finish_cell.y), max(selection_start_cell.y, selection_finish_cell.y)+1):
                selected_cell = Vect(i,j)
                # add to selection
                selection.add(selected_cell)
                # blit
                screen_topleft_cell_pos_from_cell_px = get_screen_topleft_cell_pos_from_cell_px(selected_cell, screen_cell_res_px)
                screen.blit(cell_sel_rect_surface, (screen_topleft_cell_pos_from_cell_px.x, screen_topleft_cell_pos_from_cell_px.y))

    # left button not pressed
    else:
        # Show rect on the position of the cursor
        #screen.blit(cell_pos_rect_surface, (screen_topleft_cell_pos_from_mouse_px.x+1, screen_topleft_cell_pos_from_mouse_px.y+1))

        # Show saved cells
        for s in saved:
            screen_topleft_cell_pos_from_cell_px = get_screen_topleft_cell_pos_from_cell_px(s, screen_cell_res_px)
            screen.blit(cell_save_rect_surface, screen_topleft_cell_pos_from_cell_px)

    if char_img: screen.blit(pygame.transform.scale2x(char_img), (0,0))

    if show_help: screen.blit(help_text_surf, (0, 0))  # Position the text at (250, 250)

    pygame.display.update()
