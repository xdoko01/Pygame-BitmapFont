# tests/test_bitmapfont.py

import os
import pytest
from bitmapfont.bitmapfont import BitmapFont

# Sample test asset (replace with actual test font file path)
TEST_FONT_PATH = "assets/test_font.png"

@pytest.fixture(scope="module")
def font():
    if not os.path.exists(TEST_FONT_PATH):
        # Create a dummy image for testing
        img = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
        img.save(TEST_FONT_PATH)
    return BitmapFont(TEST_FONT_PATH, char_width=8, char_height=8)

def test_init(font):
    assert font.char_width == 8
    assert font.char_height == 8
    assert font.columns == 16

def test_char_image_extraction(font):
    img = font.get_char_image("A")
    assert img is not None
    assert isinstance(img, Image.Image)
    assert img.size == (8, 8)

def test_char_image_invalid(font):
    img = font.get_char_image("\u262F")  # uncommon character not in ASCII
    assert img is None

def test_render_text(font):
    text_img = font.render_text("ABC")
    assert text_img is not None
    assert text_img.size[1] == 8  # height matches char height
    assert text_img.size[0] == 24  # 3 chars * 8px width
