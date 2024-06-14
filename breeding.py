import pygame
import sqlite3
import os
import random
import math
from tkinter import Tk, filedialog
from game import load_inventory_data, save_inventory_data, save_elixir_data, draw_inventory, define_elixir_data

# Constants
WIDTH, HEIGHT = 1200, 900
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND_IMAGE = "breedingbackground.png"
DRAGON_IMAGE_FOLDER = "dragons"  # Correct folder containing dragon images
FRUIT_SPEED_MODIFIERS = {
    "gleamberry": -0.5,
    "shimmeringapple": 0.5,
}

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module

# Define font
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 36)

# Button properties
button_font = pygame.font.Font(None, 36)
button_rect = pygame.Rect(WIDTH - 200, HEIGHT - 150, 180, 50)  # Positioned above the inventory

# Load background image
background = pygame.image.load(BACKGROUND_IMAGE)
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Define screen (surface)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

# Fruit images
ethereal_pear = pygame.image.load("etherealpear.png")
flame_fruit = pygame.image.load("flamefruit.png")
gleam_berry = pygame.image.load("gleamberry.png")
moonbeam_melon = pygame.image.load("moonbeammelon.png")
shimmering_apple = pygame.image.load("shimmeringapple.png")

# Resize fruit images
fruit_images = [gleam_berry, flame_fruit, shimmering_apple, ethereal_pear, moonbeam_melon]
fruit_images = [pygame.transform.scale(fruit, (50, 50)) for fruit in fruit_images]
fruit_names = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear", "moonbeammelon"]
fruit_images_dict = dict(zip(fruit_names, fruit_images))
# Load heart image
heart_image = pygame.image.load("heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))
hearts_on_board = []

# Load inventory data
inventory, egg_counts, inventory_slots = load_inventory_data()

# Initialize egg counts 
egg_counts = {"Black": 0, "White": 0, "Rainbow": 0, "Metallic": 0}

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

fruit_personality_keywords = {
    "gleamberry": ["Dark", "Brooding", "Responsible", "Common"],
    "flamefruit": ["Distraction", "Fierce", "Fiery", "Showy"],
    "shimmeringapple": ["Speed", "Flightiness", "Drive", "Ambition"],
    "etherealpear": ["Earthy", "Pragmatic", "Stout", "Loyal"],
    "moonbeammelon": ["Angelic", "Unique", "Pure", "Self-righteous"]
}

tested_pairs = set()

# Define the alleles and their dominance hierarchy
allele_dominance = {
    'B': 'Black',
    'W': 'White',
    'R': 'Rainbow',
    'M': 'Metallic'
}

# Possible genotypes for each phenotype
phenotype_to_genotypes = {
    'Black': [('B', 'B'), ('B', 'W'), ('B', 'R'), ('B', 'M')],
    'White': [('W', 'W'), ('W', 'R'), ('W', 'M')],
    'Rainbow': [('R', 'R'), ('R', 'M')],
    'Metallic': [('M', 'M')]
}

def load_elixirs_from_db():
    elixirs = []
    try:
        with sqlite3.connect(save_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rgb, image_file, position FROM elixirs ORDER BY position ASC")
            elixirs = cursor.fetchall()
    except Exception as e:
        print(f"Error loading elixirs from database: {e}")
    return elixirs

def initialize_eggs_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS eggs (
                        id INTEGER PRIMARY KEY,
                        genotype TEXT,
                        phenotype TEXT,
                        image_file TEXT,
                        parent1_name TEXT,
                        parent2_name TEXT
                      )''')
    conn.commit()

def draw_hearts(surface):
    current_time = pygame.time.get_ticks()
    for heart in hearts_on_board[:]:
        if current_time - heart["start_time"] > 3000:
            hearts_on_board.remove(heart)
        else:
            surface.blit(heart_image, heart["position"])

repulsor_counter = 0

save_file = os.path.join(os.getcwd(), "save.db")
if not os.path.exists(save_file):
    def select_or_create_file():
        root = Tk()
        root.withdraw()  # Hide the main tkinter window
        file_path = filedialog.asksaveasfilename(defaultextension=".db",
                                                 filetypes=[("SQLite database", "*.db"), ("JSON file", "*.json")],
                                                 title="Select or Create File")
        return file_path

    save_file = select_or_create_file()
    if not save_file:
        save_file = os.path.join(os.getcwd(), "save.db")
    
    def initialize_file(file_path):
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Create elixirs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS elixirs (
                            id INTEGER PRIMARY KEY,
                            rgb TEXT,
                            title TEXT,
                            primary_trait TEXT,
                            secondary_traits TEXT,
                            image_file TEXT,
                            position INTEGER
                        )''')
        
        # Create inventory table with fruit as UNIQUE
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY,
                            fruit TEXT UNIQUE,
                            count INTEGER
                        )''')
        
        # Initialize the eggs table
        initialize_eggs_table(conn)
        
        conn.commit()
        conn.close()

    initialize_file(save_file)
else:
    conn = sqlite3.connect(save_file)
    initialize_eggs_table(conn)

# Replace custom load_inventory_data with standardized one
inventory, egg_counts, inventory_slots = load_inventory_data()

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

        conn.commit()

# Load dragons from the database
conn = sqlite3.connect("dragonbreeding.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM dragons")
all_dragons = cursor.fetchall()
conn.close()

# Randomly select 10 unique dragons ensuring a mix of genders
selected_dragons = random.sample(all_dragons, 10)
male_dragons = [d for d in selected_dragons if d[-1] == "Male"]
female_dragons = [d for d in selected_dragons if d[-1] == "Female"]

# Ensure there are both genders
if len(male_dragons) == 0 or len(female_dragons) == 0:
    print("Not enough dragons of both genders in the selection, please check the database.")
    exit()

# Placeholder for dragons
dragons = []

# Generate positions for dragons (ensure at least 10 positions)
positions = [(x * WIDTH // 4, y * HEIGHT // 4) for x in range(1, 4) for y in range(1, 4)]
while len(positions) < 9:
    positions.append((random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 150)))  # Add random positions if not enough
positions = positions[:9]  # Ensure exactly 9 positions
positions.append((WIDTH // 2, 0))  # Position the 10th dragon at the top center
random.shuffle(positions)

def is_aspect_ratio_16_9(width, height):
    return abs((width / height) - (16 / 9)) < 0.01  # Allowing a small margin for floating point comparisons

def assign_genotype(dragon):
    phenotype = dragon["type"]  # Assuming 'type' is used for phenotype
    if phenotype in ["Gold", "Silver", "Metal"]:
        phenotype = "Metallic"
    if phenotype == "Black":
        genotype = random.choice(phenotype_to_genotypes["Black"])
    elif phenotype == "White":
        genotype = random.choice(phenotype_to_genotypes["White"])
    elif phenotype == "Rainbow":
        genotype = random.choice(phenotype_to_genotypes["Rainbow"])
    else:
        genotype = random.choice(phenotype_to_genotypes[phenotype])
    dragon["genotype"] = genotype

# Function to outline image
def outline_image(image, color, thickness=3):
    mask = pygame.mask.from_surface(image)
    outline = mask.outline()
    outline_surface = image.copy()
    pygame.draw.lines(outline_surface, color, True, outline, thickness)
    return outline_surface

def draw_button(surface, text, font, color, rect, border_color, border_width):
    pygame.draw.rect(surface, border_color, rect, border_width)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))

def handle_button_click(mouse_pos, rect, inventory, dragons, summoned_dragon_ids):
    if rect.collidepoint(mouse_pos) and inventory["moonbeammelon"] >= 10:
        summon_new_dragon(inventory, dragons, summoned_dragon_ids)

def summon_new_dragon(inventory, dragons, summoned_dragon_ids):
    if inventory["moonbeammelon"] < 10:
        print("Not enough moonbeammelon to summon a new dragon.")
        return

    inventory["moonbeammelon"] -= 10

    # Load dragons from the database
    conn = sqlite3.connect("dragonbreeding.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dragons")
    all_dragons = cursor.fetchall()
    conn.close()

    if not all_dragons:
        print("No dragons available in the database.")
        return

    # Filter out already summoned dragons
    available_dragons = [d for d in all_dragons if d[0] not in summoned_dragon_ids]
    if not available_dragons:
        print("All dragons have already been summoned.")
        return

    new_dragon_data = random.choice(available_dragons)
    dragon_image_path = os.path.join(DRAGON_IMAGE_FOLDER, new_dragon_data[1])
    dragon_image = pygame.image.load(dragon_image_path)
    
    width, height = dragon_image.get_size()
    scale_factor = 50 / min(width, height)  # Match the initial size (50x50)
    new_size = (int(width * scale_factor), int(height * scale_factor))
    dragon_image = pygame.transform.scale(dragon_image, new_size)
    outline_color = BLUE if new_dragon_data[10] == "Male" else RED
    dragon_image = outline_image(dragon_image, outline_color)

    initial_speed = 1.5 + (0.5 if "speed" in new_dragon_data[4].lower() or "Flightspeed" in new_dragon_data[6] else 0)

    phenotype = new_dragon_data[2]
    if phenotype in ["Gold", "Silver", "Metal"]:
        phenotype = "Metallic"
    genotype = random.choice(phenotype_to_genotypes[phenotype])
    
    new_dragon = {
        "id": new_dragon_data[0],
        "name": new_dragon_data[3],
        "type": new_dragon_data[2],
        "primary_characteristic": new_dragon_data[4],
        "secondary_characteristics": new_dragon_data[5].split(','),
        "special_abilities": new_dragon_data[6],
        "description": new_dragon_data[7],
        "rgb_value_range": new_dragon_data[8],
        "nurture": new_dragon_data[9],
        "gender": new_dragon_data[10],
        "image": dragon_image,
        "rect": dragon_image.get_rect(topleft=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 150))),
        "speed": initial_speed,
        "target": None,
        "holding_fruit": None,
        "genotype": genotype
    }
    new_dragon["target"] = determine_target(new_dragon)  # Immediately determine target
    dragons.append(new_dragon)
    summoned_dragon_ids.add(new_dragon_data[0])
    print(f"Summoned new dragon: {new_dragon['name']}")

# Create dragon dictionary with valid genotypes
for i, dragon_data in enumerate(selected_dragons):
    dragon_image_path = os.path.join(DRAGON_IMAGE_FOLDER, dragon_data[1])
    dragon_image = pygame.image.load(dragon_image_path)
    
    width, height = dragon_image.get_size()
    if is_aspect_ratio_16_9(width, height):
        scale_factor = 100 / min(width, height)
        new_size = (int(width * scale_factor), int(height * scale_factor))
    else:
        # Scale to fit within a 50x50 box while preserving aspect ratio
        if width > height:
            new_size = (100, int(100 * (height / width)))
        else:
            new_size = (int(100 * (width / height)), 100)
    
    dragon_image = pygame.transform.scale(dragon_image, new_size)
    outline_color = BLUE if dragon_data[10] == "Male" else RED
    dragon_image = outline_image(dragon_image, outline_color)
    
    initial_speed = 1.5 + (0.5 if "speed" in dragon_data[4].lower() or "Flightspeed" in dragon_data[6] else 0)

    phenotype = dragon_data[2]
    if phenotype in ["Gold", "Silver", "Metal"]:
        phenotype = "Metallic"
    genotype = random.choice(phenotype_to_genotypes[phenotype])
    
    dragon = {
        "id": dragon_data[0],
        "name": dragon_data[3],
        "type": dragon_data[2],
        "primary_characteristic": dragon_data[4],
        "secondary_characteristics": dragon_data[5].split(','),
        "special_abilities": dragon_data[6],
        "description": dragon_data[7],
        "rgb_value_range": dragon_data[8],
        "nurture": dragon_data[9],
        "gender": dragon_data[10],
        "image": dragon_image,
        "rect": dragon_image.get_rect(topleft=positions[i]),
        "speed": initial_speed,
        "target": None,
        "holding_fruit": None,
        "genotype": genotype
    }
    dragons.append(dragon)

for dragon in dragons:
    if "genotype" not in dragon:
        assign_genotype(dragon)

# Function to draw text
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

# Replace custom save_inventory_data with standardized one
save_inventory_data()

def handle_egg_collection(mouse_pos, egg_counts):
    for egg in eggs_on_board:
        if egg["rect"].collidepoint(mouse_pos):
            eggs_on_board.remove(egg)
            break

# Replace custom draw_inventory with standardized one
draw_inventory(screen, inventory, egg_counts, inventory_slots)

# Function to draw dragons
def draw_dragons(surface):
    for dragon in dragons:
        surface.blit(dragon["image"], dragon["rect"].topleft)
        if dragon["holding_fruit"]:
            fruit_image = fruit_images_dict[dragon["holding_fruit"]]
            surface.blit(fruit_image, (dragon["rect"].x + 25, dragon["rect"].y + 25))

# Function to draw fruits on the game board
fruits_on_board = []

def spawn_fruits():
    fruit_types = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear"]
    for fruit_type in fruit_types:
        while True:
            x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 150)
            # Ensure fruits do not spawn on top of dragons
            if all(calculate_distance((x, y), (dragon["rect"].x, dragon["rect"].y)) > 50 for dragon in dragons):
                fruits_on_board.append({"type": fruit_type, "position": (x, y)})
                break

def draw_fruits_on_board(surface):
    for fruit in fruits_on_board:
        surface.blit(fruit_images_dict[fruit["type"]], fruit["position"])

# Function to calculate distance between two points
def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos2[1] - pos2[1]) ** 2)

# Function to determine target for a dragon
def determine_target(dragon):
    if dragon["holding_fruit"] == "flamefruit":
        flamefruit_dragons = [d for d in dragons if d["holding_fruit"] == "flamefruit" and d.get("repulsor_tag") != dragon.get("repulsor_tag")]
        if flamefruit_dragons:
            flamefruit_dragons.sort(key=lambda d: calculate_distance(dragon["rect"].topleft, d["rect"].topleft))
            return flamefruit_dragons[0]["rect"].topleft

    if not dragon["holding_fruit"] and fruits_on_board:
        fruits_on_board.sort(key=lambda f: calculate_distance(dragon["rect"].topleft, f["position"]))
        return fruits_on_board[0]["position"]
    else:
        targets = [d for d in dragons if d["gender"] != dragon["gender"] and d.get("repulsor_tag") != dragon.get("repulsor_tag")]
        if targets:
            targets.sort(key=lambda d: calculate_distance(dragon["rect"].topleft, d["rect"].topleft))
            return targets[0]["rect"].topleft
    return None

def get_unique_fruit_characteristic(dragon, fruit_characteristics):
    current_characteristics = set([dragon["primary_characteristic"]] + dragon["secondary_characteristics"])
    possible_characteristics = [char for char in fruit_characteristics if char not in current_characteristics]
    if possible_characteristics:
        return random.choice(possible_characteristics)
    return None

def compatibility_test(dragon1, dragon2, fruit_personality_keywords):
    if dragon1["gender"] == dragon2["gender"]:
        return False
    
    characteristics1 = set([dragon1["primary_characteristic"]] + dragon1["secondary_characteristics"])
    characteristics2 = set([dragon2["primary_characteristic"]] + dragon2["secondary_characteristics"])

    # Add unique fruit characteristic for dragon1
    if dragon1["holding_fruit"]:
        fruit_characteristics = fruit_personality_keywords[dragon1["holding_fruit"]]
        unique_fruit_char1 = get_unique_fruit_characteristic(dragon1, fruit_characteristics)
        if unique_fruit_char1:
            characteristics1.add(unique_fruit_char1)
    
    # Add unique fruit characteristic for dragon2
    if dragon2["holding_fruit"]:
        fruit_characteristics = fruit_personality_keywords[dragon2["holding_fruit"]]
        unique_fruit_char2 = get_unique_fruit_characteristic(dragon2, fruit_characteristics)
        if unique_fruit_char2:
            characteristics2.add(unique_fruit_char2)
    
    return bool(characteristics1 & characteristics2)

def get_egg_genotype(parent1, parent2):
    allele1 = random.choice(parent1["genotype"])
    allele2 = random.choice(parent2["genotype"])
    return (allele1, allele2)

def determine_phenotype(genotype):
    if 'B' in genotype:
        return 'Black'
    elif 'W' in genotype:
        return 'White'
    elif 'R' in genotype:
        return 'Rainbow'
    else:
        return 'Metallic'

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

        conn.commit()

# Function to draw eggs on the game board
eggs_on_board = []

def draw_eggs_on_board(surface):
    for egg in eggs_on_board:
        surface.blit(egg["image"], egg["rect"].topleft)

for dragon in dragons:
    if "genotype" not in dragon:
        assign_genotype(dragon)

# Function to move dragons
def move_dragons():
    global repulsor_counter
    dragons_to_remove = []
    for dragon in dragons[:]:
        if not dragon["target"]:
            dragon["target"] = determine_target(dragon)
        if dragon["target"]:
            dx, dy = dragon["target"][0] - dragon["rect"].x, dragon["target"][1] - dragon["rect"].y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                dx, dy = dx / distance, dy / distance  # Normalize
                speed_modifier = FRUIT_SPEED_MODIFIERS.get(dragon["holding_fruit"], 0)
                speed = dragon["speed"] + speed_modifier  # Ensure speed is recalculated correctly
                new_x = dragon["rect"].x + dx * speed
                new_y = dragon["rect"].y + dy * speed

                # Check for screen boundaries
                if new_x < 0:
                    new_x = 0
                elif new_x + dragon["rect"].width > WIDTH:
                    new_x = WIDTH - dragon["rect"].width

                if new_y < 0:
                    new_y = 0
                elif new_y + dragon["rect"].height > HEIGHT:
                    new_y = HEIGHT - dragon["rect"].height

                # Check for collisions with other dragons
                dragon_rect_copy = dragon["rect"].copy()
                dragon_rect_copy.x = new_x
                dragon_rect_copy.y = new_y
                collision_occurred = False
                for other_dragon in dragons:
                    if other_dragon["id"] != dragon["id"] and dragon_rect_copy.colliderect(other_dragon["rect"]):
                        pair = tuple(sorted((dragon["id"], other_dragon["id"])))
                        if pair not in tested_pairs:
                            tested_pairs.add(pair)
                            heart_position = ((dragon["rect"].x + other_dragon["rect"].x) // 2,
                                              (dragon["rect"].y + other_dragon["rect"].y) // 2)
                            hearts_on_board.append({"position": heart_position, "start_time": pygame.time.get_ticks()})

                            compatible = compatibility_test(dragon, other_dragon, fruit_personality_keywords)
                            print(f"Compatibility test between {dragon['name']} and {other_dragon['name']}: {'Compatible' if compatible else 'Not compatible'}")

                            if compatible:
                                # Create egg and mark dragons for removal
                                create_egg(dragon, other_dragon, heart_position)
                                dragons_to_remove.append(dragon)
                                dragons_to_remove.append(other_dragon)
                            else:
                                # Assign unique repulsor tag
                                repulsor_tag = f"repulsor_{repulsor_counter}"
                                repulsor_counter += 1
                                dragon["repulsor_tag"] = repulsor_tag
                                other_dragon["repulsor_tag"] = repulsor_tag

                            dragon["target"] = None
                            other_dragon["target"] = None
                            collision_occurred = True
                            break

                if not collision_occurred:
                    dragon["rect"].x = new_x
                    dragon["rect"].y = new_y

            if distance < 5:  # Reached target
                # Collect fruit if target is a fruit
                if dragon["holding_fruit"] is None:
                    for fruit in fruits_on_board:
                        if fruit["position"] == dragon["target"]:
                            dragon["holding_fruit"] = fruit["type"]
                            fruits_on_board.remove(fruit)
                            break
                dragon["target"] = determine_target(dragon)  # Reassign target

    for dragon in dragons_to_remove:
        if dragon in dragons:
            dragons.remove(dragon)

# Example usage
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

# Main game loop with interactivity
def place_fruit(x, y, selected_fruit):
    if selected_fruit and inventory[selected_fruit] > 0:
        fruits_on_board.append({"type": selected_fruit, "position": (x - 25, y - 25)})
        inventory[selected_fruit] -= 1
        for dragon in dragons:
            if not dragon["holding_fruit"]:
                dragon["target"] = determine_target(dragon)
        print(f"Placed {selected_fruit} on the board at ({x - 25}, {y - 25})")

# Main game loop with interactivity
def main():
    running = True
    selected_inventory_slot = None
    selected_fruit = None
    spawn_fruits()  # Spawn initial fruits on the board
    clock = pygame.time.Clock()  # Create a clock object to manage frame rate

    # Load elixirs from the database
    elixirs = load_elixirs_from_db()
    inventory_slots = [(tuple(map(int, elixir[0].strip('()').split(','))), elixir[1]) for elixir in elixirs]
    
    # Pad with None if less than 5 elixirs
    while len(inventory_slots) < 5:
        inventory_slots.append(None)

    # Button properties
    button_font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(WIDTH - 200, HEIGHT - 150, 180, 50)  # Positioned above the inventory

    # Track summoned dragon IDs
    summoned_dragon_ids = set(dragon["id"] for dragon in dragons)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x, y = mouse_pos
                # Check if clicking on the button
                if button_rect.collidepoint(mouse_pos):
                    handle_button_click(mouse_pos, button_rect, inventory, dragons, summoned_dragon_ids)
                # Check if clicking on a fruit in the inventory
                elif y > HEIGHT - 100:
                    slot_index = (x - 10) // 60
                    if 0 <= slot_index < len(fruit_names):
                        selected_fruit = fruit_names[slot_index]
                # Place fruit on board
                else:
                    place_fruit(x, y, selected_fruit)
                    selected_fruit = None

                # Handle egg collection
                handle_egg_collection(mouse_pos, egg_counts)

        move_dragons()  # Update dragon positions

        screen.fill((0, 0, 0))  # Clear the screen with black
        screen.blit(background, (0, 0))  # Draw background image
        draw_inventory(screen, inventory, egg_counts, inventory_slots, selected_inventory_slot)
        draw_dragons(screen)
        draw_fruits_on_board(screen)
        draw_eggs_on_board(screen)  # Draw eggs on the board
        draw_hearts(screen)  # Draw hearts on the board
        draw_button(screen, "Invite Dragon", button_font, WHITE, button_rect, BLUE, 2)  # Draw the button
        pygame.display.flip()  # Update the display

        clock.tick(30)  # Set the frame rate to 20 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
