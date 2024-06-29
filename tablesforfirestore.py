import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the path to the service account key file from the environment variable
key_path = os.getenv('FIREBASE_KEY_PATH')

if not key_path:
    raise ValueError("FIREBASE_KEY_PATH environment variable not set.")

# Initialize the Firebase Admin SDK
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Connect to SQLite database
conn = sqlite3.connect('save.db')
cursor = conn.cursor()

# Function to update Firestore from SQLite database
def update_firestore_from_sqlite():
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

# Run the update function
update_firestore_from_sqlite()

# Close the SQLite connection
conn.close()
