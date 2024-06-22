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

    # Calculate HP
    hp = base_hp + (base_hp * stats['health'] / 100)

    # Calculate Damage
    damage = base_damage + (base_damage * stats['attack'] / 100)

    return int(hp), int(damage), int(stats['defense']), int(stats['dodge'])

def draw_area_gameboard(category, boss_dragon_filename, boss_dragon_stats, player_dragons):
    screen.fill(GREY)
    screen.blit(background, (0, 0))
    draw_text(screen, f"Area Gameboard {category}", font, WHITE, (WIDTH // 2 - 150, 20))

    # Load and display boss dragon image
    max_height = int(HEIGHT * 0.35)
    boss_dragon_image = load_boss_dragon_image(boss_dragon_filename, max_height)
    screen.blit(boss_dragon_image, (0, 0))

    # Calculate and display boss stats
    boss_hp, boss_damage, boss_defense, boss_dodge = calculate_boss_stats(boss_dragon_stats)
    stats_text = f"HP: {boss_hp}  Damage: {boss_damage}  Defense: {boss_defense}  Dodge: {boss_dodge}"
    draw_text(screen, stats_text, small_font, WHITE, (10, max_height + 10))

    # Load and display quests
    quests = load_quests(category)
    button_height = 50  # Fixed height for consistency
    grid_cols = 3
    grid_rows = 4
    total_grid_height = (HEIGHT - 100) * 0.6  # Exclude bottom 100 pixels for the inventory box
    total_grid_width = WIDTH
    grid_height = total_grid_height // grid_rows
    grid_width = total_grid_width // grid_cols
    start_y = (HEIGHT - 100) * 0.4  # Start the grid at 40% of the adjusted height

    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = (i % grid_cols) * grid_width + (grid_width - button_width) // 2
        y = start_y + (i // grid_cols) * grid_height + (grid_height - button_height) // 2
        color = CATEGORY_INFO.get(quest[1], {}).get('color', BLUE)
        if quest[5]:  # If completed
            color = GREY
        rect = pygame.Rect(x, y, button_width, button_height)
        draw_beveled_button(screen, rect, color, quest[2], small_font)

    # Draw the inventory
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    # Draw back to hub button
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 150, 150, 50)
    draw_beveled_button(screen, back_button_rect, RED, "Back to Hub", small_font)

    draw_player_dragon_slots(player_dragons)

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

def handle_back_to_hub_click(mouse_x, mouse_y):
    back_button_rect = pygame.Rect(WIDTH - 160, HEIGHT - 150, 150, 50)
    return back_button_rect.collidepoint(mouse_x, mouse_y)

def handle_quest_click(category, mouse_x, mouse_y):
    quests = load_quests(category)
    total_challenge_rating = 0
    button_height = 50
    grid_cols = 3
    grid_rows = 4
    grid_width = WIDTH // grid_cols
    grid_height = (HEIGHT * 0.6) // grid_rows
    margin_x = (grid_width - button_height) // 2
    margin_y = (grid_height - button_height) // 2

    for i, quest in enumerate(quests):
        text_surface = small_font.render(quest[2], True, WHITE)
        button_width = text_surface.get_width() + 20
        x = margin_x + (i % grid_cols) * (grid_width + margin_x)
        y = HEIGHT * 0.4 + (i // grid_cols) * grid_height + margin_y
        rect = pygame.Rect(x, y, button_width, button_height)
        if rect.collidepoint(mouse_x, mouse_y):
            if not quest[5]:  # Only handle if not already completed
                complete_quest(quest[0])
                update_inventory(quest[4])
                total_challenge_rating += quest[3]
                if total_challenge_rating >= 10:
                    flag_dragon_aggressive(category)
            break

# Calculate dragon stats from traits and save to stats variable
def calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait=None):
    # Initialize stats
    stats = {
        "health": 0,
        "attack": 0,
        "defense": 0,
        "dodge": 0
    }

    # Add stats based on primary trait
    if primary_trait in primary_traits_with_stats:
        main_stat = primary_traits_with_stats[primary_trait]["main"]
        off_stat = primary_traits_with_stats[primary_trait]["off"]
        stats[main_stat] += 10
        stats[off_stat] += 5

    # Add stats based on secondary traits
    for trait in secondary_traits:
        for fruit, traits in fruit_traits_with_stats.items():
            if trait in traits:
                stat = traits[trait]
                stats[stat] += 5

    # Add stats based on nurture trait, if available
    if nurture_trait and nurture_trait in nurture_traits_with_stats:
        stat = nurture_traits_with_stats[nurture_trait]
        stats[stat] += 15

    return stats

# Apply the bonuses to boss and player dragons
def apply_bonuses(stats, is_boss=False, tier=1, dragon_id=None):
    if is_boss:
        # Apply tier bonuses for boss dragons
        tier_bonus = tier * 25
        for stat in stats:
            stats[stat] += tier_bonus

        # Apply trait bonuses for boss dragons (same as player dragons)
        # Note: Assuming that boss dragons have primary, secondary, and possibly nurture traits
        primary_trait = "Mystical"  # Example primary trait
        secondary_traits = ["Distraction", "Courageous", "Fearsome"]  # Example secondary traits
        nurture_trait = None  # Example nurture trait, if any

        trait_stats = calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait)
        for stat in stats:
            stats[stat] += trait_stats[stat]
    else:
        if dragon_id is not None:
            # Connect to the database and fetch bonuses for the player dragon
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

# Calculate damage based on attack, defense, and trait matching
def calculate_damage(attacker_attack, defender_defense, primary_trait_match=False, secondary_traits_match=0):
    # Base damage calculation
    base_damage = 100 + (100 * attacker_attack / 100)
    
    # Apply primary trait match (double damage)
    if primary_trait_match:
        base_damage *= 2
    
    # Apply random variation (-10% to +10%)
    variation = random.uniform(0.9, 1.1)
    base_damage = int(base_damage * variation)
    
    # Apply secondary traits damage reduction
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

# Dodge mechanics
def calculate_dodge_chance(defender_dodge, attacker_dodge):
    if defender_dodge == 0 and attacker_dodge == 0:
        return 0.5  # Default to 50% dodge chance if both stats are zero
    return 0.05 + 0.90 * (defender_dodge / (defender_dodge + attacker_dodge))

def dodge_attack(defender_dodge, attacker_dodge):
    dodge_chance = calculate_dodge_chance(defender_dodge, attacker_dodge)
    return random.random() < dodge_chance

# Count trait matches
def trait_match_count(player_traits, boss_traits):
    return len(set(player_traits).intersection(set(boss_traits)))

# Player dragon attacks boss dragon
def player_attack_boss(player_dragon, boss_dragon):
    primary_trait_match = player_dragon['primary_trait'] == boss_dragon['primary_trait']
    secondary_traits_match = trait_match_count(player_dragon['secondary_traits'], boss_dragon['secondary_traits'])
    
    return calculate_damage(player_dragon['attack'], boss_dragon['defense'], primary_trait_match, secondary_traits_match)

# Boss dragon attacks player dragon
def boss_attack_player(boss_dragon, player_dragon):
    # Check if the attack is dodged
    if not dodge_attack(player_dragon['dodge'], boss_dragon['dodge']):
        # Calculate the number of matching secondary traits
        matching_traits = trait_match_count(boss_dragon['secondary_traits'], player_dragon['secondary_traits'])
        
        # Calculate the base damage
        base_damage = 100 + (100 * boss_dragon['attack'] / 100)
        
        # Apply defense and trait reductions
        effective_damage = calculate_damage_reduction(base_damage, player_dragon['defense'], matching_traits)
        
        return effective_damage
    else:
        return 0  # Attack dodged

# Calculate damage reduction with continuous scaling (max 25% reduction at defense stat 100)
def calculate_damage_reduction(incoming_damage, defender_defense, matching_traits):
    # Calculate defense reduction with continuous scaling (max 25% reduction at defense stat 100)
    defense_reduction = defender_defense / 400
    
    # Calculate trait matching reduction
    if matching_traits == 1:
        trait_reduction = 0.15
    elif matching_traits == 2:
        trait_reduction = 0.30
    elif matching_traits == 3:
        trait_reduction = 0.50
    else:
        trait_reduction = 0.0
    
    # Total reduction
    total_reduction = defense_reduction + trait_reduction
    
    # Cap the total reduction to ensure at least 25% damage is applied
    effective_reduction = min(0.75, total_reduction)
    
    # Calculate the effective damage
    effective_damage = incoming_damage * (1 - effective_reduction)
    
    # Ensure at least 25% of the damage is applied
    effective_damage = max(incoming_damage * 0.25, effective_damage)
    
    return effective_damage

def initialize_player_dragons():
    player_dragons = [None] * 9  # Initialize 9 slots for player dragons
    return player_dragons

def load_player_dragon(dragon_id):
    conn = connect_db('save.db')
    cursor = conn.cursor()
    cursor.execute("SELECT primary_trait, secondary1, secondary2, secondary3, nurture, filename, special_abilities FROM hatcheddragons WHERE id=?", (dragon_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        primary_trait, secondary1, secondary2, secondary3, nurture_trait, image_filename, special_abilities = row
        secondary_traits = [secondary1, secondary2, secondary3]
        stats = calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait)
        stats = apply_bonuses(stats, is_boss=False, dragon_id=dragon_id)
        return {
            'primary_trait': primary_trait,
            'secondary_traits': secondary_traits,
            'nurture_trait': nurture_trait,
            'image_filename': image_filename,
            'stats': stats,
            'special_attack': special_abilities  # Store the special abilities text
        }
    return None


def draw_player_dragon_slots(player_dragons):
    # Grid dimensions and positions
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
        
        if player_dragons[i] is None:
            draw_beveled_button(screen, rect, LIGHT_GREY, "Click to add dragon", small_font)
        else:
            dragon = player_dragons[i]
            image_path = os.path.join(os.path.dirname(__file__), "dragons", dragon['image_filename'])
            dragon_image = load_and_resize_image_keeping_aspect(image_path, (int(slot_width), int(slot_height)))
            screen.blit(dragon_image, (slot_x, slot_y))

            stats_text = f"H: {dragon['stats']['health']}  A: {dragon['stats']['attack']}  D: {dragon['stats']['defense']}  d: {dragon['stats']['dodge']}"
            draw_text(screen, stats_text, small_font, WHITE, (slot_x, slot_y + slot_height - 30))

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
            dragon_id = prompt_for_dragon_id()  # Placeholder for getting the dragon ID (e.g., from user input)
            player_dragons[i] = load_player_dragon(dragon_id)
            break

def prompt_for_dragon_id():
    # Placeholder function to simulate getting a dragon ID from the user
    return random.randint(1, 100)  # Random ID for demonstration purposes

# Main game loop update with combat integration
def game_loop():
    running = True
    current_screen = 'hub'
    selected_area = None
    boss_dragon_filename = None  # Store the selected boss dragon filename
    boss_dragon_stats = None  # Store the selected boss dragon stats
    player_dragons = initialize_player_dragons()

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
                            boss_dragon_filename = dragon_image_file  # Store the selected boss dragon filename
                            primary_trait = "Mystical"  # Example primary trait for boss dragon
                            secondary_traits = ["Distraction", "Courageous", "Fearsome"]  # Example secondary traits for boss dragon
                            nurture_trait = None  # Example nurture trait for boss dragon, if any
                            boss_dragon_stats = calculate_dragon_stats(primary_trait, secondary_traits, nurture_trait)
                            boss_dragon_stats = apply_bonuses(boss_dragon_stats, is_boss=True, tier=1)  # Apply both trait and tier bonuses
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    if handle_back_to_hub_click(mouse_x, mouse_y):
                        current_screen = 'hub'
                    else:
                        handle_quest_click(selected_area, mouse_x, mouse_y)
                        # Check if the player has enough tokens to initiate a boss fight
                        if player_tokens[selected_area] >= 10:
                            player_tokens[selected_area] -= 10
                            combat(player_dragons, boss_dragon_stats)
                handle_player_dragon_slot_click(mouse_x, mouse_y, player_dragons)

        if current_screen == 'hub':
            draw_hub_gameboard()
        elif current_screen == 'area' and selected_area is not None:
            draw_area_gameboard(selected_area, boss_dragon_filename, boss_dragon_stats, player_dragons)  # Pass the boss dragon filename, stats, and player dragons

        pygame.display.flip()

    pygame.quit()
    logging.info("Game loop ended")
    print("Game loop ended")

if __name__ == "__main__":
    initialize()
    load_inventory_data()
    game_loop()
    save_inventory_data()
