import sqlite3

# Connect to the database
conn = sqlite3.connect('dragonsedit.db')
cursor = conn.cursor()

# Create the quests table
cursor.execute('''
CREATE TABLE IF NOT EXISTS quests (
    ID INTEGER PRIMARY KEY,
    Category TEXT NOT NULL,
    ChallengeRating INTEGER NOT NULL,
    Description TEXT NOT NULL,
    Special TEXT,
    Reward TEXT,
    Reset DATE NOT NULL
)
''')

# Insert the first entry
cursor.execute('''
INSERT INTO quests (ID, Category, ChallengeRating, Description, Special, Reward, Reset)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', (1, 'daily', 2, 'Weigh-in', 'none', 'none', '2024-06-21'))

# Commit the changes and close the connection
conn.commit()
conn.close()
