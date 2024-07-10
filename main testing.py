import logging
import os
import random
import time
import pygame
from game import *
from combat import *
from firebase_config import db
from Mixolator import main
from breeding import mainloop
from hatchery import main_loop

# Set up logging
logging.basicConfig(level=logging.INFO)

def log_time(message):
    logging.info(f"{message}: {time.time()}")

# Set the environment variable to the path of your Firebase credentials JSON file
service_account_path = 'C:\\Users\\kayle\\PycharmProjects\\Game\\taskhatchery-firebase-admin.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
log_time("Firebase credentials set")

# Initialize the game
start_time = time.time()
initialize()
log_time(f"Game initialized in {time.time() - start_time:.2f} seconds")

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
start_time = time.time()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Activity Tracker")
log_time(f"Screen set up in {time.time() - start_time:.2f} seconds")

# Colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
REDDISH_ORANGE = (255, 69, 0)
GREEN = (0, 125, 0)
PURPLE = (128, 0, 128)
LIGHT_GREY = (220, 220, 220)

# Category to color mapping
CATEGORY_INFO = {
    'daily': {'color': MAGENTA, 'fruit': 'gleamberry'},
    'cleaning': {'color': REDDISH_ORANGE, 'fruit': 'flamefruit'},
    'dining': {'color': GREEN, 'fruit': 'shimmeringapple'},
    'exercise': {'color': BLUE, 'fruit': 'etherealpear'},
    'goals': {'color': PURPLE, 'fruit': 'moonbeammelon'}
}

# Initialize player tokens for each category
player_tokens = {
    'daily': 0,
    'cleaning': 0,
    'dining': 0,
    'exercise': 0,
    'goals': 0
}

# Load the background image using the existing load_image function from game.py
start_time = time.time()
background_path = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'background.png')
background = load_image(background_path, (WIDTH, HEIGHT))
log_time(f"Background loaded in {time.time() - start_time:.2f} seconds")

# Load fonts
start_time = time.time()
category_font = pygame.font.Font(None, 60)  # Larger font for category word
token_font = pygame.font.Font(None, 90)  # Much larger font for player token count
small_font = pygame.font.Font(None, 36)  # Smaller font for button text
log_time(f"Fonts loaded in {time.time() - start_time:.2f} seconds")

# Initialize dragons
selected_dragons = [None] * 5
selected_dragon_for_upgrade = None  # Global variable to store the selected dragon
loaded_images = {}

def initialize_dragons():
    global selected_dragons
    start_time = time.time()
    if not any(selected_dragons):
        selected_dragons = get_random_dragons()
    log_time(f"Dragons initialized in {time.time() - start_time:.2f} seconds")

def draw_hub_gameboard():
    global selected_dragon_for_upgrade
    screen.fill(GREY)
    draw_background(screen, background)
    draw_text(screen, "Hub Gameboard", category_font, WHITE, (WIDTH // 2 - 100, 20))
    initialize_dragons()
    draw_dragons(screen, selected_dragons)
    draw_inventory(screen, inventory, egg_counts, inventory_slots)
    upgrade_dragon_rect = draw_upgrade_dragon_button(screen)
    mixolator_button_rect = draw_mixolator_button(screen)
    breedery_button_rect = draw_breedery_button(screen)
    hatchery_button_rect = draw_hatchery_button(screen)

    if selected_dragon_for_upgrade:
        display_dragon_statistics(selected_dragon_for_upgrade, upgrade_dragon_rect)

    back_button_rect = draw_back_to_hub_button()

    pygame.display.flip()
    return upgrade_dragon_rect, mixolator_button_rect, breedery_button_rect, hatchery_button_rect, back_button_rect

def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None
    boss_dragon_filename = None
    player_dragons = initialize_player_dragons()
    displayed_quests = []
    global selected_dragon_for_upgrade
    boss_dragon_stats = None

    global inventory, egg_counts, inventory_slots
    inventory, egg_counts, inventory_slots = load_inventory_data()
    
    redraw_hub = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if current_screen == 'hub':
                    if not handle_fruit_click_in_inventory(mouse_x, mouse_y, selected_dragon_for_upgrade):
                        selected_dragon_for_upgrade = handle_upgrade_dragon_click(
                            mouse_x, mouse_y, upgrade_dragon_rect, player_dragons)
                    for i, pos in enumerate([(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        dragon_image_file = selected_dragons[i]
                        dragon_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'dragons', dragon_image_file)
                        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))
                        image_rect = dragon_image.get_rect(center=pos)
                        if image_rect.collidepoint(mouse_x, mouse_y):
                            selected_area = list(CATEGORY_INFO.keys())[i]
                            boss_dragon_filename = dragon_image_file
                            boss_dragon = BossDragon(boss_dragon_filename, tier=1)
                            boss_dragon_stats = (boss_dragon.stats['health'], boss_dragon.stats['attack'],
                                                 boss_dragon.stats['defense'], boss_dragon.stats['dodge'])
                            all_quests = load_quests(selected_area)
                            displayed_quests = random.sample(all_quests, min(12, len(all_quests)))
                            current_screen = 'area'
                            redraw_hub = True
                            break
                    if mixolator_button_rect.collidepoint(mouse_x, mouse_y):
                        main()
                        redraw_hub = True
                    if breedery_button_rect.collidepoint(mouse_x, mouse_y):
                        mainloop()
                        redraw_hub = True
                    if hatchery_button_rect.collidepoint(mouse_x, mouse_y):
                        main_loop()
                        redraw_hub = True
                elif current_screen == 'area':
                    if back_button_rect.collidepoint(mouse_x, mouse_y):
                        current_screen = 'hub'
                        redraw_hub = True
                    elif fight_button_rect and fight_button_rect.collidepoint(mouse_x, mouse_y):
                        if player_tokens[selected_area] >= 10:
                            player_tokens[selected_area] -= 10
                            if any(dragon is not None for dragon in player_dragons):
                                start_combat(player_dragons, boss_dragon_stats, draw_area_gameboard, screen,
                                             selected_area, player_tokens, displayed_quests, boss_dragon_filename)
                            else:
                                print("Error: At least one player dragon must be initialized.")
                    else:
                        displayed_quests, quests_updated = handle_quest_click(selected_area, mouse_x, mouse_y,
                                                                              displayed_quests)
                        handle_player_dragon_slot_click(mouse_x, mouse_y, player_dragons)
                        if quests_updated:
                            draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)

            elif event.type == pygame.KEYDOWN and selected_dragon_for_upgrade:
                if event.key == pygame.K_1:
                    if spend_fruit_and_update_stats('gleamberry', selected_dragon_for_upgrade):
                        redraw_hub = True
                elif event.key == pygame.K_2:
                    if spend_fruit_and_update_stats('flamefruit', selected_dragon_for_upgrade):
                        redraw_hub = True
                elif event.key == pygame.K_3:
                    if spend_fruit_and_update_stats('shimmeringapple', selected_dragon_for_upgrade):
                        redraw_hub = True
                elif event.key == pygame.K_4:
                    if spend_fruit_and_update_stats('etherealpear', selected_dragon_for_upgrade):
                        redraw_hub = True
                elif event.key == pygame.K_5:
                    if spend_fruit_and_update_stats('moonbeammelon', selected_dragon_for_upgrade):
                        redraw_hub = True

        if current_screen == 'hub' and redraw_hub:
            upgrade_dragon_rect, mixolator_button_rect, breedery_button_rect, hatchery_button_rect, back_button_rect = draw_hub_gameboard()
            if selected_dragon_for_upgrade:
                display_dragon_statistics(selected_dragon_for_upgrade, upgrade_dragon_rect)
            redraw_hub = False
        elif current_screen == 'area' and selected_area is not None:
            fight_button_rect, back_button_rect = draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")

if __name__ == "__main__":
    start_time = time.time()
    initialize()
    logging.info(f"Initialization completed in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    load_inventory_data()
    logging.info(f"Inventory data loaded in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    game_loop()
    logging.info(f"Game loop executed in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    save_inventory_data()
    logging.info(f"Inventory data saved in {time.time() - start_time:.2f} seconds")
