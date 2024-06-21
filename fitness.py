import pygame
import sqlite3
import logging
import os
from game import initialize, draw_text, load_image, save_inventory_data, draw_inventory, font, small_font, fruit_images_dict, egg_images_dict, fruit_names

# Initialize the game
initialize()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Game")

# Colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Background image
background = load_image("background.png", (WIDTH, HEIGHT))

# Global inventory variables
inventory = {}
egg_counts = {}
inventory_slots = []

def initialize_inventory():
    global inventory, egg_counts, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}
    egg_counts = {egg: 0 for egg in egg_images_dict.keys()}
    inventory_slots = [None] * 10

initialize_inventory()

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), 'dragonsedit.db')
    conn = sqlite3.connect(db_path)
    return conn

def modify_database():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Add 'completed' field to quests table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE quests ADD COLUMN completed INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            pass  # Column already exists, ignore the error
        else:
            raise

    conn.commit()
    conn.close()

modify_database()

def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    initialize_inventory()  # Ensure the inventory is initialized before loading data

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

def load_quests(dragon_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quest_id, title, description, challenge_rating, rewards, completed FROM quests WHERE dragon_id=?", (dragon_id,))
    quests = cursor.fetchall()
    conn.close()
    return quests

def draw_area_gameboard(dragon_id):
    screen.fill(GREY)
    draw_text(screen, f"Area Gameboard {dragon_id}", font, WHITE, (WIDTH // 2 - 150, 20))

    # Load and display quests
    quests = load_quests(dragon_id)
    for i, quest in enumerate(quests):
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        color = GREY if quest[5] else BLUE  # Grey out if completed
        pygame.draw.rect(screen, color, (x, y, 150, 50))
        draw_text(screen, quest[1], small_font, WHITE, (x + 10, y + 15))

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()

def complete_quest(quest_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE quests SET completed=1 WHERE quest_id=?", (quest_id,))
    conn.commit()
    conn.close()

def handle_quest_click(dragon_id, mouse_x, mouse_y):
    quests = load_quests(dragon_id)
    for i, quest in enumerate(quests):
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        if x <= mouse_x <= x + 150 and y <= mouse_y <= y + 50:
            if not quest[5]:  # Only handle if not already completed
                complete_quest(quest[0])
                update_inventory(quest[4])
            break

def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    inventory[fruit] += amount
    save_inventory_data()

def draw_hub_gameboard():
    screen.fill(GREY)
    draw_text(screen, "Hub Gameboard", font, WHITE, (WIDTH // 2 - 100, 20))

    # Example dragon icons (placeholders)
    dragon_positions = [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]
    for i, pos in enumerate(dragon_positions):
        pygame.draw.circle(screen, BLUE, pos, 50)
        draw_text(screen, f"Dragon {i+1}", small_font, WHITE, (pos[0] - 30, pos[1] - 10))

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()

def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if current_screen == 'hub':
                    # Check if any dragon icon is clicked
                    for i, pos in enumerate([(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        if (mouse_x - pos[0]) ** 2 + (mouse_y - pos[1]) ** 2 <= 50 ** 2:
                            selected_area = i + 1
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    handle_quest_click(selected_area, mouse_x, mouse_y)

        if current_screen == 'hub':
            draw_hub_gameboard()
        elif current_screen == 'area' and selected_area is not None:
            draw_area_gameboard(selected_area)

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")
    print("Game loop ended")

if __name__ == "__main__":
    # Initialize the game
    initialize()
    
    # Load inventory data
    try:
        load_inventory_data()
        logging.info("Initial inventory data loaded successfully")
        print("Initial inventory data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading initial inventory data: {e}")
        print(f"Error loading initial inventory data: {e}")

    # Start the game loop
    game_loop()

    # Save inventory data on exit
    save_inventory_data()
