import random
import os
import time

import pygame
from firebase_config import db

# Primary traits with their associated main and off stats
primary_traits_with_stats = {
    "Curious": {"main": "dodge", "off": "health"},
    "Playful": {"main": "dodge", "off": "attack"},
    "Adventurous": {"main": "health", "off": "attack"},
    "Resourceful": {"main": "attack", "off": "defense"},
    "Sociable": {"main": "defense", "off": "health"},
    "Thoughtful": {"main": "defense", "off": "dodge"},
    "Confident": {"main": "attack", "off": "attack"},  # New combination
    "Generous": {"main": "health", "off": "defense"},
    "Reflective": {"main": "dodge", "off": "defense"},
    "Strategic": {"main": "defense", "off": "attack"},
    "Cheerful": {"main": "health", "off": "dodge"},
    "Demonic": {"main": "attack", "off": "dodge"},
    "Mystical": {"main": "health", "off": "health"},   # New combination
    "Flamboyant": {"main": "dodge", "off": "attack"},
    "Awkward": {"main": "defense", "off": "defense"},  # New combination
    "Weird": {"main": "attack", "off": "dodge"},
    "Gross": {"main": "defense", "off": "attack"},
    "Gorgeous": {"main": "attack", "off": "defense"},
    "Ethereal": {"main": "health", "off": "dodge"},
    "Blessed": {"main": "dodge", "off": "dodge"}       # New combination
}

# Nurture traits with their associated stats
nurture_traits_with_stats = {
    "bestial": "attack",
    "independent": "dodge",
    "musical": "health",
    "hot-tempered": "defense"
}

# Personality keywords for each fruit with associated stats
fruit_traits_with_stats = {
    "gleamberry": {
        "Dark": "health",
        "Brooding": "attack",
        "Responsible": "defense",
        "Common": "dodge"
    },
    "flamefruit": {
        "Distraction": "health",
        "Fierce": "attack",
        "Fiery": "defense",
        "Showy": "dodge"
    },
    "shimmeringapple": {
        "Speed": "dodge",
        "Flightiness": "attack",
        "Drive": "defense",
        "Ambition": "health"
    },
    "etherealpear": {
        "Earthy": "health",
        "Pragmatic": "attack",
        "Stout": "defense",
        "Loyal": "dodge"
    },
    "moonbeammelon": {
        "Angelic": "health",
        "Unique": "attack",
        "Pure": "defense",
        "Self-righteous": "dodge"
    }
}
 
from firebase_admin import firestore

class BossDragon:
    def __init__(self, filename, tier=1):
        self.filename = filename
        self.id = None
        self.name = None
        self.primary_trait = None
        self.secondary_trait1 = None
        self.secondary_trait2 = None
        self.secondary_trait3 = None
        self.nurture_trait = None
        self.special_abilities = None
        self.stats = {
            'health': 0,
            'attack': 0,
            'defense': 0,
            'dodge': 0
        }
        self.current_hitpoints = 0
        self.maximum_hitpoints = 0
        self.damage = 0
        self.facing_direction = "right"  # Default value
        self.tier = tier
        self.initialized = False
        if self.filename:
            self.fetch_data()
            self.calculate_and_apply_stats()
            self.calculate_hitpoints_and_damage()
            self.initialized = True

    def fetch_data(self):
        try:
            #print(f"Fetching data for dragon with filename: {self.filename}")
            dragons_ref = db.collection('dragons')
            query = dragons_ref.where('filename', '==', self.filename)
            docs = query.stream()

            for doc in docs:
                data = doc.to_dict()
                self.id = doc.id  # Use Firestore document ID
                self.name = data.get('name')
                self.primary_trait = data.get('primary_characteristic')
                self.secondary_trait1 = data.get('secondary_trait1')
                self.secondary_trait2 = data.get('secondary_trait2')
                self.secondary_trait3 = data.get('secondary_trait3')
                self.nurture_trait = data.get('Nurture')
                self.special_abilities = data.get('special_abilities')
                self.current_hitpoints = data.get('current_hitpoints')
                self.facing_direction = data.get('facing_direction')
                return  # Exit after finding the first matching document

            raise ValueError("Boss dragon not found in the database")
        
        except Exception as e:
            raise ValueError(f"Error fetching boss dragon data: {e}")

    def calculate_and_apply_stats(self):
        # Initialize stats
        stats = {'health': 0, 'attack': 0, 'defense': 0, 'dodge': 0}

        # Add primary trait bonuses
        primary_bonus = primary_traits_with_stats.get(self.primary_trait)
        if primary_bonus:
            stats[primary_bonus['main']] += 10
            stats[primary_bonus['off']] += 5

        # Add secondary trait bonuses separately
        secondary_traits = [self.secondary_trait1, self.secondary_trait2, self.secondary_trait3]
        for trait in secondary_traits:
            if trait:  # Ensure the trait is not None or empty
                for fruit, traits in fruit_traits_with_stats.items():
                    if trait in traits:
                        stat = traits[trait]
                        stats[stat] += 5

        # Apply tier bonus
        tier_bonus = self.tier * 25
        for stat in stats:
            stats[stat] += tier_bonus

        # Update the stats
        self.stats = stats

    def calculate_hitpoints_and_damage(self):
        self.maximum_hitpoints = 1000 + (self.stats['health'] / 100 * 1000)
        self.damage = 100 + (self.stats['attack'] / 100 * 100)
        
        # Set current hitpoints to maximum hitpoints only if not already initialized
        if not self.initialized:
            self.current_hitpoints = self.maximum_hitpoints

    def save_current_hitpoints(self):
        try:
            print(f"Saving current hitpoints for dragon ID: {self.id}")
            doc_ref = db.collection('dragons').document(self.id)
            doc_ref.update({
                'current_hitpoints': self.current_hitpoints
            })
            print(f"Successfully saved current hitpoints: {self.current_hitpoints} for dragon ID: {self.id}")
        except Exception as e:
            print(f"Error saving current hitpoints: {e}")
            raise ValueError(f"Error saving current hitpoints: {e}")


class PlayerDragon:
    def __init__(self, id):
        if id is None:
            raise ValueError("The provided ID is None. Cannot fetch data for a None ID.")
        
        self.id = str(id).zfill(4)  # Ensure the id is treated as a string with leading zeros
        self.dragon_id = None  # This will be fetched from the document data
        self.dragon_name = None
        self.primary_trait = None
        self.secondary1 = None
        self.secondary2 = None
        self.secondary3 = None
        self.nurture_trait = None
        self.special_abilities = None
        self.petname = None
        self.filename = None
        self.facing_direction = None
        self.stats = {
            'health': 0,
            'attack': 0,
            'defense': 0,
            'dodge': 0
        }
        self.current_hitpoints = 0
        self.maximum_hitpoints = 0
        self.damage = 0
        self.bonus_health = 0
        self.bonus_attack = 0
        self.bonus_defense = 0
        self.bonus_dodge = 0
        self.bonus_base_hitpoints = 0
        self.fetch_data()
        self.calculate_and_apply_stats()
        self.calculate_hitpoints_and_damage()

    def fetch_data(self):
        try:
            #print(f"Fetching data for document ID: {self.id}")
            doc_ref = db.collection('hatcheddragons').document(self.id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                self.dragon_id = data.get('dragon_id')  # Fetch the dragon_id from the document data
                self.dragon_name = data.get('dragon_name')
                self.primary_trait = data.get('primary_trait')
                self.secondary1 = data.get('secondary1')
                self.secondary2 = data.get('secondary2')
                self.secondary3 = data.get('secondary3')
                self.nurture_trait = data.get('nurture')
                self.special_abilities = data.get('special_abilities')
                self.petname = data.get('petname')
                self.filename = data.get('filename')
                self.facing_direction = data.get('facing_direction')
                self.current_hitpoints = data.get('current_hitpoints')
                self.bonus_health = data.get('bonus_health', 0)  # Default to 0 if None
                self.bonus_attack = data.get('bonus_attack', 0)  # Default to 0 if None
                self.bonus_defense = data.get('bonus_defense', 0)  # Default to 0 if None
                self.bonus_dodge = data.get('bonus_dodge', 0)  # Default to 0 if None
                self.bonus_base_hitpoints = data.get('bonus_base_hitpoints', 0)  # Default to 0 if None
                self.name = self.petname if self.petname else self.dragon_name
            else:
                raise ValueError("Player dragon not found in the database")
        
        except Exception as e:
            raise ValueError(f"Error fetching player dragon data: {e}")

    def calculate_and_apply_stats(self):
        # Initialize stats
        stats = {'health': 0, 'attack': 0, 'defense': 0, 'dodge': 0}

        # Add primary trait bonuses
        primary_bonus = primary_traits_with_stats.get(self.primary_trait)
        if primary_bonus:
            stats[primary_bonus['main']] += 10
            stats[primary_bonus['off']] += 5

        # Add secondary trait bonuses separately
        secondary_traits = [self.secondary1, self.secondary2, self.secondary3]
        for trait in secondary_traits:
            if trait:  # Ensure the trait is not None or empty
                for fruit, traits in fruit_traits_with_stats.items():
                    if trait in traits:
                        stat = traits[trait]
                        stats[stat] += 5

        # Add nurture trait bonus
        nurture_bonus = nurture_traits_with_stats.get(self.nurture_trait)
        if nurture_bonus:
            stats[nurture_bonus] += 15

        # Add bonus stats
        stats['health'] += self.bonus_health if self.bonus_health is not None else 0
        stats['attack'] += self.bonus_attack if self.bonus_attack is not None else 0
        stats['defense'] += self.bonus_defense if self.bonus_defense is not None else 0
        stats['dodge'] += self.bonus_dodge if self.bonus_dodge is not None else 0

        # Update the stats
        self.stats = stats

    def calculate_hitpoints_and_damage(self):
        base_hitpoints = 100 + self.bonus_base_hitpoints if self.bonus_base_hitpoints is not None else 0
        self.maximum_hitpoints = base_hitpoints + (self.stats['health'] / 100 * base_hitpoints)
        self.damage = 100 + (self.stats['attack'] / 100 * 100)

    def save_current_hitpoints(self):
        try:
            doc_ref = db.collection('hatcheddragons').document(self.id)
            doc_ref.update({
                'current_hitpoints': self.current_hitpoints
            })
        except Exception as e:
            raise ValueError(f"Error saving current hitpoints: {e}")


def calculate_boss_stats(stats):
    base_hp = 1000
    base_damage = 100

    # Convert stats values to integers and print to verify
    health = int(stats['health'])
    attack = int(stats['attack'])
    defense = int(stats['defense'])
    dodge = int(stats['dodge'])

    print(f"health: {health}, attack: {attack}, defense: {defense}, dodge: {dodge}")

    hp = base_hp + (base_hp * health / 100)
    damage = base_damage + (base_damage * attack / 100)

    return int(hp), int(damage), defense, dodge


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

def trait_match_count(player_dragon, boss_dragon):
    player_traits = {player_dragon.secondary1, player_dragon.secondary2, player_dragon.secondary3}
    boss_traits = {boss_dragon.secondary_trait1, boss_dragon.secondary_trait2, boss_dragon.secondary_trait3}
    return len(player_traits.intersection(boss_traits))


def player_attack_boss(player_dragon, boss_dragon):
    primary_trait_match = player_dragon.primary_trait == boss_dragon.primary_trait
    secondary_traits_match = trait_match_count(player_dragon, boss_dragon)
    
    return calculate_damage(player_dragon.stats['attack'], boss_dragon.stats['defense'], primary_trait_match, secondary_traits_match)

def boss_attack_player(boss_dragon, player_dragon):
    if dodge_attack(player_dragon.stats['dodge'], boss_dragon.stats['dodge']):
        print(f"{player_dragon.dragon_name} dodges the attack!")
        return 0
    else:
        matching_traits = trait_match_count(player_dragon, boss_dragon)
        base_damage = 100 + (100 * boss_dragon.stats['attack'] / 100)
        effective_damage = calculate_damage_reduction(base_damage, player_dragon.stats['defense'], matching_traits)
        return effective_damage

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

def save_player_dragon_hitpoints(dragon):
    try:
        # Ensure the ID is correctly formatted with leading zeros if necessary
        dragon_id = str(dragon.id).zfill(4)
        
        # Reference to the specific dragon document
        dragon_doc_ref = db.collection('hatcheddragons').document(dragon_id)
        
        # Update the current hitpoints
        dragon_doc_ref.update({
            'current_hitpoints': dragon.current_hitpoints
        })

        #print(f"Successfully updated hitpoints for dragon ID {dragon_id}")

    except Exception as e:
        print(f"Error saving player dragon hitpoints: {e}")

def start_combat(player_dragons, boss_dragon_stats, draw_area_gameboard, screen, selected_area, player_tokens, displayed_quests, boss_dragon_filename):
    boss_dragon = BossDragon(filename=boss_dragon_filename)
    boss_dragon.stats = {
        'health': boss_dragon_stats[0],
        'attack': boss_dragon_stats[1],
        'defense': boss_dragon_stats[2],
        'dodge': boss_dragon_stats[3]
    }
    boss_dragon.calculate_hitpoints_and_damage()
    boss_dragon.current_hitpoints = boss_dragon.maximum_hitpoints  # Set initial current_hitpoints to maximum_hitpoints
    print(f"Boss Dragon - HP: {boss_dragon.current_hitpoints}, Attack: {boss_dragon.stats['attack']}, Defense: {boss_dragon.stats['defense']}, Dodge: {boss_dragon.stats['dodge']}")

    # Ensure all player dragons are instances of PlayerDragon
    for i in range(len(player_dragons)):
        if isinstance(player_dragons[i], dict):
            player_dragons[i] = PlayerDragon(player_dragons[i]['id'])

    for dragon in player_dragons:
        if dragon is not None:
            print(f"{dragon.name} - HP: {dragon.current_hitpoints}, Attack: {dragon.stats['attack']}, Defense: {dragon.stats['defense']}, Dodge: {dragon.stats['dodge']}")
    
    if not any(dragon is not None for dragon in player_dragons):
        print("Error: At least one player dragon must be initialized for combat.")
        return

    combat(player_dragons, boss_dragon, draw_area_gameboard, screen, selected_area, player_tokens, displayed_quests)

def combat(player_dragons, boss_dragon, draw_area_gameboard, screen, selected_area, player_tokens, displayed_quests):
    while boss_dragon.current_hitpoints > 0 and any(dragon is not None and dragon.current_hitpoints > 0 for dragon in player_dragons):
        for dragon in player_dragons:
            if dragon and dragon.current_hitpoints > 0:
                if dodge_attack(boss_dragon.stats['dodge'], dragon.stats['dodge']):
                    print(f"Boss dodges the attack from {dragon.name}!")
                    damage_to_boss = 0
                else:
                    damage_to_boss = round(player_attack_boss(dragon, boss_dragon))
                boss_dragon.current_hitpoints = max(0, round(boss_dragon.current_hitpoints - damage_to_boss, 2))
                print(f"{dragon.name} attacks boss for {damage_to_boss} damage. Boss HP: {round(boss_dragon.current_hitpoints)}")
                draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)
                pygame.display.flip()
                time.sleep(0.5)
                if boss_dragon.current_hitpoints <= 0:
                    print("Boss defeated!")
                    break

                if dodge_attack(dragon.stats['dodge'], boss_dragon.stats['dodge']):
                    print(f"{dragon.name} dodges the attack!")
                    damage_to_dragon = 0
                else:
                    damage_to_dragon = round(boss_attack_player(boss_dragon, dragon))
                dragon.current_hitpoints = max(0, round(dragon.current_hitpoints - damage_to_dragon, 2))
                print(f"Boss attacks {dragon.name} for {damage_to_dragon} damage. {dragon.name} HP: {round(dragon.current_hitpoints)}")
                draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)
                pygame.display.flip()
                time.sleep(0.5)
                if dragon.current_hitpoints <= 0:
                    print(f"{dragon.name} defeated!")

    if boss_dragon.current_hitpoints > 0:
        print("Boss wins!")
    else:
        print("Players win!")

    # After combat ends, ensure all dragons have at least 1 HP if they reached 0 and save hitpoints
    for dragon in player_dragons:
        if dragon:
            if dragon.current_hitpoints <= 0:
                dragon.current_hitpoints = 1
            save_player_dragon_hitpoints(dragon)

    print(f"Final Boss HP: {boss_dragon.current_hitpoints}")
    for dragon in player_dragons:
        if dragon:
            print(f"Final {dragon.name} HP: {dragon.current_hitpoints}")