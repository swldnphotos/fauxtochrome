import numpy as np
from PIL import Image
import os
import random

# File to store the previous dimensions
DIMENSIONS_FILE = os.path.expanduser("~/previous_dimensions.txt")

def save_previous_dimensions(final_width, final_height):
    """Save only the width and height to a file for later retrieval."""
    try:
        with open(DIMENSIONS_FILE, 'w') as file:
            file.write(f"{final_width},{final_height}")
    except Exception as e:
        print(f"Error saving dimensions: {e}")

def load_previous_dimensions():
    """Load only the width and height from a file if it exists and return them."""
    try:
        if os.path.exists(DIMENSIONS_FILE):
            with open(DIMENSIONS_FILE, 'r') as file:
                line = file.readline()
                dimensions = line.strip().split(',')
                if len(dimensions) == 2:
                    return tuple(map(int, dimensions))  # Convert each value to int
    except Exception as e:
        print(f"Error loading dimensions: {e}")
    return None

def prompt_for_dimensions():
    """Prompt the user to enter dimensions, offering saved width and height if available, followed by pattern and other options."""
    previous_dimensions = load_previous_dimensions()
    if previous_dimensions:
        saved_width, saved_height = previous_dimensions
        use_saved = input(f"Use previous width and height (Width: {saved_width}px, Height: {saved_height}px)? (y/n): ").strip().lower()
        if use_saved == 'y':
            final_width, final_height = saved_width, saved_height
        else:
            final_width = int(input("Enter the width of the image in pixels: "))
            final_height = int(input("Enter the height of the image in pixels: "))
    else:
        final_width = int(input("Enter the width of the image in pixels: "))
        final_height = int(input("Enter the height of the image in pixels: "))

    save_previous_dimensions(final_width, final_height)

    pattern_type = input("Choose pattern type:\n"
                         "  a) Bayer pattern\n"
                         "  b) RGBRGB pattern\n"
                         "  c) Diagonal Red-Green-Blue lines\n"
                         "  d) 3x3 custom pattern (Green, Blue, Red)\n"
                         "  e) Uniform distribution of Red, Green, and Blue\n"
                         "  f) Gaussian distribution of Red, Green, and Blue\n"
                         "  g) Random distribution of Red, Green, and Blue\n"
                         "  h) Balanced RGB 6x6 Grid\n"
                         "  i) Stochastic Equal Distribution\n"
                         "Enter your choice (a-i): ").strip().lower()

    cell_size = int(input("Enter the size of each colored cell in pixels: "))

    while True:
        border_size = int(input(f"Enter the size of the black border between cells (0 to {cell_size}): "))
        if 0 <= border_size <= cell_size:
            break
        print(f"Invalid border size. Please enter a value between 0 and {cell_size}.")

    return final_width, final_height, cell_size, border_size, pattern_type

def generate_pattern_with_custom_blocks(final_width, final_height, cell_size, border_size, pattern_type):
    """
    Generate a pattern with custom color blocks and black borders, ensuring the pattern fits exactly to the final dimensions.
    Includes options for all patterns a-i.
    """
    color_width = (final_width + cell_size + border_size - 1) // (cell_size + border_size)
    color_height = (final_height + cell_size + border_size - 1) // (cell_size + border_size)

    oversize_width = color_width * (cell_size + border_size)
    oversize_height = color_height * (cell_size + border_size)
    pattern_array = np.zeros((oversize_height, oversize_width, 3), dtype=np.uint8)

    colors = {
        'red': [255, 0, 0],
        'green': [0, 255, 0],
        'blue': [0, 0, 255]
    }

    if pattern_type == 'a':
        color_pattern = [
            [colors['green'], colors['red']],
            [colors['blue'], colors['green']]
        ]
    elif pattern_type == 'b':
        color_pattern = [
            [colors['red'], colors['green'], colors['blue']],
            [colors['red'], colors['green'], colors['blue']]
        ]
    elif pattern_type == 'c':
        color_pattern = [
            [colors['red'], colors['green'], colors['blue']],
            [colors['green'], colors['blue'], colors['red']],
            [colors['blue'], colors['red'], colors['green']]
        ]
    elif pattern_type == 'd':
        color_pattern = [
            [colors['green'], colors['blue'], colors['red']],
            [colors['red'], colors['blue'], colors['green']],
            [colors['blue'], colors['red'], colors['green']]
        ]
    elif pattern_type == 'e':
        flat_colors = random.choices([colors['red'], colors['green'], colors['blue']], k=color_width * color_height)
        color_pattern = np.array(flat_colors).reshape(color_height, color_width, 3)
    elif pattern_type == 'f':
        flat_colors = random.choices([colors['red'], colors['green'], colors['blue']], k=color_width * color_height)
        color_pattern = np.array(flat_colors).reshape(color_height, color_width, 3)
    elif pattern_type == 'g':
        color_pattern = [
            [random.choice([colors['red'], colors['green'], colors['blue']]) for _ in range(color_width)]
            for _ in range(color_height)
        ]
    elif pattern_type == 'h':
        color_pattern = [
            [colors['red'], colors['green'], colors['blue'], colors['green'], colors['blue'], colors['red']],
            [colors['green'], colors['blue'], colors['red'], colors['blue'], colors['red'], colors['green']]
        ]
    elif pattern_type == 'i':
        total_cells = color_width * color_height
        flat_colors = ([colors['red']] * (total_cells // 3) +
                       [colors['green']] * (total_cells // 3) +
                       [colors['blue']] * (total_cells // 3))
        random.shuffle(flat_colors)
        color_pattern = np.array(flat_colors).reshape(color_height, color_width, 3)
    else:
        raise ValueError("Invalid pattern type. Choose 'a' through 'i'.")

    for y in range(color_height):
        for x in range(color_width):
            start_y = y * (cell_size + border_size)
            start_x = x * (cell_size + border_size)
            color = color_pattern[y % len(color_pattern)][x % len(color_pattern[0])]
            pattern_array[start_y + border_size:start_y + border_size + cell_size,
                          start_x + border_size:start_x + border_size + cell_size] = color

    return pattern_array[:final_height, :final_width]

def save_image(image, final_width, final_height, cell_size, border_size, pattern_type):
    desktop_path = '/Volumes/External SSD/Autochome Experiments/RGB Patterns'
    os.makedirs(desktop_path, exist_ok=True)

    pattern_name = {
        'a': 'bayer',
        'b': 'rgb',
        'c': 'diagonal_rgb',
        'd': 'custom_3x3',
        'e': 'uniform_distribution',
        'f': 'gaussian_distribution',
        'g': 'random_distribution',
        'h': 'balanced_6x6',
        'i': 'stochastic_distribution'
    }.get(pattern_type, 'unknown_pattern')

    filename = f"{pattern_name}_{final_width}x{final_height}_{cell_size}x{cell_size}_border{border_size}.tiff"
    full_path = os.path.join(desktop_path, filename)
    image.save(full_path)
    print(f"Image saved to: {full_path}")

def main():
    final_width, final_height, cell_size, border_size, pattern_type = prompt_for_dimensions()
    pattern_array = generate_pattern_with_custom_blocks(final_width, final_height, cell_size, border_size, pattern_type)
    image = Image.fromarray(pattern_array)
    save_image(image, final_width, final_height, cell_size, border_size, pattern_type)

if __name__ == "__main__":
    main()
