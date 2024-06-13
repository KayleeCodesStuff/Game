import pygame
import random
import sys
import sqlite3
import os
from game import load_inventory_data, save_inventory_data, save_elixir_data, draw_inventory, define_elixir_data

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Hatchery")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Load images
background = pygame.image.load("hatchery.png").convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
unhatched_egg_image = pygame.image.load("unhatched.png").convert_alpha()

# Resize egg images and create egg rectangles with increased spacing
egg_size = (80, 80)
unhatched_egg_image = pygame.transform.scale(unhatched_egg_image, egg_size)
egg_positions = []
egg_colors = [WHITE] * 10  # Initialize each egg's color to WHITE
egg_images = [unhatched_egg_image] * 10  # Initialize each egg's image to unhatched

# Load and resize egg images
black_egg = pygame.image.load("black_egg.png")
black_egg = pygame.transform.scale(black_egg, egg_size)

white_egg = pygame.image.load("white_egg.png")
white_egg = pygame.transform.scale(white_egg, egg_size)

rainbow_egg = pygame.image.load("rainbow_egg.png")
rainbow_egg = pygame.transform.scale(rainbow_egg, egg_size)

metallic_egg = pygame.image.load("metallic_egg.png")
metallic_egg = pygame.transform.scale(metallic_egg, egg_size)

# Create a dictionary for egg images
egg_images_dict = {
    "Black": black_egg,
    "White": white_egg,
    "Rainbow": rainbow_egg,
    "Metallic": metallic_egg
}

# Define inventory and egg counts (extracted from breeding.py)
fruit_names = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear", "moonbeammelon"]
fruit_images_dict = {  # Make sure to load the corresponding images
    "gleamberry": pygame.image.load("gleamberry.png"),
    "flamefruit": pygame.image.load("flamefruit.png"),
    "shimmeringapple": pygame.image.load("shimmeringapple.png"),
    "etherealpear": pygame.image.load("etherealpear.png"),
    "moonbeammelon": pygame.image.load("moonbeammelon.png")
}

# Resize fruit images
fruit_images_dict = {
    "gleamberry": pygame.transform.scale(pygame.image.load("gleamberry.png"), (50, 50)),
    "flamefruit": pygame.transform.scale(pygame.image.load("flamefruit.png"), (50, 50)),
    "shimmeringapple": pygame.transform.scale(pygame.image.load("shimmeringapple.png"), (50, 50)),
    "etherealpear": pygame.transform.scale(pygame.image.load("etherealpear.png"), (50, 50)),
    "moonbeammelon": pygame.transform.scale(pygame.image.load("moonbeammelon.png"), (50, 50))
}

# Initialize inventory and egg counts
inventory, egg_counts, inventory_slots = load_inventory_data()

# Add these lines before the main function
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

# Adjust padding between eggs
EGG_PADDING = 200

# Function to check for overlapping rectangles
# Function to check for overlapping rectangles
def is_overlapping(new_rect, rect_list):
    for rect in rect_list:
        if new_rect.colliderect(rect):
            return True
    return False


# Create non-overlapping egg positions with increased padding
while len(egg_positions) < 10:
    pos = (random.randint(EGG_PADDING, WIDTH - EGG_PADDING - 80), random.randint(EGG_PADDING, HEIGHT - EGG_PADDING - 80))
    new_rect = pygame.Rect(pos, egg_size)
    if not is_overlapping(new_rect, egg_positions):
        egg_positions.append(new_rect)

# Create inventory slots with a fixed offset from the left side of the screen
x_offset = WIDTH - (60 * len(inventory_slots))
inventory_boxes = [pygame.Rect(x_offset + (60 * i), HEIGHT - 100, 50, 50) for i in range(10)]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Primary traits
primary_traits = [
    "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
    "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
    "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
    "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
]

# Combined secondary traits list from mixalator
secondary_traits_list = [
    "Dark", "Brooding", "Responsible", "Common",
    "Distraction", "Fierce", "Fiery", "Showy",
    "Speed", "Flightiness", "Drive", "Ambition",
    "Earthy", "Pragmatic", "Stout", "Loyal",
    "Angelic", "Unique", "Pure", "Self-righteous"
]

def draw_screen(selected_egg_index):
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)  # Draw red outline
        pygame.draw.rect(screen, egg_colors[i], rect)  # Draw the egg with its current color
        screen.blit(egg_images[i], rect.topleft)  # Draw the correct egg image

    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()

# Database connections
current_dir = os.path.dirname(os.path.abspath(__file__))
dragons_db_path = os.path.join(current_dir, 'dragonsedit.db')
save_db_path = os.path.join(current_dir, 'save.db')

try:
    dragons_conn = sqlite3.connect(dragons_db_path)
    dragons_cursor = dragons_conn.cursor()
    dragons_cursor.execute("SELECT * FROM dragons;")
    dragons = dragons_cursor.fetchall()
    dragons_conn.close()
except sqlite3.OperationalError as e:
    print(f"Error opening dragons database: {e}")

try:
    save_conn = sqlite3.connect(save_db_path)
    save_cursor = save_conn.cursor()
    save_cursor.execute("SELECT * FROM elixirs;")
    elixirs = save_cursor.fetchall()
    save_cursor.execute("SELECT * FROM eggs;")
    eggs = save_cursor.fetchall()
    save_conn.close()
except sqlite3.OperationalError as e:
    print(f"Error opening save database: {e}")

def display_egg_menu(selected_egg_index):
    running = True
    menu_font = pygame.font.Font(None, 28)
    menu_rects = []
    
    while running:
        screen.fill(GREY)
        menu_rects.clear()  # Clear the list to avoid duplication

        for i, egg in enumerate(eggs):
            item_text = f"ID: {egg[0]}, Phenotype: {egg[2]}, Parents: {egg[4]} & {egg[5]}"  # Assuming egg[0] is the ID, egg[2] is the phenotype, egg[4] is parent 1, and egg[5] is parent 2
            text_surf = menu_font.render(item_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 50 + i * 30))
            screen.blit(text_surf, text_rect)
            menu_rects.append((text_rect, i))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for rect, index in menu_rects:
                    if rect.collidepoint(x, y):
                        selected_egg = eggs[index]
                        phenotype = selected_egg[2]
                        
                        # Update the egg image based on the phenotype
                        if phenotype in egg_images_dict:
                            egg_images[selected_egg_index] = egg_images_dict[phenotype]
                        else:
                            egg_images[selected_egg_index] = unhatched_egg_image  # Default image if phenotype not found

                        print(f"Selected egg: {selected_egg}")
                        running = False
                        break

def get_statistical_pool(elixir, nurture_trait, dragons):
    pool = []

    elixir_primary = elixir[3]
    elixir_secondaries = elixir[4].split(',')

    for dragon in dragons:
        chances = 0

        # Check for shared primary trait
        if dragon[4] == elixir_primary:
            chances += 1

        # Check for shared secondary traits
        dragon_secondaries = dragon[5].split(',')
        for secondary in elixir_secondaries:
            if secondary in dragon_secondaries:
                chances += 1

        # Check for shared nurture trait
        if dragon[10] == nurture_trait:
            chances += 1

        if chances > 0:
            pool.extend([dragon] * chances)

    return pool

def filter_pool_by_phenotype_and_rgb(pool, egg, elixir_rgb):
    filtered_pool = []

    egg_phenotype = egg[2]
    elixir_rgb_value = eval(elixir_rgb)  # Convert string representation of RGB to tuple

    for dragon in pool:
        dragon_phenotype = dragon[2]
        dragon_rgb_range = eval(dragon[9])  # Convert string representation of RGB range to tuple

        # Check phenotype
        if egg_phenotype in ["Metallic", "Gold", "Silver"] and dragon_phenotype != "Metallic":
            continue
        elif egg_phenotype != dragon_phenotype:
            continue

        # Check RGB range
        if not (dragon_rgb_range[0] <= elixir_rgb_value[0] <= dragon_rgb_range[1] and
                dragon_rgb_range[0] <= elixir_rgb_value[1] <= dragon_rgb_range[1] and
                dragon_rgb_range[0] <= elixir_rgb_value[2] <= dragon_rgb_range[1]):
            continue

        filtered_pool.append(dragon)

    return filtered_pool

def select_dragon_from_pool(filtered_pool):
    if not filtered_pool:
        return None
    return random.choice(filtered_pool)

# Update the main function call to display the egg menu correctly
def main():
    global elixir_color
    elixir_color = None  # Initialize elixir_color
    running = True
    selected_egg_index = None

    # Load inventory data at the start of the game
    inventory, egg_counts, inventory_slots = load_inventory_data()

    # Define elixir_data
    elixir_data = define_elixir_data()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                print(f"Mouse clicked at: {event.pos}")
                # Check if an egg was clicked
                egg_selected = False
                for j, egg_rect in enumerate(egg_positions):
                    if egg_rect.collidepoint(x, y):
                        # Select the clicked egg
                        selected_egg_index = j
                        egg_selected = True
                        print(f"Egg {j} selected at position {egg_rect.topleft}")
                        display_egg_menu(selected_egg_index)  # Display egg selection menu
                        break

                if not egg_selected:
                    # Check if an inventory slot was clicked
                    for i, rect in enumerate(inventory_boxes):
                        if rect.collidepoint(x, y) and inventory_slots[i] is not None:
                            selected_elixir = inventory_slots[i]
                            elixir_color = selected_elixir[0]
                            if selected_egg_index is not None:
                                # Apply the elixir to the selected egg
                                egg_colors[selected_egg_index] = elixir_color
                                # Remove the elixir from the inventory
                                inventory_slots[i] = None
                                elixir_color = None
                                selected_egg_index = None  # Reset the selected egg index
                            break

        draw_screen(selected_egg_index)

    # Save inventory data before exiting
    save_elixir_data("save.db", elixir_data, inventory)
    save_inventory_data()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
