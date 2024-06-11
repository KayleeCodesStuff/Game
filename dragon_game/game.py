import pygame
import random
import sqlite3
import logging

# Configure logging
logging.basicConfig(filename='game.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_pygame():
    try:
        pygame.init()
        logging.info("Pygame initialized successfully")
        print("Pygame initialized successfully")
    except pygame.error as e:
        logging.error(f"Error initializing pygame: {e}")
        print(f"Error initializing pygame: {e}")

def initialize_fonts():
    try:
        global font, small_font
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        logging.info("Fonts initialized successfully")
        print("Fonts initialized successfully")
    except pygame.error as e:
        logging.error(f"Error initializing fonts: {e}")
        print(f"Error initializing fonts: {e}")

# Call initialization functions
initialize_pygame()
initialize_fonts()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Load images with error handling
def load_image(file_name, scale_to):
    try:
        image = pygame.image.load(file_name).convert_alpha()
        logging.info(f"Loaded image {file_name}")
        return pygame.transform.scale(image, scale_to)
    except pygame.error as e:
        logging.error(f"Error loading image {file_name}: {e}")
        print(f"Error loading image {file_name}: {e}")
        return pygame.Surface(scale_to)  # Return a blank surface as a placeholder

background = load_image("background.png", (WIDTH, HEIGHT))

fruit_images_dict = {
    "gleamberry": load_image("gleamberry.png", (50, 50)),
    "flamefruit": load_image("flamefruit.png", (50, 50)),
    "shimmeringapple": load_image("shimmeringapple.png", (50, 50)),
    "etherealpear": load_image("etherealpear.png", (50, 50)),
    "moonbeammelon": load_image("moonbeammelon.png", (50, 50))
}

egg_images_dict = {
    "Black": load_image("black_egg.png", (50, 50)),
    "White": load_image("white_egg.png", (50, 50)),
    "Rainbow": load_image("rainbow_egg.png", (50, 50)),
    "Metallic": load_image("metallic_egg.png", (50, 50))
}

# Initialize inventory and egg counts
fruit_names = list(fruit_images_dict.keys())
inventory = {fruit: 5 for fruit in fruit_names}
egg_counts = {egg: 0 for egg in egg_images_dict.keys()}

# Inventory slots
inventory_slots = [None] * 10

# Create inventory slots
inventory_boxes = [pygame.Rect(WIDTH - 600 + i * 60, HEIGHT - 100, 50, 50) for i in range(10)]

# Define traits lists
primary_traits = [
    "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
    "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
    "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
    "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
]

secondary_traits_list = [
    "Dark", "Brooding", "Responsible", "Common",
    "Distraction", "Fierce", "Fiery", "Showy",
    "Speed", "Flightiness", "Drive", "Ambition",
    "Earthy", "Pragmatic", "Stout", "Loyal",
    "Angelic", "Unique", "Pure", "Self-righteous"
]

def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_inventory(surface, inventory, eggs, inventory_slots, selected_inventory_slot=None):
    pygame.draw.rect(surface, BLUE, (0, HEIGHT - 100, WIDTH, 100))

    y_offset = HEIGHT - 90

    # Draw the fruits in the first section
    x_offset = 10
    for fruit, image in fruit_images_dict.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(inventory[fruit]), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw a separator line
    pygame.draw.line(surface, WHITE, (x_offset, HEIGHT - 100), (x_offset, HEIGHT))

    # Draw the eggs in the second section, even if they might not be used
    x_offset += 10
    for egg_type, count in eggs.items():
        egg_image = egg_images_dict[egg_type]
        surface.blit(egg_image, (x_offset, y_offset))
        draw_text(surface, str(count), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw the elixirs in the third section
    x_offset = WIDTH - 60 * len(inventory_slots)
    for i, slot in enumerate(inventory_slots):
        box_rect = pygame.Rect(x_offset, y_offset, 50, 50)
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)
        if slot is None:
            draw_text(surface, "?", small_font, WHITE, (x_offset + 15, y_offset + 15))
        else:
            color, image_filename = slot
            pygame.draw.rect(surface, color, box_rect)
            image = load_image(image_filename, (50, 50))
            surface.blit(image, (x_offset, y_offset))
        x_offset += 60
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)

def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}
    egg_counts = {egg: 0 for egg in egg_images_dict.keys()}

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

    except sqlite3.Error as e:
        logging.error(f"SQLite error loading inventory data: {e}")
        print(f"SQLite error loading inventory data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error loading inventory data: {e}")
        print(f"Unexpected error loading inventory data: {e}")

def generate_and_add_random_elixir():
    primary_trait = random.choice(primary_traits)
    secondary_traits = random.sample(secondary_traits_list, 3)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb_value = (r, g, b)
    for i in range(len(inventory_slots)):
        if inventory_slots[i] is None:
            image_file = "pb1.png"
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

def save_elixir_data(file_path, elixir_data, fruit_counts):
    try:
        with sqlite3.connect(file_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO elixirs (rgb, title, primary_trait, secondary_traits, image_file, position)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (str(elixir_data['rgb']), elixir_data['title'], elixir_data['primary_trait'],
                            ', '.join(elixir_data['secondary_traits']), elixir_data['image_file'], elixir_data['position']))

            for fruit, count in fruit_counts.items():
                cursor.execute('''INSERT INTO inventory (fruit, count)
                                  VALUES (?, ?)
                                  ON CONFLICT(fruit) DO UPDATE SET count = excluded.count''', (fruit, count))

            conn.commit()
            logging.info("Elixir data saved successfully")
            print("Elixir data saved successfully")
    except sqlite3.Error as e:
        logging.error(f"SQLite error saving elixir data: {e}")
        print(f"SQLite error saving elixir data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error saving elixir data: {e}")
        print(f"Unexpected error saving elixir data: {e}")

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
            logging.info("Inventory data saved successfully")
            print("Inventory data saved successfully")
    except sqlite3.Error as e:
        logging.error(f"SQLite error saving inventory data: {e}")
        print(f"SQLite error saving inventory data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error saving inventory data: {e}")
        print(f"Unexpected error saving inventory data: {e}")

# Example of handling errors during game loop
def game_loop():
    running = True
    selected_inventory_slot = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(GREY)
        screen.blit(background, (0, 0))

        # Draw inventory with error handling
        try:
            draw_inventory(screen, inventory, egg_counts, inventory_slots, selected_inventory_slot)
        except pygame.error as e:
            logging.error(f"Error drawing inventory: {e}")
            print(f"Error drawing inventory: {e}")

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")
    print("Game loop ended")

# Call load_inventory_data with exception handling
try:
    load_inventory_data()
    logging.info("Initial inventory data loaded successfully")
    print("Initial inventory data loaded successfully")
except Exception as e:
    logging.error(f"Error loading initial inventory data: {e}")
    print(f"Error loading initial inventory data: {e}")

# Start the game loop
try:
    game_loop()
except Exception as e:
    logging.error(f"Error during game loop: {e}")
    print(f"Error during game loop: {e}")
finally:
    save_inventory_data()

