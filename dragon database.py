import os
import random
import sqlite3
import pandas as pd

# Define the folder containing the images
image_folder = r'C:\Users\kayle\PycharmProjects\Game\dragons'

# Define the characteristics and lists
primary_characteristics = ["Curious", "Playful", "Adventurous", "Resourceful", "Sociable", "Thoughtful", "Confident", "Generous", "Reflective", "Strategic", "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward", "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"]
secondary_characteristics = ["Dark", "Brooding", "Responsible", "Common", "Distraction", "Fierce", "Fiery", "Showy", "Speed", "Flightiness", "Drive", "Ambition", "Earthy", "Pragmatic", "Stout", "Loyal", "Angelic", "Unique", "Pure", "Self-righteous"]

# Predefined names assigned to respective ID numbers
predefined_names = ["Quip", "Sasha", "Buggs", "Snarl", "Spitfire", "Squee", "Loki", "Jazz", "Joy", "Skye",
                    "Flare", "Blitz", "Ziggy", "Nova", "Pippin", "Zippy", "Sparx", "Razz", "Fizz",
                    "Gizmo", "Misty", "Blaze", "Pixie", "Rumble", "Flick", "Gloom", "Flash", "Sprout",
                    "Dazzle", "Whisk", "Glimmer", "Trix", "Bramble", "Fizzle", "Muddle", "Puddle", "Ruffle",
                    "Smudge", "Sparky", "Whimsy", "Wisp", "Glint", "Spark", "Glow", "Zip", "Frost", "Ember",
                    "Whirl", "Gleam", "Shine", "Twirl", "Nimbus", "Aurora", "Stormy", "Drizzle", "Flurry", "Flit",
                    "Puff", "Zephyr", "Shroud", "Tempest", "Rustle", "Tumble", "Twine", "Quirk", "Mirth",
                    "Flutter", "Twinkle", "Breezy", "Starlight", "Flicker", "Fable", "Tinker", "Glisten",
                    "Gleef", "Chirp", "Quirk", "Blip", "Pebble", "Niffler", "Glimpse", "Shimmer", "Querkle", 
                    "Giggle", "Squirm", "Thorn", "Cloud", "Moon", "Peace", "Vision", "Ghost", "Shadow", 
                    "Snow", "Dawn", "Dusk", "Zomp", "Zillow", "Xanth", "Smolder", "Smoke", "Frost", "Crimson", 
                    "Quasar", "Quark", "Quillion", "Licked", "Bounce", "Batty", "Blink", "Korax", "Steep", 
                    "Serenity", "Shade", "Ginko", "Goji", "Sparkle", "Hiccup", "Halo", "Heap", "Haze","Hoax", 
                    "Squirt", "Sprite", "Snicker", "Doodle", "Syntax", "Digit", "Pearl", "Tease", "Swing", 
                    "Jinx", "Quibble", "Jax", "Prank", "Secret", "Whisper", "Ditzel", "Speck", "Pickle", 
                    "Squeal", "Cookie", "Brownie", "Zephyr", "Lolli", "Lisp", "Spree", "Squeak", "Squish", "Squeeze"]

# Function to generate a description for the dragon
def generate_description(dragon_type, name, primary_characteristic, secondary_characteristics, additional_word):
    description = f"{name} is a {dragon_type} dragon known for being {primary_characteristic}. With traits like {', '.join(secondary_characteristics)}, it exhibits a unique personality. It is also {additional_word}, making it stand out. Its appearance is characterized by its majestic presence and the way it commands attention."
    return description

# Function to determine RGB value range based on dragon type
def get_rgb_range(dragon_type):
    if dragon_type == 'Gold':
        return "(0-21, 0-21, 0-21)"
    elif dragon_type == 'Silver':
        return "(21-51, 21-51, 21-51)"
    else:
        return "(0-255, 0-255, 0-255)"

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
    
    # Handle specific cases for primary characteristics
    special_ability = ""
    primary_char = None
    if "bless" in name:
        primary_char = "Blessed"
        name = name.replace("bless", "")
    elif "demon" in name:
        primary_char = "Demonic"
        name = name.replace("demon", "")
    
    if not primary_char:
        primary_char = next((pc for pc in primary_characteristics if name.startswith(pc.lower())), None)
        if primary_char:
            name = name[len(primary_char):]
        else:
            primary_char = next((sc for sc in secondary_characteristics if name.startswith(sc.lower())), None)
            if primary_char:
                name = name[len(primary_char):]
            else:
                primary_char = random.choice(primary_characteristics)  # Default to a random primary characteristic

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
                
                # Assign a predefined name based on the ID number
                name = predefined_names[id_number - 1]  # Adjust for zero-based index
                
                # Generate the description and RGB value range
                description = generate_description(dragon_type, name, primary_char, secondary_chars, special_ability)
                rgb_value_range = get_rgb_range(dragon_type)
                
                dragon_data = {
                    "id": id_number,
                    "filename": filename,
                    "type": dragon_type,
                    "name": name,
                    "primary_characteristic": primary_char,
                    "secondary_characteristics": secondary_chars,
                    "special_abilities": special_ability,
                    "description": description,
                    "rgb_value_range": rgb_value_range
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
        special_abilities TEXT,
        description TEXT,
        rgb_value_range TEXT
    )
    ''')
    for dragon in dragons:
        cursor.execute('''
        INSERT INTO dragons (id, filename, type, name, primary_characteristic, secondary_characteristics, special_abilities, description, rgb_value_range)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dragon['id'], dragon['filename'], dragon['type'], dragon['name'], dragon['primary_characteristic'], ','.join(dragon['secondary_characteristics']), dragon['special_abilities'], dragon['description'], dragon['rgb_value_range']))
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
