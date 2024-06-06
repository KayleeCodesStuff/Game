import os
import random
import sqlite3

# Define the folder containing the images
image_folder = 'game/dragons'

# Define the characteristics and lists
primary_characteristics = ["Curious", "Playful", "Adventurous", "Resourceful", "Sociable", "Thoughtful", "Confident", "Generous", "Reflective", "Strategic", "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward", "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"]
secondary_characteristics = [
    ["Dark", "Brooding", "Responsible", "Common"],
    ["Distraction", "Fierce", "Fiery", "Showy"],
    ["Speed", "Flightiness", "Drive", "Ambition"],
    ["Earthy", "Pragmatic", "Stout", "Loyal"],
    ["Angelic", "Unique", "Pure", "Self-righteous"]
]
additional_words = ["Musical", "neglected", "bestial", "hot tempered"]

# Function to generate a random name
def generate_name():
    names = ["Quip", "Joy", "Buggs", "Snarl", "Spitfire", "Sasha", "Squee", "Loki", "Jazz"]
    return random.choice(names)

# Function to generate RGB range
def get_rgb_range(dragon_type):
    if dragon_type == 'Gold':
        return (random.randint(0, 21), random.randint(0, 21), random.randint(0, 21))
    elif dragon_type == 'Silver':
        return (random.randint(21, 51), random.randint(21, 51), random.randint(21, 51))
    else:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Function to generate a description
def generate_description(dragon_type, name, primary_characteristic, secondary_characteristics, additional_word, rgb_value_range):
    description = f"{name} is a {dragon_type} dragon known for being {primary_characteristic}. With traits like {', '.join(secondary_characteristics)}, it exhibits a unique personality. It is also {additional_word}, making it stand out. Its appearance is characterized by colors within the RGB range {rgb_value_range}."
    return description

# Read filenames and generate data
def generate_dragon_data():
    dragons = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            type_name = ''.join([i for i in filename if not i.isdigit()]).replace('.png', '')
            dragon_type = type_name.capitalize()
            name = generate_name()
            primary_char = random.choice(primary_characteristics)
            secondary_chars = []
            while len(secondary_chars) < 3:
                secondary_char = random.choice(random.choice(secondary_characteristics))
                if secondary_char not in secondary_chars:
                    secondary_chars.append(secondary_char)
            additional_word = random.choice(additional_words)
            rgb_value_range = get_rgb_range(dragon_type)
            description = generate_description(dragon_type, name, primary_char, secondary_chars, additional_word, rgb_value_range)

            dragon_data = {
                "filename": filename,
                "type": dragon_type,
                "name": name,
                "primary_characteristic": primary_char,
                "secondary_characteristics": secondary_chars,
                "additional_word": additional_word,
                "rgb_value_range": rgb_value_range,
                "special_abilities": "",  # Leave special abilities blank for now
                "description": description
            }
            dragons.append(dragon_data)
    return dragons

# Example function to insert into database
def insert_into_db(dragons):
    conn = sqlite3.connect('dragons.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dragons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        primary_characteristic TEXT NOT NULL,
        secondary_characteristics TEXT NOT NULL,
        additional_word TEXT NOT NULL,
        rgb_value_range TEXT NOT NULL,
        special_abilities TEXT,
        description TEXT
    )
    ''')
    for dragon in dragons:
        cursor.execute('''
        INSERT INTO dragons (filename, type, name, primary_characteristic, secondary_characteristics, additional_word, rgb_value_range, special_abilities, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dragon['filename'], dragon['type'], dragon['name'], dragon['primary_characteristic'], ','.join(dragon['secondary_characteristics']), dragon['additional_word'], str(dragon['rgb_value_range']), dragon['special_abilities'], dragon['description']))
    conn.commit()
    conn.close()

# Run the script
dragons = generate_dragon_data()
insert_into_db(dragons)
