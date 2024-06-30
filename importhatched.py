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

def int_to_padded_string(num, length):
    return str(num).zfill(length)

def update_firestore_from_sqlite():
    try:
        # Update hatcheddragons collection
        cursor.execute("SELECT * FROM hatcheddragons")
        hatcheddragons_rows = cursor.fetchall()
        for row in hatcheddragons_rows:
            (id, genotype, parent1, parent2, elixir_rgb, elixir_title, dragon_id, dragon_name,
             primary_trait, secondary1, secondary2, secondary3, nurture, gender, rgb_range, filename, type,
             special_abilities, petname, bonus_health, bonus_attack, bonus_defense, bonus_dodge, facing_direction,
             current_hitpoints, bonus_base_hitpoints) = row

            padded_id = int_to_padded_string(id, 4)

            db.collection('hatcheddragons').document(padded_id).set({
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
                'rgb_range': rgb_range,  # Save the rgb_range directly as it is
                'filename': filename,
                'type': type,
                'special_abilities': special_abilities,
                'petname': petname,
                'bonus_health': int(bonus_health),
                'bonus_attack': int(bonus_attack),
                'bonus_defense': int(bonus_defense),
                'bonus_dodge': int(bonus_dodge),
                'facing_direction': facing_direction,
                'current_hitpoints': int(current_hitpoints),
                'bonus_base_hitpoints': int(bonus_base_hitpoints)
            })
            print(f"Updated hatcheddragon {padded_id} in Firestore")

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
