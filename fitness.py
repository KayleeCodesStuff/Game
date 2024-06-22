import pygame
import sqlite3
import logging
import os
from game import initialize, draw_text, load_image, draw_inventory, font, small_font, fruit_images_dict, egg_images_dict, fruit_names, inventory, egg_counts, inventory_slots

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


def connect_db(db_name):
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    return conn

def modify_database():
    conn = connect_db('dragonsedit.db')
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
    logging.info("Loading inventory data from save.db")
    
    try:
        with connect_db('save.db') as conn:
            cursor = conn.cursor()

            # Load fruits inventory
            cursor.execute("SELECT fruit, count FROM inventory")
            rows = cursor.fetchall()
            for row in rows:
                fruit, count = row
                inventory[fruit] = count
                logging.info(f"Loaded {count} of {fruit}")

            # Load eggs counts from eggs table
            cursor.execute("SELECT phenotype, COUNT(*) FROM eggs GROUP BY phenotype")
            rows = cursor.fetchall()
            for row in rows:
                phenotype, count = row
                egg_counts[phenotype] = count
                logging.info(f"Loaded {count} of {phenotype} eggs")

            # Load elixirs into inventory slots
            cursor.execute("SELECT rgb, image_file, position FROM elixirs")
            rows = cursor.fetchall()
            for row in rows:
                rgb = tuple(map(int, row[0][1:-1].split(', ')))
                image_file, position = row[1], row[2]
                inventory_slots[position - 1] = (rgb, image_file)
                logging.info(f"Loaded elixir at position {position}")

    except sqlite3.Error as e:
        logging.error(f"SQLite error loading inventory data: {e}")
        print(f"SQLite error loading inventory data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error loading inventory data: {e}")
        print(f"Unexpected error loading inventory data: {e}")

    logging.info("Inventory loaded successfully")

def save_inventory_data():
    logging.info("Saving inventory data to save.db")
    try:
        with connect_db('save.db') as conn:
            cursor = conn.cursor()
            for fruit, count in inventory.items():
                cursor.execute("UPDATE inventory SET count = ? WHERE fruit = ?", (count, fruit))
                logging.info(f"Saved {count} of {fruit}")

            for egg, count in egg_counts.items():
                cursor.execute("UPDATE egg_inventory SET count = ? WHERE phenotype = ?", (count, egg))
                logging.info(f"Saved {count} of {egg} eggs")

            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"SQLite error saving inventory data: {e}")
        print(f"SQLite error saving inventory data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error saving inventory data: {e}")
        print(f"Unexpected error saving inventory data: {e}")
    logging.info("Inventory saved successfully")

def load_quests(dragon_id):
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quest_id, title, description, challenge_rating, rewards, completed FROM quests WHERE dragon_id=?", (dragon_id,))
    quests = cursor.fetchall()
    conn.close()
    return quests

def complete_quest(quest_id):
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE quests SET completed=1 WHERE quest_id=?", (quest_id,))
    conn.commit()
    conn.close()

def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    logging.info(f"Updating inventory: Adding {amount} of {fruit}")
    inventory[fruit] += amount
    logging.info(f"New inventory count for {fruit}: {inventory[fruit]}")
    save_inventory_data()

def handle_quest_click(dragon_id, mouse_x, mouse_y):
    quests = load_quests(dragon_id)
    total_challenge_rating = 0
    for i, quest in enumerate(quests):
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        if x <= mouse_x <= x + 150 and y <= mouse_y <= y + 50:
            if not quest[5]:  # Only handle if not already completed
                complete_quest(quest[0])
                update_inventory(quest[4])
                total_challenge_rating += quest[3]
                if total_challenge_rating >= 10:
                    flag_dragon_aggressive(dragon_id)
            break

def flag_dragon_aggressive(dragon_id):
    # Placeholder function for flagging dragon as aggressive
    print(f"Dragon {dragon_id} is now aggressive!")

# Function to load images with additional logging and debug prints
def load_image_with_debug(file_name, scale_to):
    try:
        image = pygame.image.load(file_name).convert()
        logging.info(f"Loaded image {file_name}")
        print(f"Loaded image {file_name}")
        return pygame.transform.scale(image, scale_to)
    except pygame.error as e:
        logging.error(f"Error loading image {file_name}: {e}")
        print(f"Error loading image {file_name}: {e}")
        return pygame.Surface(scale_to)  # Return a blank surface as a placeholder

# Load the background image using the debug load_image function
background_path = os.path.join(os.path.dirname(__file__), "background.png")
background = load_image_with_debug(background_path, (WIDTH, HEIGHT))

# Ensure the background is displayed in the game loop
def draw_hub_gameboard():
    screen.fill(GREY)
    screen.blit(background, (0, 0))  # Add this line to blit the background image
    draw_text(screen, "Hub Gameboard", font, WHITE, (WIDTH // 2 - 100, 20))

    # Example dragon icons (placeholders)
    dragon_positions = [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]
    for i, pos in enumerate(dragon_positions):
        pygame.draw.circle(screen, BLUE, pos, 50)
        draw_text(screen, f"Dragon {i+1}", small_font, WHITE, (pos[0] - 30, pos[1] - 10))

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()

def draw_area_gameboard(dragon_id):
    screen.fill(GREY)
    screen.blit(background, (0, 0))  # Add this line to blit the background image
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
    logging.info("Saving inventory data on exit")
    save_inventory_data()
    logging.info("Inventory data saved on exit")
    print("Inventory data saved on exit")
