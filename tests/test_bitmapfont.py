import unittest
import pygame
import os

# Assuming your library will be installable, you'd import it like this:
from bitmapfont import BitmapFont
# If running directly from the repo for testing, you might need to adjust sys.path:
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from bitmapfont import BitmapFont # Or from bitmapfont.bitmapfont import BitmapFont

# Path to your test font fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
TEST_FONT_FNT = os.path.join(FIXTURES_DIR, 'test_font.fnt')
TEST_FONT_PNG = os.path.join(FIXTURES_DIR, 'test_font.png')
# Add paths for other test fonts if you support multiple formats or have more complex test cases

class TestBitmapFont(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize Pygame minimally for tests
        # This is tricky as Pygame often needs a display.
        # For non-rendering tests, you might get away without full display init.
        # For rendering tests, a display is needed.
        try:
            pygame.display.init()
            # If display init fails (e.g., in a headless CI environment),
            # some tests might need to be skipped or handled differently.
            # You might need to set SDL_VIDEODRIVER=dummy on CI
            cls.screen = pygame.display.set_mode((100, 100)) # Dummy screen for rendering tests
        except pygame.error as e:
            print(f"Warning: Pygame display init failed: {e}. Some rendering tests might not run correctly.")
            cls.screen = None


    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        # This method is called before each test function.
        # You can create a fresh font instance here if needed,
        # but often it's better to load it once if it's read-only.
        self.font = BitmapFont(TEST_FONT_FNT, TEST_FONT_PNG)
        if TestBitmapFont.screen:
            self.test_surface = pygame.Surface((100, 50)) # A small surface for rendering tests
            self.test_surface.fill((0,0,0)) # Fill with black
        else:
            self.test_surface = None


    # 1. Font Loading Tests
    def test_load_valid_font(self):
        """Test loading a correctly formatted font."""
        self.assertIsNotNone(self.font, "Font should be loaded.")
        # Add more specific assertions, e.g., check if character data is loaded
        self.assertIn(65, self.font.chars, "Character 'A' (ASCII 65) should be in font data.")
        # Check properties like line_height, base, etc. if your class stores them
        # self.assertEqual(self.font.line_height, 16)

    def test_load_missing_fnt_file(self):
        """Test loading with a missing .fnt file."""
        with self.assertRaises(FileNotFoundError): # Or your specific exception
            BitmapFont("non_existent.fnt", TEST_FONT_PNG)

    def test_load_missing_png_file(self):
        """Test loading with a missing .png file."""
        with self.assertRaises(FileNotFoundError): # Or your specific exception
            BitmapFont(TEST_FONT_FNT, "non_existent.png")

    def test_load_corrupted_fnt_file(self):
        """Test loading a corrupted or incorrectly formatted .fnt file."""
        # Create a dummy corrupted_font.fnt in fixtures
        corrupted_fnt_path = os.path.join(FIXTURES_DIR, "corrupted_font.fnt")
        # with open(corrupted_fnt_path, "w") as f:
        #     f.write("this is not a valid font file")
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(corrupted_fnt_path, TEST_FONT_PNG)

    # 2. Rendering Tests
    def test_render_simple_text(self):
        """Test rendering a simple string."""
        if not self.test_surface:
            self.skipTest("Pygame screen not available for rendering test.")

        text_to_render = "A"
        position = (10, 10)
        color = (255, 0, 0) # Red

        # Clear surface
        self.test_surface.fill((0,0,0))
        # Render
        rendered_rect = self.font.render(self.test_surface, position, text_to_render, color)

        self.assertIsNotNone(rendered_rect, "Render method should return a rect.")
        self.assertEqual(rendered_rect.topleft, position)
        # self.assertEqual(rendered_rect.width, expected_width_of_A) # Calculate expected width

        # Very basic check: See if *any* pixel of the expected color is in the rendered area.
        # More precise checks would involve knowing the exact glyph shape.
        char_a_data = self.font.chars.get(ord('A'))
        if char_a_data:
            char_width = char_a_data.get('xadvance') # or 'width' depending on your structure
            char_height = char_a_data.get('height') # or lineHeight
            found_pixel = False
            for x_offset in range(char_width):
                for y_offset in range(char_height):
                    # Only check within the bounds of the surface
                    check_x = position[0] + x_offset
                    check_y = position[1] + y_offset
                    if 0 <= check_x < self.test_surface.get_width() and \
                       0 <= check_y < self.test_surface.get_height():
                        if self.test_surface.get_at((check_x, check_y))[:3] == color:
                            found_pixel = True
                            break
                if found_pixel:
                    break
            self.assertTrue(found_pixel, f"Expected to find red pixel for char 'A' at {position}")

    def test_render_empty_text(self):
        """Test rendering an empty string."""
        if not self.test_surface:
            self.skipTest("Pygame screen not available for rendering test.")

        rendered_rect = self.font.render(self.test_surface, (0,0), "", (255,255,255))
        self.assertIsNotNone(rendered_rect)
        self.assertEqual(rendered_rect.width, 0, "Rendering empty string should result in zero width.")
        self.assertEqual(rendered_rect.height, self.font.line_height if hasattr(self.font, 'line_height') else 0) # Or 0, depending on behavior

    def test_render_unknown_character(self):
        """Test rendering text with characters not in the font."""
        if not self.test_surface:
            self.skipTest("Pygame screen not available for rendering test.")
        # Assuming 'Z' is not in your test_font.fnt
        rendered_rect = self.font.render(self.test_surface, (0,0), "AZA", (255,255,255))
        # Behavior depends on your implementation:
        # - It might skip the character.
        # - It might render a default character (e.g., a box).
        # - It might raise an error.
        # Assert the expected behavior. For example, if it skips:
        # expected_width = width_of_A + width_of_A
        # self.assertEqual(rendered_rect.width, expected_width)

    def test_render_different_colors(self):
        """Test rendering text with different colors."""
        if not self.test_surface:
            self.skipTest("Pygame screen not available for rendering test.")

        blue = (0, 0, 255)
        self.test_surface.fill((0,0,0))
        self.font.render(self.test_surface, (5,5), "A", blue)
        # Check a pixel where 'A' should be rendered
        # This is a very simplified check, assumes top-left of char glyph is colored
        char_a_data = self.font.chars.get(ord('A'))
        if char_a_data:
             # Find a non-transparent pixel in the 'A' glyph from your test_font.png
             # and check its color on the test_surface.
             # For a robust test, you'd need to know where the actual pixels of 'A' are.
             # Let's assume the char 'A' has a pixel at its local (0,0) for simplicity.
             # This requires that your font's 'A' glyph has a pixel at its top-left corner.
            try:
                pixel_color = self.test_surface.get_at((5 + char_a_data.get('xoffset', 0), 5 + char_a_data.get('yoffset', 0)))[:3]
                self.assertEqual(pixel_color, blue, "Text should be rendered in the specified blue color.")
            except IndexError:
                self.fail("Pixel check out of bounds for color test.")


    # 3. Text Measurement / Metrics (if applicable)
    # If you have methods like `get_text_width()` or `get_text_size()`
    # def test_get_text_width(self):
    #     width_A = self.font.chars.get(ord('A')).get('xadvance')
    #     width_B = self.font.chars.get(ord('B')).get('xadvance')
    #     self.assertEqual(self.font.get_text_width("AB"), width_A + width_B)
    #     self.assertEqual(self.font.get_text_width(""), 0)

    # 4. Kerning Tests (if implemented)
    # def test_kerning(self):
    #     # You'll need a font with kerning pairs defined
    #     # e.g., if 'A' and 'V' have negative kerning
    #     width_A = self.font.chars.get(ord('A')).get('xadvance')
    #     width_V = self.font.chars.get(ord('V')).get('xadvance')
    #     kerning_AV = self.font.get_kerning(ord('A'), ord('V')) # Assuming such a method
    #     self.assertEqual(self.font.get_text_width("AV"), width_A + width_V + kerning_AV)

if __name__ == '__main__':
    unittest.main()