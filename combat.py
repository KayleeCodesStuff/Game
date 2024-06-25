import random
import sqlite3
import os

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


def apply_bonuses(stats, is_boss=False, tier=1, dragon_id=None):
    print("Initial stats (before bonuses):", stats)
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
    
    print("Final stats (after bonuses):", stats)
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
    
    return calculate_damage(player_dragon['stats']['attack'], boss_dragon['defense'], primary_trait_match, secondary_traits_match)

def boss_attack_player(boss_dragon, player_dragon):
    if not dodge_attack(player_dragon['stats']['dodge'], boss_dragon['dodge']):
        matching_traits = trait_match_count(boss_dragon['secondary_traits'], player_dragon['secondary_traits'])
        base_damage = 100 + (100 * boss_dragon['attack'] / 100)
        effective_damage = calculate_damage_reduction(base_damage, player_dragon['stats']['defense'], matching_traits)
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
        self.fetch_data()
        self.calculate_stats()
        self.apply_tier_bonus()
        self.calculate_hitpoints_and_damage()

    def fetch_data(self):
        db_path = os.path.join(os.path.dirname(__file__), 'dragonsedit.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, primary_characteristic, secondary_trait1, secondary_trait2, secondary_trait3, Nurture, special_abilities, current_hitpoints, facing_direction
            FROM dragons
            WHERE filename = ?
        """, (self.filename,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            self.id = row[0]
            self.name = row[1]
            self.primary_trait = row[2]
            self.secondary_trait1 = row[3]
            self.secondary_trait2 = row[4]
            self.secondary_trait3 = row[5]
            self.nurture_trait = row[6]
            self.special_abilities = row[7]
            self.current_hitpoints = row[8]
            self.facing_direction = row[9]
        else:
            raise ValueError("Boss dragon not found in the database")

    def calculate_stats(self):
        # Initialize stats
        stats = {'health': 0, 'attack': 0, 'defense': 0, 'dodge': 0}

        # Add primary trait bonuses
        primary_bonus = primary_traits_with_stats.get(self.primary_trait)
        if primary_bonus:
            stats[primary_bonus['main']] += 10
            stats[primary_bonus['off']] += 5

        # Add secondary trait bonuses
        secondary_traits = [self.secondary_trait1, self.secondary_trait2, self.secondary_trait3]
        for trait in secondary_traits:
            for fruit, traits in fruit_traits_with_stats.items():
                if trait in traits:
                    stats[traits[trait]] += 5

        # Add nurture trait bonus
        nurture_bonus = nurture_traits_with_stats.get(self.nurture_trait)
        if nurture_bonus:
            stats[nurture_bonus] += 15

        # Update the stats
        self.stats = stats

    def apply_tier_bonus(self):
        tier_bonus = self.tier * 25
        for stat in self.stats:
            self.stats[stat] += tier_bonus

    def calculate_hitpoints_and_damage(self):
        self.maximum_hitpoints = 1000 + (self.stats['health'] / 100 * 1000)
        self.damage = 100 + (self.stats['attack'] / 100 * 100)

    def save_current_hitpoints(self):
        db_path = os.path.join(os.path.dirname(__file__), 'dragonsedit.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dragons
            SET current_hitpoints = ?
            WHERE id = ?
        """, (self.current_hitpoints, self.id))
        
        conn.commit()
        conn.close()

class PlayerDragon:
    def __init__(self, dragon_id):
        self.id = dragon_id
        self.dragon_name = None
        self.primary_trait = None
        self.secondary1 = None
        self.secondary2 = None
        self.secondary3 = None
        self.nurture_trait = None
        self.special_abilities = None
        self.petname = None
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
        self.calculate_stats()
        self.calculate_hitpoints_and_damage()

    def fetch_data(self):
        db_path = os.path.join(os.path.dirname(__file__), 'save.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, dragon_name, primary_trait, secondary1, secondary2, secondary3, nurture, special_abilities, petname, current_hitpoints, bonus_health, bonus_attack, bonus_defense, bonus_dodge, bonus_base_hitpoints
            FROM hatcheddragons
            WHERE id = ?
        """, (self.id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            self.id = row[0]
            self.dragon_name = row[1]
            self.primary_trait = row[2]
            self.secondary1 = row[3]
            self.secondary2 = row[4]
            self.secondary3 = row[5]
            self.nurture_trait = row[6]
            self.special_abilities = row[7]
            self.petname = row[8]
            self.current_hitpoints = row[9]
            self.bonus_health = row[10]
            self.bonus_attack = row[11]
            self.bonus_defense = row[12]
            self.bonus_dodge = row[13]
            self.bonus_base_hitpoints = row[14]
            self.name = self.petname if self.petname else self.dragon_name
        else:
            raise ValueError("Player dragon not found in the database")

    def calculate_stats(self):
        # Initialize stats
        stats = {'health': 0, 'attack': 0, 'defense': 0, 'dodge': 0}

        # Add primary trait bonuses
        primary_bonus = primary_traits_with_stats.get(self.primary_trait)
        if primary_bonus:
            stats[primary_bonus['main']] += 10
            stats[primary_bonus['off']] += 5

        # Add secondary trait bonuses
        secondary_traits = [self.secondary1, self.secondary2, self.secondary3]
        for trait in secondary_traits:
            for fruit, traits in fruit_traits_with_stats.items():
                if trait in traits:
                    stats[traits[trait]] += 5

        # Add nurture trait bonus
        nurture_bonus = nurture_traits_with_stats.get(self.nurture_trait)
        if nurture_bonus:
            stats[nurture_bonus] += 15

        # Add bonus stats
        stats['health'] += self.bonus_health
        stats['attack'] += self.bonus_attack
        stats['defense'] += self.bonus_defense
        stats['dodge'] += self.bonus_dodge

        # Update the stats
        self.stats = stats

    def calculate_hitpoints_and_damage(self):
        base_hitpoints = 100 + self.bonus_base_hitpoints
        self.maximum_hitpoints = base_hitpoints + (self.stats['health'] / 100 * base_hitpoints)
        self.damage = 100 + (self.stats['attack'] / 100 * 100)

    def save_current_hitpoints(self):
        db_path = os.path.join(os.path.dirname(__file__), 'save.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hatcheddragons
            SET current_hitpoints = ?
            WHERE id = ?
        """, (self.current_hitpoints, self.id))
        
        conn.commit()
        conn.close()


def combat(player_dragons, boss_dragon_stats):
    boss_hp, boss_damage, boss_defense, boss_dodge = boss_dragon_stats
    boss_dragon = {
        'primary_trait': 'Boss Primary',  # Placeholder
        'secondary_traits': ['Boss Secondary 1', 'Boss Secondary 2', 'Boss Secondary 3'],  # Placeholder
        'attack': boss_damage,
        'defense': boss_defense,
        'dodge': boss_dodge
    }

    while boss_hp > 0 and any(dragon['current_hitpoints'] > 0 for dragon in player_dragons):
        for dragon in player_dragons:
            if dragon and dragon['current_hitpoints'] > 0:
                damage_to_boss = player_attack_boss(dragon, boss_dragon)
                boss_hp -= damage_to_boss
                print(f"{dragon['dragon_name']} attacks boss for {damage_to_boss} damage. Boss HP: {boss_hp}")
                if boss_hp <= 0:
                    print("Boss defeated!")
                    return
                damage_to_dragon = boss_attack_player(boss_dragon, dragon)
                dragon['current_hitpoints'] -= damage_to_dragon
                print(f"Boss attacks {dragon['dragon_name']} for {damage_to_dragon} damage. {dragon['dragon_name']} HP: {dragon['current_hitpoints']}")
                if dragon['current_hitpoints'] <= 0:
                    print(f"{dragon['dragon_name']} defeated!")

    if boss_hp > 0:
        print("Boss wins!")
    else:
        print("Players win!")
        
def start_combat(player_dragons, boss_dragon_stats):
    boss_hp, boss_damage, boss_defense, boss_dodge = boss_dragon_stats
    print(f"Boss Dragon - HP: {boss_hp}, Attack: {boss_damage}, Defense: {boss_defense}, Dodge: {boss_dodge}")
    for dragon in player_dragons:
        if dragon is not None:
            print(f"{dragon['dragon_name']} - HP: {dragon['current_hitpoints']}, Attack: {dragon['stats']['attack']}, Defense: {dragon['stats']['defense']}, Dodge: {dragon['stats']['dodge']}")
    
    combat(player_dragons, boss_dragon_stats)

