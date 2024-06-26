import random
import sqlite3

class Dragon:
    def __init__(self, filename, primary_characteristic, secondary_traits, nurture_trait, name):
        self.id = self.parse_id(filename)
        self.filename = filename
        self.type = self.parse_type(filename)
        self.name = name
        self.primary_characteristic = primary_characteristic
        self.secondary_trait1 = secondary_traits[0]
        self.secondary_trait2 = secondary_traits[1]
        self.secondary_trait3 = secondary_traits[2]
        self.Nurture = nurture_trait
        self.current_hitpoints = 1000
        self.max_hitpoints = 1000
        self.rgb_value_range = self.set_rgb_value_range()

    @staticmethod
    def parse_id(filename):
        return int(''.join(filter(str.isdigit, filename)))

    @staticmethod
    def parse_type(filename):
        return ''.join(filter(str.isalpha, filename.split('.')[0]))

    def set_rgb_value_range(self):
        if 'gold' in self.type:
            return '(204-255, 204-255, 204-255)'
        elif 'silver' in self.type:
            return '(204-255, 204-255, 204-255)'
        else:
            return '(0-255, 0-255, 0-255)'

def define_dragon_traits(filenames, names):
    primary_traits = [
        "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
        "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
        "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
        "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
    ]

    secondary_traits_list = [
        "Dark", "Brooding", "Responsible", "Common",
        "Distraction", "Fierce", "Fiery", "Showy",
        "Speed", "Flightiness", "Drive", "Ambition",
        "Earthy", "Pragmatic", "Stout", "Loyal",
        "Angelic", "Unique", "Pure", "Self-righteous"
    ]

    nurture_traits = ['Hot-tempered', 'Independent', 'Bestial', 'Musical']

    dragon_traits = []
    for filename, name in zip(filenames, names):
        primary_characteristic = random.choice(primary_traits)
        secondary_traits = random.choices(secondary_traits_list, k=3)
        nurture_trait = random.choice(nurture_traits)
        dragon = Dragon(filename, primary_characteristic, secondary_traits, nurture_trait, name)
        dragon_traits.append(dragon)
    
    return dragon_traits

# Filenames from 168 to 184
filenames = [
    'rainbow168.png', 'metal169.png', 'metal170.png', 'metal171.png', 
    'metal172.png', 'metal173.png', 'rainbow174.png', 'metal175.png', 
    'metal176.png', 'metal177.png', 'metal178.png', 'metal179.png', 
    'metal180.png', 'metal181.png', 'rainbow182.png', 'rainbow183.png', 
    'metal184.png'
]

# Names from 168 to 184
names = [
    'Flair', 'Xara', 'Berry', 'Wave', 'Hazel', 'Glade', 'Xena', 'Quince',
    'Yara', 'Gale', 'Yuri', 'Zara', 'Jet', 'Elara', 'Myth', 'Jewel', 'Luna'
]

# Generate traits for dragons
assigned_dragons = define_dragon_traits(filenames, names)

# Check if all required dragons are prepared
if len(assigned_dragons) == len(filenames):
    print("All required dragons are prepared.")
else:
    print(f"Only {len(assigned_dragons)} dragons are prepared. Please check the data preparation step.")

# Function to insert dragons into the database with logging
def insert_dragons_to_db(dragons, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL query to insert data into the specified columns
    insert_query = '''
        INSERT INTO dragons (
            id, filename, type, name, primary_characteristic, 
            secondary_trait1, secondary_trait2, secondary_trait3, 
            Nurture, current_hitpoints, max_hitpoints, rgb_value_range
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Prepare data for insertion
    dragon_data = [
        (
            dragon.id, dragon.filename, dragon.type, dragon.name, dragon.primary_characteristic,
            dragon.secondary_trait1, dragon.secondary_trait2, dragon.secondary_trait3,
            dragon.Nurture, dragon.current_hitpoints, dragon.max_hitpoints,
            dragon.rgb_value_range
        )
        for dragon in dragons
    ]
    
    # Execute the insertion and log errors
    errors = []
    for data in dragon_data:
        try:
            cursor.execute(insert_query, data)
        except sqlite3.IntegrityError as e:
            errors.append((data[0], str(e)))
    
    conn.commit()
    conn.close()
    
    if errors:
        print("Errors encountered during insertion:")
        for error in errors:
            print(f"ID {error[0]}: {error[1]}")
    else:
        print("All records inserted successfully.")

# Ensure all required dragons are prepared before accessing the database
if len(assigned_dragons) == len(filenames):
    # Path to the database
    db_path = 'dragonsedit.db'

    # Insert the generated dragon data into the database
    insert_dragons_to_db(assigned_dragons, db_path)
else:
    print("Error: Not all required dragons are prepared. Please check the data preparation step.")
