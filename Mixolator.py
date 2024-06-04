import pygame
import random
import sys
import webcolors
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Elixir Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)
SELECTED_COLOR = (100, 100, 255)

# Load images
background = pygame.image.load("potionbackground.png").convert_alpha()  # Load with alpha for transparency
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale the background to fit the screen
ethereal_pear = pygame.image.load("etherealpear.png")
flame_fruit = pygame.image.load("flamefruit.png")
gleam_berry = pygame.image.load("gleamberry.png")
moonbeam_melon = pygame.image.load("moonbeammelon.png")
shimmering_apple = pygame.image.load("shimmeringapple.png")
pb15 = pygame.image.load("pb15.png")  # Load the overlay image

# Resize fruit images
fruit_images = [gleam_berry, flame_fruit, shimmering_apple, ethereal_pear, moonbeam_melon]
fruit_images = [pygame.transform.scale(fruit, (50, 50)) for fruit in fruit_images]

# Scale the pb15 image to fit within a 100x100 box without distorting its aspect ratio
pb15_rect = pb15.get_rect()
if pb15_rect.width > pb15_rect.height:
    scale_factor = 100 / pb15_rect.width
else:
    scale_factor = 100 / pb15_rect.height
new_size = (int(pb15_rect.width * scale_factor), int(pb15_rect.height * scale_factor))
pb15 = pygame.transform.scale(pb15, new_size)

# RGB ranges for each fruit
fruit_rgb_ranges = {
    0: range(0, 51),     # Gleam Berry
    1: range(153, 204),  # Flame Fruit
    2: range(51, 102),   # Shimmering Apple
    3: range(102, 153),  # Ethereal Pear
    4: range(204, 255)   # Moonbeam Melon
}

# Personality keywords for each fruit
fruit_personality_keywords = {
    0: ["Dark", "Brooding", "Responsible", "Common"],  # Gleam Berry
    1: ["Distraction", "Fierce", "Fiery", "Showy"],  # Flame Fruit
    2: ["Speed", "Flightiness", "Drive", "Ambition"],  # Shimmering Apple
    3: ["Earthy", "Pragmatic", "Stout", "Loyal"],  # Ethereal Pear
    4: ["Angelic", "Unique", "Pure", "Self-righteous"]  # Moonbeam Melon
}

# Position of the fruit selection boxes
fruit_positions = [(100, 20), (250, 20), (400, 20), (550, 20), (700, 20)]

# Personality keywords for player selection
personality_keywords = [
    "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
    "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
    "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
    "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Create boxes for selections
selection_boxes = [pygame.Rect(150, 100, 100, 100), pygame.Rect(300, 100, 100, 100),
                   pygame.Rect(450, 100, 100, 100), pygame.Rect(600, 100, 100, 100)]

# Move the personality word selection box to the first position
selection_boxes.insert(0, selection_boxes.pop())

# Create mixalate button
mixalate_button = pygame.Rect(400, 250, 200, 50)

# Store selections
selections = [None, None, None, None]

# Store result elixir
elixir_color = None
elixir_personality = None
elixir_color_name = None
elixir_title = None

def closest_color(requested_color):
    min_colors = {}
    for key, name in CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(requested_color):
    try:
        closest_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)
    return closest_name

def draw_screen():
    # Draw the color swatch in the center of the screen behind the background
    if elixir_color:
         pygame.draw.rect(screen, elixir_color, pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 400, 400))

    # Draw the background on top
    screen.blit(background, (0, 0))

    # Draw fruit options at the top
    for i, pos in enumerate(fruit_positions):
        if pygame.Rect(pos[0], pos[1], 50, 50).collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, HOVER_COLOR, pygame.Rect(pos[0] - 5, pos[1] - 5, 60, 60))
        screen.blit(fruit_images[i], pos)

    # Draw selection boxes
    for i, box in enumerate(selection_boxes):
        pygame.draw.rect(screen, GREY if selections[i] is None else SELECTED_COLOR, box)
        if selections[i] is None:
            text = font.render("?", True, BLACK)
            screen.blit(text, (box.x + 35, box.y + 35))
        else:
            if i == 0:  # Personality word selection
                text = font.render(personality_keywords[selections[i]], True, BLACK)
                screen.blit(text, (box.x + 5, box.y + 35))
            else:  # Fruit selections
                screen.blit(fruit_images[selections[i]], (box.x + 25, box.y + 15))
                fruit_name_lines = ["Gleam Berry", "Flame Fruit", "Shimmering Apple", "Ethereal Pear", "Moonbeam Melon"][selections[i]].split()
                for line_index, line in enumerate(fruit_name_lines):
                    text = small_font.render(line, True, BLACK)
                    screen.blit(text, (box.x + 5, box.y + 75 + 20 * line_index))

    # Draw personality word options on the left
    for i, keyword in enumerate(personality_keywords):
        color = HOVER_COLOR if pygame.Rect(10, 100 + 30 * i, 200, 30).collidepoint(pygame.mouse.get_pos()) else BLACK
        text = small_font.render(keyword, True, color)
        screen.blit(text, (10, 100 + 30 * i))

    # Draw mixalate button
    pygame.draw.rect(screen, GREY if None in selections else WHITE, mixalate_button)
    text = font.render("Mixalate", True, BLACK)
    screen.blit(text, (mixalate_button.x + 10, mixalate_button.y + 10))

    if elixir_color and elixir_personality and elixir_color_name and elixir_title:
        pygame.draw.rect(screen, elixir_color, pygame.Rect(800, 500, 100, 100))
        pb15_x = 800 + (100 - new_size[0]) // 2  # Center the pb15 image within the 100x100 box
        pb15_y = 500 + (100 - new_size[1]) // 2
        screen.blit(pb15, (pb15_x, pb15_y))  # Overlay the pb15 image
        for i, word in enumerate(elixir_personality):
            text = small_font.render(word, True, BLACK)
            screen.blit(text, (910, 500 + i * 30))
        color_name_text = small_font.render(elixir_color_name, True, BLACK)
        screen.blit(color_name_text, (800, 610))
        title_text = small_font.render(elixir_title, True, BLACK)
        screen.blit(title_text, (800, 640))

    pygame.display.flip()

def main():
    global elixir_color, elixir_personality, elixir_color_name, elixir_title
    running = True
    selected_box = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, box in enumerate(selection_boxes):
                    if box.collidepoint(x, y):
                        selected_box = i
                for i, pos in enumerate(fruit_positions):
                    if pygame.Rect(pos[0], pos[1], 50, 50).collidepoint(x, y):
                        if selected_box is not None and selected_box > 0:
                            selections[selected_box] = i
                            selected_box = None
                for i in range(len(personality_keywords)):
                    if pygame.Rect(10, 100 + 30 * i, 200, 30).collidepoint(x, y):
                        if selected_box == 0:
                            selections[selected_box] = i
                            selected_box = None
                if mixalate_button.collidepoint(x, y) and None not in selections:
                    # Create dragon elixir
                    r = random.choice(fruit_rgb_ranges[selections[1]])
                    g = random.choice(fruit_rgb_ranges[selections[2]])
                    b = random.choice(fruit_rgb_ranges[selections[3]])
                    elixir_color = (r, g, b)
                    elixir_color_name = get_color_name(elixir_color)
                    elixir_personality = [
                        random.choice(fruit_personality_keywords[selections[i]]) for i in range(1, 4)
                    ]
                    elixir_personality.insert(0, personality_keywords[selections[0]])
                    elixir_title = f"{personality_keywords[selections[0]]} {elixir_color_name} Elixir of Dragon Breeding"
                    print(f"Dragon Elixir Created! Color: {elixir_color_name}, Personality: {elixir_personality}")

        draw_screen()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

