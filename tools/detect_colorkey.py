from PIL import Image

# Load the image
image = Image.open("fonts/good_neighbours_font.png")

# Get pixel data
pixels = image.getdata()

# Find the most common color in the corners (assuming they represent the colorkey)
width, height = image.size
corners = [
    pixels[0],                            # Top-left
    pixels[width - 1],                    # Top-right
    pixels[width * (height - 1)],         # Bottom-left
    pixels[width * height - 1]            # Bottom-right
]

# Check if all corners are the same color
if len(set(corners)) == 1:
    colorkey = corners[0]
    print(f"Detected colorkey: {colorkey}")
else:
    print(f"{corners=}")
    print("No consistent colorkey detected in the corners.")