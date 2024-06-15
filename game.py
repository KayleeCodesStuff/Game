import pygame
import random
import sqlite3
import logging

# Configure logging
logging.basicConfig(filename='game.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define initialization functions
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

# Initialization function to be called on import
def initialize():
    initialize_pygame()
    initialize_fonts()

# Call initialization functions when the module is imported
initialize()

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
def define_elixir_data():
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

    image_filenames = ["pb1.png", "pb2.png", "pb3.png", "pb4.png", "pb5.png", "pb6.png", "pb7.png", "pb8.png", "pb9.png", "pb10.png", "pb11.png", "pb12.png"]

    primary_trait = random.choice(primary_traits)
    secondary_traits = random.sample(secondary_traits_list, 3)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb_value = (r, g, b)
    image_file = random.choice(image_filenames)  # Choose a random image file for the elixir

    elixir_data = {
        'rgb': rgb_value,
        'title': f"{primary_trait} Elixir",
        'primary_trait': primary_trait,
        'secondary_trait1': secondary_traits[0],  # First secondary trait
        'secondary_trait2': secondary_traits[1],  # Second secondary trait
        'secondary_trait3': secondary_traits[2],  # Third secondary trait
        'image_file': image_file,
        'position': 1  # Default position, change as necessary
    }
    return elixir_data



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
    inventory_slots = [None] * 10

    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()

            # Load fruits inventory
            cursor.execute("SELECT fruit, count FROM inventory")
            rows = cursor.fetchall()
            for row in rows:
                fruit, count = row
                inventory[fruit] = count

            # Load eggs counts from eggs table
            cursor.execute("SELECT phenotype, COUNT(*) FROM eggs GROUP BY phenotype")
            rows = cursor.fetchall()
            for row in rows:
                phenotype, count = row
                egg_counts[phenotype] = count

            # Load elixirs into inventory slots
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

    return inventory, egg_counts, inventory_slots

def create_egg(dragon1, dragon2, position):
    egg_genotype = get_egg_genotype(dragon1, dragon2)
    egg_phenotype = determine_phenotype(egg_genotype)
    egg_image = egg_images_dict[egg_phenotype]
    egg_image_path = os.path.join(DRAGON_IMAGE_FOLDER, f"{egg_phenotype.lower()}_egg.png")
    parent1_name = dragon1["name"]
    parent2_name = dragon2["name"]
    print(f"Created {egg_phenotype} egg with genotype {egg_genotype} at {position} from parents {parent1_name} and {parent2_name}")

    eggs_on_board.append({
        "genotype": egg_genotype,
        "phenotype": egg_phenotype,
        "image": egg_image,
        "rect": egg_image.get_rect(topleft=position)
    })

    # Database operations
    with sqlite3.connect(save_file) as conn:
        cursor = conn.cursor()

        # Insert a new row into the eggs table for the picked up egg
        cursor.execute("""
            INSERT INTO eggs (genotype, phenotype, image_file, parent1_name, parent2_name)
            VALUES (?, ?, ?, ?, ?)
        """, (str(egg_genotype), egg_phenotype, egg_image_path, parent1_name, parent2_name))

        # Check if the phenotype already exists in egg_inventory
        cursor.execute("SELECT count FROM egg_inventory WHERE phenotype=?", (egg_phenotype,))
        row = cursor.fetchone()
        if row:
            # If it exists, increment the count
            egg_count = row[0] + 1
            cursor.execute("UPDATE egg_inventory SET count=? WHERE phenotype=?", (egg_count, egg_phenotype))
        else:
            # If it does not exist, insert a new row with count 1
            cursor.execute("INSERT INTO egg_inventory (phenotype, count) VALUES (?, ?)", (egg_phenotype, 1))

        conn.commit()

import sqlite3
import logging

def save_elixir_data(elixir_data):
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            # Log each field explicitly
            logging.debug(f"RGB: {elixir_data['rgb']}")
            logging.debug(f"Title: {elixir_data['title']}")
            logging.debug(f"Primary Trait: {elixir_data['primary_trait']}")
            logging.debug(f"Secondary Trait 1: {elixir_data['secondary_trait1']}")
            logging.debug(f"Secondary Trait 2: {elixir_data['secondary_trait2']}")
            logging.debug(f"Secondary Trait 3: {elixir_data['secondary_trait3']}")
            logging.debug(f"Image File: {elixir_data['image_file']}")
            logging.debug(f"Position: {elixir_data['position']}")

            # Save the elixir data
            cursor.execute('''INSERT INTO elixirs (rgb, title, primary_trait, secondary_trait1, secondary_trait2, secondary_trait3, image_file, position)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (str(elixir_data['rgb']), elixir_data['title'], elixir_data['primary_trait'],
                            elixir_data['secondary_trait1'], elixir_data['secondary_trait2'], elixir_data['secondary_trait3'],
                            elixir_data['image_file'], elixir_data['position']))
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
            # Update fruits inventory
            for fruit, count in inventory.items():
                cursor.execute("UPDATE inventory SET count = ? WHERE fruit = ?", (count, fruit))

            # Update egg counts
            for egg, count in egg_counts.items():
                cursor.execute("UPDATE egg_inventory SET count = ? WHERE phenotype = ?", (count, egg))

            # Update elixirs
            for i, slot in enumerate(inventory_slots):
                if slot is not None:
                    rgb, image_file, title, primary_trait, secondary_trait1, secondary_trait2, secondary_trait3 = slot
                    cursor.execute(
                        '''INSERT OR REPLACE INTO elixirs (position, rgb, image_file, title, primary_trait, secondary_trait1, secondary_trait2, secondary_trait3)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (i + 1, str(rgb), image_file, title, primary_trait, secondary_trait1, secondary_trait2, secondary_trait3)
                    )

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

def main():
    # Call initialization functions
    initialize_pygame()
    initialize_fonts()
    
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

if __name__ == "__main__":
    main()
