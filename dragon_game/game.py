import pygame
import random
import sys
import sqlite3

pygame.init()

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

# Load images
background = pygame.image.load("background.png").convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load images
fruit_images_dict = {
    "gleamberry": pygame.transform.scale(pygame.image.load("gleamberry.png"), (50, 50)),
    "flamefruit": pygame.transform.scale(pygame.image.load("flamefruit.png"), (50, 50)),
    "shimmeringapple": pygame.transform.scale(pygame.image.load("shimmeringapple.png"), (50, 50)),
    "etherealpear": pygame.transform.scale(pygame.image.load("etherealpear.png"), (50, 50)),
    "moonbeammelon": pygame.transform.scale(pygame.image.load("moonbeammelon.png"), (50, 50))
}

# Initialize inventory
fruit_names = list(fruit_images_dict.keys())
inventory = {fruit: 5 for fruit in fruit_names}

# Inventory slots
inventory_slots = [None] * 10

# Create inventory slots
inventory_boxes = [pygame.Rect(WIDTH - 600 + i * 60, HEIGHT - 100, 50, 50) for i in range(10)]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_inventory(surface, inventory, inventory_slots, selected_inventory_slot=None):
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

    # Draw the elixirs in the second section
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
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (50, 50))
            surface.blit(image, (x_offset, y_offset))
        x_offset += 60
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)

def draw_screen():
    screen.fill(BLACK)
    screen.blit(background, (0, 0))  # Ensure the background is being drawn
    draw_inventory(screen, inventory, inventory_slots)
    pygame.display.flip()  # Ensure the screen updates correctly

def load_inventory_data():
    global inventory, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}

    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fruit, count FROM inventory")
            rows = cursor.fetchall()
            for row in rows:
                fruit, count = row
                inventory[fruit] = count

            cursor.execute("SELECT rgb, image_file, position FROM elixirs")
            rows = cursor.fetchall()
            for row in rows:
                rgb = tuple(map(int, row[0][1:-1].split(', ')))
                image_file, position = row[1], row[2]
                inventory_slots[position - 1] = (rgb, image_file)

    except Exception as e:
        print(f"Error loading inventory data: {e}")

def save_elixir_data(file_path, elixir_data, fruit_counts):
    conn = sqlite3.connect(file_path)
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
    conn.close()

def save_inventory_data():
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            for fruit, count in inventory.items():
                cursor.execute("UPDATE inventory SET count = ? WHERE fruit = ?", (count, fruit))
            cursor.execute("DELETE FROM elixirs")
            for i, slot in enumerate(inventory_slots):
                if slot is not None:
                    rgb, image_file = slot
                    cursor.execute("INSERT INTO elixirs (rgb, image_file, position) VALUES (?, ?, ?)", (str(rgb), image_file, i + 1))
            conn.commit()
    except Exception as e:
        print(f"Error saving inventory data: {e}")

def run_game():
    global elixir_color
    elixir_color = None
    running = True
    selected_inventory_slot = None

    load_inventory_data()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                print(f"Mouse clicked at: {event.pos}")

                for i, rect in enumerate(inventory_boxes):
                    if rect.collidepoint(x, y) and inventory_slots[i] is not None:
                        print(f"Clicked on inventory slot {i} at {rect.topleft}")
                        selected_elixir = inventory_slots[i]
                        elixir_color = selected_elixir[0]
                        break

        draw_screen()

    save_inventory_data()
    pygame.quit()
    sys.exit()
