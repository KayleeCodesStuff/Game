import sqlite3

def update_database_schema():
    conn = connect_db('dragonsedit.db')
    cursor = conn.cursor()
    
    # Add new columns if they don't already exist
    try:
        cursor.execute("ALTER TABLE dragons ADD COLUMN current_hitpoints INTEGER DEFAULT 1000")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE dragons ADD COLUMN max_hitpoints INTEGER DEFAULT 1000")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

# Call the function to update the database schema
update_database_schema()


