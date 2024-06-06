import pygame
import random
import sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon Hatchery")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Load images
background = pygame.image.load("hatchery.png").convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
egg_image = pygame.image.load("unhatched.png").convert_alpha()

# Resize egg images and create egg rectangles with increased spacing
egg_image = pygame.transform.scale(egg_image, (80, 80))
egg_positions = []
egg_colors = [WHITE] * 10  # Initialize each egg's color to WHITE

# Function to check for overlapping rectangles
def is_overlapping(new_rect, rect_list):
    for rect in rect_list:
        if new_rect.colliderect(rect):
            return True
    return False

# Create non-overlapping egg positions with increased padding
while len(egg_positions) < 10:
    pos = (random.randint(50, WIDTH - 300), random.randint(50, HEIGHT - 500))
    new_rect = pygame.Rect(pos, (80, 80))
    if not is_overlapping(new_rect, egg_positions):
        egg_positions.append(new_rect)

# Inventory slots
inventory_slots = [None] * 10

# Create inventory slots
inventory_boxes = [pygame.Rect(20 + i * 60, HEIGHT - 100, 50, 50) for i in range(10)]

# Create font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Primary traits
primary_traits = [
    "Curious", "Playful", "Adventurous", "Resourceful", "Sociable",
    "Thoughtful", "Confident", "Generous", "Reflective", "Strategic",
    "Cheerful", "Demonic", "Mystical", "Flamboyant", "Awkward",
    "Weird", "Gross", "Gorgeous", "Ethereal", "Blessed"
]

# Combined secondary traits list from mixalator
secondary_traits_list = [
    "Dark", "Brooding", "Responsible", "Common",
    "Distraction", "Fierce", "Fiery", "Showy",
    "Speed", "Flightiness", "Drive", "Ambition",
    "Earthy", "Pragmatic", "Stout", "Loyal",
    "Angelic", "Unique", "Pure", "Self-righteous"
]

# Function to generate a random elixir
def generate_random_elixir():
    primary_trait = random.choice(primary_traits)
    secondary_traits = random.sample(secondary_traits_list, 3)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb_value = (r, g, b)
    return primary_trait, secondary_traits, rgb_value

# Function to draw the inventory
def draw_inventory(surface, inventory):
    pygame.draw.rect(surface, BLUE, (0, HEIGHT - 100, WIDTH, 100))

    for i, slot in enumerate(inventory_slots):
        if slot is None:
            pygame.draw.rect(surface, BLACK, inventory_boxes[i])
        else:
            color, image_filename = slot
            pygame.draw.rect(surface, color, inventory_boxes[i])
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (50, 50))
            surface.blit(image, (inventory_boxes[i].x, inventory_boxes[i].y))

def draw_screen(selected_egg_index):
    screen.fill(BLACK)
    screen.blit(background, (0, 0))

    for i, rect in enumerate(egg_positions):
        if i == selected_egg_index:
            pygame.draw.rect(screen, RED, rect.inflate(4, 4), 2)  # Draw red outline
        pygame.draw.rect(screen, egg_colors[i], rect)  # Draw the egg with its current color
        screen.blit(egg_image, rect.topleft)

    draw_inventory(screen, inventory_slots)

    pygame.display.flip()

def main():
    global elixir_color
    elixir_color = None  # Initialize elixir_color
    running = True
    selected_egg_index = None

    # Generate a random elixir at the start of the game
    primary_trait, secondary_traits, rgb_value = generate_random_elixir()
    inventory_slots[0] = (rgb_value, "pb1.png")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Check if an egg was clicked
                egg_selected = False
                for j, egg_rect in enumerate(egg_positions):
                    if egg_rect.collidepoint(x, y):
                        # Select the clicked egg
                        selected_egg_index = j
                        egg_selected = True
                        break

                if not egg_selected:
                    # Check if an inventory slot was clicked
                    for i, rect in enumerate(inventory_boxes):
                        if rect.collidepoint(x, y) and inventory_slots[i] is not None:
                            selected_elixir = inventory_slots[i]
                            elixir_color = selected_elixir[0]
                            if selected_egg_index is not None:
                                # Apply the elixir to the selected egg
                                egg_colors[selected_egg_index] = elixir_color
                                # Remove the elixir from the inventory
                                inventory_slots[i] = None
                                elixir_color = None
                                selected_egg_index = None  # Reset the selected egg index
                            break

        draw_screen(selected_egg_index)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
