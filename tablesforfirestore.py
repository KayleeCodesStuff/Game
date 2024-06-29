import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Get the path to the service account key file from the environment variable
key_path = os.getenv('FIREBASE_KEY_PATH')

if not key_path:
    raise ValueError("FIREBASE_KEY_PATH environment variable not set.")

# Initialize the Firebase Admin SDK
try:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    raise ValueError(f"Failed to initialize Firebase Admin SDK: {e}")

# Initialize Firestore
try:
    db = firestore.client()
    print("Firestore client initialized successfully.")
except Exception as e:
    raise ValueError(f"Failed to initialize Firestore client: {e}")

# Connect to SQLite database
try:
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    print("Connected to SQLite database successfully.")
except sqlite3.Error as e:
    raise ValueError(f"Failed to connect to SQLite database: {e}")

def validate_and_format_rgb(rgb_str):
    # Check if the RGB string is in the correct format
    match = re.match(r'\((\d{1,3}), (\d{1,3}), (\d{1,3})\)', rgb_str)
    if match:
        r, g, b = map(int, match.groups())
        if all(0 <= value <= 255 for value in (r, g, b)):
            return f'({r}, {g}, {b})'
    return None

def update_firestore_from_sqlite():
    try:
        # Update inventory collection
        cursor.execute("SELECT * FROM inventory")
        inventory_rows = cursor.fetchall()
        for row in inventory_rows:
            inventory_id, fruit, count = row
            db.collection('inventory').document(str(inventory_id)).set({
                'fruit': fruit,
                'count': count
            })
            print(f"Updated inventory {inventory_id} in Firestore")

        # Update eggs collection
        cursor.execute("SELECT * FROM eggs")
        eggs_rows = cursor.fetchall()
        for row in eggs_rows:
            egg_id, genotype, phenotype, image_file, parent1_name, parent2_name = row
            db.collection('eggs').document(str(egg_id)).set({
                'genotype': genotype,
                'phenotype': phenotype,
                'image_file': image_file,
                'parent1_name': parent1_name,
                'parent2_name': parent2_name
            })
            print(f"Updated egg {egg_id} with phenotype {phenotype} in Firestore")

        # Update elixirs collection
        cursor.execute("SELECT * FROM elixirs")
        elixirs_rows = cursor.fetchall()
        for row in elixirs_rows:
            elixir_id, rgb, title, primary_trait, secondary_trait1, secondary_trait2, secondary_trait3, image_file, position = row
            validated_rgb = validate_and_format_rgb(rgb)
            if validated_rgb:
                db.collection('elixirs').document(str(elixir_id)).set({
                    'rgb': validated_rgb,
                    'title': title,
                    'primary_trait': primary_trait,
                    'secondary_trait1': secondary_trait1,
                    'secondary_trait2': secondary_trait2,
                    'secondary_trait3': secondary_trait3,
                    'image_file': image_file,
                    'position': position
                })
                print(f"Updated elixir {elixir_id} in Firestore with valid RGB")
            else:
                print(f"Invalid RGB format for elixir {elixir_id}: {rgb}")

        # Update hatcheddragons collection
        cursor.execute("SELECT * FROM hatcheddragons")
        hatcheddragons_rows = cursor.fetchall()
        for row in hatcheddragons_rows:
            (dragon_id, genotype, parent1, parent2, elixir_rgb, elixir_title, dragon_id, dragon_name,
             primary_trait, secondary1, secondary2, secondary3, nurture, gender, rgb_range, filename, type,
             special_abilities, petname, bonus_health, bonus_attack, bonus_defense, bonus_dodge, facing_direction,
             current_hitpoints, bonus_base_hitpoints) = row
            validated_rgb_range = validate_and_format_rgb(rgb_range)
            if validated_rgb_range:
                db.collection('hatcheddragons').document(str(dragon_id)).set({
                    'genotype': genotype,
                    'parent1': parent1,
                    'parent2': parent2,
                    'elixir_rgb': elixir_rgb,
                    'elixir_title': elixir_title,
                    'dragon_id': dragon_id,
                    'dragon_name': dragon_name,
                    'primary_trait': primary_trait,
                    'secondary1': secondary1,
                    'secondary2': secondary2,
                    'secondary3': secondary3,
                    'nurture': nurture,
                    'gender': gender,
                    'rgb_range': validated_rgb_range,
                    'filename': filename,
                    'type': type,
                    'special_abilities': special_abilities,
                    'petname': petname,
                    'bonus_health': bonus_health,
                    'bonus_attack': bonus_attack,
                    'bonus_defense': bonus_defense,
                    'bonus_dodge': bonus_dodge,
                    'facing_direction': facing_direction,
                    'current_hitpoints': current_hitpoints,
                    'bonus_base_hitpoints': bonus_base_hitpoints
                })
                print(f"Updated hatcheddragon {dragon_id} in Firestore with valid RGB range")
            else:
                print(f"Invalid RGB range format for hatcheddragon {dragon_id}: {rgb_range}")

        # Update playerquests collection
        cursor.execute("SELECT * FROM playerquests")
        playerquests_rows = cursor.fetchall()
        for row in playerquests_rows:
            quest_id, category, challenge_rating, description, special, reward, reset, completed, tally = row
            db.collection('playerquests').document(str(quest_id)).set({
                'category': category,
                'challenge_rating': challenge_rating,
                'description': description,
                'special': special,
                'reward': reward,
                'reset': reset,
                'completed': completed,
                'tally': tally
            })
            print(f"Updated playerquest {quest_id} in Firestore")

    except Exception as e:
        print(f"Error updating Firestore: {e}")

# Run the update function
update_firestore_from_sqlite()

# Close the SQLite connection
try:
    conn.close()
    print("SQLite connection closed successfully.")
except sqlite3.Error as e:
    print(f"Failed to close SQLite connection: {e}")
