import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INITIAL_TREE_SIZE = (50, 50)  # Initial size for trees
FINAL_TREE_SIZE = (80, 80)  # Final size for mature trees
PLAYABLE_HEIGHT = 540  # Leave space for inventory at the bottom
GROWTH_TIME = 5  # Time in seconds for plants to grow
HARVEST_TIME = 10  # Time in seconds for plants to be ready for harvest
RESPAWN_TIME = 5  # Time in seconds for fruit to respawn
CORNER_RADIUS = 20  # Radius for rounding corners
MAX_HARVESTS = 5  # Maximum number of harvests before tree disappears

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fairy Farm")

# Load and adjust background image
background = pygame.image.load("fairyfarm1.png")
background_width, background_height = background.get_size()
aspect_ratio = background_width / background_height
new_height = PLAYABLE_HEIGHT
new_width = int(aspect_ratio * new_height)
background = pygame.transform.scale(background, (new_width, new_height))

# Function to create a mask for rounded corners
def create_rounded_mask(size, radius):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (0, 0, 0, 0), (0, 0, *size))
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0] - radius, radius), radius)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, size[1] - radius), radius)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0] - radius, size[1] - radius), radius)
    pygame.draw.rect(mask, (255, 255, 255, 255), (radius, 0, size[0] - 2 * radius, size[1]))
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, radius, size[0], size[1] - 2 * radius))
    return mask

# Function to apply the rounded mask to an image
def apply_rounded_mask(image, mask):
    image_with_mask = image.copy()
    image_with_mask.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return image_with_mask

# Load and round the corners of tree images
def load_rounded_image(image_path, size, radius):
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, size)
    mask = create_rounded_mask(size, radius)
    rounded_image = apply_rounded_mask(image, mask)
    return rounded_image

tree_images = [load_rounded_image(f"tree{i}.png", INITIAL_TREE_SIZE, CORNER_RADIUS) for i in range(5)]
fruit_images = {
    "gleamberry": pygame.transform.scale(pygame.image.load("gleamberry.png"), (45, 45)),
    "shimmeringapple": pygame.transform.scale(pygame.image.load("shimmeringapple.png"), (45, 45)),
    "etherealpear": pygame.transform.scale(pygame.image.load("etherealpear.png"), (45, 45)),
    "flamefruit": pygame.transform.scale(pygame.image.load("flamefruit.png"), (45, 45)),
    "moonbeammelon": pygame.transform.scale(pygame.image.load("moonbeammelon.png"), (45, 45)),
}

# Pair trees with fruits
tree_fruit_pairs = [
    (tree_images[0], fruit_images["gleamberry"]),
    (tree_images[1], fruit_images["shimmeringapple"]),
    (tree_images[2], fruit_images["etherealpear"]),
    (tree_images[3], fruit_images["flamefruit"]),
    (tree_images[4], fruit_images["moonbeammelon"]),
]

# Weighted list for selecting trees
weighted_trees = (
    [0] * 12 +   # Gleamberry: 50% chance
    [1] * 2 +    # Shimmeringapple: 8% chance
    [2] * 2 +    # Etherealpear: 8% chance
    [3] * 5 +    # Flamefruit: 20% chance
    [4] * 1      # Moonbeammelon: 4% chance
)

# Game data
plants = []

# Plant class
class Plant:
    def __init__(self, tree, fruit, pos):
        self.tree = tree
        self.fruit = fruit
        self.pos = pos
        self.planted_time = time.time()
        self.size = INITIAL_TREE_SIZE
        self.harvested = False
        self.harvest_count = 0
        self.respawn_start_time = None
        self.countdown = RESPAWN_TIME
        self.fruit_visible = False
        self.fruit_positions = []

    def update(self):
        elapsed_time = time.time() - self.planted_time
        if elapsed_time >= GROWTH_TIME and elapsed_time < HARVEST_TIME:
            self.size = FINAL_TREE_SIZE
        elif elapsed_time >= HARVEST_TIME:
            self.size = FINAL_TREE_SIZE
            if not self.harvested:
                self.fruit_visible = True
                if not self.fruit_positions:
                    tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
                    self.fruit_positions = [
                        (tree_pos[0] + random.randint(0, self.size[0] - 45), tree_pos[1] + random.randint(0, self.size[1] - 45))
                        for _ in range(self.harvest_count + 1)
                    ]

        if self.harvested and self.respawn_start_time:
            time_since_harvest = time.time() - self.respawn_start_time
            self.countdown = max(0, RESPAWN_TIME - int(time_since_harvest))
            if time_since_harvest >= RESPAWN_TIME:
                self.harvested = False
                self.fruit_visible = True
                self.fruit_positions = []
                self.harvest_count += 1

    def draw(self, screen):
        tree_image = pygame.transform.scale(self.tree, self.size)
        tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
        screen.blit(tree_image, tree_pos)
        if self.fruit_visible:
            for fruit_pos in self.fruit_positions:
                screen.blit(self.fruit, fruit_pos)
        elif self.harvested and self.harvest_count < MAX_HARVESTS:
            draw_text(screen, str(self.countdown), 24, self.pos[0], self.pos[1] - 50, (0, 255, 0))

    def is_clicked(self, mouse_pos):
        tree_rect = pygame.Rect(self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2, self.size[0], self.size[1])
        return tree_rect.collidepoint(mouse_pos)

def is_position_valid(pos, existing_plants, radius=50):
    for plant in existing_plants:
        plant_pos = plant.pos
        distance = ((pos[0] - plant_pos[0]) ** 2 + (pos[1] - plant_pos[1]) ** 2) ** 0.5
        if distance < radius:
            return False
    return True

# Player class
class Player:
    def __init__(self):
        self.inventory = {fruit: 0 for fruit in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}
        self.inventory["gleamberry"] = max(5, self.inventory["gleamberry"])
        self.selected_fruit = "gleamberry"  # Default selected fruit for planting

    def collect_fruit(self, fruit):
        self.inventory[fruit] += 1

    def remove_selected_fruit(self):
        if self.inventory[self.selected_fruit] > 0:
            self.inventory[self.selected_fruit] -= 1

    def set_selected_fruit(self, fruit):
        if fruit in self.inventory:
            self.selected_fruit = fruit

player = Player()

# Function to draw the inventory
def draw_inventory(surface, player):
    pygame.draw.rect(surface, (0, 0, 255), (0, PLAYABLE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYABLE_HEIGHT))
    x_offset, y_offset = 10, PLAYABLE_HEIGHT + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, (255, 255, 255))
        if fruit == player.selected_fruit:
            pygame.draw.rect(surface, (255, 0, 0), (x_offset - 5, y_offset - 5, 50, 50), 2)  # Highlight selected fruit
        x_offset += 50

# Function to draw text on the screen
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] <= PLAYABLE_HEIGHT:
                if event.button == 1:  # Left click for planting
                    if is_position_valid(mouse_pos, plants):
                        if player.inventory[player.selected_fruit] > 0:
                            selected_tree = random.choice(weighted_trees)
                            tree, fruit = tree_fruit_pairs[selected_tree]
                            plants.append(Plant(tree, fruit, mouse_pos))
                            player.remove_selected_fruit()
            if event.button == 3:
                x_offset = 10
                selected = False
                for fruit in fruit_images.keys():
                    if x_offset <= mouse_pos[0] <= x_offset + 45 and PLAYABLE_HEIGHT + 10 <= mouse_pos[1] <= PLAYABLE_HEIGHT + 55:
                        player.set_selected_fruit(fruit)
                        selected = True
                        break
                    x_offset += 50
                if not selected:
                    for plant in plants:
                        if plant.is_clicked(mouse_pos) and plant.fruit_visible:
                            fruit_name = list(fruit_images.keys())[tree_images.index(plant.tree)]
                            for _ in plant.fruit_positions:
                                player.collect_fruit(fruit=fruit_name)
                            plant.fruit_visible = False
                            plant.harvested = True
                            plant.respawn_start_time = time.time()
                            if plant.harvest_count >= MAX_HARVESTS:
                                plants.remove(plant)
                            break

    # Update plants
    for plant in plants:
        plant.update()

    # Draw the background
    screen.fill((0, 0, 0))  # Clear the screen with black color
    background_x = (SCREEN_WIDTH - new_width) // 2  # Center the background horizontally
    screen.blit(background, (background_x, 0))

    # Draw the plants
    for plant in plants:
        plant.draw(screen)

    # Draw the inventory
    draw_inventory(screen, player)

    pygame.display.flip()

pygame.quit()
sys.exit()
