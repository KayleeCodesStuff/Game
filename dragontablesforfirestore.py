import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the path to the service account key file from the environment variable
key_path = os.getenv('FIREBASE_KEY_PATH')

# Print the path to verify
print(f"Using service account key from: {key_path}")

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
    conn = sqlite3.connect('dragonsedit.db')
    cursor = conn.cursor()
    print("Connected to SQLite database successfully.")
except sqlite3.Error as e:
    raise ValueError(f"Failed to connect to SQLite database: {e}")

def update_firestore_from_sqlite():
    try:
        # Update dragons collection
        cursor.execute("SELECT id, filename, type, name, primary_characteristic, special_abilities, rgb_value_range, Nurture, gender, secondary_trait1, secondary_trait2, secondary_trait3, facing_direction, current_hitpoints, max_hitpoints FROM dragons")
        dragons_rows = cursor.fetchall()
        for row in dragons_rows:
            (id, filename, type, name, primary_characteristic, special_abilities, rgb_value_range, Nurture, gender, secondary_trait1, secondary_trait2, secondary_trait3, facing_direction, current_hitpoints, max_hitpoints) = row
            db.collection('dragons').document(str(id)).set({
                'filename': filename,
                'type': type,
                'name': name,
                'primary_characteristic': primary_characteristic,
                'special_abilities': special_abilities,
                'rgb_value_range': rgb_value_range,
                'Nurture': Nurture,
                'gender': gender,
                'secondary_trait1': secondary_trait1,
                'secondary_trait2': secondary_trait2,
                'secondary_trait3': secondary_trait3,
                'facing_direction': facing_direction,
                'current_hitpoints': current_hitpoints,
                'max_hitpoints': max_hitpoints
            })
            print(f"Updated dragon {id} in Firestore")

        # Update nurture collection
        cursor.execute("SELECT id, option, text, trait FROM nurture")
        nurture_rows = cursor.fetchall()
        for row in nurture_rows:
            (id, option, text, trait) = row
            db.collection('nurture').document(str(id)).set({
                'option': option,
                'text': text,
                'trait': trait
            })
            print(f"Updated nurture {id} in Firestore")

        # Update quests collection
        cursor.execute("SELECT ID, Category, ChallengeRating, Description, Special, Reward, Reset, completed FROM quests")
        quests_rows = cursor.fetchall()
        for row in quests_rows:
            (ID, Category, ChallengeRating, Description, Special, Reward, Reset, completed) = row
            db.collection('quests').document(str(ID)).set({
                'Category': Category,
                'ChallengeRating': ChallengeRating,
                'Description': Description,
                'Special': Special,
                'Reward': Reward,
                'Reset': Reset,
                'completed': completed
            })
            print(f"Updated quest {ID} in Firestore")

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
