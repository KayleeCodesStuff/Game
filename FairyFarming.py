import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INITIAL_TREE_SIZE = (50, 50)  # Initial size for trees
FINAL_TREE_SIZE = (100, 100)  # Final size for trees
PLAYABLE_HEIGHT = 540  # Leave space for inventory at the bottom
GROWTH_TIME = 5  # Time in seconds for plants to grow
HARVEST_TIME = 10  # Time in seconds for plants to be ready for harvest
RESPAWN_TIME = 5  # Time in seconds for fruit to respawn

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fairy Farm")

# Load images
background = pygame.image.load("fairyfarm1.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

tree_images = [pygame.transform.scale(pygame.image.load(f"tree{i}.png"), INITIAL_TREE_SIZE) for i in range(5)]
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

    def update(self):
        elapsed_time = time.time() - self.planted_time
        if elapsed_time >= GROWTH_TIME and elapsed_time < HARVEST_TIME:
            self.size = FINAL_TREE_SIZE
        elif elapsed_time >= HARVEST_TIME:
            self.size = FINAL_TREE_SIZE
            if not self.harvested:
                self.fruit_visible = True

        if self.harvested and self.respawn_start_time:
            time_since_harvest = time.time() - self.respawn_start_time
            self.countdown = max(0, RESPAWN_TIME - int(time_since_harvest))
            if time_since_harvest >= RESPAWN_TIME:
                self.harvested = False
                self.fruit_visible = True
                self.harvest_count += 1
                if self.harvest_count >= 5:
                    plants.remove(self)

    def draw(self, screen):
        tree_image = pygame.transform.scale(self.tree, self.size)
        tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
        screen.blit(tree_image, tree_pos)
        if self.fruit_visible:
            fruit_pos = (tree_pos[0] + self.size[0] // 2 - 22, tree_pos[1] - 20)
            screen.blit(self.fruit, fruit_pos)
        elif self.harvested and self.harvest_count < 5:
            draw_text(screen, str(self.countdown), 24, self.pos[0], self.pos[1] - 50, (0, 255, 0))

    def is_clicked(self, mouse_pos):
        tree_rect = pygame.Rect(self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2, self.size[0], self.size[1])
        return tree_rect.collidepoint(mouse_pos)

# Player class
class Player:
    def __init__(self):
        self.inventory = {fruit: 0 for fruit in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}

    def collect_fruit(self, fruit):
        self.inventory[fruit] += 1

player = Player()

# Function to draw the inventory
def draw_inventory(surface, player):
    pygame.draw.rect(surface, (0, 0, 255), (0, PLAYABLE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYABLE_HEIGHT))
    x_offset, y_offset = 10, PLAYABLE_HEIGHT + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, (255, 255, 255))
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
                for plant in plants:
                    if plant.is_clicked(mouse_pos) and plant.fruit_visible:
                        player.collect_fruit(fruit=list(fruit_images.keys())[tree_images.index(plant.tree)])
                        plant.fruit_visible = False
                        plant.harvested = True
                        plant.respawn_start_time = time.time()
                        break
                else:
                    tree, fruit = tree_fruit_pairs[len(plants) % len(tree_fruit_pairs)]
                    plants.append(Plant(tree, fruit, mouse_pos))

    # Update plants
    for plant in plants:
        plant.update()

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw the plants
    for plant in plants:
        plant.draw(screen)

    # Draw the inventory
    draw_inventory(screen, player)

    pygame.display.flip()

pygame.quit()
sys.exit()
