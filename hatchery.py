import pygame
import random
import sys
import sqlite3

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
egg_image = pygame.image.load("unhatched.png").convert_alpha()

# Resize egg images and create egg rectangles with increased spacing
egg_image = pygame.transform.scale(egg_image, (80, 80))
egg_positions = []
egg_colors = [WHITE] * 10  # Initialize each egg's color to WHITE

# Load and resize egg images
black_egg = pygame.image.load("black_egg.png")
black_egg = pygame.transform.scale(black_egg, (50, 50))

white_egg = pygame.image.load("white_egg.png")
white_egg = pygame.transform.scale(white_egg, (50, 50))

rainbow_egg = pygame.image.load("rainbow_egg.png")
rainbow_egg = pygame.transform.scale(rainbow_egg, (50, 50))

metallic_egg = pygame.image.load("metallic_egg.png")
metallic_egg = pygame.transform.scale(metallic_egg, (50, 50))

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
inventory = {fruit: 5 for fruit in fruit_names}
egg_counts = {"Black": 0, "White": 0, "Rainbow": 0, "Metallic": 0}

# Add these lines before the main function
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

# Adjust padding between eggs
EGG_PADDING = 200

# Function to check for overlapping rectangles
def is_overlapping(new_rect, rect_list):
    for rect in rect_list:
        if new_rect.colliderect(rect):
            return True
    return False

# Create non-overlapping egg positions with increased padding
while len(egg_positions) < 10:
    pos = (random.randint(EGG_PADDING, WIDTH - EGG_PADDING - 80), random.randint(EGG_PADDING, HEIGHT - EGG_PADDING - 80))
    new_rect = pygame.Rect(pos, (80, 80))
    if not is_overlapping(new_rect, egg_positions):
        egg_positions.append(new_rect)

# Inventory slots
inventory_slots = [None] * 10


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

# Function to generate a random elixir
def generate_random_elixir():
    primary_trait = random.choice(primary_traits)
    secondary_traits = random.sample(secondary_traits_list, 3)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb_value = (r, g, b)
    return primary_trait, secondary_traits, rgb_value

# Function to draw the inventory
def draw_inventory(surface, inventory, eggs, inventory_slots, selected_inventory_slot=None):
    pygame.draw.rect(surface, BLUE, (0, HEIGHT - 100, WIDTH, 100))  # Adjusted to fit within the screen dimensions

    y_offset = HEIGHT - 90  # Define y_offset for consistency

    # Draw the fruits in the first section
    x_offset = 10
    for fruit, image in fruit_images_dict.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(inventory[fruit]), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw a separator line
    pygame.draw.line(surface, WHITE, (x_offset, HEIGHT - 100), (x_offset, HEIGHT))

    # Draw the eggs in the second section
    x_offset += 10  # Add some padding after the separator
    for egg_type, count in eggs.items():
        egg_image = egg_images_dict[egg_type]
        surface.blit(egg_image, (x_offset, y_offset))
        draw_text(surface, str(count), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw the elixirs in the third section
    x_offset = WIDTH - 60 * len(inventory_slots)  # Start from the rightmost part of the screen
    for i, slot in enumerate(inventory_slots):
        box_rect = pygame.Rect(x_offset, y_offset, 50, 50)
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)  # Highlight selected slot
        if slot is None:
            # Draw empty slot with ?
            draw_text(surface, "?", small_font, WHITE, (x_offset + 15, y_offset + 15))
        else:
            color, image_filename = slot
            pygame.draw.rect(surface, color, box_rect)
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (50, 50))  # Resize the image to fit the box
            surface.blit(image, (x_offset, y_offset))
        x_offset += 60  # Move left for the next slot

        # Draw outline if this slot is selected
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)  # Draw the outline on top
def save_elixir_data(file_path, elixir_data, inventory):
    try:
        with sqlite3.connect(file_path) as conn:
            cursor = conn.cursor()
            # Insert elixir data
            cursor.execute('''INSERT INTO elixirs (rgb, title, primary_trait, secondary_traits, image_file, position)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (str(elixir_data['rgb']), elixir_data['title'], elixir_data['primary_trait'],
                            ', '.join(elixir_data['secondary_traits']), elixir_data['image_file'], elixir_data['position']))
            # Update fruit counts
            for fruit, count in inventory.items():
                cursor.execute('''INSERT INTO inventory (fruit, count)
                                  VALUES (?, ?)
                                  ON CONFLICT(fruit) DO UPDATE SET count = excluded.count''', (fruit, count))
            conn.commit()
    except Exception as e:
        print(f"Error saving elixir data: {e}")

def draw_screen(selected_egg_index):
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)  # Draw red outline
        pygame.draw.rect(screen, egg_colors[i], rect)  # Draw the egg with its current color
        screen.blit(egg_image, rect.topleft)

    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()
# Define the function to load inventory data from the database
def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}
    egg_counts = {"Black": 0, "White": 0, "Rainbow": 0, "Metallic": 0}

    # Load from the database
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fruit, count FROM inventory")
            rows = cursor.fetchall()
            for row in rows:
                fruit, count = row
                inventory[fruit] = count

            cursor.execute("SELECT phenotype, count FROM egg_inventory")
            rows = cursor.fetchall()
            for row in rows:
                phenotype, count = row
                egg_counts[phenotype] = count

            cursor.execute("SELECT rgb, image_file, position FROM elixirs")
            rows = cursor.fetchall()
            for row in rows:
                rgb = tuple(map(int, row[0][1:-1].split(', ')))
                image_file, position = row[1], row[2]
                inventory_slots[position - 1] = (rgb, image_file)

    except Exception as e:
        print(f"Error loading inventory data: {e}")

# Define the function to generate and add a random elixir
def generate_and_add_random_elixir():
    primary_trait, secondary_traits, rgb_value = generate_random_elixir()
    for i in range(len(inventory_slots)):
        if inventory_slots[i] is None:
            image_file = "pb1.png"  # Choose a default image file for the elixir
            inventory_slots[i] = (rgb_value, image_file)
            elixir_data = {
                'rgb': rgb_value,
                'title': f"{primary_trait} Elixir",
                'primary_trait': primary_trait,
                'secondary_traits': secondary_traits,
                'image_file': image_file,
                'position': i + 1
            }
            save_elixir_data('save.db', elixir_data, inventory)
            break

# Check if the inventory is empty and generate a random elixir if necessary
if all(slot is None for slot in inventory_slots):
    generate_and_add_random_elixir()

# Define the function to save inventory data to the database
def save_inventory_data():
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            for fruit, count in inventory.items():
                cursor.execute("UPDATE inventory SET count = ? WHERE fruit = ?", (count, fruit))
            for egg, count in egg_counts.items():
                cursor.execute("UPDATE egg_inventory SET count = ? WHERE phenotype = ?", (count, egg))
            cursor.execute("DELETE FROM elixirs")
            for i, slot in enumerate(inventory_slots):
                if slot is not None:
                    rgb, image_file = slot
                    cursor.execute("INSERT INTO elixirs (rgb, image_file, position) VALUES (?, ?, ?)", (str(rgb), image_file, i + 1))
            conn.commit()
    except Exception as e:
        print(f"Error saving inventory data: {e}")
def main():
    global elixir_color
    elixir_color = None  # Initialize elixir_color
    running = True
    selected_egg_index = None

    # Load inventory data at the start of the game
    load_inventory_data()

    # Check if the inventory is empty and generate a random elixir if necessary
    if all(slot is None for slot in inventory_slots):
        generate_and_add_random_elixir()

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
    save_inventory_data()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
