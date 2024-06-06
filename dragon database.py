import os
import random
import sqlite3

# Define the folder containing the images using a raw string for the path
image_folder = r'C:\Users\kayle\PycharmProjects\Game\dragons'

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

# Function to determine RGB value range based on dragon type
def get_rgb_range(dragon_type):
    if dragon_type == 'Gold':
        return "(0-21, 0-21, 0-21)"
    elif dragon_type == 'Silver':
        return "(21-51, 21-51, 21-51)"
    else:
        return "(0-255, 0-255, 0-255)"

# Function to generate a description
def generate_description(dragon_type, name, primary_characteristic, secondary_characteristics, additional_word):
    description = f"{name} is a {dragon_type} dragon known for being {primary_characteristic}. With traits like {', '.join(secondary_characteristics)}, it exhibits a unique personality. It is also {additional_word}, making it stand out. Its appearance is characterized by its majestic presence and the way it commands attention."
    return description

# Read filenames and generate data
def generate_dragon_data():
    dragons = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            parts = filename.replace('.png', '').split('_')
            type_name = ''.join([i for i in parts[0] if not i.isdigit()])
            dragon_type = type_name.capitalize()
            name = generate_name()
            
            # Check for additional trait in filename
            primary_char = random.choice(primary_characteristics)
            if len(parts) > 1:
                partial_trait = parts[1]
                for trait in primary_characteristics + [item for sublist in secondary_characteristics for item in sublist]:
                    if trait.startswith(partial_trait):
                        primary_char = trait
                        break

            secondary_chars = []
            while len(secondary_chars) < 3:
                secondary_char = random.choice(random.choice(secondary_characteristics))
                if secondary_char not in secondary_chars:
                    secondary_chars.append(secondary_char)
            additional_word = random.choice(additional_words)
            rgb_value_range = get_rgb_range(dragon_type)
            
            # Check for "twin" in filename
            special_abilities = "Twin Tailed" if "twin" in filename.lower() else ""
            
            description = generate_description(dragon_type, name, primary_char, secondary_chars, additional_word)

            dragon_data = {
                "filename": filename,
                "type": dragon_type,
                "name": name,
                "primary_characteristic": primary_char,
                "secondary_characteristics": secondary_chars,
                "additional_word": additional_word,
                "rgb_value_range": rgb_value_range,
                "special_abilities": special_abilities,
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
        ''', (dragon['filename'], dragon['type'], dragon['name'], dragon['primary_characteristic'], ','.join(dragon['secondary_characteristics']), dragon['additional_word'], dragon['rgb_value_range'], dragon['special_abilities'], dragon['description']))
    conn.commit()
    conn.close()

# Run the script
dragons = generate_dragon_data()
insert_into_db(dragons)

# Query to check inserted data
conn = sqlite3.connect('dragons.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM dragons')
rows = cursor.fetchall()
conn.close()

import pandas as pd
import ace_tools as tools

# Convert rows to DataFrame for better display
df = pd.DataFrame(rows, columns=["ID", "Filename", "Type", "Name", "Primary Characteristic", "Secondary Characteristics", "Additional Word", "RGB Value Range", "Special Abilities", "Description"])
tools.display_dataframe_to_user(name="Dragon Data", dataframe=df)

df
