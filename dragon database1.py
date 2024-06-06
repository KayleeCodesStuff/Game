import os
import random
import sqlite3
import pandas as pd
from g4f.client import Client

# Define the folder containing the images
image_folder = r'C:\Users\kayle\PycharmProjects\Game\dragons'

# Define the characteristics and lists
primary_characteristics = ["Curious", "Playful", "Adventurous", "Resourceful", "Sociable", "Thoughtful", "Confident", "Generous", "Reflective", "Strategic", "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward", "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"]
secondary_characteristics = ["Dark", "Brooding", "Responsible", "Common", "Distraction", "Fierce", "Fiery", "Showy", "Speed", "Flightiness", "Drive", "Ambition", "Earthy", "Pragmatic", "Stout", "Loyal", "Angelic", "Unique", "Pure", "Self-righteous"]

# List of predefined names for fallback
predefined_names = ["Quip", "Joy", "Buggs", "Snarl", "Spitfire", "Sasha", "Squee", "Loki", "Jazz"]

# Initialize the client
client = Client()

# Function to generate a GPT-created name
def generate_name():
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "In a 1 word response, generate a short, cute, unique name for a dragon."}],
        )
        name = chat_completion.choices[0].message.content.strip()
        # Ensure the name is appropriate
        if len(name) <= 10 and name.isalpha():
            return name
        else:
            return random.choice(predefined_names)  # Use predefined name if generated name is not appropriate
    except Exception as e:
        print(f"Error generating name: {e}")
        return random.choice(predefined_names)

# Function to parse the filename
def parse_filename(filename):
    # Remove the file extension
    name = filename.replace('.png', '')
    
    # Identify the dragon type
    dragon_type = next((dt for dt in ["black", "white", "rainbow", "metal", "silver", "gold"] if name.startswith(dt)), None)
    if not dragon_type:
        raise ValueError(f"Unknown dragon type in filename: {filename}")
    
    # Remove the dragon type from the name
    name = name[len(dragon_type):]
    
    # Extract the ID number
    id_str = ''.join([char for char in name if char.isdigit()])
    if not id_str:
        raise ValueError(f"No ID number found in filename: {filename}")
    
    id_number = int(id_str)
    
    # Remove the ID number from the name
    name = name[len(id_str):]
    
    # Extract special words
    special_ability = ""
    primary_char = next((pc for pc in primary_characteristics if name.startswith(pc.lower())), None)
    if primary_char:
        name = name[len(primary_char):]
    else:
        primary_char = next((sc for sc in secondary_characteristics if name.startswith(sc.lower())), None)
        if primary_char:
            name = name[len(primary_char):]
        else:
            primary_char = random.choice(predefined_names)  # Default to the first predefined name

    secondary_chars = []
    for secondary in secondary_characteristics:
        if name.startswith(secondary.lower()):
            secondary_chars.append(secondary)
            name = name[len(secondary):]
    
    if "twin" in name:
        special_ability = "Twin Tailed"
    
    # Ensure three secondary characteristics
    while len(secondary_chars) < 3:
        sec = random.choice(secondary_characteristics)
        if sec not in secondary_chars:
            secondary_chars.append(sec)
    
    return dragon_type.capitalize(), id_number, primary_char, secondary_chars, special_ability

# Function to generate dragon data
def generate_dragon_data(image_folder):
    dragons = []
    processed_ids = set()
    
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            try:
                dragon_type, id_number, primary_char, secondary_chars, special_ability = parse_filename(filename)
                if id_number in processed_ids:
                    continue  # Skip if this ID has already been processed
                
                # Generate a name for the dragon
                name = generate_name()
                
                dragon_data = {
                    "id": id_number,
                    "filename": filename,
                    "type": dragon_type,
                    "name": name,
                    "primary_characteristic": primary_char,
                    "secondary_characteristics": secondary_chars,
                    "special_abilities": special_ability,
                }
                dragons.append(dragon_data)
                processed_ids.add(id_number)
            except ValueError as e:
                print(e)
    return dragons

# Function to insert data into the database
def insert_into_db(dragons, db_name='dragons.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dragons (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        primary_characteristic TEXT NOT NULL,
        secondary_characteristics TEXT NOT NULL,
        special_abilities TEXT
    )
    ''')
    for dragon in dragons:
        cursor.execute('''
        INSERT INTO dragons (id, filename, type, name, primary_characteristic, secondary_characteristics, special_abilities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (dragon['id'], dragon['filename'], dragon['type'], dragon['name'], dragon['primary_characteristic'], ','.join(dragon['secondary_characteristics']), dragon['special_abilities']))
    conn.commit()
    conn.close()

# Function to save data to a CSV file
def save_to_csv(dragons, filename='dragons_data.csv'):
    df = pd.DataFrame(dragons)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Generate dragon data
dragons = generate_dragon_data(image_folder)

# Insert data into the database
insert_into_db(dragons)

# Save data to CSV file
save_to_csv(dragons)
