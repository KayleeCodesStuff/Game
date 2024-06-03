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
growth_time = 5  # Time in seconds for plants to grow
harvest_time = 10  # Time in seconds for plants to be ready for harvest

# Plant class
class Plant:
    def __init__(self, tree, fruit, pos):
        self.tree = tree
        self.fruit = fruit
        self.pos = pos
        self.planted_time = time.time()
        self.size = INITIAL_TREE_SIZE
        self.harvested = False

    def update(self):
        elapsed_time = time.time() - self.planted_time
        if elapsed_time >= growth_time and elapsed_time < harvest_time:
            self.size = FINAL_TREE_SIZE
        elif elapsed_time >= harvest_time:
            self.size = FINAL_TREE_SIZE
            self.harvested = True

    def draw(self, screen):
        tree_image = pygame.transform.scale(self.tree, self.size)
        tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
        screen.blit(tree_image, tree_pos)
        if self.harvested:
            fruit_pos = (tree_pos[0] + self.size[0] // 2 - 22, tree_pos[1] - 20)  # Adjust fruit positions relative to trees
            screen.blit(self.fruit, fruit_pos)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
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

    pygame.display.flip()

pygame.quit()
sys.exit()
