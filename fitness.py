import random
import sqlite3
import logging

import pygame

from game import initialize, draw_text, load_image, load_inventory_data, save_inventory_data, draw_inventory

# Initialize the game
initialize()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fitness Tracker")

# Colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Background image
background = load_image("background.png", (WIDTH, HEIGHT))

initialize()

def draw_hub_gameboard():
    screen.fill(GREY)
    draw_text(screen, "Hub Gameboard", font, WHITE, (WIDTH // 2 - 100, 20))

    # Example dragon icons (placeholders)
    dragon_positions = [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]
    for i, pos in enumerate(dragon_positions):
        pygame.draw.circle(screen, BLUE, pos, 50)
        draw_text(screen, f"Dragon {i+1}", small_font, WHITE, (pos[0] - 30, pos[1] - 10))

    pygame.display.flip()

def draw_area_gameboard(dragon_id):
    screen.fill(GREY)
    draw_text(screen, f"Area Gameboard {dragon_id}", font, WHITE, (WIDTH // 2 - 150, 20))

    # Placeholder for dragon and quests
    draw_text(screen, f"Dragon {dragon_id}", small_font, WHITE, (WIDTH // 2 - 50, 100))
    for i in range(9):
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        pygame.draw.rect(screen, BLUE, (x, y, 150, 50))
        draw_text(screen, f"Quest {i+1}", small_font, WHITE, (x + 40, y + 15))

    pygame.display.flip()
    
    def complete_quest(quest_id):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quests WHERE quest_id=?", (quest_id,))
    conn.commit()
    conn.close()

def handle_quest_click(dragon_id, mouse_x, mouse_y):
    quests = load_quests(dragon_id)
    for i, quest in enumerate(quests):
        x = (i % 3) * 200 + 300
        y = (i // 3) * 100 + 200
        if x <= mouse_x <= x + 150 and y <= mouse_y <= y + 50:
            complete_quest(quest[0])
            update_inventory(quest[3])
            break

def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    inventory[fruit] += amount
    save_inventory_data()
    
def setup_sample_quests():
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()

    # Add sample quests if they don't already exist
    cursor.execute("SELECT COUNT(*) FROM quests")
    if cursor.fetchone()[0] == 0:
        sample_quests = [
            ("Clean the kitchen", "Clean all surfaces and mop the floor.", 2, "2 flamefruit", 1),
            ("Daily run", "Run 5 kilometers.", 3, "3 etherealpear", 2),
            ("Cook dinner", "Prepare a healthy meal.", 1, "1 shimmeringapple", 3),
            # Add more sample quests as needed
        ]
        cursor.executemany("INSERT INTO quests (title, description, challenge_rating, rewards, dragon_id) VALUES (?, ?, ?, ?, ?)", sample_quests)

    conn.commit()
    conn.close()

setup_sample_quests()

def load_quests(dragon_id):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quest_id, title, description, challenge_rating, rewards FROM quests WHERE dragon_id=?", (dragon_id,))
    quests = cursor.fetchall()
    conn.close()
    return quests

def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_screen == 'hub':
                    mouse_x, mouse_y = event.pos
                    # Check if any dragon icon is clicked
                    for i, pos in enumerate([(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        if (mouse_x - pos[0]) ** 2 + (mouse_y - pos[1]) ** 2 <= 50 ** 2:
                            selected_area = i + 1
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    # Implement quest button clicks here
                    pass

        if current_screen == 'hub':
            draw_hub_gameboard()
        elif current_screen == 'area' and selected_area is not None:
            draw_area_gameboard(selected_area)

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")
    print("Game loop ended")

if __name__ == "__main__":
    try:
        load_inventory_data()
        logging.info("Initial inventory data loaded successfully")
        print("Initial inventory data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading initial inventory data: {e}")
        print(f"Error loading initial inventory data: {e}")

    game_loop()

    save_inventory_data()
