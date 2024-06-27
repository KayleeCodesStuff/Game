import pygame
import sqlite3
import logging
import os
import random
import time
from game import *
from combat import *

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
background_path = os.path.join(os.path.dirname(__file__), "background.png")
background = load_image(background_path, (WIDTH, HEIGHT))

category_font = pygame.font.Font(None, 60)  # Larger font for category word
# Much larger font for player token count
token_font = pygame.font.Font(None, 90)
small_font = pygame.font.Font(None, 36)  # Smaller font for button text

selected_dragon_for_upgrade = None  # Global variable to store the selected dragon


def connect_db(db_name='save.db'):
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    return conn


def load_quests(category):
    conn = connect_db('save.db')
    cursor = conn.cursor()

    # Update the quests that need to be reset
    cursor.execute("""
        UPDATE playerquests
        SET completed = 0, reset = NULL
        WHERE Category = ? AND reset IS NOT NULL AND reset <= date('now')
    """, (category,))
    conn.commit()

    # Fetch the quests
    cursor.execute(
        "SELECT ID, Category, Description, ChallengeRating, Reward, completed, reset, tally FROM playerquests WHERE Category = ?",
        (category,
         ))
    quests = cursor.fetchall()
    conn.close()
    return quests


def complete_daily_quest(quest_id):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    logging.info(f"Completing daily quest ID {quest_id}")
    cursor.execute(
        "UPDATE playerquests SET completed = 1, reset = date('now', '+1 day') WHERE ID = ?",
        (quest_id,
         ))
    conn.commit()
    conn.close()


def flag_dragon_aggressive(category):
    print(f"Category {category} is now aggressive!")


def draw_beveled_button(surface, rect, color, text, font):
    # Draw the button with beveled edges
    pygame.draw.rect(surface, color, rect, border_radius=10)
    # Outline with white color
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def load_boss_dragon_image(dragon_filename, max_height):
    dragon_image_path = os.path.join(
        os.path.dirname(__file__),
        "dragons",
        dragon_filename)
    try:
        image = pygame.image.load(dragon_image_path).convert_alpha()
        width, height = image.get_size()
        aspect_ratio = width / height

        new_height = max_height
        new_width = new_height * aspect_ratio

        new_size = (int(new_width), int(new_height))
        logging.info(
            f"Loaded and resized boss dragon image {dragon_image_path} to {new_size}")
        return pygame.transform.scale(image, new_size)
    except pygame.error as e:
        logging.error(
            f"Error loading boss dragon image {dragon_image_path}: {e}")
        print(f"Error loading boss dragon image {dragon_image_path}: {e}")
        # Return a blank surface as a placeholder
        return pygame.Surface((max_height * aspect_ratio, max_height))


def draw_beveled_button_gradient(surface, rect, text, font, gradient_colors):
    outline_rect = rect.inflate(4, 4)
    pygame.draw.rect(
        surface,
        gradient_colors[0],
        outline_rect,
        border_radius=10)  # Start of gradient
    pygame.draw.rect(
        surface,
        gradient_colors[1],
        outline_rect,
        2,
        border_radius=10)  # End of gradient

    pygame.draw.rect(surface, RED, rect, border_radius=10)
    # White outline for the button
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_area_gameboard(category, boss_dragon, player_dragons, quests):
    screen.fill(GREY)
    screen.blit(background, (0, 0))

    big_box = pygame.Surface((WIDTH, int(HEIGHT * 0.4)))
    big_box.set_alpha(128)
    big_box.fill((0, 0, 0))
    screen.blit(big_box, (0, 0))

    draw_text(screen, category.capitalize(),
              category_font, WHITE, (WIDTH // 2 - 20, 10))
    token_text = str(player_tokens[category])
    draw_text(screen, token_text, token_font, WHITE, (WIDTH // 2 + 50, 75))

    max_height = int(HEIGHT * 0.35)
    boss_dragon_image = load_boss_dragon_image(
        boss_dragon.filename, max_height)

    if boss_dragon.facing_direction != "right":
        boss_dragon_image = flip_dragon_image(
            boss_dragon_image, boss_dragon.facing_direction, "right")

    screen.blit(boss_dragon_image, (0, 0))

    boss_hp = boss_dragon.current_hitpoints
    boss_max_hp = boss_dragon.maximum_hitpoints
    boss_damage = boss_dragon.damage
    boss_defense = boss_dragon.stats['defense']
    boss_dodge = boss_dragon.stats['dodge']

    stats_text = f"HP: {boss_hp} / {boss_max_hp}  Damage: {boss_damage}  Defense: {boss_defense}  Dodge: {boss_dodge}"
    draw_text(screen, stats_text, small_font, WHITE, (20, max_height + 15))

    box_top_left = (WIDTH // 2 - 45, 140)
    box_bottom_right = (WIDTH - 420, 265)
    draw_center_fruits(
        screen,
        box_top_left,
        box_bottom_right,
        fruit_images_dict)

    button_height = 50
    grid_cols = 3
    grid_rows = 4
    total_grid_height = (HEIGHT - 100) * 0.6 - 20
    total_grid_width = WIDTH
    grid_height = total_grid_height // grid_rows
    grid_width = total_grid_width // grid_cols
    start_y = (HEIGHT - 100) * 0.45

    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = start_y + (i // grid_cols) * grid_height + \
            (grid_height - button_height) // 2
        color = CATEGORY_INFO.get(quest[1], {}).get('color', BLUE)
        if quest[5]:
            color = GREY
        rect = pygame.Rect(x, y, button_width, button_height)
        draw_beveled_button(screen, rect, color, quest[2], small_font)

    draw_inventory(screen, inventory, egg_counts, inventory_slots)
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 60, 150, 50)
    draw_beveled_button(
        screen,
        back_button_rect,
        RED,
        "Back to Hub",
        small_font)

    fight_button_rect = pygame.Rect(WIDTH // 2 - 10, 285, 150, 50)
    draw_beveled_button(screen, fight_button_rect, RED, "Fight!", small_font)

    draw_player_dragon_slots(player_dragons)

    pygame.display.flip()

    return fight_button_rect


def get_random_dragon():
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM dragons")
    dragons = cursor.fetchall()
    conn.close()
    return random.choice(dragons)[0]


selected_dragons = [None] * 5


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
            if new_height > max_size[1]:
                new_height = max_size[1]
                new_width = new_height * aspect_ratio
        else:
            new_height = max_size[1]
            new_width = new_height * aspect_ratio
            if new_width > max_size[0]:
                new_width = max_size[0]
                new_height = new_width / aspect_ratio

        new_size = (int(new_width), int(new_height))
        return pygame.transform.scale(image, new_size)
    except pygame.error as e:
        logging.error(f"Error loading image {file_path}: {e}")
        print(f"Error loading image {file_path}: {e}")
        return pygame.Surface(max_size)


def draw_hub_gameboard():
    global selected_dragon_for_upgrade
    screen.fill(GREY)
    screen.blit(background, (0, 0))
    draw_text(screen, "Hub Gameboard", category_font,
              WHITE, (WIDTH // 2 - 100, 20))

    initialize_dragons()

    dragon_positions = [(100, 200), (300, 200),
                        (500, 200), (700, 200), (900, 200)]

    for i, pos in enumerate(dragon_positions):
        dragon_image_file = selected_dragons[i]
        dragon_image_path = os.path.join(
            os.path.dirname(__file__), "dragons", dragon_image_file)
        dragon_image = load_and_resize_image_keeping_aspect(
            dragon_image_path, (150, 150))
        image_rect = dragon_image.get_rect(center=pos)
        screen.blit(dragon_image, image_rect.topleft)
        draw_text(
            screen,
            f"Dragon {
                i + 1}",
            small_font,
            WHITE,
            (pos[0] - 30,
             pos[1] + 60))

    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    upgrade_dragon_rect = pygame.Rect(
        WIDTH // 3, HEIGHT - 300, WIDTH // 3, 200)
    draw_beveled_button(
        screen,
        upgrade_dragon_rect,
        LIGHT_GREY,
        "Upgrade Dragon",
        small_font)

    if selected_dragon_for_upgrade:
        display_dragon_statistics(
            selected_dragon_for_upgrade,
            upgrade_dragon_rect)

    pygame.display.flip()
    return upgrade_dragon_rect


def display_dragon_statistics(dragon, upgrade_dragon_rect):
    name = dragon.petname if dragon.petname else dragon.dragon_name
    draw_text(
        screen,
        name,
        small_font,
        WHITE,
        (upgrade_dragon_rect.centerx -
         small_font.size(name)[0] //
         2,
         upgrade_dragon_rect.y -
         30))

    # Display dragon image within the upgrade rectangle
    image_path = os.path.join(
        os.path.dirname(__file__),
        "dragons",
        dragon.filename)
    dragon_image = load_and_resize_image_keeping_aspect(
        image_path, (upgrade_dragon_rect.width, upgrade_dragon_rect.height))
    image_rect = dragon_image.get_rect(center=upgrade_dragon_rect.center)
    screen.blit(dragon_image, image_rect.topleft)

    # Display stats above corresponding fruits
    fruit_stat_mapping = {
        'gleamberry': 'health',
        'flamefruit': 'attack',
        'shimmeringapple': 'defense',
        'etherealpear': 'dodge'
    }

    # Reduced font size for stat labels
    reduced_font = pygame.font.Font(None, 24)
    # Larger font size for stat numbers
    large_font = pygame.font.Font(None, 48)

    # Define positions for the stats
    positions = {
        'health': (5, HEIGHT - 110),
        'attack': (65, HEIGHT - 110),
        'defense': (125, HEIGHT - 110),
        'dodge': (200, HEIGHT - 110)
    }

    for fruit, stat in fruit_stat_mapping.items():
        derived_stat_value = dragon.stats[stat]
        stat_text = f"{stat.capitalize()}"
        stat_pos = positions[stat]
        draw_text(screen, str(derived_stat_value), large_font,
                  WHITE, (stat_pos[0] + 10, stat_pos[1] - 60))
        draw_text(screen, stat_text, reduced_font,
                  WHITE, (stat_pos[0], stat_pos[1] - 20))

    # Display current and maximum hitpoints
    hp_text = f"HP: {dragon.current_hitpoints} / {dragon.maximum_hitpoints:.0f}"
    draw_text(
        screen,
        hp_text,
        small_font,
        WHITE,
        (upgrade_dragon_rect.centerx -
         small_font.size(hp_text)[0] //
         2,
         upgrade_dragon_rect.y +
         10))


def draw_text(surface, text, font, color, pos):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)


def handle_upgrade_dragon_click(
        mouse_x,
        mouse_y,
        upgrade_dragon_rect,
        player_dragons):
    if upgrade_dragon_rect.collidepoint(mouse_x, mouse_y):
        selected_dragon_id = display_player_dragon_selection(player_dragons)
        if selected_dragon_id:
            return PlayerDragon(selected_dragon_id)
    return None


def handle_fruit_click_in_inventory(mouse_x, mouse_y, selected_dragon_for_upgrade):
    x_offset = 10
    y_offset = HEIGHT - 90

    for fruit, image in fruit_images_dict.items():
        rect = pygame.Rect(x_offset, y_offset, 50, 50)
        if rect.collidepoint(mouse_x, mouse_y):
            if spend_fruit_and_update_stats(fruit, selected_dragon_for_upgrade, display_error):
                return True
        x_offset += 60
    return False


def spend_fruit_and_update_stats(fruit_type, dragon, display_error):
    if dragon is None:
        print("Error: Dragon object is None.")
        return False

    fruit_to_stat = {
        'gleamberry': 'health',
        'flamefruit': 'attack',
        'shimmeringapple': 'defense',
        'etherealpear': 'dodge',
        'moonbeammelon': 'dodge'  # Adjust as needed
    }

    max_values = {
        'health': 500,
        'attack': 100,
        'defense': 100,
        'dodge': 100
    }

    if fruit_type in inventory and inventory[fruit_type] > 0:
        stat_to_increase = fruit_to_stat[fruit_type]

        # Check if the bonus stat is already at the maximum
        current_bonus_stat = getattr(dragon, 'bonus_' + stat_to_increase)
        if current_bonus_stat >= max_values[stat_to_increase]:
            display_error(f"Maximum {stat_to_increase} reached!")
            return False

        inventory[fruit_type] -= 1  # Decrease the inventory

        # Update the corresponding bonus stat
        if stat_to_increase == 'health':
            dragon.bonus_health += 1
            dragon.current_hitpoints = min(
                dragon.current_hitpoints + 5,
                dragon.maximum_hitpoints + 1)
        elif stat_to_increase == 'attack':
            dragon.bonus_attack += 1
        elif stat_to_increase == 'defense':
            dragon.bonus_defense += 1
        elif stat_to_increase == 'dodge':
            dragon.bonus_dodge += 1

        # Recalculate stats and maximum hitpoints
        dragon.calculate_and_apply_stats()
        dragon.calculate_hitpoints_and_damage()

        # Update dragon stats in the database
        update_dragon_stats_in_db(dragon)

        # Debugging prints
        print(f"Updated {stat_to_increase}: {dragon.stats[stat_to_increase]}")
        print(f"Updated bonus {stat_to_increase}: {getattr(dragon, 'bonus_' + stat_to_increase)}")
        print(f"New maximum hitpoints: {dragon.maximum_hitpoints}")
        print(f"New current hitpoints: {dragon.current_hitpoints}")

        return True
    return False


def display_error(message):
    font = pygame.font.SysFont(None, 72)  # Larger font size
    text = font.render(message, True, pygame.Color('red'))
    text_rect = text.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)  # Adjust position as needed

    # Save the current screen content under the text area
    original_screen_content = screen.subsurface(text_rect).copy()
    
    start_time = time.time()

    # Display the message for 3 seconds
    while time.time() - start_time < 3:
        screen.blit(text, text_rect)
        pygame.display.update(text_rect)  # Only update the text area
        pygame.time.delay(100)

    # Restore the original screen content
    screen.blit(original_screen_content, text_rect)
    pygame.display.update(text_rect)  # Only update the text area
    
def update_dragon_stats_in_db(dragon):
    db_path = os.path.join(os.path.dirname(__file__), 'save.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE hatcheddragons
        SET bonus_health = ?, bonus_attack = ?, bonus_defense = ?, bonus_dodge = ?, current_hitpoints = ?, bonus_base_hitpoints = ?
        WHERE id = ?
    """, (dragon.bonus_health, dragon.bonus_attack, dragon.bonus_defense, dragon.bonus_dodge, dragon.current_hitpoints, dragon.bonus_base_hitpoints, dragon.id))
    conn.commit()
    conn.close()


def remove_and_replace_quest(quest_id, category, displayed_quests):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    try:
        # Increment the tally of the quest
        cursor.execute(
            "UPDATE playerquests SET tally = tally + 1 WHERE ID = ?", (quest_id,))
        # Set the completion status of the quest
        cursor.execute(
            "UPDATE playerquests SET completed = 1, reset = date('now', '+1 day') WHERE ID = ?",
            (quest_id,
             ))

        # Get all quests for the category
        cursor.execute(
            "SELECT ID, Category, Description, ChallengeRating, Reward, completed, tally FROM playerquests WHERE Category = ?",
            (category,
             ))
        all_quests = cursor.fetchall()

        # Filter out displayed quests and the current quest
        displayed_quest_ids = set(q[0] for q in displayed_quests)
        displayed_quest_descriptions = set(q[2] for q in displayed_quests)
        available_quests = [
            quest for quest in all_quests
            if quest[0] not in displayed_quest_ids and quest[2] not in displayed_quest_descriptions and quest[0] != quest_id
        ]

        # Prioritize quests that are not completed
        not_completed_quests = [
            quest for quest in available_quests if not quest[5]]

        if not_completed_quests:
            new_quest = random.choice(not_completed_quests)
        else:
            if available_quests:
                new_quest = random.choice(available_quests)
            else:
                # Fallback to the original quest
                new_quest = next(
                    (q for q in all_quests if q[0] == quest_id), None)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        new_quest = None
    except Exception as e:
        print(f"Error: {e}")
        new_quest = None
    finally:
        conn.close()

    return new_quest


def handle_quest_click(category, mouse_x, mouse_y, displayed_quests):
    quests_updated = False  # Flag to track if quests were updated
    button_height = 50
    grid_cols = 3
    grid_rows = 4
    total_grid_height = (HEIGHT - 100) * 0.6
    total_grid_width = WIDTH
    grid_height = total_grid_height // grid_rows
    grid_width = total_grid_width // grid_cols
    start_y = (HEIGHT - 100) * 0.45

    # Only handle clicks within the quest button area
    if mouse_y < start_y or mouse_y > start_y + grid_rows * grid_height:
        return displayed_quests, quests_updated

    for i, quest in enumerate(displayed_quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = start_y + (i // grid_cols) * grid_height + \
            (grid_height - button_height) // 2
        rect = pygame.Rect(x, y, button_width, button_height)

        if rect.collidepoint(mouse_x, mouse_y):
            print(f"Quest '{quest[2]}' clicked!")

            update_inventory(f"{quest[3]} {CATEGORY_INFO[category]['fruit']}")
            additional_fruits = random.sample(
                list(CATEGORY_INFO.values()), k=quest[3] // 2)
            for fruit_info in additional_fruits:
                update_inventory(f"1 {fruit_info['fruit']}")
            player_tokens[category] += quest[3]

            # Complete the quest and remove it from the list
            complete_daily_quest(quest[0])
            new_quest = remove_and_replace_quest(
                quest[0], category, displayed_quests)
            if new_quest:
                displayed_quests[i] = new_quest
                quests_updated = True  # Set the flag to True when quests are updated
            else:
                print(f"Failed to replace quest {quest[0]}")
            break

    return displayed_quests, quests_updated


def initialize_player_dragons():
    player_dragons = [None] * 9  # Initialize with None
    return player_dragons


def load_player_dragon(dragon_id):
    return PlayerDragon(dragon_id)


def display_player_dragon_selection(player_dragons):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM hatcheddragons")
    rows = cursor.fetchall()
    conn.close()

    dragons = []
    for row in rows:
        dragon_instance = PlayerDragon(row[0])
        if dragon_instance.id not in [
                d.id for d in player_dragons if d is not None]:
            dragons.append(dragon_instance)

    running = True
    selected_dragon_id = None
    while running:
        screen.fill((30, 30, 30))
        draw_text(screen, "Select a Dragon", small_font,
                  WHITE, (WIDTH // 2 - 100, 20))

        for i, dragon in enumerate(dragons):
            display_name = dragon.petname if dragon.petname else dragon.dragon_name
            max_hp = dragon.maximum_hitpoints
            damage = dragon.stats['attack']
            defense = dragon.stats['defense']
            dodge = dragon.stats['dodge']

            text = f"{display_name}: HP: {
                dragon.current_hitpoints}/{max_hp} DMG: {damage} DEF: {defense} DODGE: {dodge}"
            y_pos = 100 + i * 30
            text_surf = small_font.render(text, True, WHITE)
            screen.blit(text_surf, (50, y_pos))

            rect = pygame.Rect(50, y_pos, 700, 30)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, RED, rect, 2)
                if pygame.mouse.get_pressed()[0]:
                    selected_dragon_id = dragon.id
                    running = False

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    return selected_dragon_id


def flip_dragon_image(image, facing_direction, target_direction):
    if facing_direction == target_direction:
        return image
    else:
        return pygame.transform.flip(image, True, False)


def draw_player_dragon_slots(player_dragons):
    grid_start_x = WIDTH * 0.65
    grid_start_y = 0
    grid_width = WIDTH * 0.35
    grid_height = HEIGHT * 0.35
    slot_width = grid_width / 3
    slot_height = grid_height / 3

    small_font = pygame.font.Font(None, 24)

    for i in range(9):
        slot_x = grid_start_x + (i % 3) * slot_width
        slot_y = grid_start_y + (i // 3) * slot_height
        rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)

        if player_dragons[i] is None:
            draw_beveled_button(
                screen,
                rect,
                LIGHT_GREY,
                "Add dragon",
                small_font)
        else:
            dragon = player_dragons[i]
            image_path = os.path.join(
                os.path.dirname(__file__), "dragons", dragon.filename)
            dragon_image = load_and_resize_image_keeping_aspect(
                image_path, (int(slot_width), int(slot_height)))
            dragon_image = flip_dragon_image(
                dragon_image, dragon.facing_direction, "left")
            screen.blit(dragon_image, (slot_x, slot_y))

            current_hp = dragon.current_hitpoints
            max_hp = 100 + \
                int((100 * (dragon.stats['health'] + dragon.bonus_health)) / 100)
            damage = 100 + \
                int((100 * (dragon.stats['attack'] + dragon.bonus_attack)) / 100)
            stats_text = f"hp {current_hp} dmg {damage}"

            box_width, box_height = small_font.size(stats_text)
            box_rect = pygame.Rect(
                slot_x + 5,
                slot_y + slot_height - 30,
                box_width + 10,
                box_height + 5)
            s = pygame.Surface((box_rect.width, box_rect.height))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            screen.blit(s, box_rect.topleft)

            draw_text(screen, stats_text, small_font, WHITE,
                      (slot_x + 10, slot_y + slot_height - 25))


def handle_player_dragon_slot_click(mouse_x, mouse_y, player_dragons):
    grid_start_x = WIDTH * 0.65
    grid_start_y = 0
    grid_width = WIDTH * 0.35
    grid_height = HEIGHT * 0.35
    slot_width = grid_width / 3
    slot_height = grid_height / 3

    for i in range(9):
        slot_x = grid_start_x + (i % 3) * slot_width
        slot_y = grid_start_y + (i // 3) * slot_height
        rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
        if rect.collidepoint(mouse_x, mouse_y):
            dragon_id = display_player_dragon_selection(player_dragons)
            if dragon_id:
                player_dragons[i] = load_player_dragon(
                    dragon_id)  # Initialize dragon with data
            break


def prompt_for_dragon_id():
    return random.randint(1, 100)


def handle_back_to_hub_click(mouse_x, mouse_y):
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 60, 150, 50)
    return back_button_rect.collidepoint(mouse_x, mouse_y)


def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None
    boss_dragon_filename = None
    player_dragons = initialize_player_dragons()
    displayed_quests = []
    global selected_dragon_for_upgrade
    boss_dragon_stats = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if current_screen == 'hub':
                    upgrade_dragon_rect = draw_hub_gameboard()
                    if not handle_fruit_click_in_inventory(
                            mouse_x, mouse_y, selected_dragon_for_upgrade):
                        selected_dragon_for_upgrade = handle_upgrade_dragon_click(
                            mouse_x, mouse_y, upgrade_dragon_rect, player_dragons)
                    for i, pos in enumerate(
                            [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        dragon_image_file = selected_dragons[i]
                        dragon_image_path = os.path.join(
                            os.path.dirname(__file__), "dragons", dragon_image_file)
                        dragon_image = load_and_resize_image_keeping_aspect(
                            dragon_image_path, (150, 150))
                        image_rect = dragon_image.get_rect(center=pos)
                        if image_rect.collidepoint(mouse_x, mouse_y):
                            selected_area = list(CATEGORY_INFO.keys())[i]
                            boss_dragon_filename = dragon_image_file
                            boss_dragon = BossDragon(
                                boss_dragon_filename, tier=1)  # Creating instance of BossDragon
                            boss_dragon_stats = (
                                boss_dragon.stats['health'],
                                boss_dragon.stats['attack'],
                                boss_dragon.stats['defense'],
                                boss_dragon.stats['dodge'])  # Set boss_dragon_stats variable
                            all_quests = load_quests(selected_area)
                            displayed_quests = random.sample(
                                all_quests, min(12, len(all_quests)))
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    if handle_back_to_hub_click(mouse_x, mouse_y):
                        current_screen = 'hub'
                    elif fight_button_rect and fight_button_rect.collidepoint(mouse_x, mouse_y):
                        if player_tokens[selected_area] >= 10:
                            player_tokens[selected_area] -= 10
                            # Ensure at least one player dragon is initialized
                            if any(
                                    dragon is not None for dragon in player_dragons):
                                start_combat(
                                    player_dragons,
                                    boss_dragon_stats,
                                    draw_area_gameboard,
                                    screen,
                                    selected_area,
                                    player_tokens,
                                    displayed_quests,
                                    boss_dragon_filename)  # Include boss_dragon_filename here
                            else:
                                print(
                                    "Error: At least one player dragon must be initialized.")
                    else:
                        displayed_quests, quests_updated = handle_quest_click(
                            selected_area, mouse_x, mouse_y, displayed_quests)
                        handle_player_dragon_slot_click(
                            mouse_x, mouse_y, player_dragons)
                        if quests_updated:
                            draw_area_gameboard(
                                selected_area, boss_dragon, player_dragons, displayed_quests)

            elif event.type == pygame.KEYDOWN and selected_dragon_for_upgrade:
                if event.key == pygame.K_1:
                    if spend_fruit_and_update_stats(
                            'gleamberry', selected_dragon_for_upgrade):
                        draw_hub_gameboard()
                        display_dragon_statistics(
                            selected_dragon_for_upgrade, upgrade_dragon_rect)
                elif event.key == pygame.K_2:
                    if spend_fruit_and_update_stats(
                            'flamefruit', selected_dragon_for_upgrade):
                        draw_hub_gameboard()
                        display_dragon_statistics(
                            selected_dragon_for_upgrade, upgrade_dragon_rect)
                elif event.key == pygame.K_3:
                    if spend_fruit_and_update_stats(
                            'shimmeringapple', selected_dragon_for_upgrade):
                        draw_hub_gameboard()
                        display_dragon_statistics(
                            selected_dragon_for_upgrade, upgrade_dragon_rect)
                elif event.key == pygame.K_4:
                    if spend_fruit_and_update_stats(
                            'etherealpear', selected_dragon_for_upgrade):
                        draw_hub_gameboard()
                        display_dragon_statistics(
                            selected_dragon_for_upgrade, upgrade_dragon_rect)
                elif event.key == pygame.K_5:
                    if spend_fruit_and_update_stats(
                            'moonbeammelon', selected_dragon_for_upgrade):
                        draw_hub_gameboard()
                        display_dragon_statistics(
                            selected_dragon_for_upgrade, upgrade_dragon_rect)

        if current_screen == 'hub':
            upgrade_dragon_rect = draw_hub_gameboard()
            if selected_dragon_for_upgrade:
                display_dragon_statistics(
                    selected_dragon_for_upgrade, upgrade_dragon_rect)
        elif current_screen == 'area' and selected_area is not None:
            fight_button_rect = draw_area_gameboard(
                selected_area, boss_dragon, player_dragons, displayed_quests)

        pygame.display.flip()

    pygame.quit()
    print("Game loop ended")


if __name__ == "__main__":
    initialize()
    load_inventory_data()
    game_loop()
    save_inventory_data()
