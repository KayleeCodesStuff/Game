# Standard library imports
import random
import sys
import time
import os
from firebase_config import db

# Third-party imports
import pygame

# Custom imports
from game import *

# Initialize pygame and fonts
initialize()

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
background = load_and_resize_image("hatchery.png", (WIDTH, HEIGHT))
unhatched_egg_image = load_and_resize_image("unhatched.png", (80, 80))
DRAGON_IMAGE_FOLDER = os.path.join("assets", "images", "dragons")  # Correct folder containing dragon images

# Resize egg images and create egg rectangles with increased spacing
egg_size = (80, 80)
unhatched_egg_image = pygame.transform.scale(unhatched_egg_image, egg_size)
egg_positions = []
egg_colors = [WHITE] * 10  # Initialize each egg's color to WHITE
egg_images = [unhatched_egg_image] * 10  # Initialize each egg's image to unhatched
egg_selected_from_db = [False] * 10  # Track if eggs have been selected from the database
# Adjust padding between eggs
EGG_PADDING = 200

# Load and resize egg images
# Load and resize egg images
egg_images_dict = {
    "black": load_and_resize_image(os.path.join("eggs", "black_egg.png"), egg_size),
    "white": load_and_resize_image(os.path.join("eggs", "white_egg.png"), egg_size),
    "rainbow": load_and_resize_image(os.path.join("eggs", "rainbow_egg.png"), egg_size),
    "metallic": load_and_resize_image(os.path.join("eggs", "metallic_egg.png"), egg_size)
}


# Load and resize fruit images
fruit_size = (50, 50)
fruit_names = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear", "moonbeammelon"]
fruit_images_dict = {name: load_and_resize_image(os.path.join("fruits", f"{name}.png"), fruit_size) for name in fruit_names}

# Initialize inventory and other variables
inventory, egg_counts, inventory_slots = load_inventory_data()
placed_egg_ids = []
egg_ids_on_board = [None] * 10
dragons = []
ddragon_save_list = []
ddragon_instances = [None] * 10
elixir_data = None
current_elixir_details = None  # Go-between variable to store elixir details
active_timers_dict = {}

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

# Database connections
current_dir = os.path.dirname(os.path.abspath(__file__))
dragons_db_path = os.path.join(current_dir, 'dragonsedit.db')
save_db_path = os.path.join(current_dir, 'save.db')

def fetch_dragons_from_firestore():
    try:
        dragons_ref = db.collection('dragons')
        dragons_docs = dragons_ref.stream()

        dragons = []
        for dragon_doc in dragons_docs:
            if dragon_doc.exists:
                dragon_data = dragon_doc.to_dict()
                dragon_data['id'] = dragon_doc.id  # Add the document ID to the dragon data
                print(f"Dragon data fetched: {dragon_data}")
                dragons.append(dragon_data)

        print(f"Number of dragons fetched: {len(dragons)}")
        return dragons
    except Exception as e:
        print(f"Firestore error retrieving dragons: {e}")
        return []


def fetch_elixirs_from_firestore():
    try:
        elixirs_ref = db.collection('elixirs')
        elixirs_docs = elixirs_ref.get()

        elixirs = []
        for elixir_doc in elixirs_docs:
            if elixir_doc.exists:
                elixir_data = elixir_doc.to_dict()
                elixirs.append(elixir_data)

        return elixirs
    except Exception as e:
        print(f"Firestore error retrieving elixirs: {e}")
        return []

def fetch_eggs_from_firestore():
    try:
        eggs_ref = db.collection('eggs')
        eggs_docs = eggs_ref.get()

        eggs = []
        for egg_doc in eggs_docs:
            if egg_doc.exists:
                egg_data = egg_doc.to_dict()
                egg_data['id'] = egg_doc.id  # Add the document ID to the egg data
                eggs.append(egg_data)

        return eggs
    except Exception as e:
        print(f"Firestore error retrieving eggs: {e}")
        return []
    
# Define load_image function
def load_image(file_path):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        #print(f"Loaded image from {file_path} with original size {image.get_size()}")  # Debug print
        return image
    except pygame.error as e:
        print(f"Error loading image {file_path}: {e}")
        return None  # Return None if loading fails

def load_image_with_max_dimensions(file_path, max_width, max_height):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        width, height = image.get_size()
        aspect_ratio = width / height

        if width > max_width or height > max_height:
            if aspect_ratio > 1:  # Wider than tall
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:  # Taller than wide
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            image = pygame.transform.scale(image, (new_width, new_height))

        #print(f"Loaded and resized image from {file_path} to size {image.get_size()}")  # Debug print
        return image
    except pygame.error as e:
        print(f"Error loading image {file_path}: {e}")
        return None  # Return None if loading fails

    
base_directory = os.path.dirname(__file__)
MAX_BABY_DRAGON_WIDTH = 150
MAX_BABY_DRAGON_HEIGHT = 150

baby_images = {
    "black": [load_image_with_max_dimensions(os.path.join(base_directory, "assets/images/baby", f"blackbaby{i}.png"), MAX_BABY_DRAGON_WIDTH, MAX_BABY_DRAGON_HEIGHT) for i in range(1, 6)],
    "white": [load_image_with_max_dimensions(os.path.join(base_directory, "assets/images/baby", f"whitebaby{i}.png"), MAX_BABY_DRAGON_WIDTH, MAX_BABY_DRAGON_HEIGHT) for i in range(1, 6)],
    "rainbow": [load_image_with_max_dimensions(os.path.join(base_directory, "assets/images/baby", f"rainbowbaby{i}.png"), MAX_BABY_DRAGON_WIDTH, MAX_BABY_DRAGON_HEIGHT) for i in range(1, 6)],
    "metallic": [load_image_with_max_dimensions(os.path.join(base_directory, "assets/images/baby", f"metallicbaby{i}.png"), MAX_BABY_DRAGON_WIDTH, MAX_BABY_DRAGON_HEIGHT) for i in range(1, 6)]
}


class EggTimer:
    def __init__(self, egg_index, egg_position, egg, duration=10, default_trait="independent"):
        self.egg_index = egg_index
        self.egg_position = egg_position
        self.egg_id = egg['id']
        self.egg_phenotype = egg['phenotype']
        self.duration = duration
        self.default_trait = default_trait
        self.start_ticks = pygame.time.get_ticks()
        self.selected_trait = None
        self.running = True
        self.baby_dragon_image = None
        self.adult_dragon_image = None
        self.mid_image_loaded = False
        self.hide_egg_rect = False
        self.events = {5: self.mid_timer_event, 0: self.end_timer_event}


    def update(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        countdown = self.duration - int(seconds)

        if countdown in self.events:
            self.events[countdown]()

        return countdown

    def display(self):
        countdown = self.update()
        if self.running:
            timer_text = font.render(str(countdown), True, (57, 255, 20))
            screen.blit(timer_text, (self.egg_position[0], self.egg_position[1] - 30))
        else:
            if self.baby_dragon_image:
                print(f"Displaying baby dragon image for egg index: {self.egg_index} at position: {self.egg_position}")
                screen.blit(self.baby_dragon_image, self.egg_position)
            elif self.adult_dragon_image:
                screen.blit(self.adult_dragon_image, self.egg_position)
        return self.selected_trait if not self.running else None

    def mid_timer_event(self):
        if not self.mid_image_loaded:
            if self.egg_phenotype in baby_images:
                self.baby_dragon_image = random.choice(baby_images[self.egg_phenotype])
                if self.baby_dragon_image:
                    print(f"Mid-timer event: {self.baby_dragon_image} loaded for egg index: {self.egg_index} with size {self.baby_dragon_image.get_size()}")
                else:
                    print(f"Mid-timer event: Failed to load baby image for egg index: {self.egg_index}")
                self.mid_image_loaded = True
                self.hide_egg_rect = True

    def end_timer_event(self):
        self.running = False
        self.selected_trait = self.default_trait
        self.adult_dragon_image = get_dragon_image(self.egg_id)
        print(f"Dragon image loaded for egg index: {self.egg_index}")

import random
import string

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
        self.type = phenotype  # egg phenotype to start
        self.special_abilities = None
        self.petname = None
        self.facing_direction = None  # Ensure facing_direction is initialized
        self.doc_id = None  # Add doc_id attribute

    def add_elixir_info(self, rgb, title, primary, secondaries):
        print(f"Adding elixir info: rgb={rgb}, type={type(rgb)}, title={title}, primary={primary}, secondaries={secondaries}")  # Debugging print
        self.elixir_rgb = rgb
        self.elixir_title = title
        self.elixir_primary = primary
        self.elixir_secondaries = secondaries

    def add_dragon_info(self, dragon_data):
        self.dragon_id = dragon_data.get('id')
        self.dragon_name = dragon_data.get('name')
        self.primary = dragon_data.get('primary_characteristic')
        self.secondary1 = dragon_data.get('secondary_trait1')
        self.secondary2 = dragon_data.get('secondary_trait2')
        self.secondary3 = dragon_data.get('secondary_trait3')
        self.nurture = dragon_data.get('Nurture')
        self.gender = dragon_data.get('gender')
        self.rgb_range = dragon_data.get('rgb_value_range')
        self.filename = dragon_data.get('filename')
        self.type = dragon_data.get('type')  # Dragon type overrides egg
        self.special_abilities = dragon_data.get('special_abilities')
        self.facing_direction = dragon_data.get('facing_direction', None)  # Ensure facing_direction is assigned
        print(f"Assigned facing_direction: {self.facing_direction} for dragon_id: {self.dragon_id}")  # Debugging print

    def set_petname(self, petname):
        self.petname = petname

    def _generate_unique_doc_id(self):
        while True:
            new_doc_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
            doc_ref = db.collection('hatcheddragons').document(new_doc_id)
            if not doc_ref.get().exists:
                return new_doc_id

    def save_to_db(self):
        try:
            # Generate a unique doc_id
            self.doc_id = self._generate_unique_doc_id()
            dragon_ref = db.collection('hatcheddragons').document(self.doc_id)
            
            # Create dragon data dictionary
            dragon_data = {
                'genotype': self.genotype,
                'parent1': self.parent1,
                'parent2': self.parent2,
                'elixir_rgb': self.elixir_rgb,
                'elixir_title': self.elixir_title,
                'dragon_id': self.dragon_id,
                'dragon_name': self.dragon_name,
                'primary_trait': self.primary,
                'secondary1': self.secondary1,
                'secondary2': self.secondary2,
                'secondary3': self.secondary3,
                'nurture': self.nurture,
                'gender': self.gender,
                'rgb_range': self.rgb_range,
                'filename': self.filename,
                'type': self.type,
                'special_abilities': self.special_abilities,
                'petname': self.petname,
                'facing_direction': self.facing_direction
            }
            
            # Save dragon data to Firestore
            dragon_ref.set(dragon_data)
            print(f"Dragon with facing_direction: {self.facing_direction} saved successfully to Firestore with doc_id: {self.doc_id}")  # Debugging print

        except Exception as e:
            print(f"Error saving dragon to Firestore: {e}")

# Add these lines before the main function
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)


# Function to check for overlapping rectangles
def is_overlapping(new_rect, rect_list):
    for rect in rect_list:
        if new_rect.colliderect(rect):
            return True
    return False

while len(egg_positions) < 10:
    pos = (random.randint(EGG_PADDING, WIDTH - EGG_PADDING - 80), random.randint(EGG_PADDING, HEIGHT - EGG_PADDING - 80))
    new_rect = pygame.Rect(pos, egg_size)
    if not is_overlapping(new_rect, egg_positions):
        egg_positions.append(new_rect)

def draw_screen(selected_egg_index, active_timers, dragon_images):
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)

        if not any(timer.hide_egg_rect for timer in active_timers if timer.egg_index == i):
            pygame.draw.rect(screen, egg_colors[i], rect)
            if egg_images[i] is not None:
                screen.blit(egg_images[i], rect.topleft)

        if dragon_images[i] is not None:
            #print(f"Drawing adult dragon image at position: {rect.topleft}")
            screen.blit(dragon_images[i], rect.topleft)

        for egg_timer in active_timers:
            if egg_timer.egg_index == i and egg_timer.baby_dragon_image is not None:
                #print(f"Drawing baby dragon image at position: {egg_timer.egg_position}")
                screen.blit(egg_timer.baby_dragon_image, egg_timer.egg_position)  # Draw baby dragon at resized size

    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    for egg_timer in active_timers[:]:
        egg_timer.display()

    pygame.display.flip()

 
def display_egg_menu(selected_egg_index, eggs):
    running = True
    menu_font = pygame.font.Font(None, 28)
    menu_rects = []

    while running:
        screen.fill(GREY)
        menu_rects.clear()  # Clear the list to avoid duplication

        # Filter out placed eggs
        available_eggs = [egg for egg in eggs if egg['id'] not in placed_egg_ids]

        for i, egg in enumerate(available_eggs):
            item_text = f"{egg['id']}, {egg['phenotype']}, P1: {egg['parent1_name']} & {egg['parent2_name']}"  # Assuming field names
            text_surf = menu_font.render(item_text, True, BLACK)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 50 + i * 30))
            screen.blit(text_surf, text_rect)
            menu_rects.append((text_rect, egg['id']))  # Store the egg ID

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for rect, egg_id in menu_rects:
                    if rect.collidepoint(x, y):
                        selected_egg = next((egg for egg in available_eggs if egg['id'] == egg_id), None)
                        if selected_egg:
                            phenotype = selected_egg['phenotype']
                            # Update the egg image based on the phenotype
                            if phenotype in egg_images_dict:
                                egg_images[selected_egg_index] = egg_images_dict[phenotype]
                            else:
                                egg_images[selected_egg_index] = unhatched_egg_image  # Default image if phenotype not found

                            egg_selected_from_db[selected_egg_index] = True  # Mark egg as selected from database
                            placed_egg_ids.append(selected_egg['id'])  # Add egg ID to placed eggs list
                            running = False
                            print(f"Egg selected from menu: {selected_egg['id']}")  # Debug print
                            return selected_egg['id']  # Return the selected egg ID
    return None

                      

def fetch_random_nurture_options():
    try:
        options = {}
        for option in ['A', 'B', 'C', 'D']:
            nurture_ref = db.collection('nurture').where('option', '==', option)
            nurture_docs = nurture_ref.get()
            nurture_list = list(nurture_docs)
            if nurture_list:
                selected_doc = random.choice(nurture_list)
                options[option] = (selected_doc.get('text'),)  # Fetch only the 'text' field
        return options
    except Exception as e:
        print(f"Firestore error fetching nurture options: {e}")
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
                    selected_trait = option_value[0]  # Correctly fetch the trait
                    running = False
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    return selected_trait


def delete_egg_from_db(egg_id):
    try:
        egg_ref = db.collection('eggs').document(egg_id)
        egg_ref.delete()
        print(f"Egg with ID {egg_id} deleted from Firestore.")
    except Exception as e:
        print(f"Firestore error deleting egg: {e}")



def get_elixir_details(position):
    try:
        elixir_ref = db.collection('elixirs').where(field_path='position', op_string='==', value=position)
        elixir_docs = elixir_ref.get()

        for elixir_doc in elixir_docs:
            if elixir_doc.exists:
                elixir_data = elixir_doc.to_dict()
                rgb = elixir_data.get('rgb')
                if not isinstance(rgb, str):
                    rgb = str(rgb)
                elixir_data['rgb'] = rgb
                print(f"Elixir data retrieved: {elixir_data}")
                return elixir_data
        return None
    except Exception as e:
        print(f"Firestore error retrieving elixir details: {e}")
        return None


def get_statistical_pool(ddragon_instance, dragons, selected_trait):
    pool = []

    elixir_primary = ddragon_instance.elixir_primary if ddragon_instance.elixir_primary is not None else ""
    elixir_secondaries = ddragon_instance.elixir_secondaries if ddragon_instance.elixir_secondaries is not None else []

    for dragon in dragons:
        chances = 0  # Initialize chances for each dragon

        primary_trait = dragon.get('primary_trait') or dragon.get('primary_characteristic')
        nurture_trait = dragon.get('nurture') or dragon.get('Nurture')

        print(f"Processing dragon: {dragon.get('id', 'No ID')} with traits {primary_trait}, {dragon.get('secondary_trait1')}, {dragon.get('secondary_trait2')}, {dragon.get('secondary_trait3')}, nurture: {nurture_trait}")

        # Check for shared primary trait
        if primary_trait == elixir_primary:
            chances += 1

        # Check for shared secondary traits
        for secondary in elixir_secondaries:
            if secondary == dragon.get('secondary_trait1'):
                chances += 1

            if secondary == dragon.get('secondary_trait2'):
                chances += 1

            if secondary == dragon.get('secondary_trait3'):
                chances += 1

        # Adjust chances based on nurture trait
        if chances > 0 and nurture_trait == selected_trait:  # Only increase if there are already some chances
            chances += 1

        if chances > 0:
            pool.extend([dragon] * chances)

    print(f"Generated pool size: {len(pool)}")
    ddragon_instance.pool = pool  # Assign the pool to the Ddragon instance

    return pool


def filter_pool_by_phenotype_and_rgb(pool, egg, elixir_rgb):
    filtered_pool = []

    egg_phenotype = egg['phenotype']
    try:
        # Print to debug the elixir_rgb value and its type before eval
        print(f"elixir_rgb received before eval: {elixir_rgb}, type: {type(elixir_rgb)}")

        # Ensure elixir_rgb is correctly formatted as a string
        elixir_rgb_value = eval(elixir_rgb)  # Convert string representation of RGB to tuple

        print(f"elixir_rgb_value after eval: {elixir_rgb_value}, type: {type(elixir_rgb_value)}")

        for dragon in pool:
            dragon_phenotype = dragon['type']  # Assuming 'type' field represents phenotype
            rgb_ranges = dragon['rgb_value_range'].strip('()').split(', ')  # Adjusted field name

            try:
                dragon_rgb_range = [(int(r.split('-')[0]), int(r.split('-')[1])) for r in rgb_ranges]
            except ValueError as e:
                print(f"Error parsing RGB range for dragon {dragon['id']}: {e}")
                continue

            if egg_phenotype == "metallic":
                if dragon_phenotype not in ["gold", "silver", "metal"]:
                    continue
            elif egg_phenotype != dragon_phenotype:
                continue

            if not (dragon_rgb_range[0][0] <= elixir_rgb_value[0] <= dragon_rgb_range[0][1] and
                    dragon_rgb_range[1][0] <= elixir_rgb_value[1] <= dragon_rgb_range[1][1] and
                    dragon_rgb_range[2][0] <= elixir_rgb_value[2] <= dragon_rgb_range[2][1]):
                continue

            filtered_pool.append(dragon)

    except (SyntaxError, TypeError) as e:
        print(f"Error evaluating elixir_rgb: {elixir_rgb}, type: {type(elixir_rgb)}, error: {e}")
        return filtered_pool

    print(f"Filtered pool size: {len(filtered_pool)}")

    return filtered_pool



#Load baby dragon images
def load_image(file_path):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        print(f"Loaded image from {file_path} with original size {image.get_size()}")  # Debug print
        return image
    except pygame.error as e:
        print(f"Error loading image {file_path}: {e}")
        return None  # Return None if loading fails
    

 #Load baby dragon images   
def load_image_and_resize(file_path, max_width=None, max_height=None):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        if max_width and max_height:
            width, height = image.get_size()
            aspect_ratio = width / height
            if width > max_width or height > max_height:
                if aspect_ratio > 1:  # Wider than tall
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:  # Taller than wide
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
                image = pygame.transform.scale(image, (new_width, new_height))
        return image
    except pygame.error as e:
        print(f"Error loading image {file_path}: {e}")
        return None    
    
def load_selected_dragon_images(ddragon_instances):
    dragon_images = [None] * len(ddragon_instances)
    for i, ddragon in enumerate(ddragon_instances):
        if ddragon and ddragon.filename:
            #print(f"Loading image for dragon {ddragon.dragon_id} with facing direction {ddragon.facing_direction}")  # Debugging print
            dragon_image = load_dragon_image(ddragon.filename)
            dragon_images[i] = dragon_image
    return dragon_images


def load_dragon_image(dragon_filename):
    base_directory = os.path.dirname(__file__)
    dragon_image_path = os.path.join(base_directory, "assets/images/dragons", dragon_filename)

    if not os.path.exists(dragon_image_path):
        print(f"File not found: {dragon_image_path}")
        return unhatched_egg_image

    try:
        dragon_image = pygame.image.load(dragon_image_path).convert_alpha()
        width, height = dragon_image.get_size()
        scale_factor = 80 / min(width, height)
        new_size = (int(width * scale_factor), int(height * scale_factor))
        dragon_image = pygame.transform.scale(dragon_image, new_size)
        return dragon_image
    except pygame.error as e:
        print(f"Error loading image {dragon_filename}: {e}")
        return unhatched_egg_image


def get_dragon_image(dragon_id):
    try:
        dragon_ref = db.collection('dragons').document(dragon_id)
        dragon_doc = dragon_ref.get()
        if dragon_doc.exists:
            dragon_filename = dragon_doc.to_dict().get('filename')
            if dragon_filename:
                return load_dragon_image(dragon_filename)
        return unhatched_egg_image
    except Exception as e:
        print(f"Firestore error retrieving dragon image: {e}")
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


def get_elixir_details_from_variable():
    return current_elixir_details


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
        for ddragon in ddragon_list:
            # Generate a unique document ID for each dragon
            doc_id = ddragon._generate_unique_doc_id()
            dragon_ref = db.collection('hatcheddragons').document(doc_id)
            
            # Create dragon data dictionary
            dragon_data = {
                'genotype': ddragon.genotype,
                'parent1': ddragon.parent1,
                'parent2': ddragon.parent2,
                'elixir_rgb': ddragon.elixir_rgb,
                'elixir_title': ddragon.elixir_title,
                'dragon_id': ddragon.dragon_id,
                'dragon_name': ddragon.dragon_name,
                'primary_trait': ddragon.primary,
                'secondary1': ddragon.secondary1,
                'secondary2': ddragon.secondary2,
                'secondary3': ddragon.secondary3,
                'nurture': ddragon.nurture,
                'gender': ddragon.gender,
                'rgb_range': ddragon.rgb_range,
                'filename': ddragon.filename,
                'type': ddragon.type,
                'special_abilities': ddragon.special_abilities,
                'petname': ddragon.petname,
                'facing_direction': ddragon.facing_direction
            }
            
            # Save dragon data to Firestore
            dragon_ref.set(dragon_data)
            print(f"Dragon with facing_direction: {ddragon.facing_direction} saved successfully to Firestore with doc_id: {doc_id}")  # Debugging print

        print(f"Saved {len(ddragon_list)} Ddragon instances to Firestore")
    except Exception as e:
        print(f"Error saving ddragon instances to Firestore: {e}")


def main():
    global elixir_color, eggs, dragons  # Declare dragons as global
    elixir_color = None
    running = True
    selected_egg_index = None  # For egg position on the board
    print("Initial selected_egg_index:", selected_egg_index)
    active_timers = []
    elixir_data = None  # Initialize elixir_data
    current_elixir_details = None  # Go-between variable to store elixir details

    # Fetch eggs from Firestore
    eggs = fetch_eggs_from_firestore()

    # Fetch dragons from Firestore
    dragons = fetch_dragons_from_firestore()

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
                        print("selected_egg_index set to:", selected_egg_index)
                        egg_selected = True
                        selected_egg_id = display_egg_menu(selected_egg_index, eggs)
                        if selected_egg_id is not None:
                            # Fetch the selected egg from the database using the selected_egg_id
                            selected_egg = next((egg for egg in eggs if egg['id'] == selected_egg_id), None)
                            print("Selected egg from database:", selected_egg)
                            if selected_egg:
                                phenotype = selected_egg['phenotype']
                                print("Phenotype from selected egg:", phenotype)
                                ddragon_instance = Ddragon(selected_egg['genotype'], selected_egg['parent1_name'], selected_egg['parent2_name'], phenotype)
                                ddragon_instances[selected_egg_index] = ddragon_instance
                                egg_ids_on_board[selected_egg_index] = selected_egg_id
                                print(f"Created Ddragon instance for egg index {selected_egg_index} with ID {selected_egg_id} and phenotype {phenotype}")
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
                                    selected_egg = next((egg for egg in eggs if egg['id'] == egg_id), None)
                                    new_timer = EggTimer(selected_egg_index, egg_position, selected_egg)  # Pass the egg dictionary
                                    active_timers.append(new_timer)
                                    active_timers_dict[selected_egg_index] = new_timer

                                # Update the Ddragon instance with elixir information
                                if ddragon_instances[selected_egg_index] is not None:
                                    ddragon_instances[selected_egg_index].add_elixir_info(
                                        elixir['rgb'],
                                        elixir['title'],
                                        elixir['primary_trait'],
                                        [elixir['secondary_trait1'], elixir['secondary_trait2'], elixir['secondary_trait3']]
                                    )

                                    # Display nurture options and update the Ddragon instance
                                    selected_trait = display_nurture_options()
                                    if selected_trait is not None:
                                        ddragon_instances[selected_egg_index].nurture = selected_trait

                                        # Update the pool in the Ddragon instance
                                        ddragon_instances[selected_egg_index].pool = get_statistical_pool(ddragon_instances[selected_egg_index], dragons, selected_trait)

                                # Remove elixir from inventory and delete from database
                                inventory_slots[i] = None
                                elixir_color = None
                                delete_elixir_data(i + 1)  # Use the position argument
                                break


        for egg_timer in active_timers[:]:
            selected_trait = egg_timer.display()
            if selected_trait is not None:
                ddragon_instance = ddragon_instances[egg_timer.egg_index]  # Get the correct Ddragon instance
                if selected_trait and ddragon_instance:
                    # Use the correct egg from the database
                    selected_egg = next((egg for egg in eggs if egg['id'] == egg_ids_on_board[egg_timer.egg_index]), None)
                    filtered_pool = filter_pool_by_phenotype_and_rgb(ddragon_instance.pool, selected_egg, ddragon_instance.elixir_rgb)
                    selected_dragon = select_dragon_from_pool(filtered_pool, egg_positions[egg_timer.egg_index])
                    if selected_dragon:
                        print(f"Selected dragon: {selected_dragon['id']} for egg index {egg_timer.egg_index}")
                        if ddragon_instances[egg_timer.egg_index] is not None:
                            ddragon_instances[egg_timer.egg_index].add_dragon_info(selected_dragon)

                            # Prompt the user for a pet name with a timeout
                            petname = get_text_input(f"Enter a pet name for your dragon (Egg Index {egg_timer.egg_index}): ", font, screen, timeout=10)
                            ddragon_instances[egg_timer.egg_index].set_petname(petname)

                            # Accumulate the Ddragon instance to save later
                            ddragon_save_list.append(ddragon_instances[egg_timer.egg_index])
                    else:
                        print(f"No dragon selected for egg {egg_timer.egg_index}")
                        # Ensure egg is deleted from database when timer ends

                egg_id = egg_ids_on_board[egg_timer.egg_index]
                delete_egg_from_db(egg_id)  # Call the existing delete function

                active_timers.remove(egg_timer)
                del active_timers_dict[egg_timer.egg_index]  # Remove from dictionary

        # Load the selected dragon images
        dragon_images = load_selected_dragon_images(ddragon_instances)

        draw_screen(selected_egg_index, active_timers, dragon_images)
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

