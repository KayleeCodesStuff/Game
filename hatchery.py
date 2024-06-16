import pygame
import random
import sys
import sqlite3
import time
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
DRAGON_IMAGE_FOLDER = "dragons"  # Correct folder containing dragon images

# Resize egg images and create egg rectangles with increased spacing
egg_size = (80, 80)
unhatched_egg_image = pygame.transform.scale(unhatched_egg_image, egg_size)
egg_positions = []
egg_colors = [WHITE] * 10  # Initialize each egg's color to WHITE
egg_images = [unhatched_egg_image] * 10  # Initialize each egg's image to unhatched
egg_selected_from_db = [False] * 10  # Track if eggs have been selected from the database

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

ddragon_save_list = []

# Initialize inventory and egg counts
inventory, egg_counts, inventory_slots = load_inventory_data()

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

def draw_screen(selected_egg_index, active_timers):
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)  # Draw red outline
        pygame.draw.rect(screen, egg_colors[i], rect)  # Draw the egg with its current color
        
        screen.blit(egg_images[i], rect.topleft)  # Draw the correct egg/dragon image

    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    # Draw all active timers
    for egg_timer in active_timers[:]:
        selected_trait = egg_timer.display()
        if selected_trait is not None:
            ddragon_instance = ddragon_instances[egg_timer.egg_index]
            if selected_trait and ddragon_instance:
                statistical_pool = get_statistical_pool(ddragon_instance, dragons, selected_trait)
                filtered_pool = filter_pool_by_phenotype_and_rgb(statistical_pool, eggs[egg_timer.egg_index], ddragon_instance.elixir_rgb)
                selected_dragon = select_dragon_from_pool(filtered_pool, egg_positions[egg_timer.egg_index])
                if selected_dragon:
                    print(f"Selected dragon: {selected_dragon[0]} for egg index {egg_timer.egg_index}")
                    if ddragon_instances[egg_timer.egg_index] is not None:
                        ddragon_instances[egg_timer.egg_index].add_dragon_info(selected_dragon)
                        
                        petname = get_text_input(f"Enter a pet name for your dragon (Egg Index {egg_timer.egg_index}): ", font, screen, timeout=10)
                        ddragon_instances[egg_timer.egg_index].set_petname(petname)
                        
                        ddragon_save_list.append(ddragon_instances[egg_timer.egg_index])
                else:
                    print(f"No dragon selected for egg {egg_timer.egg_index}")

            active_timers.remove(egg_timer)
            del active_timers_dict[egg_timer.egg_index]

    pygame.display.flip()



dragons = []

# Database connections
current_dir = os.path.dirname(os.path.abspath(__file__))
dragons_db_path = os.path.join(current_dir, 'dragonsedit.db')
save_db_path = os.path.join(current_dir, 'save.db')

try:
    dragons_conn = sqlite3.connect(dragons_db_path)
    dragons_cursor = dragons_conn.cursor()
    dragons_cursor.execute("SELECT id, filename, type, name, primary_characteristic, secondary_characteristics, special_abilities, rgb_value_range, Nurture, gender, secondary_trait1, secondary_trait2, secondary_trait3 FROM dragons;")
    dragons = dragons_cursor.fetchall()
    print(f"Number of dragons fetched: {len(dragons)}")  # Debugging print statement
except sqlite3.OperationalError as e:
    print(f"Error opening dragons database: {e}")
finally:
    dragons_conn.close()



try:
    save_conn = sqlite3.connect(save_db_path)
    save_cursor = save_conn.cursor()
    save_cursor.execute("SELECT * FROM elixirs;")
    elixirs = save_cursor.fetchall()
    #print(f"Elixirs fetched: {elixirs}")  # Print elixirs for debugging
    save_cursor.execute("SELECT * FROM eggs;")
    eggs = save_cursor.fetchall()
    #print(f"Eggs fetched: {eggs}")  # Print eggs for debugging
except sqlite3.OperationalError as e:
    print(f"Error opening save database: {e}")
finally:
    save_conn.close()

placed_egg_ids = []

def display_egg_menu(selected_egg_index):
    running = True
    menu_font = pygame.font.Font(None, 28)
    menu_rects = []
    
    while running:
        screen.fill(GREY)
        menu_rects.clear()  # Clear the list to avoid duplication

        # Filter out placed eggs
        available_eggs = [egg for egg in eggs if egg[0] not in placed_egg_ids]

        for i, egg in enumerate(available_eggs):
            item_text = f"ID: {egg[0]}, Phenotype: {egg[2]}, Parents: {egg[4]} & {egg[5]}"  # Assuming egg[0] is the ID, egg[2] is the phenotype, egg[4] is parent 1, and egg[5] is parent 2
            text_surf = menu_font.render(item_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 50 + i * 30))
            screen.blit(text_surf, text_rect)
            menu_rects.append((text_rect, egg[0]))  # Store the egg ID

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for rect, egg_id in menu_rects:
                    if rect.collidepoint(x, y):
                        selected_egg = next((egg for egg in available_eggs if egg[0] == egg_id), None)
                        if selected_egg:
                            phenotype = selected_egg[2]
                            # Update the egg image based on the phenotype
                            if phenotype in egg_images_dict:
                                egg_images[selected_egg_index] = egg_images_dict[phenotype]
                            else:
                                egg_images[selected_egg_index] = unhatched_egg_image  # Default image if phenotype not found

                            egg_selected_from_db[selected_egg_index] = True  # Mark egg as selected from database
                            placed_egg_ids.append(selected_egg[0])  # Add egg ID to placed eggs list
                            #print(f"Selected egg: {selected_egg}")
                            running = False
                            return selected_egg[0]  # Return the selected egg ID
    return None

                      
def delete_elixir_from_db(elixir_id):
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM elixirs WHERE id = ?", (elixir_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error deleting elixir: {e}")
    except Exception as e:
        print(f"Unexpected error deleting elixir: {e}")

def fetch_random_nurture_options():
    try:
        conn = sqlite3.connect('option dragonsedit.db')
        cursor = conn.cursor()
        
        options = {}
        for option in ['A', 'B', 'C', 'D']:
            cursor.execute(f"SELECT text, trait FROM nurture WHERE option = '{option}' ORDER BY RANDOM() LIMIT 1;")
            options[option] = cursor.fetchone()
        
        conn.close()
        return options
    except Exception as e:
        print(f"Error fetching nurture options: {e}")
        return None

def display_nurture_options():
    options = fetch_random_nurture_options()
    if not options:
        return None

    running = True
    selected_trait = None
    
    while running:
        screen.fill(GREY)
        
        for i, (option_key, option_value) in enumerate(options.items()):
            text_surf = font.render(option_value[0], True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 100 + i * 50))
            screen.blit(text_surf, text_rect)
            
            if text_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, RED, text_rect.inflate(10, 10), 2)
                if pygame.mouse.get_pressed()[0]:
                    selected_trait = option_value[1]
                    running = False
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    return selected_trait

# Update the egg deletion function to use egg ID
def delete_egg_from_db(egg_id):
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eggs WHERE id = ?", (egg_id,))
            conn.commit()
            cursor.execute("SELECT * FROM eggs WHERE id = ?", (egg_id,))
            result = cursor.fetchone()
            if result:
                print(f"Error: Egg with ID {egg_id} was not deleted.")
    except sqlite3.Error as e:
        print(f"SQLite error deleting egg: {e}")
    except Exception as e:
        print(f"Unexpected error deleting egg: {e}")



class EggTimer:
    def __init__(self, egg_index, egg_position, egg_id, duration=10, default_trait="independent"):
        self.egg_index = egg_index
        self.egg_position = egg_position
        self.egg_id = egg_id  # Store egg ID correctly
        self.duration = duration
        self.default_trait = default_trait
        self.start_ticks = pygame.time.get_ticks()
        self.selected_trait = None
        self.running = True
    
    def update(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        countdown = self.duration - int(seconds)

        if countdown <= 0:
            self.running = False
            self.selected_trait = self.default_trait
            delete_egg_from_db(self.egg_id)  # Delete the egg from the database when the timer ends

        return countdown

    def display(self):
        countdown = self.update()
        if self.running:
            timer_text = font.render(str(countdown), True, (57, 255, 20))  # Neon green color
            screen.blit(timer_text, (self.egg_position[0], self.egg_position[1] - 30))  # Adjust position as needed
        return self.selected_trait if not self.running else None


elixir_data = None

def get_elixir_details(position):
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM elixirs WHERE position = ?", (position,))
            elixir = cursor.fetchone()
           
            return elixir
    except sqlite3.Error as e:
        print(f"SQLite error retrieving elixir details: {e}")
        return None


def get_statistical_pool(ddragon_instance, dragons, selected_trait):
    pool = []

    elixir_primary = ddragon_instance.elixir_primary if ddragon_instance.elixir_primary is not None else ""
    elixir_secondaries = ddragon_instance.elixir_secondaries if ddragon_instance.elixir_secondaries is not None else []
    
    for dragon in dragons:
        chances = 0  # Initialize chances for each dragon

        # Check for shared primary trait
        if dragon[4] == elixir_primary:
            chances += 1

        # Check for shared secondary traits
        for secondary in elixir_secondaries:
            if secondary in (dragon[10], dragon[11], dragon[12]):  # Adjusted indices
                chances += 1

        # Adjust chances based on nurture trait
        if chances > 0 and dragon[7] == selected_trait:  # Only increase if there are already some chances
            chances += 1

        if chances > 0:
            pool.extend([dragon] * chances)

    ddragon_instance.pool = pool  # Assign the pool to the Ddragon instance

    return pool

def filter_pool_by_phenotype_and_rgb(pool, egg, elixir_rgb):
    filtered_pool = []

    egg_phenotype = egg[2]
    elixir_rgb_value = eval(elixir_rgb)  # Convert string representation of RGB to tuple

    for dragon in pool:
        dragon_phenotype = dragon[2]
        rgb_ranges = dragon[7].strip('()').split(', ')  # Adjusted index
        try:
            dragon_rgb_range = [(int(r.split('-')[0]), int(r.split('-')[1])) for r in rgb_ranges]
        except ValueError as e:
            print(f"Error parsing RGB range for dragon {dragon[0]}: {e}")
            continue

        # Check phenotype
        if egg_phenotype in ["Metallic", "Gold", "Silver"] and dragon_phenotype != "Metallic":
            continue
        elif egg_phenotype != dragon_phenotype:
            continue

        # Check RGB range
        if not (dragon_rgb_range[0][0] <= elixir_rgb_value[0] <= dragon_rgb_range[0][1] and
                dragon_rgb_range[1][0] <= elixir_rgb_value[1] <= dragon_rgb_range[1][1] and
                dragon_rgb_range[2][0] <= elixir_rgb_value[2] <= dragon_rgb_range[2][1]):
            continue

        filtered_pool.append(dragon)

    return filtered_pool


def load_dragon_image(dragon_filename):
    base_directory = os.path.dirname(__file__)
    dragon_image_path = os.path.join(base_directory, "dragons", dragon_filename)
    #print(f"Loading image from path: {dragon_image_path}")
    
    # Check if file exists
    if not os.path.exists(dragon_image_path):
        print(f"File not found: {dragon_image_path}")
        return unhatched_egg_image  # Return a default image if file not found

    try:
        dragon_image = pygame.image.load(dragon_image_path).convert_alpha()
        width, height = dragon_image.get_size()
        scale_factor = 80 / min(width, height)  # Adjust the scale to fit the egg size
        new_size = (int(width * scale_factor), int(height * scale_factor))
        dragon_image = pygame.transform.scale(dragon_image, new_size)
        return dragon_image
    except pygame.error as e:
        print(f"Error loading image {dragon_filename}: {e}")
        return unhatched_egg_image  # Return a default image if loading fails


def get_dragon_image(dragon_id):
    conn = sqlite3.connect('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM dragons WHERE id = ?", (dragon_id,))
    dragon_filename = cursor.fetchone()
    conn.close()
    if dragon_filename:
        #print(f"Loading image for dragon {dragon_id}: {dragon_filename[0]}")
        return load_dragon_image(dragon_filename[0])
    return unhatched_egg_image


# Function to select a dragon from the pool
def select_dragon_from_pool(filtered_pool, egg_position):
    if not filtered_pool:
        return None
    selected_dragon = random.choice(filtered_pool)
    dragon_image = get_dragon_image(selected_dragon[0])  # Use the dragon ID
    egg_index = egg_positions.index(egg_position)  # Find the index of the egg position
    egg_images[egg_index] = dragon_image  # Update the egg image with the dragon image
    return selected_dragon

current_elixir_details = None  # Go-between variable to store elixir details
def get_elixir_details_from_variable():
    return current_elixir_details

active_timers_dict = {}

import sqlite3

class Ddragon:
    def __init__(self, genotype, parent1, parent2, phenotype):
        self.genotype = genotype
        self.parent1 = parent1
        self.parent2 = parent2
        self.elixir_rgb = None
        self.elixir_title = None
        self.elixir_primary = None
        self.elixir_secondaries = []
        self.dragon_id = None
        self.dragon_name = None
        self.primary = None
        self.secondary1 = None
        self.secondary2 = None
        self.secondary3 = None
        self.nurture = None
        self.gender = None
        self.rgb_range = None
        self.filename = None
        self.type = phenotype #egg phenotype to start
        self.special_abilities = None
        self.petname = None
        self.pool = []  # Add pool attribute

    def add_elixir_info(self, rgb, title, primary, secondaries):
        self.elixir_rgb = rgb
        self.elixir_title = title
        self.elixir_primary = primary
        self.elixir_secondaries = secondaries

    def add_dragon_info(self, dragon):
        self.dragon_id = dragon[0]
        self.dragon_name = dragon[3]
        self.primary = dragon[4]
        self.secondary1 = dragon[10]
        self.secondary2 = dragon[11]
        self.secondary3 = dragon[12]
        self.nurture = dragon[8]
        self.gender = dragon[9]
        self.rgb_range = dragon[7]
        self.filename = dragon[1]
        self.type = dragon[2] #Dragon type overrides egg 
        self.special_abilities = dragon[6]

    def set_petname(self, petname):
        self.petname = petname

    def save_to_db(self):
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hatcheddragons (
                    id INTEGER PRIMARY KEY,
                    genotype TEXT,
                    parent1 TEXT,
                    parent2 TEXT,
                    elixir_rgb TEXT,
                    elixir_title TEXT,
                    dragon_id INTEGER,
                    dragon_name TEXT,
                    primary_trait TEXT,
                    secondary1 TEXT,
                    secondary2 TEXT,
                    secondary3 TEXT,
                    nurture TEXT,
                    gender TEXT,
                    rgb_range TEXT,
                    filename TEXT,
                    type TEXT,
                    special_abilities TEXT,
                    petname TEXT
                )
            ''')
            cursor.execute('''
                INSERT INTO hatcheddragons (
                    genotype, parent1, parent2, elixir_rgb, elixir_title, dragon_id, dragon_name,
                    primary_trait, secondary1, secondary2, secondary3, nurture, gender,
                    rgb_range, filename, type, special_abilities, petname
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.genotype, self.parent1, self.parent2, self.elixir_rgb, self.elixir_title, self.dragon_id, self.dragon_name,
                self.primary, self.secondary1, self.secondary2, self.secondary3, self.nurture, self.gender,
                self.rgb_range, self.filename, self.type, self.special_abilities, self.petname
            ))
            conn.commit()


# Ensure you have an empty list to hold Ddragon instances
ddragon_instances = [None] * 10

egg_ids_on_board = [None] * 10


def get_text_input(prompt, font, screen, timeout=10):
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    start_time = time.time()

    while not done:
        current_time = time.time()
        if current_time - start_time > timeout:
            print("Timeout reached. Leaving pet name blank.")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(prompt + text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()


    return text
def save_all_ddragon_instances(ddragon_list):
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hatcheddragons (
                    id INTEGER PRIMARY KEY,
                    genotype TEXT,
                    parent1 TEXT,
                    parent2 TEXT,
                    elixir_rgb TEXT,
                    elixir_title TEXT,
                    dragon_id INTEGER,
                    dragon_name TEXT,
                    primary_trait TEXT,
                    secondary1 TEXT,
                    secondary2 TEXT,
                    secondary3 TEXT,
                    nurture TEXT,
                    gender TEXT,
                    rgb_range TEXT,
                    filename TEXT,
                    type TEXT,
                    special_abilities TEXT,
                    petname TEXT
                )
            ''')
            for ddragon in ddragon_list:
                cursor.execute('''
                    INSERT INTO hatcheddragons (
                        genotype, parent1, parent2, elixir_rgb, elixir_title, dragon_id, dragon_name,
                        primary_trait, secondary1, secondary2, secondary3, nurture, gender,
                        rgb_range, filename, type, special_abilities, petname
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ddragon.genotype, ddragon.parent1, ddragon.parent2, ddragon.elixir_rgb, ddragon.elixir_title, ddragon.dragon_id, ddragon.dragon_name,
                    ddragon.primary, ddragon.secondary1, ddragon.secondary2, ddragon.secondary3, ddragon.nurture, ddragon.gender,
                    ddragon.rgb_range, ddragon.filename, ddragon.type, ddragon.special_abilities, ddragon.petname
                ))
            conn.commit()
            print(f"Saved {len(ddragon_list)} Ddragon instances to the database")
    except sqlite3.Error as e:
        print(f"SQLite error saving ddragon instances: {e}")
    except Exception as e:
        print(f"Unexpected error saving ddragon instances: {e}")

def main():
    global elixir_color
    elixir_color = None
    running = True
    selected_egg_index = None
    active_timers = []
    elixir_data = None  # Initialize elixir_data
    current_elixir_details = None  # Go-between variable to store elixir details

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                egg_selected = False
                for j, egg_rect in enumerate(egg_positions):
                    if egg_rect.collidepoint(x, y):
                        selected_egg_index = j
                        egg_selected = True
                        selected_egg_id = display_egg_menu(selected_egg_index)  # Get the selected egg ID
                        if selected_egg_id is not None:
                            ddragon_instance = Ddragon(eggs[selected_egg_index][1], eggs[selected_egg_index][4], eggs[selected_egg_index][5])
                            ddragon_instances[selected_egg_index] = ddragon_instance
                            egg_ids_on_board[selected_egg_index] = selected_egg_id  # Map the egg ID to the board position
                            
                        break
                if not egg_selected:
                    for i, rect in enumerate(inventory_boxes):
                        if rect.collidepoint(x, y) and inventory_slots[i] is not None:
                            selected_elixir = inventory_slots[i]
                            elixir_color = selected_elixir[0]
                            elixir_image_file = selected_elixir[1]

                            # Get elixir details based on position before removing it from inventory
                            elixir = get_elixir_details(i + 1)
                            if not elixir:
                                print(f"Could not find elixir details for position {i + 1}")
                                continue

                            if selected_egg_index is not None and egg_selected_from_db[selected_egg_index]:
                                egg_colors[selected_egg_index] = elixir_color

                                # Ensure correct egg ID is passed to EggTimer
                                egg_position = egg_positions[selected_egg_index].topleft
                                egg_id = egg_ids_on_board[selected_egg_index]

                                # Check if timer already exists for this egg
                                if selected_egg_index not in active_timers_dict:
                                    new_timer = EggTimer(selected_egg_index, egg_position, egg_id)
                                    active_timers.append(new_timer)
                                    active_timers_dict[selected_egg_index] = new_timer

                                # Update the Ddragon instance with elixir information
                                if ddragon_instances[selected_egg_index] is not None:
                                    ddragon_instances[selected_egg_index].add_elixir_info(elixir[1], elixir[2], elixir[3], elixir[4:7])

                                    # Display nurture options and update the Ddragon instance
                                    selected_trait = display_nurture_options()
                                    if selected_trait is not None:
                                        ddragon_instances[selected_egg_index].nurture = selected_trait

                                        # Update the pool in the Ddragon instance
                                        ddragon_instances[selected_egg_index].pool = get_statistical_pool(ddragon_instances[selected_egg_index], dragons, selected_trait)

                                # Remove elixir from inventory and delete from database
                                inventory_slots[i] = None
                                elixir_color = None
                                delete_elixir_from_db(elixir[0])
                                break

        for egg_timer in active_timers[:]:
            selected_trait = egg_timer.display()
            if selected_trait is not None:
                ddragon_instance = ddragon_instances[egg_timer.egg_index]  # Get the correct Ddragon instance
                if selected_trait and ddragon_instance:
                    filtered_pool = filter_pool_by_phenotype_and_rgb(ddragon_instance.pool, eggs[egg_timer.egg_index], ddragon_instance.elixir_rgb)
                    selected_dragon = select_dragon_from_pool(filtered_pool, egg_positions[egg_timer.egg_index])
                    if selected_dragon:
                        print(f"Selected dragon: {selected_dragon[0]} for egg index {egg_timer.egg_index}")
                        if ddragon_instances[egg_timer.egg_index] is not None:
                            ddragon_instances[egg_timer.egg_index].add_dragon_info(selected_dragon)
                            
                            # Prompt the user for a pet name with a timeout
                            petname = get_text_input(f"Enter a pet name for your dragon (Egg Index {egg_timer.egg_index}): ", font, screen, timeout=10)
                            ddragon_instances[egg_timer.egg_index].set_petname(petname)
                            
                            # Accumulate the Ddragon instance to save later
                            ddragon_save_list.append(ddragon_instances[egg_timer.egg_index])
                    else:
                        print(f"No dragon selected for egg {egg_timer.egg_index}")
                active_timers.remove(egg_timer)
                del active_timers_dict[egg_timer.egg_index]  # Remove from dictionary
                egg_positions[egg_timer.egg_index] = pygame.Rect(-100, -100, 0, 0)
                egg_images[egg_timer.egg_index] = unhatched_egg_image  # Reset to unhatched if no dragon is selected

        draw_screen(selected_egg_index, active_timers)
        pygame.display.flip()  # Force a screen redraw

    if elixir_data:
        try:
            save_elixir_data(elixir_data)  # Pass the elixir_data variable
        except Exception as e:
            print(f"Unexpected error saving elixir data: {e}")

    # Save all accumulated Ddragon instances
    save_all_ddragon_instances(ddragon_save_list)
    save_inventory_data()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
