import unittest
import pygame
import os
from pathlib import Path

# Assuming your library will be installable, you'd import it like this:
#from pgbitmapfont import BitmapFont

# If running directly from the repo for testing, you might need to adjust sys.path:
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pgbitmapfont import BitmapFont # Or from bitmapfont.bitmapfont import BitmapFont

# Path to your test font fixtures
TEST_FONT_DIR = Path(os.path.join(os.path.dirname(__file__), 'fonts'))

# Free Dims Test Font
TEST_FREE_DIMS_CORRECT_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/correct_font.json'))
TEST_FREE_DIMS_CORRUPTED_JSON_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/corrupted_json_font.json'))
TEST_FREE_DIMS_MISSING_IMAGE_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/miss_image_font.json'))
TEST_FREE_DIMS_MISSING_CHARS_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/miss_chars_font.json'))
TEST_FREE_DIMS_EMPTY_CHARS_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/empty_chars_font.json'))
TEST_FREE_DIMS_INCORRECT_CHARS_FONT = Path(os.path.join(TEST_FONT_DIR, 'free_dims/incorrect_chars_font.json'))

class TestBitmapFontFreeDims(unittest.TestCase):

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
        self.correct_font = BitmapFont(path=TEST_FREE_DIMS_CORRECT_FONT)
        # Create scaled font
        self.scaled_font = BitmapFont(path=TEST_FREE_DIMS_CORRECT_FONT, size=32, spacing=(2,2))

        if TestBitmapFontFreeDims.screen:
            self.test_surface = pygame.Surface((100, 50)) # A small surface for rendering tests
            self.test_surface.fill((0,0,0)) # Fill with black
        else:
            self.test_surface = None


    # 1. Font Loading Tests
    def test_load_valid_font(self):
        """Test loading a correctly formatted font."""
        self.assertIsNotNone(self.correct_font, "Font should be loaded.")
        # Add more specific assertions, e.g., check if character data is loaded
        self.assertIn('A', self.correct_font.characters, "Character 'A' (ASCII 65) should be in font data.")
        # Check properties like line_height, base, etc. if your class stores them
        self.assertEqual(self.correct_font.font_height, self.correct_font.characters['A']['height'])
        # Check that default character is loaded
        self.assertIsNotNone(self.correct_font.characters[self.correct_font.default_char], "Default character not loaded properly")
        # Check that umber of characters is characters dict > len of character_order
        self.assertGreaterEqual(len(self.correct_font.characters), 1)

    def test_load_missing_font_file(self):
        """Test loading with a missing font file."""
        with self.assertRaises(FileNotFoundError): # Or your specific exception
            BitmapFont("non_existent_font.json")

    def test_load_corrupted_json_font_file(self):
        """Test loading a corrupted or incorrectly formatted font file."""
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(TEST_FREE_DIMS_CORRUPTED_JSON_FONT)

    def test_load_error_data_font_file(self):
        """Test loading a corrupted/incorrectly/erroreous formatted font file."""

        # Test missing font image file path
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(TEST_FREE_DIMS_MISSING_IMAGE_FONT)

        # Chars missing
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(TEST_FREE_DIMS_MISSING_CHARS_FONT)

        # Chars empty
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(TEST_FREE_DIMS_EMPTY_CHARS_FONT)

        # Chars not a dictionary
        with self.assertRaises(Exception): # Replace with your specific parsing error
            BitmapFont(TEST_FREE_DIMS_INCORRECT_CHARS_FONT)


    # 2. Rendering Tests
    def test_render_simple_text(self):
        """Test rendering a simple string."""
        if not self.test_surface: self.skipTest("Pygame screen not available for rendering test.")

        # Clear surface
        self.test_surface.fill((0,0,0))
        # Render
        rendered_text = self.correct_font.render(text="Ahoj", fgcolor=pygame.Color('blue'))
        self.assertIsNotNone(rendered_text[1], "Render method should return a rect.")
        # Check the height, width
        self.assertEqual(rendered_text[1].height, self.correct_font.font_height)
        self.assertGreater(rendered_text[1].width, 0)

    def test_render_scaled_text(self):
        """Test rendering a scaled string."""
        if not self.test_surface: self.skipTest("Pygame screen not available for rendering test.")

        # Clear surface
        self.test_surface.fill((0,0,0))
        # Render
        rendered_text = self.scaled_font.render(text="Ahoj")
        self.assertIsNotNone(rendered_text[1], "Render method should return a rect.")
        # Check the height is equal to size
        self.assertEqual(rendered_text[1].height, self.scaled_font.font_height + self.scaled_font.spacing[1])
        self.assertEqual(self.scaled_font.font_height, 32)

    def test_render_empty_text(self):
        """Test rendering an empty string."""
        if not self.test_surface: self.skipTest("Pygame screen not available for rendering test.")

        rendered_text = self.correct_font.render(text="")
        self.assertIsNotNone(rendered_text)
        self.assertEqual(rendered_text[1].width, 0, "Rendering empty string should result in zero width.")

    def test_render_unknown_character(self):
        """Test rendering text with characters not in the font."""
        if not self.test_surface: self.skipTest("Pygame screen not available for rendering test.")
        # Assuming 'š' is not in your correct_font.json
        rendered_text = self.correct_font.render(text='AšA')
        # By default is substituted with the _ character if exists in the font
        underscore_char = self.correct_font.render(text='_')
        a_character_char = self.correct_font.render(text='A')
        # The resulting with should be the sum of widths taking into account the spacing
        self.assertEqual(rendered_text[1].width, 2*a_character_char[1].width + 2*self.correct_font.spacing[0] + underscore_char[1].width)


    # 3. Text Measurement / Metrics (if applicable)
    def test_text_width(self):
        """Test that the dimensions are reflecting characters and spoacing"""
        width_A = self.correct_font.render('A')[1].width
        width_B = self.correct_font.render('B')[1].width
        width_AB = self.correct_font.render('AB')[1].width
        width_empty = self.correct_font.render('')[1].width

        self.assertEqual(width_AB, width_A + width_B + self.correct_font.spacing[0])
        self.assertEqual(width_empty, 0)

    def test_text_scaled_width(self):
        """Test that the dimensions are reflecting characters and spacing when scaled"""
        width_A = self.scaled_font.render('A')[1].width
        width_B = self.scaled_font.render('B')[1].width
        width_AB = self.scaled_font.render('AB')[1].width
        width_empty = self.scaled_font.render('')[1].width

        self.assertEqual(width_AB, width_A + width_B + self.correct_font.spacing[0])
        self.assertEqual(width_empty, 0)

    def test_get_metrics_width(self):
        """Test that the dimensions are reflecting characters and spacing"""

        test_string = 'Hello'

        test_get_metrics = self.correct_font.get_metrics(test_string)
        test_get_metrics_sum_min_x = sum([c[0] for c in test_get_metrics])
        test_get_metrics_sum_max_x = sum([c[1] for c in test_get_metrics])
        test_get_metrics_sum_hor_adv_x = sum([c[4] for c in test_get_metrics])

        test_render = self.correct_font.render(test_string)[1]
        test_get_rect = self.correct_font.get_rect(test_string)

        self.assertEqual(test_get_metrics_sum_min_x, test_get_metrics_sum_max_x)
        self.assertEqual(test_get_metrics_sum_max_x, test_get_metrics_sum_hor_adv_x)
        self.assertEqual(test_get_metrics_sum_max_x, test_render.width)
        self.assertEqual(test_get_metrics_sum_max_x, test_get_rect.width)

    def test_get_metrics_scaled_width(self):
        """Test that the dimensions are reflecting characters and spacing when scaled"""

        test_string = 'Hello'

        test_get_metrics = self.scaled_font.get_metrics(test_string)
        test_get_metrics_sum_min_x = sum([c[0] for c in test_get_metrics])
        test_get_metrics_sum_max_x = sum([c[1] for c in test_get_metrics])
        test_get_metrics_sum_hor_adv_x = sum([c[4] for c in test_get_metrics])

        test_render = self.scaled_font.render(test_string)[1]
        test_get_rect = self.scaled_font.get_rect(test_string)

        self.assertEqual(test_get_metrics_sum_min_x, test_get_metrics_sum_max_x)
        self.assertEqual(test_get_metrics_sum_max_x, test_get_metrics_sum_hor_adv_x)
        self.assertEqual(test_get_metrics_sum_max_x, test_render.width)
        self.assertEqual(test_get_metrics_sum_max_x, test_get_rect.width)

if __name__ == '__main__':
    unittest.main()