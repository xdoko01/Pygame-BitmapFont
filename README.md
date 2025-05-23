 - [ ] Experiment with pipelines in GitHub
 - [ ] Make the demo more consistent
 - [ ] Prepare README.md
 - [ ] Fix the test suite
 - [x] Prepare the test suite 
 - [x] Must support generation even if character does not exist. First character in the fixed height and default in the Free Dims
   - [x] FixedHeight font
   - [x] FreeDims font

# Pygame-BitmapFont

A lightweight and easy-to-use library for rendering bitmap fonts in Pygame.

## Overview

BitmapFont provides a simple way to load and render text using pre-rendered bitmap font images and associated font data files. This approach is often preferred in game development for its performance and consistent look across different platforms.

**Key Features:**

* **Easy Integration:** Designed specifically for Pygame, ensuring smooth integration into your game projects.
* **Multiple Font Formats:** Supports [mention the specific formats your library handles, e.g., plain text `.fnt`, XML-based formats].
* **Efficient Rendering:** Leverages Pygame's `Surface` and drawing capabilities for fast text rendering.
* **Customizable:** Offers options for color and potentially other styling (if implemented).
* **Clear Examples:** Comes with illustrative examples to get you started quickly.
* **Installable via pip:** Easily install the library using the Python package installer.

## Installation

1.  **Prerequisites:** Make sure you have Pygame installed in your Python environment. If not, you can install it using pip:
    ```bash
    pip install pygame
    ```
2.  **Install via pip (Recommended):** Once the package is available on PyPI, you can install BitmapFont using:
    ```bash
    pip install bitmapfont
    ```
3.  **Alternatively (for development or if not yet on PyPI):**
    * **Download or Clone:** Clone the entire repository:
        ```bash
        git clone [https://github.com/xdoko01/BitmapFont.git](https://github.com/xdoko01/BitmapFont.git)
        cd BitmapFont
        ```
    * **Place the `bitmapfont` package:** Ensure the `bitmapfont` directory (containing the library's `__init__.py` and other modules) is in your Python project's site-packages directory or within your project structure where Python can import it.

## Usage

Here's a basic example of how to use the BitmapFont library in your Pygame project after installing it (either via pip or by placing the package):

```python
import pygame
from bitmapfont import BitmapFont

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("BitmapFont Example")

# Load the font
font = BitmapFont("path/to/your/font.fnt", "path/to/your/font.png")

# Text to render
text = "Hello, Pygame!"
text_position = (100, 100)
text_color = (255, 255, 0)  # Yellow

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))  # Black

    # Render the text
    font.render(screen, text_position, text, text_color)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()