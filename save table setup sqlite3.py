import sqlite3

def create_tables():
    with sqlite3.connect('save.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elixirs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rgb TEXT,
                title TEXT,
                primary_trait TEXT,
                secondary_trait1 TEXT,
                secondary_trait2 TEXT,
                secondary_trait3 TEXT,
                image_file TEXT,
                position INTEGER
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    create_tables()
    print("Database setup complete.")
