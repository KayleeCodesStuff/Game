import pygame
import random
import sys
import sqlite3

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Load images
fruit_images_dict = {
    "gleamberry": pygame.transform.scale(pygame.image.load("gleamberry.png"), (50, 50)),
    "flamefruit": pygame.transform.scale(pygame.image.load("flamefruit.png"), (50, 50)),
    "shimmeringapple": pygame.transform.scale(pygame.image.load("shimmeringapple.png"), (50, 50)),
    "etherealpear": pygame.transform.scale(pygame.image.load("etherealpear.png"), (50, 50)),
    "moonbeammelon": pygame.transform.scale(pygame.image.load("moonbeammelon.png"), (50, 50))
}

egg_images_dict = {
    "Black": pygame.transform.scale(pygame.image.load("black_egg.png"), (50, 50)),
    "White": pygame.transform.scale(pygame.image.load("white_egg.png"), (50, 50)),
    "Rainbow": pygame.transform.scale(pygame.image.load("rainbow_egg.png"), (50, 50)),
    "Metallic": pygame.transform.scale(pygame.image.load("metallic_egg.png"), (50, 50))
}

# Initialize inventory and egg counts
fruit_names = list(fruit_images_dict.keys())
inventory = {fruit: 5 for fruit in fruit_names}
egg_counts = {egg: 0 for egg in egg_images_dict.keys()}

# Inventory slots
inventory_slots = [None] * 10

# Create inventory slots
inventory_boxes = [pygame.Rect(WIDTH - (60 * (i + 1)), HEIGHT - 100, 50, 50) for i in range(10)]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

def draw_text(surface, text, font, color, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_inventory(surface, inventory, eggs, inventory_slots, selected_inventory_slot=None):
    pygame.draw.rect(surface, BLUE, (0, HEIGHT - 100, WIDTH, 100))

    y_offset = HEIGHT - 90

    # Draw the fruits in the first section
    x_offset = 10
    for fruit, image in fruit_images_dict.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(inventory[fruit]), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw a separator line
    pygame.draw.line(surface, WHITE, (x_offset, HEIGHT - 100), (x_offset, HEIGHT))

    # Draw the eggs in the second section
    x_offset += 10
    for egg_type, count in eggs.items():
        egg_image = egg_images_dict[egg_type]
        surface.blit(egg_image, (x_offset, y_offset))
        draw_text(surface, str(count), small_font, WHITE, (x_offset + 20, y_offset + 45))
        x_offset += 60

    # Draw the elixirs in the third section
    x_offset = WIDTH - 60 * len(inventory_slots)
    for i, slot in enumerate(inventory_slots):
        box_rect = pygame.Rect(x_offset, y_offset, 50, 50)
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)
        if slot is None:
            draw_text(surface, "?", small_font, WHITE, (x_offset + 15, y_offset + 15))
        else:
            color, image_filename = slot
            pygame.draw.rect(surface, color, box_rect)
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (50, 50))
            surface.blit(image, (x_offset, y_offset))
        x_offset += 60
        if i == selected_inventory_slot:
            pygame.draw.rect(surface, RED, box_rect, 3)

def draw_screen(selected_egg_index):
    screen.fill(BLACK)

    # Example background, replace as necessary
    # screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)
        pygame.draw.rect(screen, egg_colors[i], rect)
        screen.blit(egg_image, rect.topleft)

    draw_inventory(screen, inventory, egg_counts, inventory_slots)
    pygame.display.flip()

def load_inventory_data():
    global inventory, egg_counts, inventory_slots
    inventory = {fruit: 0 for fruit in fruit_names}
    egg_counts = {egg: 0 for egg in egg_images_dict.keys()}

    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fruit, count FROM inventory")
            rows = cursor.fetchall()
            for row in rows:
                fruit, count = row
                inventory[fruit] = count

            cursor.execute("SELECT phenotype, count FROM egg_inventory")
            rows = cursor.fetchall()
            for row in rows:
                phenotype, count = row
                egg_counts[phenotype] = count

            cursor.execute("SELECT rgb, image_file, position FROM elixirs")
            rows = cursor.fetchall()
            for row in rows:
                rgb = tuple(map(int, row[0][1:-1].split(', ')))
                image_file, position = row[1], row[2]
                inventory_slots[position - 1] = (rgb, image_file)

    except Exception as e:
        print(f"Error loading inventory data: {e}")

def generate_and_add_random_elixir():
    primary_trait = random.choice(primary_traits)
    secondary_traits = random.sample(secondary_traits_list, 3)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb_value = (r, g, b)
    for i in range(len(inventory_slots)):
        if inventory_slots[i] is None:
            image_file = "pb1.png"
            inventory_slots[i] = (rgb_value, image_file)
            elixir_data = {
                'rgb': rgb_value,
                'title': f"{primary_trait} Elixir",
                'primary_trait': primary_trait,
                'secondary_traits': secondary_traits,
                'image_file': image_file,
                'position': i + 1
            }
            save_elixir_data('save.db', elixir_data, inventory)
            break

def save_elixir_data(file_path, elixir_data, fruit_counts):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO elixirs (rgb, title, primary_trait, secondary_traits, image_file, position)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (str(elixir_data['rgb']), elixir_data['title'], elixir_data['primary_trait'],
                    ', '.join(elixir_data['secondary_traits']), elixir_data['image_file'], elixir_data['position']))

    for fruit, count in fruit_counts.items():
        cursor.execute('''INSERT INTO inventory (fruit, count)
                          VALUES (?, ?)
                          ON CONFLICT(fruit) DO UPDATE SET count = excluded.count''', (fruit, count))

    conn.commit()
    conn.close()

def save_inventory_data():
    try:
        with sqlite3.connect('save.db') as conn:
            cursor = conn.cursor()
            for fruit, count in inventory.items():
                cursor.execute("UPDATE inventory SET count = ? WHERE fruit = ?", (count, fruit))
            for egg, count in egg_counts.items():
                cursor.execute("UPDATE egg_inventory SET count = ? WHERE phenotype = ?", (count, egg))
            cursor.execute("DELETE FROM elixirs")
            for i, slot in enumerate(inventory_slots):
                if slot is not None:
                    rgb, image_file = slot
                    cursor.execute("INSERT INTO elixirs (rgb, image_file, position) VALUES (?, ?, ?)", (str(rgb), image_file, i + 1))
            conn.commit()
    except Exception as e:
        print(f"Error saving inventory data: {e}")

def main():
    global elixir_color
    elixir_color = None
    running = True
    selected_egg_index = None

    load_inventory_data()

    if all(slot is None for slot in inventory_slots):
        generate_and_add_random_elixir()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                print(f"Mouse clicked at: {event.pos}")
                egg_selected = False
                for j, egg_rect in enumerate(egg_positions):
                    if egg_rect.collidepoint(x, y):
                        selected_egg_index = j
                        egg_selected = True
                        print(f"Egg {j} selected at position {egg_rect.topleft}")
                        break

                if not egg_selected:
                    for i, rect in enumerate(inventory_boxes):
                        if rect.collidepoint(x, y) and inventory_slots[i] is not None:
                            selected_elixir = inventory_slots[i]
                            elixir_color = selected_elixir[0]
                            if selected_egg_index is not None:
                                egg_colors[selected_egg_index] = elixir_color
                                inventory_slots[i] = None
                                elixir_color = None
                                selected_egg_index = None
                            break

        draw_screen(selected_egg_index)

    save_inventory_data()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
