import sqlite3

# Connect to the second SQLite database
db_path_2 = 'option dragonsedit.db'
conn_2 = sqlite3.connect(db_path_2)
cursor_2 = conn_2.cursor()

# Add new columns for the secondary traits
cursor_2.execute("ALTER TABLE dragons ADD COLUMN secondary_trait1 TEXT;")
cursor_2.execute("ALTER TABLE dragons ADD COLUMN secondary_trait2 TEXT;")
cursor_2.execute("ALTER TABLE dragons ADD COLUMN secondary_trait3 TEXT;")

# Fetch data from the `dragons` table
cursor_2.execute("SELECT id, secondary_characteristics FROM dragons")
dragons_data = cursor_2.fetchall()

# Function to split secondary characteristics
def split_secondary_characteristics(secondary_characteristics):
    return secondary_characteristics.split(',')

# Iterate through the fetched data and update the table
for dragon in dragons_data:
    dragon_id, secondary_characteristics = dragon
    secondary_characteristics_list = split_secondary_characteristics(secondary_characteristics)
    
    # Ensure there are exactly three secondary characteristics
    secondary_trait1 = secondary_characteristics_list[0] if len(secondary_characteristics_list) > 0 else None
    secondary_trait2 = secondary_characteristics_list[1] if len(secondary_characteristics_list) > 1 else None
    secondary_trait3 = secondary_characteristics_list[2] if len(secondary_characteristics_list) > 2 else None

    # Update the table with the new columns
    cursor_2.execute("""
        UPDATE dragons
        SET secondary_trait1 = ?, secondary_trait2 = ?, secondary_trait3 = ?
        WHERE id = ?
    """, (secondary_trait1, secondary_trait2, secondary_trait3, dragon_id))

# Commit the changes and close the connection
conn_2.commit()
conn_2.close()
