import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
INITIAL_TREE_SIZE, FINAL_TREE_SIZE = (50, 50), (80, 80)
PLAYABLE_HEIGHT = 540
GROWTH_TIME, HARVEST_TIME, RESPAWN_TIME = 5, 10, 5
CORNER_RADIUS, MAX_HARVESTS = 20, 5
BLUE, WHITE, GREEN, RED, BLACK = (0, 0, 255), (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0)
FRUIT_SIZE = (45, 45)

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fairy Farm")
background = pygame.transform.scale(pygame.image.load("fairyfarm1.png"), (int(pygame.image.load("fairyfarm1.png").get_width() * PLAYABLE_HEIGHT / pygame.image.load("fairyfarm1.png").get_height()), PLAYABLE_HEIGHT))

def load_images():
    def create_rounded_mask(size, radius):
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, WHITE, pygame.Rect(0, 0, *size), border_radius=radius)
        return mask

    def apply_rounded_mask(image, mask):
        image_with_mask = image.copy()
        image_with_mask.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image_with_mask

    def load_rounded_image(image_path, size, radius):
        image = pygame.transform.scale(pygame.image.load(image_path), size)
        mask = create_rounded_mask(size, radius)
        return apply_rounded_mask(image, mask)

    tree_imgs = [load_rounded_image(f"tree{i}.png", INITIAL_TREE_SIZE, CORNER_RADIUS) for i in range(5)]
    fruit_imgs = {name: pygame.transform.scale(pygame.image.load(f"{name}.png"), FRUIT_SIZE) for name in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}
    return tree_imgs, fruit_imgs

tree_images, fruit_images = load_images()
tree_fruit_pairs = [(tree_images[i], fruit_images[name]) for i, name in enumerate(["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"])]
weighted_trees = [0] * 12 + [1] * 2 + [2] * 2 + [3] * 5 + [4]
plants = []

class Plant:
    def __init__(self, tree, fruit, pos):
        self.tree, self.fruit, self.pos = tree, fruit, pos
        self.planted_time, self.size = time.time(), INITIAL_TREE_SIZE
        self.harvested, self.harvest_count, self.respawn_start_time = False, 0, None
        self.countdown, self.fruit_visible, self.fruit_positions = RESPAWN_TIME, False, []

    def update(self):
        elapsed_time = time.time() - self.planted_time
        if elapsed_time >= GROWTH_TIME:
            self.size = FINAL_TREE_SIZE
            if elapsed_time >= HARVEST_TIME and not self.harvested:
                self.fruit_visible = True
                if not self.fruit_positions:
                    tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
                    self.fruit_positions = [(tree_pos[0] + random.randint(0, self.size[0] - FRUIT_SIZE[0]), tree_pos[1] + random.randint(0, self.size[1] - FRUIT_SIZE[1])) for _ in range(self.harvest_count + 1)]

        if self.harvested and self.respawn_start_time:
            time_since_harvest = time.time() - self.respawn_start_time
            self.countdown = max(0, RESPAWN_TIME - int(time_since_harvest))
            if time_since_harvest >= RESPAWN_TIME:
                self.harvested, self.fruit_visible, self.fruit_positions = False, True, []
                self.harvest_count += 1

    def draw(self, screen):
        tree_image = pygame.transform.scale(self.tree, self.size)
        tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
        screen.blit(tree_image, tree_pos)
        if self.fruit_visible:
            for fruit_pos in self.fruit_positions:
                screen.blit(self.fruit, fruit_pos)
        elif self.harvested and self.harvest_count < MAX_HARVESTS:
            draw_text(screen, str(self.countdown), 24, self.pos[0], self.pos[1] - 50, GREEN)

    def is_clicked(self, mouse_pos):
        return pygame.Rect(self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2, self.size[0], self.size[1]).collidepoint(mouse_pos)

def is_position_valid(pos, existing_plants, radius=50):
    return all(((pos[0] - plant.pos[0]) ** 2 + (pos[1] - plant.pos[1]) ** 2) ** 0.5 >= radius for plant in existing_plants)

class Player:
    def __init__(self):
        self.inventory = {fruit: 0 for fruit in fruit_images}
        self.inventory["gleamberry"] = max(5, self.inventory["gleamberry"])
        self.selected_fruit = "gleamberry"

    def collect_fruit(self, fruit):
        self.inventory[fruit] += 1

    def remove_selected_fruit(self):
        if self.inventory[self.selected_fruit] > 0:
            self.inventory[self.selected_fruit] -= 1

    def set_selected_fruit(self, fruit):
        if fruit in self.inventory:
            self.selected_fruit = fruit

player = Player()

def draw_inventory(surface, player):
    pygame.draw.rect(surface, BLUE, (0, PLAYABLE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYABLE_HEIGHT))
    x_offset, y_offset = 10, PLAYABLE_HEIGHT + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, WHITE)
        if fruit == player.selected_fruit:
            pygame.draw.rect(surface, RED, (x_offset - 5, y_offset - 5, 50, 50), 2)
        x_offset += 50

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    surface.blit(font.render(text, True, color), font.render(text, True, color).get_rect(midtop=(x, y)))

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1 and mouse_pos[1] <= PLAYABLE_HEIGHT:
                if is_position_valid(mouse_pos, plants):
                    if player.inventory[player.selected_fruit] > 0:
                        tree, fruit = tree_fruit_pairs[random.choice(weighted_trees)]
                        plants.append(Plant(tree, fruit, mouse_pos))
                        player.remove_selected_fruit()
            elif event.button == 3:
                x_offset, selected = 10, False
                for fruit in fruit_images.keys():
                    if x_offset <= mouse_pos[0] <= x_offset + FRUIT_SIZE[0] and PLAYABLE_HEIGHT + 10 <= mouse_pos[1] <= PLAYABLE_HEIGHT + FRUIT_SIZE[1] + 10:
                        player.set_selected_fruit(fruit)
                        selected = True
                        break
                    x_offset += 50
                if not selected:
                    for plant in plants:
                        if plant.is_clicked(mouse_pos) and plant.fruit_visible:
                            for _ in plant.fruit_positions:
                                player.collect_fruit(list(fruit_images.keys())[tree_images.index(plant.tree)])
                            plant.fruit_visible, plant.harvested = False, True
                            plant.respawn_start_time = time.time()
                            if plant.harvest_count >= MAX_HARVESTS:
                                plants.remove(plant)
                            break
    return True

def update_game():
    for plant in plants:
        plant.update()

def render_game():
    screen.fill(BLACK)
    screen.blit(background, ((SCREEN_WIDTH - background.get_width()) // 2, 0))
    for plant in plants:
        plant.draw(screen)
    draw_inventory(screen, player)
    pygame.display.flip()

running = True
while running:
    running = handle_events()
    update_game()
    render_game()

pygame.quit()
sys.exit()
