import pygame
import sqlite3
import logging
import os
import random
from game import initialize, draw_text, load_image, draw_inventory, font, small_font, fruit_images_dict, egg_images_dict, fruit_names, inventory, egg_counts, inventory_slots, load_and_resize_image
# Initialize the game
initialize()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Activity Tracker")

# Colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
REDDISH_ORANGE = (255, 69, 0)
GREEN = (0, 125, 0)
PURPLE = (128, 0, 128)

# Category to color mapping
CATEGORY_INFO = {
    'daily': {'color': MAGENTA, 'fruit': 'gleamberry'},
    'cleaning': {'color': REDDISH_ORANGE, 'fruit': 'flamefruit'},
    'dining': {'color': GREEN, 'fruit': 'shimmeringapple'},
    'exercise': {'color': BLUE, 'fruit': 'etherealpear'},
    'goals': {'color': PURPLE, 'fruit': 'moonbeammelon'}
}

# Load the background image using the existing load_image function from game.py
background_path = os.path.join(os.path.dirname(__file__), "background.png")
background = load_image(background_path, (WIDTH, HEIGHT))

def connect_db(db_name):
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    return conn

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

def load_quests(category):
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Category, Description, ChallengeRating, Reward, completed FROM quests WHERE Category=?", (category,))
    quests = cursor.fetchall()
    conn.close()
    #print(f"Loaded quests for category {category}: {quests}")
    return quests

def complete_quest(quest_id):
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE quests SET completed=1 WHERE ID=?", (quest_id,))
    conn.commit()
    conn.close()

def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    logging.info(f"Updating inventory: Adding {amount} of {fruit}")
    inventory[fruit] += amount
    logging.info(f"New inventory count for {fruit}: {inventory[fruit]}")
    save_inventory_data()



def flag_dragon_aggressive(category):
    # Placeholder function for flagging dragon as aggressive
    print(f"Category {category} is now aggressive!")

def draw_beveled_button(surface, rect, color, text, font):
    pygame.draw.rect(surface, color, rect, border_radius=10)  # Draw the button with beveled edges
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)  # Outline with white color
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_area_gameboard(category):
    screen.fill(GREY)
    screen.blit(background, (0, 0))
    draw_text(screen, f"Area Gameboard {category}", font, WHITE, (WIDTH // 2 - 150, 20))

    # Load and display quests
    quests = load_quests(category)
    # print(f"Drawing quests for category {category}: {quests}")
    button_height = 50  # Fixed height for consistency
    grid_cols = 3
    grid_rows = 4
    grid_width = WIDTH // grid_cols
    grid_height = (HEIGHT * 0.6) // grid_rows
    margin_x = (grid_width - button_height) // 2
    margin_y = (grid_height - button_height) // 2

    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = HEIGHT * 0.4 + (i // grid_cols) * grid_height + margin_y
        color = CATEGORY_INFO.get(quest[1], {}).get('color', BLUE)
        if quest[5]:  # If completed
            color = GREY
        rect = pygame.Rect(x, y, button_width, button_height)
        # print(f"Drawing button for quest {quest[0]} at {rect} with color {color}")
        draw_beveled_button(screen, rect, color, quest[2], small_font)

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    # Draw back to hub button
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 150, 150, 50)
    draw_beveled_button(screen, back_button_rect, RED, "Back to Hub", small_font)

    pygame.display.flip()


def get_random_dragon():
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM dragons")
    dragons = cursor.fetchall()
    conn.close()
    return random.choice(dragons)[0]

# Initialize the selected dragons
selected_dragons = [None] * 5  # Placeholder for the selected dragons

def initialize_dragons():
    for i in range(len(selected_dragons)):
        if selected_dragons[i] is None:
            selected_dragons[i] = get_random_dragon()

def load_and_resize_image_keeping_aspect(file_path, max_size):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        width, height = image.get_size()
        aspect_ratio = width / height

        if width > height:
            new_width = max_size[0]
            new_height = new_width / aspect_ratio
        else:
            new_height = max_size[1]
            new_width = new_height * aspect_ratio

        new_size = (int(new_width), int(new_height))
        logging.info(f"Loaded and resized image {file_path} to {new_size}")
        return pygame.transform.scale(image, new_size)
    except pygame.error as e:
        logging.error(f"Error loading image {file_path}: {e}")
        print(f"Error loading image {file_path}: {e}")
        return pygame.Surface(max_size)  # Return a blank surface as a placeholder

def draw_hub_gameboard():
    screen.fill(GREY)
    screen.blit(background, (0, 0))
    draw_text(screen, "Hub Gameboard", font, WHITE, (WIDTH // 2 - 100, 20))

    # Initialize dragons if not already done
    initialize_dragons()

    # Example dragon icons (randomly selected from database)
    dragon_positions = [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]

    for i, pos in enumerate(dragon_positions):
        dragon_image_file = selected_dragons[i]
        dragon_image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon_image_file)
        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))  # Resize to fit within 150x150 while keeping aspect ratio
        image_rect = dragon_image.get_rect(center=pos)
        screen.blit(dragon_image, image_rect.topleft)
        draw_text(screen, f"Dragon {i+1}", small_font, WHITE, (pos[0] - 30, pos[1] + 60))

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    pygame.display.flip()

def handle_quest_click(category, mouse_x, mouse_y):
    quests = load_quests(category)
    total_challenge_rating = 0
    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        rect = pygame.Rect(x, y, button_width, 50)
        if rect.collidepoint(mouse_x, mouse_y):
            if not quest[5]:  # Only handle if not already completed
                complete_quest(quest[0])
                update_inventory(quest[4])
                total_challenge_rating += quest[3]
                if total_challenge_rating >= 10:
                    flag_dragon_aggressive(category)
            break

# Sample game loop calling the updated draw_hub_gameboard function
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
                    for i, pos in enumerate([(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        dragon_image_file = selected_dragons[i]
                        dragon_image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon_image_file)
                        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))  # Resize to fit within 150x150
                        image_rect = dragon_image.get_rect(center=pos)
                        if image_rect.collidepoint(mouse_x, mouse_y):
                            selected_area = list(CATEGORY_INFO.keys())[i]
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    if WIDTH - 200 <= mouse_x <= WIDTH - 50 and HEIGHT - 100 <= mouse_y <= HEIGHT - 50:
                        current_screen = 'hub'
                    else:
                        handle_quest_click(selected_area, mouse_x, mouse_y)

        if current_screen == 'hub':
            draw_hub_gameboard()
        elif current_screen == 'area' and selected_area is not None:
            draw_area_gameboard(selected_area)

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")
    print("Game loop ended")

# Call the game loop to test the updated function
if __name__ == "__main__":
    initialize()
    load_inventory_data()
    game_loop()
    save_inventory_data()