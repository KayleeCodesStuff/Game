import pygame
import os
import random
import sys
import webcolors
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb
import tkinter as tk
from tkinter import filedialog
from game import *


pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
INVENTORY_HEIGHT = 100  # Height reserved for inventory at the bottom
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Elixir Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)
SELECTED_COLOR1 = (100, 100, 255)
SELECTED_COLOR2 = (255, 100, 100)
TEXT_HIGHLIGHT = (255, 0, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Ensure the correct path is used for all images
assets_path = os.path.join(os.path.dirname(__file__), 'assets', 'images')

# Load images
background = load_and_resize_image(os.path.join(assets_path, "potionbackgroundscaled.png"), (WIDTH, HEIGHT))
ethereal_pear = load_and_resize_image(os.path.join(assets_path, "etherealpear.png"), (50, 50))
flame_fruit = load_and_resize_image(os.path.join(assets_path, "flamefruit.png"), (50, 50))
gleam_berry = load_and_resize_image(os.path.join(assets_path, "gleamberry.png"), (50, 50))
moonbeam_melon = load_and_resize_image(os.path.join(assets_path, "moonbeammelon.png"), (50, 50))
shimmering_apple = load_and_resize_image(os.path.join(assets_path, "shimmeringapple.png"), (50, 50))



# Resize fruit images
fruit_images = [gleam_berry, flame_fruit, shimmering_apple, ethereal_pear, moonbeam_melon]
fruit_names = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear", "moonbeammelon"]
fruit_images_dict = dict(zip(fruit_names, fruit_images))


# RGB ranges for each fruit
fruit_rgb_ranges = {
    "gleamberry": range(0, 51),
    "flamefruit": range(51, 102),
    "shimmeringapple": range(102, 153),
    "etherealpear": range(153, 204),
    "moonbeammelon": range(204, 255)
}
#egg_counts = {"Black": 0, "White": 0, "Rainbow": 0, "Metallic": 0}

inventory, egg_counts, inventory_slots = load_inventory_data()
#load_inventory_data()

# Personality keywords for each fruit
fruit_personality_keywords = {
    "gleamberry": ["Dark", "Brooding", "Responsible", "Common"],
    "flamefruit": ["Distraction", "Fierce", "Fiery", "Showy"],
    "shimmeringapple": ["Speed", "Flightiness", "Drive", "Ambition"],
    "etherealpear": ["Earthy", "Pragmatic", "Stout", "Loyal"],
    "moonbeammelon": ["Angelic", "Unique", "Pure", "Self-righteous"]
}

# Personality keywords for player selection
personality_keywords = [
    "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
    "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
    "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
    "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
]

# Define the "Bottle Elixir" button
bottle_button = pygame.Rect(850, HEIGHT - 150, 120, 40)

# Define the "delete" button
delete_button = pygame.Rect(850, HEIGHT - 200, 120, 40)

# List of image filenames
image_filenames = [os.path.join(assets_path, 'pb{}.png'.format(i)) for i in range(1, 13)]



# Define inventory slots
#inventory_slots = [None] * 10  # None means empty, else it will store the color and image

# Create inventory slots
inventory_boxes = [pygame.Rect(20 + i * 60, HEIGHT - 100, 50, 50) for i in range(10)]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
fancy_font = pygame.font.Font(pygame.font.match_font('georgia', bold=True), 32)
fancy_small_font = pygame.font.Font(pygame.font.match_font('timesnewroman', bold=True), 28)

# Create boxes for selections,
selection_boxes = [
    pygame.Rect(10, 640, 200, 65),  # Primary trait selection box
    pygame.Rect(10, 720, 80, 65),   # First fruit selection box
    pygame.Rect(100, 720, 80, 65),  # Second fruit selection box
    pygame.Rect(190, 720, 80, 65)   # Third fruit selection box
]

# Create mixalate button
mixalate_button = pygame.Rect(540, 530, 120, 40)

# Store selections
selections = [None, None, None, None]

# Store result elixir
elixir_color = None
elixir_personality = None
elixir_color_name = None
elixir_title = None

def draw_delete_button():
    delete_button_rect = pygame.Rect(850, HEIGHT - 200, 120, 40)
    color = RED
    text = "Delete"
    
    # Draw the button with beveled edges
    pygame.draw.rect(screen, color, delete_button_rect, border_radius=10)
    # Outline with white color
    pygame.draw.rect(screen, WHITE, delete_button_rect, 2, border_radius=10)
    text_surface = small_font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=delete_button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return delete_button_rect

def draw_bottle_button():
    bottle_button_rect = pygame.Rect(850, HEIGHT - 150, 120, 40)
    color = RED
    text = "Bottle"
    
    # Draw the button with beveled edges
    pygame.draw.rect(screen, color, bottle_button_rect, border_radius=10)
    # Outline with white color
    pygame.draw.rect(screen, WHITE, bottle_button_rect, 2, border_radius=10)
    text_surface = small_font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=bottle_button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return bottle_button_rect

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
    return closest_name.capitalize()

def draw_text(screen, text, font, color, rect, highlight=None):
    if highlight:
        highlight_surface = font.render(text, True, elixir_color)
        screen.blit(highlight_surface, (rect.x + 1, rect.y + 1))
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, rect)

def draw_beveled_button(screen, rect, color, text=None, font=None, text_color=BLACK):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.line(screen, WHITE, rect.topleft, (rect.right, rect.top), 3)
    pygame.draw.line(screen, WHITE, rect.topleft, (rect.left, rect.bottom), 3)
    pygame.draw.line(screen, BLACK, rect.bottomleft, (rect.right, rect.bottom), 3)
    pygame.draw.line(screen, BLACK, rect.topright, (rect.right, rect.bottom), 3)
    
    if text and font:
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_gradient_rect(screen, rect, color1, color2):
    for y in range(rect.top, rect.bottom):
        blend = (y - rect.top) / (rect.height)
        color = [
            int(color1[i] * (1 - blend) + color2[i] * blend)
            for i in range(3)
        ]
        pygame.draw.line(screen, color, (rect.left, y), (rect.right, y))
def draw_beveled_box(screen, rect, border_color, fill_color=WHITE, outline_thickness=12):
    pygame.draw.rect(screen, fill_color, rect)
    pygame.draw.line(screen, border_color, rect.topleft, (rect.right, rect.top), outline_thickness)
    pygame.draw.line(screen, border_color, rect.topleft, (rect.left, rect.bottom), outline_thickness)
    pygame.draw.line(screen, border_color, rect.bottomleft, (rect.right, rect.bottom), outline_thickness)
    pygame.draw.line(screen, border_color, rect.topright, (rect.right, rect.bottom), outline_thickness)


def draw_screen(selected_box, selected_inventory_slot):
    # Clear screen
    screen.fill(BLACK)
    
    if elixir_color:
        pygame.draw.rect(screen, elixir_color, (0, 0, WIDTH, HEIGHT))  # Draw the background image, moved up to align with the inventory
    
    screen.blit(background, (0, -100))  # Adjust the y-coordinate to move the background up

    # Draw a beveled box behind the primary trait selection list
    beveled_box_rect = pygame.Rect(5, 5, 150, 620)  # Adjust dimensions and position as needed
    border_color = elixir_color if elixir_color else GREY  # Default to GREY if elixir_color is not set
    draw_beveled_box(screen, beveled_box_rect, border_color)
    
    # Draw the selection boxes
    for i, box in enumerate(selection_boxes):
        if i == selected_box:  # Highlight the selected box
            draw_gradient_rect(screen, box, SELECTED_COLOR1, SELECTED_COLOR2)  # Draw a gradient in the selected box
        else:
            pygame.draw.rect(screen, GREY if selections[i] is None else SELECTED_COLOR1, box)
        if selections[i] is not None:
            if i == 0:  # Personality word selection
                text = font.render(personality_keywords[selections[i]], True, BLACK)
                screen.blit(text, (box.x + (box.width - text.get_width()) // 2, box.y + (box.height - text.get_height()) // 2))
            else:  # Fruit selections
                screen.blit(fruit_images[selections[i]], (box.x + 15, box.y + 15))

    # Draw personality word options on the left
    for i, keyword in enumerate(personality_keywords):
        color = HOVER_COLOR if pygame.Rect(10, 10 + 30 * i, 200, 30).collidepoint(pygame.mouse.get_pos()) else BLACK
        text = small_font.render(keyword, True, color)
        screen.blit(text, (20, 20 + 30 * i))

    # Draw mixalate button with rainbow gradient and beveled edges
    gradient_rect = pygame.Rect(mixalate_button.x - 5, mixalate_button.y - 5, mixalate_button.width + 10, mixalate_button.height + 10)
    draw_gradient_rect(screen, gradient_rect, (255, 0, 0), (0, 0, 255))  # Simple gradient from red to blue for demonstration
    draw_beveled_button(screen, mixalate_button, GREY if None in selections else WHITE, "Mixalate", font)

    # Draw elixir result if created
    if elixir_color and elixir_personality and elixir_color_name and elixir_title:
        # Draw the elixir result title with an x offset
        x_offset = 50  # Adjust the offset as needed
        title_text = fancy_font.render(elixir_title, True, BLACK)
        text_rect = pygame.Rect((WIDTH//2 - title_text.get_width()//2) + x_offset, 250, title_text.get_width(), title_text.get_height())
        draw_text(screen, elixir_title, fancy_font, BLACK, text_rect, highlight=elixir_color_name)

        # Draw the trait words in two columns of two under the Mixalate button
        for i, word in enumerate(elixir_personality):
            text = fancy_small_font.render(word, True, WHITE)
            col = i % 2  # Column 0 or 1
            row = i // 2  # Row 0 or 1
            x_pos = 430 + col * 180  # Base x-coordinate for columns
            screen.blit(text, (x_pos + (150 - text.get_width()) // 2, 585 + row * 40))  # Adjusted position

        # Draw "Bottle" button
        gradient_rect = pygame.Rect(bottle_button.x - 5, bottle_button.y - 5, bottle_button.width + 10, bottle_button.height + 10)
        draw_gradient_rect(screen, gradient_rect, (255, 0, 0), (0, 0, 255))  # Same gradient as Mixalate button
        draw_beveled_button(screen, bottle_button, GREY, "Bottle", font)  # Same style as Mixalate button
        draw_beveled_button(screen, delete_button, GREY, "Delete", font)

    # Draw buttons
    back_button_rect = draw_back_to_hub_button()  # Draw the "Back to Hub" button
    delete_button_rect = draw_delete_button()  # Draw the "Delete" button
    bottle_button_rect = draw_bottle_button()  # Draw the "Bottle" button

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots, selected_inventory_slot)

    pygame.display.flip()


def main():
    global elixir_color, elixir_personality, elixir_color_name, elixir_title, selected_inventory_slot
    running = True
    selected_box = 0  # Start with the primary trait selection box selected
    selected_inventory_slot = None

    # Declare button rects at the beginning
    back_button_rect = None
    delete_button_rect = None
    bottle_button_rect = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                save_inventory_data()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Handle selection box clicks
                for i, box in enumerate(selection_boxes):
                    if box.collidepoint(x, y):
                        selected_box = i

                # Handle primary trait selection
                for i in range(len(personality_keywords)):
                    if pygame.Rect(10, 10 + 30 * i, 200, 30).collidepoint((x, y)):
                        if selected_box == 0:
                            selections[selected_box] = i
                            selected_box = 1  # Automatically move to the next selection box

                # Handle fruit selection
                x_offset = 10
                for i, fruit in enumerate(fruit_names):
                    if pygame.Rect(x_offset, HEIGHT - 90, 50, 50).collidepoint(x, y):
                        if selected_box is not None and selected_box > 0:
                            selections[selected_box] = i
                            selected_box += 1  # Move to the next selection box
                            if selected_box >= len(selection_boxes):
                                selected_box = None  # Deselect if all boxes are filled
                    x_offset += 60

                if mixalate_button.collidepoint(x, y) and None not in selections:
                    # Create dragon elixir
                    r = random.choice(fruit_rgb_ranges[fruit_names[selections[1]]])
                    g = random.choice(fruit_rgb_ranges[fruit_names[selections[2]]])
                    b = random.choice(fruit_rgb_ranges[fruit_names[selections[3]]])
                    elixir_color = (r, g, b)
                    elixir_color_name = get_color_name(elixir_color).capitalize()
                    elixir_personality = [
                        random.choice(fruit_personality_keywords[fruit_names[selections[i]]]) for i in range(1, 4)
                    ]
                    elixir_personality.insert(0, personality_keywords[selections[0]])
                    elixir_title = f"{elixir_color_name} {personality_keywords[selections[0]]} Dragon Egg Elixir"
                    # Remove used fruits from inventory
                    for i in range(1, 4):
                        fruit_name = fruit_names[selections[i]]
                        inventory[fruit_name] -= 1
                        print(f"Reduced {fruit_name} count to {inventory[fruit_name]}")

                    # Save the updated inventory
                    save_inventory_data()
                    print("Inventory data saved successfully")


                    # Assign primary trait and secondary traits separately
                    primary_trait = personality_keywords[selections[0]]
                    secondary_traits = elixir_personality[1:]  # Exclude the primary trait

                    # Create the elixir data but do not save it yet
                    elixir_data = {
                        'rgb': elixir_color,
                        'title': elixir_title,
                        'primary_trait': primary_trait,
                        'secondary_trait1': secondary_traits[0],  # First secondary trait
                        'secondary_trait2': secondary_traits[1],  # Second secondary trait
                        'secondary_trait3': secondary_traits[2],  # Third secondary trait
                        'image_file': random.choice(image_filenames),
                    }
                    logging.debug(f"Elixir data created: {elixir_data}")

                if elixir_color and bottle_button_rect.collidepoint(x, y):
                    try:
                        # Save the elixir data when the "Bottle" button is clicked
                        elixir_data['position'] = next(i for i, slot in enumerate(inventory_slots) if slot is None) + 1  # Find the next available slot
                        save_elixir_data(elixir_data)
                        save_inventory_data()
                        # Draw color swatch behind the background
                        pygame.draw.rect(screen, elixir_color, (0, 0, WIDTH, HEIGHT))

                        # Add the elixir to the inventory
                        for i in range(len(inventory_slots)):
                            if inventory_slots[i] is None:
                                image_file = elixir_data['image_file']
                                inventory_slots[i] = (elixir_color, image_file)
                                save_inventory_data()
                                break

                    except StopIteration:
                        print("Inventory is full! Cannot save more elixirs.")
                        # Handle full inventory case, e.g., display a message to the user or take other actions

                # Handle elixir slot click
                x_offset = WIDTH - 60 * len(inventory_slots)  # Start from the rightmost part of the screen
                y_offset = HEIGHT - 90
                for i in range(len(inventory_slots)):
                    if pygame.Rect(x_offset + i * 60, y_offset, 50, 50).collidepoint(x, y):
                        selected_inventory_slot = i

                # Handle delete button press
                if delete_button_rect.collidepoint(x, y) and selected_inventory_slot is not None:
                    delete_elixir_data(selected_inventory_slot + 1)
                    inventory_slots[selected_inventory_slot] = None
                    save_inventory_data()
                    selected_inventory_slot = None

                # Handle "Back to Hub" button press
                if back_button_rect.collidepoint(x, y):
                    running = False  # Exit the current loop to return to the hub

        # Draw the screen
        draw_screen(selected_box, selected_inventory_slot)

        # Update button rects
        back_button_rect = draw_back_to_hub_button()  # Draw the "Back to Hub" button
        delete_button_rect = draw_delete_button()  # Draw the "Delete" button
        bottle_button_rect = draw_bottle_button()  # Draw the "Bottle" button

        # Update the display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()