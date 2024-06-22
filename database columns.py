import sqlite3

def add_bonus_columns_to_database():
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    
    # Add columns for bonuses
    cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN bonus_health INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN bonus_attack INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN bonus_defense INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN bonus_dodge INTEGER DEFAULT 0")
    
    conn.commit()
    conn.close()

# Run the function to add columns
add_bonus_columns_to_database()