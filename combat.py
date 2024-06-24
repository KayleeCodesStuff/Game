import random

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

