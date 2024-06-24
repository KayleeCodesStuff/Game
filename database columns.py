import sqlite3
def update_database_schema():
    conn = connect_db('save.db')
    cursor = conn.cursor()
    
    # Add new columns if they don't already exist
    try:
        cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN current_hitpoints INTEGER DEFAULT 100")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE hatcheddragons ADD COLUMN bonus_base_hitpoints INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

# Call the function to update the database schema
update_database_schema()
