import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('tasktamer-firebase-admin.json')  # Use the renamed file
firebase_admin.initialize_app(cred)
db = firestore.client()

# Connect to the SQLite database
conn = sqlite3.connect('dragonsedit.db')  # Replace with the actual path to your SQLite database
cursor = conn.cursor()

# Function to upload data to Firestore
def upload_to_firestore(collection_name, data, id_field, max_id_length):
    collection_ref = db.collection(collection_name)
    for item in data:
        doc_id = str(item[id_field]).zfill(max_id_length)  # Pad the ID with leading zeros
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f'Uploaded document with ID: {doc_id}')

# Function to get the maximum length of numeric IDs for padding
def get_max_id_length(table_name, id_field):
    cursor.execute(f"SELECT MAX(LENGTH(CAST({id_field} AS TEXT))) FROM {table_name}")
    max_length = cursor.fetchone()[0]
    return max_length

# Export and upload data for each table, with modifications for the 'dragons' table
tables = {
    "dragons": {"query": "SELECT id, filename, type, name, primary_characteristic, special_abilities, rgb_value_range, Nurture, gender, secondary_trait1, secondary_trait2, secondary_trait3, facing_direction, current_hitpoints, max_hitpoints FROM dragons", "id_field": "id"},
    "nurture": {"query": "SELECT * FROM nurture", "id_field": "id"},
    "quests": {"query": "SELECT * FROM quests", "id_field": "ID"}
}

for table_name, table_info in tables.items():
    cursor.execute(table_info["query"])
    columns = [description[0] for description in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    max_id_length = get_max_id_length(table_name, table_info["id_field"])
    upload_to_firestore(table_name, data, table_info["id_field"], max_id_length)

# Close the database connection
conn.close()
