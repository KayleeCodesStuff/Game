import pygame
import sqlite3
from tkinter import Tk, filedialog
import os

# Constants
WIDTH, HEIGHT = 800, 600
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module

# Define font
small_font = pygame.font.Font(None, 24)

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

save_file = "/mnt/data/save.db"
if os.path.exists(save_file):
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

def draw_text(surface, text, font, color, rect):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))

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
            draw_text(surface, "?", small_font, WHITE, box_rect)
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
        draw_text(surface, str(inventory[fruit]), small_font, WHITE, pygame.Rect(x_offset + 20, y_offset + 45, 30, 30))
        x_offset += 60  # Move right for the next fruit

def select_or_create_file():
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.asksaveasfilename(defaultextension=".db",
                                             filetypes=[("SQLite database", "*.db"), ("JSON file", "*.json")],
                                             title="Select or Create File")
    return file_path

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
    
    conn.commit()
    conn.close()

# Example usage
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Breeding Game")

def main():
    running = True
    selected_inventory_slot = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear the screen with black
        draw_inventory(screen, fruit_counts, selected_inventory_slot)
        pygame.display.flip()  # Update the display

    pygame.quit()

if __name__ == "__main__":
    main()
