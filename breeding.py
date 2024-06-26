import pygame
import os
import random
import time
from firebase_config import db
import math
from tkinter import Tk, filedialog
from game import initialize, draw_inventory, load_inventory_data, save_inventory_data, load_and_resize_image, draw_inventory, define_elixir_data

import time
# Constants
WIDTH, HEIGHT = 1200, 900
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

DRAGON_IMAGE_FOLDER = os.path.join("assets", "images", "dragons")  # Correct folder containing dragon images
FRUIT_SPEED_MODIFIERS = {
    "gleamberry": -0.5,
    "shimmeringapple": 0.5,
}

# Initialization pygame and fonts from Game module
initialize()

# Define font
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 36)

# Button properties
button_font = pygame.font.Font(None, 36)
invite_dragon_button_rect = pygame.Rect(WIDTH - 220, HEIGHT - 170, 200, 60)  # Increased size
hatched_dragon_button_rect = pygame.Rect(WIDTH - 220, HEIGHT - 240, 200, 60)  # Increased sizey

# Define screen (surface)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

# Load images
background = load_and_resize_image("breedingbackground.png", (WIDTH, HEIGHT))
heart_image = load_and_resize_image("heart.png", (30, 30))
hearts_on_board = []
fruit_names = ["gleamberry", "flamefruit", "shimmeringapple", "etherealpear", "moonbeammelon"]
fruit_images = [load_and_resize_image(f"{fruit}.png", (50, 50)) for fruit in fruit_names]

egg_names = ["black", "white", "rainbow", "metallic"]
egg_images = [load_and_resize_image(f"{egg}_egg.png", (70, 70)) for egg in egg_names]

# Create a dictionary mapping names to their images
fruit_images_dict = dict(zip(fruit_names, fruit_images))
egg_images_dict = dict(zip(egg_names, egg_images))
   
# Placeholder for dragons
dragons = []
repulsor_counter = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

tested_pairs = set()

# Function to draw eggs on the game board
eggs_on_board = []

# Function to draw fruits on the game board
fruits_on_board = []

inventory, egg_counts, inventory_slots = load_inventory_data()
# Replace custom draw_inventory with standardized one
draw_inventory(screen, inventory, egg_counts, inventory_slots)

fruit_personality_keywords = {
    "gleamberry": ["Dark", "Brooding", "Responsible", "Common"],
    "flamefruit": ["Distraction", "Fierce", "Fiery", "Showy"],
    "shimmeringapple": ["Speed", "Flightiness", "Drive", "Ambition"],
    "etherealpear": ["Earthy", "Pragmatic", "Stout", "Loyal"],
    "moonbeammelon": ["Angelic", "Unique", "Pure", "Self-righteous"]
}

# Define the alleles and their dominance hierarchy
allele_dominance = {
    'B': 'black',
    'W': 'white',
    'R': 'rainbow',
    'M': 'metallic'
}

# Possible genotypes for each phenotype
phenotype_to_genotypes = {
    'black': [('B', 'B'), ('B', 'W'), ('B', 'R'), ('B', 'M')],
    'white': [('W', 'W'), ('W', 'R'), ('W', 'M')],
    'rainbow': [('R', 'R'), ('R', 'M')],
    'metallic': [('M', 'M')]
}


def draw_hearts(surface):
    current_time = pygame.time.get_ticks()
    for heart in hearts_on_board[:]:
        if current_time - heart["start_time"] > 3000:
            hearts_on_board.remove(heart)
        else:
            surface.blit(heart_image, heart["position"])


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

    # Firestore operations
    egg_data = {
        'genotype': str(egg_genotype),
        'phenotype': egg_phenotype,
        'image_file': egg_image_path,
        'parent1_name': parent1_name,
        'parent2_name': parent2_name
    }

    # Generate a custom ID for the document
    custom_id = f"{parent1_name}{parent2_name}{int(time.time())}"

    try:
        egg_ref = db.collection('eggs').document(custom_id)
        egg_ref.set(egg_data)
        print(f"Egg data saved successfully with ID: {egg_ref.id}")
    except Exception as e:
        print(f"Error saving egg data: {e}")

  

def load_dragons_from_db():
    all_dragons = []
    try:
        # Load dragons data from Firestore
        dragons_ref = db.collection('dragons')
        docs = dragons_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            #print(f"Loaded dragon data: {data}")  # Debug print to show loaded data
            all_dragons.append((
                int(doc.id),  # Convert document ID to integer if needed
                data.get('filename'),
                data.get('type'),
                data.get('name'),
                data.get('primary_characteristic'),
                data.get('secondary_trait1'),
                data.get('secondary_trait2'),
                data.get('secondary_trait3'),
                data.get('special_abilities'),
                data.get('description'),
                data.get('rgb_value_range'),
                data.get('Nurture'),
                data.get('gender')
            ))
    except Exception as e:
        print(f"Error loading dragons data: {e}")

    return all_dragons


def initialize_dragons():
    all_dragons = load_dragons_from_db()
    selected_dragons = random.sample(all_dragons, 10)
    male_dragons = [d for d in selected_dragons if d[-1] == "Male"]
    female_dragons = [d for d in selected_dragons if d[-1] == "Female"]

    # Ensure there are both genders
    if len(male_dragons) == 0 or len(female_dragons) == 0:
        print("Not enough dragons of both genders in the selection, please check the database.")
        exit()

    # Generate positions for dragons (ensure at least 10 positions)
    positions = [(x * WIDTH // 4, y * HEIGHT // 4) for x in range(1, 4) for y in range(1, 4)]
    while len(positions) < 9:
        positions.append((random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 150)))  # Add random positions if not enough
    positions = positions[:9]  # Ensure exactly 9 positions
    positions.append((WIDTH // 2, 0))  # Position the 10th dragon at the top center
    random.shuffle(positions)

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
        outline_color = BLUE if dragon_data[12] == "Male" else RED
        dragon_image = outline_image(dragon_image, outline_color)
        
        initial_speed = 1.5 

        phenotype = dragon_data[2]
        if phenotype in ["gold", "silver", "metal"]:
            phenotype = "metallic"
        genotype = random.choice(phenotype_to_genotypes[phenotype])
        
        dragon = {
            "id": dragon_data[0],
            "name": dragon_data[3],
            "type": dragon_data[2],
            "primary_characteristic": dragon_data[4],
            "secondary_traits": [dragon_data[5], dragon_data[6], dragon_data[7]],
            "special_abilities": dragon_data[8],
            "description": dragon_data[9],
            "rgb_value_range": dragon_data[10],
            "nurture": dragon_data[11],
            "gender": dragon_data[12],
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
            
def load_hatched_dragons_from_db():
    hatched_dragons = []
    try:
        # Load hatched dragons data from Firestore
        hatched_dragons_ref = db.collection('hatcheddragons')
        docs = hatched_dragons_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            doc_id = int(doc.id)  # Convert Firestore document ID to integer to handle leading zeros
            print(f"Loaded hatched dragon document ID: {doc_id}, data: {data}")  # Debugging statement
            hatched_dragons.append((
                doc_id,  # Use the document ID as the dragon's ID
                data.get('filename'),
                data.get('type'),
                data.get('petname'),
                data.get('primary_trait'),
                data.get('secondary1'),
                data.get('secondary2'),
                data.get('secondary3'),
                data.get('special_abilities'),
                data.get('dragon_name'),
                data.get('rgb_range'),
                data.get('nurture'),
                data.get('gender')
            ))
    except Exception as e:
        print(f"Error loading hatched dragons data: {e}")

    return hatched_dragons

        
def draw_hatched_dragon_list(surface, hatched_dragons, font, selected_index):
    start_y = 50
    item_height = 30
    padding = 20  # Padding around the text

    # Calculate the width of the longest text field
    max_text_width = max(font.size(dragon[3] if dragon[3] else dragon[9])[0] for dragon in hatched_dragons)
    list_width = max_text_width + padding * 2  # Add padding to the width
    list_height = len(hatched_dragons) * item_height + 10  # Calculate height based on the number of dragons
    background_rect = pygame.Rect(40, start_y - 10, list_width, list_height)  # Create the background rectangle

    # Draw the background
    pygame.draw.rect(surface, (0, 0, 0, 200), background_rect)  # Opaque black background

    for index, dragon in enumerate(hatched_dragons):
        text_color = WHITE if index != selected_index else BLUE
        dragon_name = dragon[3] if dragon[3] else dragon[9]  # Use petname if available, otherwise fallback to dragon_name
        text_surface = font.render(dragon_name, True, text_color)
        surface.blit(text_surface, (background_rect.x + padding, start_y + index * item_height))
    return start_y, item_height


def handle_hatched_dragon_selection(event, hatched_dragons, selected_index):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_index = (selected_index - 1) % len(hatched_dragons)
        elif event.key == pygame.K_DOWN:
            selected_index = (selected_index + 1) % len(hatched_dragons)
        elif event.key == pygame.K_RETURN:
            return selected_index
    return None

def handle_hatched_dragon_click(mouse_pos, hatched_dragons, start_y, item_height):
    x, y = mouse_pos
    if 50 <= x <= 300:  # Assuming the names are drawn within this range
        index = (y - start_y) // item_height
        if 0 <= index < len(hatched_dragons):
            return index
    return None

def summon_hatched_dragon_by_index(hatched_dragons, index, dragons, summoned_dragon_ids):
    new_dragon_data = hatched_dragons.pop(index)  # Remove the summoned dragon from the list
    dragon_image_path = os.path.join(DRAGON_IMAGE_FOLDER, new_dragon_data[1])
    dragon_image = pygame.image.load(dragon_image_path)
    
    width, height = dragon_image.get_size()
    scale_factor = 50 / min(width, height)  # Match the initial size (50x50)
    new_size = (int(width * scale_factor), int(height * scale_factor))
    dragon_image = pygame.transform.scale(dragon_image, new_size)
    outline_color = BLUE if new_dragon_data[12] == "Male" else RED
    dragon_image = outline_image(dragon_image, outline_color)

    initial_speed = 1.5
    if new_dragon_data[4] is not None and "speed" in new_dragon_data[4].lower():
        initial_speed += 0.5
    if new_dragon_data[8] is not None and "Flightspeed" in new_dragon_data[8]:
        initial_speed += 0.5
        
    phenotype = new_dragon_data[2]
    if phenotype in ["gold", "silver", "metal"]:
        phenotype = "metallic"
    genotype = random.choice(phenotype_to_genotypes[phenotype])
    
    dragon_name = new_dragon_data[3] if new_dragon_data[3] else new_dragon_data[9]  # Use petname if available, otherwise fallback to dragon_name
    
    new_dragon = {
        "id": new_dragon_data[0],
        "name": dragon_name,
        "type": new_dragon_data[2],
        "primary_characteristic": new_dragon_data[4],
        "secondary_traits": [new_dragon_data[5], new_dragon_data[6], new_dragon_data[7]],
        "special_abilities": new_dragon_data[8],
        "description": new_dragon_data[9],
        "rgb_value_range": new_dragon_data[10],
        "nurture": new_dragon_data[11],
        "gender": new_dragon_data[12],
        "image": dragon_image,
        "rect": dragon_image.get_rect(topleft=(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 150))),
        "speed": initial_speed,
        "target": None,
        "holding_fruit": None,
        "genotype": genotype,
        "source": "hatched"
    }
    new_dragon["target"] = determine_target(new_dragon)  # Immediately determine target
    dragons.append(new_dragon)
    summoned_dragon_ids.add(new_dragon_data[0])
    print(f"Summoned new hatched dragon: {new_dragon['name']}")


def is_aspect_ratio_16_9(width, height):
    return abs((width / height) - (16 / 9)) < 0.01  # Allowing a small margin for floating point comparisons

def assign_genotype(dragon):
    phenotype = dragon["type"]  # Assuming 'type' is used for phenotype
    if phenotype in ["gold", "silver", "metal"]:
        phenotype = "metallic"
    if phenotype == "black":
        genotype = random.choice(phenotype_to_genotypes["black"])
    elif phenotype == "white":
        genotype = random.choice(phenotype_to_genotypes["white"])
    elif phenotype == "rainbow":
        genotype = random.choice(phenotype_to_genotypes["rainbow"])
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

def draw_button(surface, text, font, text_color, rect, border_color, border_width, bg_color):
    pygame.draw.rect(surface, bg_color, rect)  # Draw opaque background
    pygame.draw.rect(surface, border_color, rect, border_width)  # Draw border
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))


def handle_button_click(mouse_pos, rect, inventory, dragons, summoned_dragon_ids):
    if rect.collidepoint(mouse_pos) and inventory["moonbeammelon"] >= 10:
        summon_new_dragon(inventory, dragons, summoned_dragon_ids)

def summon_new_dragon(inventory, dragons, summoned_dragon_ids):
    if inventory["moonbeammelon"] < 10:
        print("Not enough moonbeammelon to summon a new dragon.")
        return

    inventory["moonbeammelon"] -= 10

    # Load dragons from Firestore
    all_dragons = load_dragons_from_db()
    print(f"All dragons loaded from Firestore: {all_dragons}")  # Debugging statement

    if not all_dragons:
        print("No dragons available in the database.")
        return

    # Filter out already summoned dragons
    available_dragons = [d for d in all_dragons if d[0] not in summoned_dragon_ids]
    #print(f"Available dragons after filtering: {available_dragons}")  # Debugging statement

    if not available_dragons:
        print("All dragons have already been summoned.")
        return

    new_dragon_data = random.choice(available_dragons)
    #print(f"Selected dragon data: {new_dragon_data}")  # Debugging statement
    dragon_image_path = os.path.join("assets", "images", "dragons", new_dragon_data[1])
    #print(f"Dragon image path: {dragon_image_path}")  # Debugging statement
    dragon_image = pygame.image.load(dragon_image_path)
    
    width, height = dragon_image.get_size()
    scale_factor = 50 / min(width, height)  # Match the initial size (50x50)
    new_size = (int(width * scale_factor), int(height * scale_factor))
    dragon_image = pygame.transform.scale(dragon_image, new_size)
    outline_color = BLUE if new_dragon_data[12] == "Male" else RED
    dragon_image = outline_image(dragon_image, outline_color)

    initial_speed = 1.5

    phenotype = new_dragon_data[2]
    if phenotype in ["gold", "silver", "metal"]:
        phenotype = "metallic"
    genotype = random.choice(phenotype_to_genotypes[phenotype])
    
    new_dragon = {
        "id": new_dragon_data[0],
        "name": new_dragon_data[3],
        "type": new_dragon_data[2],
        "primary_characteristic": new_dragon_data[4],
        "secondary_traits": [new_dragon_data[5], new_dragon_data[6], new_dragon_data[7]],
        "special_abilities": new_dragon_data[8],
        "description": new_dragon_data[9],
        "rgb_value_range": new_dragon_data[10],
        "nurture": new_dragon_data[11],
        "gender": new_dragon_data[12],
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
    #print(f"Summoned new dragon: {new_dragon['name']}")  # Debugging statement



# Function to draw text
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)



def handle_egg_collection(mouse_pos, egg_counts):
    for egg in eggs_on_board:
        if egg["rect"].collidepoint(mouse_pos):
            eggs_on_board.remove(egg)
            break



# Function to draw dragons
def draw_dragons(surface):
    for dragon in dragons:
        surface.blit(dragon["image"], dragon["rect"].topleft)
        if dragon["holding_fruit"]:
            fruit_image = fruit_images_dict[dragon["holding_fruit"]]
            surface.blit(fruit_image, (dragon["rect"].x + 25, dragon["rect"].y + 25))


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
    current_characteristics = set([dragon["primary_characteristic"]] + dragon["secondary_traits"])
    possible_characteristics = [char for char in fruit_characteristics if char not in current_characteristics]
    if possible_characteristics:
        return random.choice(possible_characteristics)
    return None

def compatibility_test(dragon1, dragon2, fruit_personality_keywords):
    if dragon1["gender"] == dragon2["gender"]:
        return False
    
    characteristics1 = set([dragon1["primary_characteristic"], dragon1["secondary_traits"][0], dragon1["secondary_traits"][1], dragon1["secondary_traits"][2]])
    characteristics2 = set([dragon2["primary_characteristic"], dragon2["secondary_traits"][0], dragon2["secondary_traits"][1], dragon2["secondary_traits"][2]])

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
        return 'black'
    elif 'W' in genotype:
        return 'white'
    elif 'R' in genotype:
        return 'rainbow'
    else:
        return 'metallic'


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
            if dragon.get("source") == "hatched":
                delete_hatched_dragon(dragon["id"])  # Delete the hatched dragon from Firestore using document ID
            dragons.remove(dragon)


def place_fruit(x, y, selected_fruit):
    if selected_fruit and inventory[selected_fruit] > 0:
        fruits_on_board.append({"type": selected_fruit, "position": (x - 25, y - 25)})
        inventory[selected_fruit] -= 1
        for dragon in dragons:
            if not dragon["holding_fruit"]:
                dragon["target"] = determine_target(dragon)
        else:
            print(f"Cannot place fruit {selected_fruit}. Inventory: {inventory[selected_fruit] if selected_fruit else 'None'}")

def delete_hatched_dragon(doc_id):
    try:
        # Pad the doc_id with leading zeros to ensure it matches the Firestore document ID format
        padded_doc_id = str(doc_id).zfill(4)
        # Get the reference to the document with the padded_doc_id
        hatched_dragons_ref = db.collection('hatcheddragons').document(padded_doc_id)
        hatched_dragons_ref.delete()
        print(f"Hatched dragon with document ID {padded_doc_id} deleted successfully from Firestore")
    except Exception as e:
        print(f"Error deleting hatched dragon with document ID {padded_doc_id} from Firestore: {e}")


# Main game loop with interactivity
def main():
    
    initialize_dragons()

    running = True
    selected_inventory_slot = None
    selected_fruit = None
    selected_hatched_dragon_index = None
    hatched_dragon_list_visible = False
    spawn_fruits()  # Spawn initial fruits on the board
    clock = pygame.time.Clock()  # Create a clock object to manage frame rate

    # Track summoned dragon IDs
    summoned_dragon_ids = set(dragon["id"] for dragon in dragons)
    hatched_dragons = load_hatched_dragons_from_db()  # Load hatched dragons from save.db

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                save_inventory_data()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x, y = mouse_pos

                # Check if clicking on the buttons
                if invite_dragon_button_rect.collidepoint(mouse_pos):
                    handle_button_click(mouse_pos, invite_dragon_button_rect, inventory, dragons, summoned_dragon_ids)
                elif hatched_dragon_button_rect.collidepoint(mouse_pos):
                    hatched_dragon_list_visible = True
                elif hatched_dragon_list_visible:
                    selected_index = handle_hatched_dragon_click(mouse_pos, hatched_dragons, start_y, item_height)
                    if selected_index is not None:
                        summon_hatched_dragon_by_index(hatched_dragons, selected_index, dragons, summoned_dragon_ids)
                        hatched_dragon_list_visible = False
                # Check if clicking on a fruit in the inventory
                elif y > HEIGHT - 100:
                    slot_index = (x - 10) // 60
                    if 0 <= slot_index < len(fruit_names):
                        selected_fruit = fruit_names[slot_index]
                else:
                    if selected_fruit is not None:
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
        draw_button(screen, "Invite Dragon", button_font, WHITE, invite_dragon_button_rect, BLUE, 2, (0, 0, 0, 200))  # Draw the button with opaque background
        draw_button(screen, "Hatched Dragon", button_font, WHITE, hatched_dragon_button_rect, BLUE, 2, (0, 0, 0, 200))  # Draw the new button with opaque background
        if hatched_dragon_list_visible:
            start_y, item_height = draw_hatched_dragon_list(screen, hatched_dragons, small_font, selected_hatched_dragon_index)
        pygame.display.flip()  # Update the display

        clock.tick(50)  # Set the frame rate to 50 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
