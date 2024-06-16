import sqlite3
### i commented out the important part so i dont oopsy click this ever. 
def delete_hatcheddragons_table():
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS hatcheddragons")

    conn.commit()
    conn.close()

    print("hatcheddragons table deleted successfully.")

if __name__ == "__main__":
    ####delete_hatcheddragons_table()
