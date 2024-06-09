import pygame
import sqlite3
import os
import random
import math
from tkinter import Tk, filedialog

# Constants
WIDTH, HEIGHT = 800, 600
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

# Load background image
background = pygame.image.load(BACKGROUND_IMAGE)
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

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

# Load fruit counts from the save file or use default values
default_fruit_counts = {"gleamberry": 5, "flamefruit": 5, "shimmeringapple": 5, "etherealpear": 5, "moonbeammelon": 5}
fruit_counts = default_fruit_counts.copy()

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
        
        # Insert default fruit counts
        for fruit, count in default_fruit_counts.items():
            cursor.execute("INSERT INTO inventory (fruit, count) VALUES (?, ?)", (fruit, count))
        
        conn.commit()
        conn.close()
    
    initialize_file(save_file)

try:
    conn = sqlite3.connect(save_file)
    cursor = conn.cursor()
    cursor.execute("SELECT fruit, count FROM inventory")
    rows = cursor.fetchall()
    for row in rows:
        fruit, count = row
        fruit_counts[fruit] = count
    conn.close()
except Exception as e:
    print(f"Error loading save file: {e}")
    fruit_counts = default_fruit_counts.copy()

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

# Function to outline image
def outline_image(image, color, thickness=3):
    mask = pygame.mask.from_surface(image)
    outline = mask.outline()
    outline_surface = image.copy()
    pygame.draw.lines(outline_surface, color, True, outline, thickness)
    return outline_surface

# Create dragon dictionary
for i, dragon_data in enumerate(selected_dragons):
    dragon_image_path = os.path.join(DRAGON_IMAGE_FOLDER, dragon_data[1])
    dragon_image = pygame.image.load(dragon_image_path)
    
    width, height = dragon_image.get_size()
    if is_aspect_ratio_16_9(width, height):
        scale_factor = 50 / min(width, height)
        new_size = (int(width * scale_factor), int(height * scale_factor))
    else:
        # Scale to fit within a 50x50 box while preserving aspect ratio
        if width > height:
            new_size = (50, int(50 * (height / width)))
        else:
            new_size = (int(50 * (width / height)), 50)
    
    dragon_image = pygame.transform.scale(dragon_image, new_size)
    outline_color = BLUE if dragon_data[10] == "Male" else RED
    dragon_image = outline_image(dragon_image, outline_color)
    
    initial_speed = 1.5 + (0.5 if "speed" in dragon_data[4].lower() or "Flightspeed" in dragon_data[6] else 0)
    
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
        "holding_fruit": None
    }
    dragons.append(dragon)

# Function to draw text
def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

# Function to draw inventory
def draw_inventory(surface, inventory, selected_inventory_slot=None):
    pygame.draw.rect(surface, BLUE, (0, HEIGHT - 100, WIDTH, 100))  # Adjusted to fit within the screen dimensions

    # Example inventory slots for potions (assuming inventory_slots is defined elsewhere)
    inventory_slots = [None] * 5  # Placeholder for actual inventory slot data
    x_offset = WIDTH - 60 * len(inventory_slots)  # Start from the rightmost part of the screen
    y_offset = HEIGHT - 90
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

    # Draw the fruits in the remaining space
    x_offset = 10  # Reset x_offset for fruit images
    for fruit, image in fruit_images_dict.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(inventory[fruit]), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60  # Move right for the next fruit

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
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

# Function to determine target for a dragon
def determine_target(dragon):
    if not dragon["holding_fruit"] and fruits_on_board:
        fruits_on_board.sort(key=lambda f: calculate_distance(dragon["rect"].topleft, f["position"]))
        return fruits_on_board[0]["position"]
    else:
        targets = [d for d in dragons if d["gender"] != dragon["gender"]]
        if targets:
            targets.sort(key=lambda d: calculate_distance(dragon["rect"].topleft, d["rect"].topleft))
            return targets[0]["rect"].topleft
    return None

# Function to move dragons
def move_dragons():
    for dragon in dragons:
        if not dragon["target"]:
            dragon["target"] = determine_target(dragon)
            print(f"Dragon {dragon['name']} targeting {dragon['target']}")
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
                if not any(dragon_rect_copy.colliderect(d["rect"]) for d in dragons if d["id"] != dragon["id"]):
                    dragon["rect"].x = new_x
                    dragon["rect"].y = new_y
                    print(f"Dragon {dragon['name']} moving to {dragon['rect'].topleft}")

            if distance < 5:  # Reached target
                # Collect fruit if target is a fruit
                if dragon["holding_fruit"] is None:
                    for fruit in fruits_on_board:
                        if fruit["position"] == dragon["target"]:
                            dragon["holding_fruit"] = fruit["type"]
                            fruits_on_board.remove(fruit)
                            print(f"Dragon {dragon['name']} collected {fruit['type']}")
                            break
                dragon["target"] = determine_target(dragon)  # Reassign target
# Example usage
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

# Main game loop with interactivity
def place_fruit(x, y, selected_fruit):
    if selected_fruit and fruit_counts[selected_fruit] > 0:
        fruits_on_board.append({"type": selected_fruit, "position": (x - 25, y - 25)})
        fruit_counts[selected_fruit] -= 1
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
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x, y = mouse_pos
                # Check if clicking on a fruit in the inventory
                if y > HEIGHT - 100:
                    slot_index = (x - 10) // 60
                    if 0 <= slot_index < len(fruit_names):
                        selected_fruit = fruit_names[slot_index]
                # Place fruit on board
                else:
                    place_fruit(x, y, selected_fruit)
                    selected_fruit = None

        move_dragons()  # Update dragon positions

        screen.fill((0, 0, 0))  # Clear the screen with black
        screen.blit(background, (0, 0))  # Draw background image
        draw_inventory(screen, fruit_counts, selected_inventory_slot)
        draw_dragons(screen)
        draw_fruits_on_board(screen)
        pygame.display.flip()  # Update the display

        clock.tick(10)  # Set the frame rate to 10 FPS

    pygame.quit()

if __name__ == "__main__":
    main()