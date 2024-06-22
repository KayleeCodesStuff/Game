import sqlite3

def add_facing_direction_column(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add the facing_direction column to the hatcheddragons table
    cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN facing_direction TEXT")
    
    conn.commit()
    conn.close()
    print("Column facing_direction added successfully.")

# Path to your database file
db_path = 'save.db'  # Adjust the path if necessary

add_facing_direction_column(db_path)
