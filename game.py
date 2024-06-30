import pygame
import random
import sqlite3
import logging
from firebase_config import db
import os

# Configure logging
logging.basicConfig(filename='game.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

font = None
small_font = None

# Define initialization functions
def initialize_pygame():
    try:
        pygame.init()
        logging.info("Pygame initialized successfully")
        
    except pygame.error as e:
        logging.error(f"Error initializing pygame: {e}")
        print(f"Error initializing pygame: {e}")

def initialize_fonts():
    try:
        global font, small_font
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)
        logging.info("Fonts initialized successfully")
        
    except pygame.error as e:
        logging.error(f"Error initializing fonts: {e}")
        print(f"Error initializing fonts: {e}")

# Initialization function to be called on import
def initialize():
    initialize_pygame()
    initialize_fonts()
    
# Initialization pygame and fonts from Game module
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
    base_path = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    # Ensure the correct path is used for all images
    if not os.path.isabs(file_name):
        file_name = os.path.join(base_path, file_name)
    elif not file_name.startswith(base_path):
        file_name = os.path.join(base_path, file_name)
    
    try:
        image = pygame.image.load(file_name).convert_alpha()
        logging.info(f"Loaded image {file_name}")
        return pygame.transform.scale(image, scale_to)
    except pygame.error as e:
        logging.error(f"Error loading image {file_name}: {e}")
        print(f"Error loading image {file_name}: {e}")
        return pygame.Surface(scale_to)  # Return a blank surface as a placeholder


background = load_image(os.path.join('background.png'), (WIDTH, HEIGHT))

fruit_images_dict = {
"gleamberry": load_image(os.path.join('gleamberry.png'), (50, 50)),
"flamefruit": load_image(os.path.join('flamefruit.png'), (50, 50)),
"shimmeringapple": load_image(os.path.join('shimmeringapple.png'), (50, 50)),
"etherealpear": load_image(os.path.join('etherealpear.png'), (50, 50)),
"moonbeammelon": load_image(os.path.join('moonbeammelon.png'), (50, 50))
}

egg_images_dict = {
    "black": load_image('eggs/black_egg.png', (65, 65)),
    "white": load_image('eggs/white_egg.png', (65, 65)),
    "rainbow": load_image('eggs/rainbow_egg.png', (65, 65)),
    "metallic": load_image('eggs/metallic_egg.png', (65, 65))
}

# Initialize inventory and egg counts
fruit_names = list(fruit_images_dict.keys())
inventory = {fruit: 5 for fruit in fruit_names}
egg_counts = {egg: 0 for egg in egg_images_dict.keys()}

# Inventory slots
inventory_slots = [None] * 10

# Create inventory slots
inventory_boxes = [pygame.Rect(WIDTH - 600 + i * 60, HEIGHT - 100, 50, 50) for i in range(10)]

def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}
    egg_counts = {egg: 0 for egg in egg_images_dict.keys()}
    inventory_slots = [None] * 10

    try:
        # Load fruits inventory from Firestore
        inventory_ref = db.collection('inventory')
        docs = inventory_ref.stream()
        for doc in docs:
            fruit = doc.id
            count = doc.to_dict().get('count', 0)
            inventory[fruit] = count
            
        # Load eggs counts from Firestore
        eggs_ref = db.collection('eggs')
        docs = eggs_ref.stream()
        phenotype_counts = {}
        for doc in docs:
            phenotype = doc.to_dict().get('phenotype')
            if phenotype:
                if phenotype in phenotype_counts:
                    phenotype_counts[phenotype] += 1
                else:
                    phenotype_counts[phenotype] = 1

        for phenotype, count in phenotype_counts.items():
            egg_counts[phenotype] = count
            

        # Load elixirs into inventory slots from Firestore
        elixirs_ref = db.collection('elixirs')
        docs = elixirs_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            rgb = tuple(map(int, data.get('rgb', '0,0,0').strip('()').split(', ')))
            image_file = data.get('image_file')
            position = data.get('position', 0)
            if 0 < position <= len(inventory_slots):
                inventory_slots[position - 1] = (rgb, image_file)
            #print(f"Loaded elixir at position {position}: {rgb}, {image_file}")

        logging.info("Inventory data loaded successfully")

    except Exception as e:
        logging.error(f"Error loading inventory data: {e}")
        print(f"Error loading inventory data: {e}")

    return inventory, egg_counts, inventory_slots

inventory, egg_counts, inventory_slots = load_inventory_data()


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

    image_filenames = [os.path.join('assets', 'images', 'elixirs', f'pb{i}.png') for i in range(1, 13)]



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

def draw_inventory(surface, inventory, egg_counts, inventory_slots, selected_inventory_slot=None):
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

    # Draw the eggs in the second section, using egg_counts
    x_offset += 10
    for egg_type, count in egg_counts.items():
        egg_image = egg_images_dict[egg_type]
        surface.blit(egg_image, (x_offset, y_offset))
        draw_text(surface, str(count), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 70

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
            # image_filename should already be the correct path
            image = load_image(image_filename, (50, 50))
            surface.blit(image, (x_offset, y_offset))
        x_offset += 60
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)


def save_inventory_data():
    try:
        # Update fruits inventory in Firestore
        for fruit, count in inventory.items():
            db.collection('inventory').document(fruit).set({'count': count})
           
        #print("Inventory data saved successfully")
    except Exception as e:
        logging.error(f"Error saving inventory data: {e}")
        print(f"Error saving inventory data: {e}")



def save_elixir_data(elixir_data):
    try:
        elixirs_ref = db.collection('elixirs')
        #print(f"Saving elixir data at position {elixir_data['position']}")

        # Convert the RGB tuple to a string
        rgb_str = f"({elixir_data['rgb'][0]}, {elixir_data['rgb'][1]}, {elixir_data['rgb'][2]})"

        elixirs_ref.document(str(elixir_data['position'])).set({
            'rgb': rgb_str,
            'title': elixir_data['title'],
            'primary_trait': elixir_data['primary_trait'],
            'secondary_trait1': elixir_data['secondary_trait1'],
            'secondary_trait2': elixir_data['secondary_trait2'],
            'secondary_trait3': elixir_data['secondary_trait3'],
            'image_file': elixir_data['image_file'],
            'position': elixir_data['position']
        })

        #print("Elixir data saved successfully")
    except Exception as e:
        print(f"Error saving elixir data: {e}")

def delete_elixir_data(position):
    try:
        elixirs_ref = db.collection('elixirs')
        query = elixirs_ref.where('position', '==', position).stream()
        
        found = False
        for doc in query:
            found = True
            #print(f"Attempting to delete elixir data with ID {doc.id} at position {position}")
            elixirs_ref.document(doc.id).delete()
            #print(f"Elixir data with ID {doc.id} at position {position} deleted successfully")
        
        if not found:
            print(f"No elixir data found at position {position} to delete")
    except Exception as e:
        print(f"Error deleting elixir data: {e}")


#Updae the inventory in the fitness game after 
def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    print(f"Updating inventory: Adding {amount} of {fruit}")

    # Ensure the fruit exists in the inventory before updating
    if fruit in inventory:
        inventory[fruit] += amount
    else:
        inventory[fruit] = amount
        

    # Save the updated inventory to the database
    save_inventory_data()

def create_egg(dragon1, dragon2, position):
    egg_genotype = get_egg_genotype(dragon1, dragon2)
    egg_phenotype = determine_phenotype(egg_genotype)
    egg_image_path = os.path.join('assets', 'images', 'eggs', f"{egg_phenotype.lower()}_egg.png")
    parent1_name = dragon1["name"]
    parent2_name = dragon2["name"]

    egg_data = {
        "genotype": egg_genotype,
        "phenotype": egg_phenotype,
        "image_file": egg_image_path,
        "parent1_name": parent1_name,
        "parent2_name": parent2_name
    }

    # Save egg data to Firestore
    try:
        egg_ref = db.collection('eggs').document()
        egg_ref.set(egg_data)
        #print(f"Egg data saved successfully with ID: {egg_ref.id}")
    except Exception as e:
        print(f"Error saving egg data: {e}")

    eggs_on_board.append({
        "genotype": egg_genotype,
        "phenotype": egg_phenotype,
        "image": load_image(egg_image_path, (65, 65)),  # Ensure load_image function is defined
        "rect": load_image(egg_image_path, (65, 65)).get_rect(topleft=position)
    })

    # Updating the egg counts in Firestore
    try:
        egg_inventory_ref = db.collection('egg_inventory').document(egg_phenotype)
        egg_inventory_doc = egg_inventory_ref.get()
        if egg_inventory_doc.exists:
            egg_count = egg_inventory_doc.to_dict().get('count', 0) + 1
            egg_inventory_ref.update({'count': egg_count})
        else:
            egg_inventory_ref.set({'count': 1})
        #print(f"Egg inventory updated successfully for phenotype: {egg_phenotype}")
    except Exception as e:
        print(f"Error updating egg inventory: {e}")

    # Removing SQLite related operations
    # (This section was responsible for updating SQLite DB, which is now replaced with Firestore operations)

       
 #load images in the hatchery
def load_and_resize_image(file_path, size):
    base_path = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    # Ensure the correct path is used for all images
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_path, file_path)
    elif not file_path.startswith(base_path):
        file_path = os.path.join(base_path, file_path)
    
    try:
        image = pygame.image.load(file_path).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        logging.error(f"Error loading image {file_path}: {e}")
        print(f"Error loading image {file_path}: {e}")
        return pygame.Surface(size)  # Return a blank surface as a placeholder


# Function to check for overlapping rectangles
def is_overlapping(new_rect, rect_list):
    for rect in rect_list:
        if new_rect.colliderect(rect):
            return True
    return False     
def draw_center_fruits(screen, box_top_left, box_bottom_right, fruit_images_dict):
    box_width = box_bottom_right[0] - box_top_left[0]
    box_height = box_bottom_right[1] - box_top_left[1]

    # Load the fruit images
    gleamberry_image = fruit_images_dict["gleamberry"]
    flamefruit_image = fruit_images_dict["flamefruit"]
    shimmeringapple_image = fruit_images_dict["shimmeringapple"]
    etherealpear_image = fruit_images_dict["etherealpear"]
    moonbeammelon_image = fruit_images_dict["moonbeammelon"]

    # Align the images within the box
    screen.blit(gleamberry_image, box_top_left)
    flamefruit_position = (box_top_left[0], box_top_left[1] + box_height - flamefruit_image.get_height())
    screen.blit(flamefruit_image, flamefruit_position)

    # Calculate the position for the right side images
    shimmeringapple_position = (box_top_left[0] + box_width - shimmeringapple_image.get_width(), box_top_left[1])
    etherealpear_position = (box_top_left[0] + box_width - etherealpear_image.get_width(), box_top_left[1] + box_height - etherealpear_image.get_height())

    # Draw the right side images
    screen.blit(shimmeringapple_image, shimmeringapple_position)
    screen.blit(etherealpear_image, etherealpear_position)

    # Calculate the space for the moonbeammelon image
    space_left = flamefruit_position[0] + flamefruit_image.get_width() + 10
    space_right = shimmeringapple_position[0] - 10
    available_width = space_right - space_left
    available_height = box_height

    # Resize the moonbeammelon image to fit the available space while keeping its aspect ratio
    moonbeammelon_aspect_ratio = moonbeammelon_image.get_width() / moonbeammelon_image.get_height()

    if available_width / moonbeammelon_aspect_ratio <= available_height:
        moonbeammelon_new_width = available_width
        moonbeammelon_new_height = available_width / moonbeammelon_aspect_ratio
    else:
        moonbeammelon_new_height = available_height
        moonbeammelon_new_width = available_height * moonbeammelon_aspect_ratio

    moonbeammelon_image = pygame.transform.scale(moonbeammelon_image, (int(moonbeammelon_new_width), int(moonbeammelon_new_height)))

    # Calculate the position for the moonbeammelon image
    moonbeammelon_position = (
        space_left + (available_width - moonbeammelon_new_width) // 2,
        box_top_left[1] + (available_height - moonbeammelon_new_height) // 2
    )

    screen.blit(moonbeammelon_image, moonbeammelon_position)
