import pygame
import sqlite3
import logging
import os
import random
from game import *

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
token_font = pygame.font.Font(None, 90)  # Much larger font for player token count
small_font = pygame.font.Font(None, 36)  # Smaller font for button text

def connect_db(db_name='save.db'):
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    return conn

def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    
    try:
        with connect_db('save.db') as conn:
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
    conn = connect_db('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Category, Description, ChallengeRating, Reward, completed, tally FROM playerquests WHERE Category = ? AND (reset IS NULL OR reset <= date('now'))", (category,))
    quests = cursor.fetchall()
    conn.close()
    return quests

def complete_daily_quest(quest_id):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    logging.info(f"Completing daily quest ID {quest_id}")
    cursor.execute("UPDATE playerquests SET completed = 1, reset = date('now', '+1 day') WHERE ID = ?", (quest_id,))
    conn.commit()
    conn.close()

def update_inventory(reward_str):
    rewards = reward_str.split()
    fruit, amount = rewards[1], int(rewards[0])
    print(f"Updating inventory: Adding {amount} of {fruit}")

    # Ensure the fruit exists in the inventory before updating
    if fruit in inventory:
        inventory[fruit] += amount
        print(f"New inventory count for {fruit}: {inventory[fruit]}")
    else:
        inventory[fruit] = amount
        print(f"Added new fruit {fruit} with count: {amount}")

    # Save the updated inventory to the database
    save_inventory_data()

def flag_dragon_aggressive(category):
    print(f"Category {category} is now aggressive!")

def draw_beveled_button(surface, rect, color, text, font):
    pygame.draw.rect(surface, color, rect, border_radius=10)  # Draw the button with beveled edges
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)  # Outline with white color
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def load_boss_dragon_image(dragon_filename, max_height):
    dragon_image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon_filename)
    try:
        image = pygame.image.load(dragon_image_path).convert_alpha()
        width, height = image.get_size()
        aspect_ratio = width / height

        new_height = max_height
        new_width = new_height * aspect_ratio

        new_size = (int(new_width), int(new_height))
        logging.info(f"Loaded and resized boss dragon image {dragon_image_path} to {new_size}")
        return pygame.transform.scale(image, new_size)
    except pygame.error as e:
        logging.error(f"Error loading boss dragon image {dragon_image_path}: {e}")
        print(f"Error loading boss dragon image {dragon_image_path}: {e}")
        return pygame.Surface((max_height * aspect_ratio, max_height))  # Return a blank surface as a placeholder

def calculate_boss_stats(stats):
    base_hp = 1000
    base_damage = 100

    hp = base_hp + (base_hp * stats['health'] / 100)
    damage = base_damage + (base_damage * stats['attack'] / 100)

    return int(hp), int(damage), int(stats['defense']), int(stats['dodge'])

def draw_beveled_button_gradient(surface, rect, text, font, gradient_colors):
    outline_rect = rect.inflate(4, 4)
    pygame.draw.rect(surface, gradient_colors[0], outline_rect, border_radius=10)  # Start of gradient
    pygame.draw.rect(surface, gradient_colors[1], outline_rect, 2, border_radius=10)  # End of gradient

    pygame.draw.rect(surface, RED, rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)  # White outline for the button
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_area_gameboard(category, boss_dragon_filename, boss_dragon_stats, player_dragons, quests):
    screen.fill(GREY)
    screen.blit(background, (0, 0))

    draw_text(screen, category.capitalize(), category_font, WHITE, (WIDTH // 2 - 20, 10))
    token_text = str(player_tokens[category])
    draw_text(screen, token_text, token_font, WHITE, (WIDTH // 2 + 50, 75))

    box_width, box_height = category_font.size(category.capitalize())
    s = pygame.Surface((box_width + 10, box_height + 10))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (WIDTH // 2 - 25, 5))

    box_width, box_height = token_font.size(token_text)
    s = pygame.Surface((box_width + 20, box_height + 10))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (WIDTH // 2 + 40, 65))

    max_height = int(HEIGHT * 0.35)
    boss_dragon_image = load_boss_dragon_image(boss_dragon_filename, max_height)

    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    cursor.execute("SELECT facing_direction FROM dragons WHERE filename=?", (boss_dragon_filename,))
    facing_direction = cursor.fetchone()
    conn.close()

    if facing_direction and facing_direction[0] != "right":
        boss_dragon_image = flip_dragon_image(boss_dragon_image, facing_direction[0], "right")

    screen.blit(boss_dragon_image, (0, 0))

    boss_hp, boss_damage, boss_defense, boss_dodge = calculate_boss_stats(boss_dragon_stats)
    stats_text = f"HP: {boss_hp}  Damage: {boss_damage}  Defense: {boss_defense}  Dodge: {boss_dodge}"
    
    stats_box_width, stats_box_height = small_font.size(stats_text)
    stats_box_surface = pygame.Surface((stats_box_width + 20, stats_box_height + 10))
    stats_box_surface.set_alpha(128)
    stats_box_surface.fill((0, 0, 0))
    screen.blit(stats_box_surface, (10, max_height + 10))

    draw_text(screen, stats_text, small_font, WHITE, (20, max_height + 15))

    box_top_left = (WIDTH // 2 - 45, 140)
    box_bottom_right = (WIDTH - 420, 265)
    draw_center_fruits(screen, box_top_left, box_bottom_right, fruit_images_dict)

    button_height = 50
    grid_cols = 3
    grid_rows = 4
    total_grid_height = (HEIGHT - 100) * 0.6
    total_grid_width = WIDTH
    grid_height = total_grid_height // grid_rows
    grid_width = total_grid_width // grid_cols
    start_y = (HEIGHT - 100) * 0.4

    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = start_y + (i // grid_cols) * grid_height + (grid_height - button_height) // 2
        color = CATEGORY_INFO.get(quest[1], {}).get('color', BLUE)
        if quest[5]:
            color = GREY
        rect = pygame.Rect(x, y, button_width, button_height)
        draw_beveled_button(screen, rect, color, quest[2], small_font)

    draw_inventory(screen, inventory, egg_counts, inventory_slots)
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 150, 150, 50)
    draw_beveled_button(screen, back_button_rect, RED, "Back to Hub", small_font)

    fight_button_rect = pygame.Rect(WIDTH // 2 - 10, 265, 150, 50)
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
    screen.fill(GREY)
    screen.blit(background, (0, 0))
    draw_text(screen, "Hub Gameboard", category_font, WHITE, (WIDTH // 2 - 100, 20))

    initialize_dragons()

    dragon_positions = [(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]

    for i, pos in enumerate(dragon_positions):
        dragon_image_file = selected_dragons[i]
        dragon_image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon_image_file)
        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))
        image_rect = dragon_image.get_rect(center=pos)
        screen.blit(dragon_image, image_rect.topleft)
        draw_text(screen, f"Dragon {i+1}", small_font, WHITE, (pos[0] - 30, pos[1] + 60))

    draw_inventory(screen, inventory, egg_counts, inventory_slots)
    pygame.display.flip()

def handle_back_to_hub_click(mouse_x, mouse_y):
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 150, 150, 50)
    return back_button_rect.collidepoint(mouse_x, mouse_y)

def remove_and_replace_quest(quest_id, category, displayed_quests):
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE playerquests SET tally = tally + 1 WHERE ID = ?", (quest_id,))
        cursor.execute("UPDATE playerquests SET completed = 0, reset = NULL WHERE ID = ?", (quest_id,))
        
        displayed_quest_ids = set(q[0] for q in displayed_quests)
        displayed_quest_descriptions = set(q[2] for q in displayed_quests)
        
        cursor.execute("SELECT ID, Category, Description, ChallengeRating, Reward, completed, tally FROM playerquests WHERE Category = ?", (category,))
        all_cleaning_quests = cursor.fetchall()
        
        available_quests = [
            quest for quest in all_cleaning_quests 
            if quest[0] not in displayed_quest_ids and quest[2] not in displayed_quest_descriptions and quest[0] != quest_id
        ]
        
        if not available_quests:
            # Fallback to the original quest
            new_quest = next((q for q in all_cleaning_quests if q[0] == quest_id), None)
        else:
            new_quest = random.choice(available_quests)
        
        conn.commit()
    except sqlite3.Error as e:
        new_quest = None
    except Exception as e:
        new_quest = None
    finally:
        conn.close()
    
    return new_quest


def handle_quest_click(category, mouse_x, mouse_y, displayed_quests):
    print(f"Handling quest click for category {category} at position ({mouse_x}, {mouse_y})")
    quests_updated = False  # Flag to track if quests were updated
    
    button_height = 50
    grid_cols = 3
    grid_rows = 4
    total_grid_height = (HEIGHT - 100) * 0.6
    total_grid_width = WIDTH
    grid_height = total_grid_height // grid_rows
    grid_width = total_grid_width // grid_cols
    start_y = (HEIGHT - 100) * 0.4

    # Only handle clicks within the quest button area
    if mouse_y < start_y or mouse_y > start_y + grid_rows * grid_height:
        return displayed_quests, quests_updated

    for i, quest in enumerate(displayed_quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = start_y + (i // grid_cols) * grid_height + (grid_height - button_height) // 2
        rect = pygame.Rect(x, y, button_width, button_height)

        if rect.collidepoint(mouse_x, mouse_y):
            print(f"Quest '{quest[2]}' clicked!")
            update_inventory(f"{quest[3]} {CATEGORY_INFO[category]['fruit']}")
            additional_fruits = random.sample(list(CATEGORY_INFO.values()), k=quest[3] // 2)
            for fruit_info in additional_fruits:
                update_inventory(f"1 {fruit_info['fruit']}")
            player_tokens[category] += quest[3]
            if category == 'daily':
                complete_daily_quest(quest[0])
            else:
                new_quest = remove_and_replace_quest(quest[0], category, displayed_quests)
                if new_quest:
                    displayed_quests[i] = new_quest
                    quests_updated = True  # Set the flag to True when quests are updated
                    print(f"Replaced quest {quest[0]} with new quest {new_quest[0]}")
                else:
                    print(f"Failed to replace quest {quest[0]}")
            break
    return displayed_quests, quests_updated

def calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait=None):
    stats = {
        "health": 0,
        "attack": 0,
        "defense": 0,
        "dodge": 0
    }

    if primary_trait in primary_traits_with_stats:
        main_stat = primary_traits_with_stats[primary_trait]["main"]
        off_stat = primary_traits_with_stats[primary_trait]["off"]
        stats[main_stat] += 10
        stats[off_stat] += 5

    for trait in secondary_traits:
        for fruit, traits in fruit_traits_with_stats.items():
            if trait in traits:
                stat = traits[trait]
                stats[stat] += 5

    if nurture_trait and nurture_trait in nurture_traits_with_stats:
        stat = nurture_traits_with_stats[nurture_trait]
        stats[stat] += 15

    return stats

def apply_bonuses(stats, is_boss=False, tier=1, dragon_id=None):
    if is_boss:
        tier_bonus = tier * 25
        for stat in stats:
            stats[stat] += tier_bonus

        primary_trait = "Mystical"
        secondary_traits = ["Distraction", "Courageous", "Fearsome"]
        nurture_trait = None

        trait_stats = calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait)
        for stat in stats:
            stats[stat] += trait_stats[stat]
    else:
        if dragon_id is not None:
            conn = sqlite3.connect('save.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT bonus_health, bonus_attack, bonus_defense, bonus_dodge FROM hatcheddragons WHERE id=?", (dragon_id,))
            row = cursor.fetchone()
            
            if row:
                stats["health"] += row[0]
                stats["attack"] += row[1]
                stats["defense"] += row[2]
                stats["dodge"] += row[3]
            
            conn.close()

    return stats

def calculate_damage(attacker_attack, defender_defense, primary_trait_match=False, secondary_traits_match=0):
    base_damage = 100 + (100 * attacker_attack / 100)
    
    if primary_trait_match:
        base_damage *= 2
    
    variation = random.uniform(0.9, 1.1)
    base_damage = int(base_damage * variation)
    
    if secondary_traits_match == 1:
        damage_reduction = 0.15
    elif secondary_traits_match == 2:
        damage_reduction = 0.30
    elif secondary_traits_match == 3:
        damage_reduction = 0.50
    else:
        damage_reduction = 0.0
    
    final_damage = int(base_damage * (1 - damage_reduction))
    
    return final_damage

def calculate_dodge_chance(defender_dodge, attacker_dodge):
    if defender_dodge == 0 and attacker_dodge == 0:
        return 0.5
    return 0.05 + 0.90 * (defender_dodge / (defender_dodge + attacker_dodge))

def dodge_attack(defender_dodge, attacker_dodge):
    dodge_chance = calculate_dodge_chance(defender_dodge, attacker_dodge)
    return random.random() < dodge_chance

def trait_match_count(player_traits, boss_traits):
    return len(set(player_traits).intersection(set(boss_traits)))

def player_attack_boss(player_dragon, boss_dragon):
    primary_trait_match = player_dragon['primary_trait'] == boss_dragon['primary_trait']
    secondary_traits_match = trait_match_count(player_dragon['secondary_traits'], boss_dragon['secondary_traits'])
    
    return calculate_damage(player_dragon['attack'], boss_dragon['defense'], primary_trait_match, secondary_traits_match)

def boss_attack_player(boss_dragon, player_dragon):
    if not dodge_attack(player_dragon['dodge'], boss_dragon['dodge']):
        matching_traits = trait_match_count(boss_dragon['secondary_traits'], player_dragon['secondary_traits'])
        base_damage = 100 + (100 * boss_dragon['attack'] / 100)
        effective_damage = calculate_damage_reduction(base_damage, player_dragon['defense'], matching_traits)
        return effective_damage
    else:
        return 0

def calculate_damage_reduction(incoming_damage, defender_defense, matching_traits):
    defense_reduction = defender_defense / 400
    
    if matching_traits == 1:
        trait_reduction = 0.15
    elif matching_traits == 2:
        trait_reduction = 0.30
    elif matching_traits == 3:
        trait_reduction = 0.50
    else:
        trait_reduction = 0.0
    
    total_reduction = defense_reduction + trait_reduction
    effective_reduction = min(0.75, total_reduction)
    effective_damage = incoming_damage * (1 - effective_reduction)
    effective_damage = max(incoming_damage * 0.25, effective_damage)
    
    return effective_damage

def initialize_player_dragons():
    player_dragons = [None] * 9
    return player_dragons

def load_player_dragon(dragon_id):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, dragon_name, petname, primary_trait, secondary1, secondary2, secondary3, nurture, filename, special_abilities, facing_direction, bonus_health, bonus_attack, bonus_defense, bonus_dodge FROM hatcheddragons WHERE id=?", (dragon_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        dragon = {
            'id': row[0],
            'dragon_name': row[1],
            'petname': row[2],
            'primary_trait': row[3],
            'secondary1': row[4],
            'secondary2': row[5],
            'secondary3': row[6],
            'nurture': row[7],
            'filename': row[8],
            'special_abilities': row[9],
            'facing_direction': row[10],
            'bonus_health': row[11],
            'bonus_attack': row[12],
            'bonus_defense': row[13],
            'bonus_dodge': row[14]
        }
        secondary_traits = [dragon['secondary1'], dragon['secondary2'], dragon['secondary3']]
        stats = calculate_dragon_stats(dragon['primary_trait'], secondary_traits, dragon['nurture'])
        stats = apply_bonuses(stats, is_boss=False, dragon_id=dragon_id)
        dragon['stats'] = stats
        return dragon
    return None

def display_player_dragon_selection(player_dragons):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, dragon_name, petname, primary_trait, secondary1, secondary2, secondary3, nurture, filename, special_abilities, facing_direction, bonus_health, bonus_attack, bonus_defense, bonus_dodge FROM hatcheddragons")
    rows = cursor.fetchall()
    conn.close()
    
    dragons = []
    for row in rows:
        dragon = {
            'id': row[0],
            'dragon_name': row[1],
            'petname': row[2],
            'primary_trait': row[3],
            'secondary1': row[4],
            'secondary2': row[5],
            'secondary3': row[6],
            'nurture': row[7],
            'filename': row[8],
            'special_abilities': row[9],
            'facing_direction': row[10],
            'bonus_health': row[11],
            'bonus_attack': row[12],
            'bonus_defense': row[13],
            'bonus_dodge': row[14]
        }
        secondary_traits = [dragon['secondary1'], dragon['secondary2'], dragon['secondary3']]
        stats = calculate_dragon_stats(dragon['primary_trait'], secondary_traits, dragon['nurture'])
        stats = apply_bonuses(stats, is_boss=False, dragon_id=dragon['id'])
        dragon['stats'] = stats
        
        if dragon['id'] not in [d['id'] for d in player_dragons if d is not None]:
            dragons.append(dragon)

    running = True
    selected_dragon_id = None
    while running:
        screen.fill((30, 30, 30))
        draw_text(screen, "Select a Dragon", small_font, WHITE, (WIDTH // 2 - 100, 20))

        for i, dragon in enumerate(dragons):
            display_name = dragon['petname'] if dragon['petname'] else dragon['dragon_name']
            max_hp = 100 + int((100 * (dragon['stats']['health'] + dragon['bonus_health'])) / 100)
            damage = 100 + int((100 * (dragon['stats']['attack'] + dragon['bonus_attack'])) / 100)
            defense = dragon['stats']['defense'] + dragon['bonus_defense']
            dodge = dragon['stats']['dodge'] + dragon['bonus_dodge']

            text = f"{display_name}: HP: {max_hp} DMG: {damage} DEF: {defense} DODGE: {dodge}"
            y_pos = 100 + i * 30
            text_surf = small_font.render(text, True, WHITE)
            screen.blit(text_surf, (50, y_pos))

            rect = pygame.Rect(50, y_pos, 700, 30)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, RED, rect, 2)
                if pygame.mouse.get_pressed()[0]:
                    selected_dragon_id = dragon['id']
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
            draw_beveled_button(screen, rect, LIGHT_GREY, "Add dragon", small_font)
        else:
            dragon = player_dragons[i]
            image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon['filename'])
            dragon_image = load_and_resize_image_keeping_aspect(image_path, (int(slot_width), int(slot_height)))
            dragon_image = flip_dragon_image(dragon_image, dragon['facing_direction'], "left")
            screen.blit(dragon_image, (slot_x, slot_y))

            max_hp = 100 + int((100 * (dragon['stats']['health'] + dragon['bonus_health'])) / 100)
            damage = 100 + int((100 * (dragon['stats']['attack'] + dragon['bonus_attack'])) / 100)
            stats_text = f"hp {max_hp} dmg {damage}"
            
            box_width, box_height = small_font.size(stats_text)
            box_rect = pygame.Rect(slot_x + 5, slot_y + slot_height - 30, box_width + 10, box_height + 5)
            s = pygame.Surface((box_rect.width, box_rect.height))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            screen.blit(s, box_rect.topleft)

            draw_text(screen, stats_text, small_font, WHITE, (slot_x + 10, slot_y + slot_height - 25))

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
                player_dragons[i] = load_player_dragon(dragon_id)
            break

def prompt_for_dragon_id():
    return random.randint(1, 100)

def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None
    boss_dragon_filename = None
    boss_dragon_stats = None
    player_dragons = initialize_player_dragons()
    displayed_quests = []  # Initialize an empty list for displayed quests
    
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
                        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))
                        image_rect = dragon_image.get_rect(center=pos)
                        if image_rect.collidepoint(mouse_x, mouse_y):
                            selected_area = list(CATEGORY_INFO.keys())[i]
                            boss_dragon_filename = dragon_image_file
                            primary_trait = "Mystical"
                            secondary_traits = ["Distraction", "Courageous", "Fearsome"]
                            nurture_trait = None
                            boss_dragon_stats = calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait)
                            boss_dragon_stats = apply_bonuses(boss_dragon_stats, is_boss=True, tier=1)
                            all_quests = load_quests(selected_area)
                            displayed_quests = random.sample(all_quests, min(12, len(all_quests)))  # Randomly select 12 quests or fewer if there are less than 12
                            print(f"Switched to area screen: {selected_area}, Loaded quests: {displayed_quests}")
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    if handle_back_to_hub_click(mouse_x, mouse_y):
                        current_screen = 'hub'
                        print("Switched to hub screen")
                    elif fight_button_rect and fight_button_rect.collidepoint(mouse_x, mouse_y):
                        if player_tokens[selected_area] >= 10:
                            player_tokens[selected_area] -= 10
                            combat(player_dragons, boss_dragon_stats)
                    else:
                        displayed_quests, quests_updated = handle_quest_click(selected_area, mouse_x, mouse_y, displayed_quests)
                        handle_player_dragon_slot_click(mouse_x, mouse_y, player_dragons)
                        if quests_updated:
                            print(f"Updated quests: {displayed_quests}")
                            draw_area_gameboard(selected_area, boss_dragon_filename, boss_dragon_stats, player_dragons, displayed_quests)  # Redraw gameboard with updated quests

        if current_screen == 'hub':
            draw_hub_gameboard()
        elif current_screen == 'area' and selected_area is not None:
            fight_button_rect = draw_area_gameboard(selected_area, boss_dragon_filename, boss_dragon_stats, player_dragons, displayed_quests)

        pygame.display.flip()

    pygame.quit()
    print("Game loop ended")

if __name__ == "__main__":
    initialize()
    load_inventory_data()
    game_loop()
    save_inventory_data()
