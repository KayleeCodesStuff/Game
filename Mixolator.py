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
background = pygame.image.load("potionbackground.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale the background to fit the screen
ethereal_pear = pygame.image.load("etherealpear.png")
flame_fruit = pygame.image.load("flamefruit.png")
gleam_berry = pygame.image.load("gleamberry.png")
moonbeam_melon = pygame.image.load("moonbeammelon.png")
shimmering_apple = pygame.image.load("shimmeringapple.png")

# Resize fruit images
fruit_images = [gleam_berry, flame_fruit, shimmering_apple, ethereal_pear, moonbeam_melon]
fruit_images = [pygame.transform.scale(fruit, (50, 50)) for fruit in fruit_images]

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

# Create mixalate button
mixalate_button = pygame.Rect(400, 250, 200, 50)

# Store selections
selections = [None, None, None, None]

# Store result elixir
elixir_color = None
elixir_personality = None
elixir_color_name = None

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
            if i < 3:  # Fruit selections
                screen.blit(fruit_images[selections[i]], (box.x + 25, box.y + 25))
                fruit_name = ["Gleam Berry", "Flame Fruit", "Shimmering Apple", "Ethereal Pear", "Moonbeam Melon"][selections[i]]
                text = small_font.render(fruit_name, True, BLACK)
                screen.blit(text, (box.x, box.y + 75))
            else:  # Personality word selection
                text = font.render(personality_keywords[selections[i]], True, BLACK)
                screen.blit(text, (box.x + 5, box.y + 35))

    # Draw personality word options on the right
    for i, keyword in enumerate(personality_keywords):
        color = HOVER_COLOR if pygame.Rect(WIDTH - 250, 100 + 30 * i, 200, 30).collidepoint(pygame.mouse.get_pos()) else BLACK
        text = small_font.render(keyword, True, color)
        screen.blit(text, (WIDTH - 250, 100 + 30 * i))

    # Draw mixalate button
    pygame.draw.rect(screen, GREY if None in selections else WHITE, mixalate_button)
    text = font.render("Mixalate", True, BLACK)
    screen.blit(text, (mixalate_button.x + 10, mixalate_button.y + 10))

    # Draw elixir result if created
    if elixir_color and elixir_personality:
        pygame.draw.rect(screen, elixir_color, pygame.Rect(50, 500, 100, 100))
        for i, word in enumerate(elixir_personality):
            text = small_font.render(word, True, BLACK)
            screen.blit(text, (160, 500 + i * 30))
        color_name_text = small_font.render(elixir_color_name, True, BLACK)
        screen.blit(color_name_text, (50, 610))

    pygame.display.flip()

def main():
    global elixir_color, elixir_personality, elixir_color_name
    running = True
    selected_box = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event
