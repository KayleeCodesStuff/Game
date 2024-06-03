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
UNPLAYABLE_HEIGHT = 40
CORNER_RADIUS, FRUIT_SIZE = 20, (45, 45)
BLUE, WHITE, GREEN, RED, BLACK, NEON_GREEN, PURPLE = (0, 0, 255), (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0), (57, 255, 20), (128, 0, 128)
NYX_SPEED = 5
NYX_DESPAWN_AFTER_SPAWN = 8  # Nyx despawn time after spawning
RIPPLE_SPEED = 1
LUMINARA_SPEED = 2
LUMINARA_COST = 25  # Updated cost
LUMINARA_MAX_FRUITS = 100
SPEED_BOOST_COST = 20  # Updated cost
LURE_COST = 15  # Updated cost
LURE_DURATION = 3
SPEED_BOOST_DURATION = 5
RIPPLE_COST = 75  # Updated cost
MAX_SPEED = 10
WIN_CONDITION = 50
LOSS_CONDITION = 50

# Colors for the trees
TREE_COLORS = [(128, 0, 128), (255, 192, 203), (0, 128, 128), (255, 165, 0), (0, 0, 255)]  # Purple, Pink, Teal, Orange, Blue

# Probabilities for each fruit
probabilities = {
    "gleamberry": [("gleamberry", 50), ("shimmeringapple", 12.5), ("etherealpear", 12.5), ("flamefruit", 20), ("moonbeammelon", 4)],
    "shimmeringapple": [("gleamberry", 12.5), ("shimmeringapple", 50), ("etherealpear", 12.5), ("flamefruit", 20), ("moonbeammelon", 4)],
    "etherealpear": [("gleamberry", 12.5), ("shimmeringapple", 12.5), ("etherealpear", 50), ("flamefruit", 20), ("moonbeammelon", 4)],
    "flamefruit": [("gleamberry", 20), ("shimmeringapple", 12.5), ("etherealpear", 12.5), ("flamefruit", 50), ("moonbeammelon", 4)],
    "moonbeammelon": [("gleamberry", 4), ("shimmeringapple", 12.5), ("etherealpear", 12.5), ("flamefruit", 20), ("moonbeammelon", 50)]
}

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
        image = pygame.image.load(image_path)
        aspect_ratio = image.get_width() / image.get_height()
        if aspect_ratio > 1:
            size = (size[0], int(size[0] / aspect_ratio))
        else:
            size = (int(size[1] * aspect_ratio), size[1])
        image = pygame.transform.scale(image, size)
        mask = create_rounded_mask(size, radius)
        return apply_rounded_mask(image, mask)

    tree_imgs = [load_rounded_image(f"tree{i}.png", INITIAL_TREE_SIZE, CORNER_RADIUS) for i in range(5)]
    fruit_imgs = {name: pygame.transform.scale(pygame.image.load(f"{name}.png"), FRUIT_SIZE) for name in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}
    nyx_img = pygame.transform.scale(pygame.image.load("nyx.png"), (60, 60))  # Assuming nyx.png is the image for Nyx
    ripple_img = pygame.transform.scale(pygame.image.load("ripple2.png"), (40, 40))  # Assuming ripple2.png is the image for Ripple
    luminara_img = pygame.transform.scale(pygame.image.load("luminara.png"), (60, 60))  # Assuming luminara.png is the image for Luminara
    lure_img = pygame.transform.scale(pygame.image.load("flamefruit.png"), (FRUIT_SIZE[0] * 4, FRUIT_SIZE[1] * 4))  # Enlarged flamefruit image for lure
    return tree_imgs, fruit_imgs, nyx_img, ripple_img, luminara_img, lure_img

tree_images, fruit_images, nyx_img, ripple_img, luminara_img, lure_img = load_images()
tree_fruit_pairs = [(tree_images[i], fruit_images[name]) for i, name in enumerate(["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"])]

# Tree names for easy reference
tree_names = ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]

# Tree attributes
tree_attributes = [
    {"type": "Gleaming Berry", "mature_time": 5, "respawn_time": 5, "fruits_per_spawn": [1, 2, 3, 4, 5], "max_harvests": 5},
    {"type": "Shimmering Apple", "mature_time": 6, "respawn_time": 6, "fruits_per_spawn": [1, 2, 3, 3, 4], "max_harvests": 4},
    {"type": "Ethereal Pear", "mature_time": 7, "respawn_time": 7, "fruits_per_spawn": [1, 2, 2, 3, 3], "max_harvests": 3},
    {"type": "Flamefruit", "mature_time": 8, "respawn_time": 8, "fruits_per_spawn": [1, 2, 2, 2, 3], "max_harvests": 3},
    {"type": "Moonbeam Melon", "mature_time": 10, "respawn_time": 10, "fruits_per_spawn": [1, 2, 2, 2, 2], "max_harvests": 2},
]

plants = []
nyx = None  # Nyx is initially not present
ripple = None  # Ripple is initially not present
luminaras = []  # List to hold Luminara instances
temporary_ripples = []  # List to hold temporary Ripple instances
lures = []  # List to hold lure instances
nyx_melon_count = 0  # Nyx's melon count
luminara_melon_count = 0  # Luminara's melon count
game_over = False  # Game over state

class Ripple:
    def __init__(self):
        self.image = ripple_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.base_speed = RIPPLE_SPEED
        self.speed = self.base_speed
        self.speed_boost_timer = None
        self.target = None

    def update(self):
        if self.speed_boost_timer and time.time() >= self.speed_boost_timer:
            self.speed = self.base_speed
            self.speed_boost_timer = None

        closest_fruit = None
        closest_distance = float('inf')
        for plant in plants:
            if plant.fruit_visible:
                if plant.fruit == fruit_images["gleamberry"]:
                    distance = ((self.rect.centerx - plant.pos[0]) ** 2 + (self.rect.centery - plant.pos[1]) ** 2) ** 0.5
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_fruit = plant
        if not closest_fruit:
            for plant in plants:
                if plant.fruit_visible:
                    distance = ((self.rect.centerx - plant.pos[0]) ** 2 + (self.rect.centery - plant.pos[1]) ** 2) ** 0.5
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_fruit = plant

        self.target = closest_fruit

        if self.target:
            target_pos = self.target.pos
            dx, dy = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            for plant in plants:
                if plant.fruit_visible and plant.fruit_positions and self.rect.colliderect(pygame.Rect(plant.fruit_positions[0][0], plant.fruit_positions[0][1], FRUIT_SIZE[0], FRUIT_SIZE[1])):
                    while plant.fruit_positions:
                        plant.fruit_positions.pop(0)
                        inventory.collect_fruit(tree_names[tree_images.index(plant.tree)])
                    plant.fruit_visible = False
                    plant.harvested = True
                    plant.respawn_start_time = time.time()
                    if plant.harvest_count >= plant.max_harvests:
                        plants.remove(plant)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Nyx:
    def __init__(self):
        self.image = nyx_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 0))  # Spawn at top center
        self.speed = NYX_SPEED
        self.target = None
        self.is_spawned = False
        self.despawn_timer = None

    def update(self):
        if self.is_spawned:
            closest_fruit = None
            closest_distance = float('inf')
            for plant in plants:
                if plant.fruit_visible:
                    if plant.fruit == fruit_images["moonbeammelon"]:
                        closest_fruit = plant
                        break
                    else:
                        distance = ((self.rect.centerx - plant.pos[0]) ** 2 + (self.rect.centery - plant.pos[1]) ** 2) ** 0.5
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_fruit = plant

            # Check for lures
            for lure in lures:
                distance = ((self.rect.centerx - lure.rect.centerx) ** 2 + (self.rect.centery - lure.rect.centery) ** 2) ** 0.5
                if distance < closest_distance:
                    closest_distance = distance
                    closest_fruit = lure

            self.target = closest_fruit

            if self.target:
                target_pos = self.target.pos if isinstance(self.target, Plant) else self.target.rect.center
                dx, dy = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance != 0:
                    dx, dy = dx / distance, dy / distance
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed

                if isinstance(self.target, Plant) and self.rect.colliderect(pygame.Rect(target_pos[0], target_pos[1], FRUIT_SIZE[0], FRUIT_SIZE[1])):
                    if self.target.fruit_positions:
                        self.target.fruit_positions.pop(0)
                        global nyx_melon_count
                        nyx_melon_count += 1
                    if not self.target.fruit_positions:
                        self.target.fruit_visible = False
                        self.target.harvested = True
                        self.target.respawn_start_time = time.time()
                        if self.target.harvest_count >= self.target.max_harvests:
                            plants.remove(self.target)

            if self.despawn_timer and time.time() >= self.despawn_timer:
                self.is_spawned = False
                self.despawn_timer = None

    def draw(self, screen):
        if self.is_spawned:
            screen.blit(self.image, self.rect.topleft)

nyx = Nyx()  # Instantiate Nyx object
ripple = Ripple()  # Instantiate Ripple object

class Luminara:
    def __init__(self):
        self.image = luminara_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.base_speed = LUMINARA_SPEED
        self.speed = self.base_speed
        self.speed_boost_timer = None
        self.target = None
        self.collected_fruits = 0

    def update(self):
        if self.speed_boost_timer and time.time() >= self.speed_boost_timer:
            self.speed = self.base_speed
            self.speed_boost_timer = None

        closest_fruit = None
        closest_distance = float('inf')
        for plant in plants:
            if plant.fruit_visible:
                if plant.fruit == fruit_images["moonbeammelon"]:
                    closest_fruit = plant
                    break
                else:
                    distance = ((self.rect.centerx - plant.pos[0]) ** 2 + (self.rect.centery - plant.pos[1]) ** 2) ** 0.5
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_fruit = plant
        if not closest_fruit:
            for plant in plants:
                if plant.fruit_visible:
                    fruit_rarity = ["moonbeammelon", "etherealpear", "shimmeringapple", "flamefruit", "gleamberry"]
                    current_fruit_index = fruit_rarity.index(tree_names[tree_images.index(plant.tree)])
                    target_fruit_index = fruit_rarity.index(tree_names[tree_images.index(closest_fruit.tree)]) if closest_fruit else float('inf')
                    if current_fruit_index < target_fruit_index:
                        closest_fruit = plant
                    elif current_fruit_index == target_fruit_index:
                        distance = ((self.rect.centerx - plant.pos[0]) ** 2 + (self.rect.centery - plant.pos[1]) ** 2) ** 0.5
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_fruit = plant

        self.target = closest_fruit

        if self.target:
            target_pos = self.target.pos
            dx, dy = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            for plant in plants:
                if plant.fruit_visible and plant.fruit_positions and self.rect.colliderect(pygame.Rect(plant.fruit_positions[0][0], plant.fruit_positions[0][1], FRUIT_SIZE[0], FRUIT_SIZE[1])):
                    while plant.fruit_positions:
                        plant.fruit_positions.pop(0)
                        inventory.collect_fruit(tree_names[tree_images.index(plant.tree)])
                        self.collected_fruits += 1
                        global luminara_melon_count
                        if plant.fruit == fruit_images["moonbeammelon"]:
                            luminara_melon_count += 1
                    plant.fruit_visible = False
                    plant.harvested = True
                    plant.respawn_start_time = time.time()
                    if plant.harvest_count >= plant.max_harvests:
                        plants.remove(plant)

        if self.collected_fruits >= LUMINARA_MAX_FRUITS:
            luminaras.remove(self)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Lure:
    def __init__(self, pos):
        self.image = lure_img
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = time.time()

    def update(self):
        if time.time() - self.spawn_time >= LURE_DURATION:
            lures.remove(self)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

def check_melon_timers():
    for plant in plants:
        if plant.fruit == fruit_images["moonbeammelon"]:
            time_left = plant.mature_time + plant.respawn_time - (time.time() - plant.planted_time)
            if time_left <= NYX_DESPAWN_AFTER_SPAWN and not nyx.is_spawned:
                nyx.rect.center = (SCREEN_WIDTH // 2, 0)
                nyx.is_spawned = True
                nyx.despawn_timer = time.time() + NYX_DESPAWN_AFTER_SPAWN

def predict_next_tree(selected_fruit):
    global predicted_tree_type, next_tree_color
    predicted_tree_type = select_tree_based_on_probability(selected_fruit)
    next_tree_color = TREE_COLORS[tree_names.index(predicted_tree_type)]
    cursor_surface = create_cursor_surface(next_tree_color)
    pygame.mouse.set_visible(False)

def select_tree_based_on_probability(selected_fruit):
    tree_choices = probabilities[selected_fruit]
    total_weight = sum(weight for tree, weight in tree_choices)
    rand_val = random.uniform(0, total_weight)
    cumulative_weight = 0
    
    for tree, weight in tree_choices:
        cumulative_weight += weight
        if rand_val < cumulative_weight:
            return tree
    return tree_choices[-1][0]  # Default to the last tree type in case of rounding errors

def create_cursor_surface(color):
    cursor_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(cursor_surface, color, (16, 16), 16)
    return cursor_surface

class Plant:
    def __init__(self, tree, fruit, pos, attributes):
        self.tree, self.fruit, self.pos = tree, fruit, pos
        self.mature_time = attributes["mature_time"]
        self.respawn_time = attributes["respawn_time"]
        self.fruits_per_spawn = attributes["fruits_per_spawn"]
        self.max_harvests = attributes["max_harvests"]
        self.planted_time = time.time()
        self.size = INITIAL_TREE_SIZE
        self.harvested = False
        self.harvest_count = 0
        self.respawn_start_time = None
        self.countdown = self.respawn_time
        self.fruit_visible = False
        self.fruit_positions = []

    def update(self):
        elapsed_time = time.time() - self.planted_time
        if elapsed_time >= self.mature_time:
            self.size = FINAL_TREE_SIZE
            if elapsed_time >= self.mature_time + self.respawn_time and not self.harvested:
                self.fruit_visible = True
                if not self.fruit_positions:
                    tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
                    fruits_count = self.fruits_per_spawn[min(self.harvest_count, len(self.fruits_per_spawn) - 1)]
                    self.fruit_positions = [(tree_pos[0] + random.randint(0, self.size[0] - FRUIT_SIZE[0]), tree_pos[1] + random.randint(0, self.size[1] - FRUIT_SIZE[1])) for _ in range(fruits_count)]

        if self.harvested and self.respawn_start_time:
            time_since_harvest = time.time() - self.respawn_start_time
            self.countdown = max(0, self.respawn_time - int(time_since_harvest))
            if time_since_harvest >= self.respawn_time:
                self.harvested, self.fruit_visible, self.fruit_positions = False, True, []
                self.harvest_count += 1

    def draw(self, screen):
        tree_image = pygame.transform.scale(self.tree, self.size)
        tree_pos = (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2)
        screen.blit(tree_image, tree_pos)
        if self.fruit_visible:
            for fruit_pos in self.fruit_positions:
                screen.blit(self.fruit, fruit_pos)
        elif self.harvested and self.harvest_count < self.max_harvests:
            draw_text(screen, str(self.countdown), 24, self.pos[0], self.pos[1] - 50, GREEN)

    def is_clicked(self, mouse_pos):
        return pygame.Rect(self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2, self.size[0], self.size[1]).collidepoint(mouse_pos)

def is_position_valid(pos, existing_plants, radius=50):
    return all(((pos[0] - plant.pos[0]) ** 2 + (pos[1] - plant.pos[1]) ** 2) ** 0.5 >= radius for plant in existing_plants)

class Inventory:
    def __init__(self):
        self.items = {fruit: 0 for fruit in fruit_images}
        self.items["gleamberry"] = 5
        self.selected_fruit = "gleamberry"
        predict_next_tree(self.selected_fruit)  # Initialize the prediction

    def collect_fruit(self, fruit):
        self.items[fruit] += 1

    def remove_selected_fruit(self):
        if self.items[self.selected_fruit] > 0:
            self.items[self.selected_fruit] -= 1

    def set_selected_fruit(self, fruit):
        if fruit in self.items:
            self.selected_fruit = fruit
            predict_next_tree(fruit)

inventory = Inventory()  # Ensure this is instantiated before the main loop

def draw_inventory(surface, inventory):
    pygame.draw.rect(surface, BLUE, (0, PLAYABLE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYABLE_HEIGHT))
    x_offset, y_offset = 10, PLAYABLE_HEIGHT + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(inventory.items[fruit]), 18, x_offset + 30, y_offset, WHITE)
        if fruit == inventory.selected_fruit:
            pygame.draw.rect(surface, RED, (x_offset - 5, y_offset - 5, 50, 50), 2)
        x_offset += 50

    # Draw the Luminara spawn button
    luminara_button_rect = pygame.Rect(SCREEN_WIDTH - 120, PLAYABLE_HEIGHT + 10, 110, 50)
    pygame.draw.rect(surface, GREEN, luminara_button_rect)
    draw_text(surface, "Luminara", 18, luminara_button_rect.centerx, luminara_button_rect.y + 5, BLACK)
    draw_text(surface, f"{LUMINARA_COST} Pears", 18, luminara_button_rect.centerx, luminara_button_rect.y + 25, BLACK)

    # Draw the Speed Boost button
    speed_boost_button_rect = pygame.Rect(SCREEN_WIDTH - 240, PLAYABLE_HEIGHT + 10, 110, 50)
    pygame.draw.rect(surface, GREEN, speed_boost_button_rect)
    draw_text(surface, "Speed", 18, speed_boost_button_rect.centerx, speed_boost_button_rect.y + 5, BLACK)
    draw_text(surface, f"{SPEED_BOOST_COST} Apples", 18, speed_boost_button_rect.centerx, speed_boost_button_rect.y + 25, BLACK)

    # Draw the Lure button
    lure_button_rect = pygame.Rect(SCREEN_WIDTH - 360, PLAYABLE_HEIGHT + 10, 110, 50)
    pygame.draw.rect(surface, GREEN, lure_button_rect)
    draw_text(surface, "Lure", 18, lure_button_rect.centerx, lure_button_rect.y + 5, BLACK)
    draw_text(surface, f"{LURE_COST} Flamefruit", 18, lure_button_rect.centerx, lure_button_rect.y + 25, BLACK)

    # Draw the Ripple clone button
    ripple_clone_button_rect = pygame.Rect(SCREEN_WIDTH - 480, PLAYABLE_HEIGHT + 10, 110, 50)
    pygame.draw.rect(surface, GREEN, ripple_clone_button_rect)
    draw_text(surface, "Ripple", 18, ripple_clone_button_rect.centerx, ripple_clone_button_rect.y + 5, BLACK)
    draw_text(surface, f"75 Berries", 18, ripple_clone_button_rect.centerx, ripple_clone_button_rect.y + 25, BLACK)

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    surface.blit(font.render(text, True, color), font.render(text, True, color).get_rect(midtop=(x, y)))

def handle_events():
    global predicted_tree_type, game_over  # Ensure we use the predicted tree type

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                return True
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1:
                if mouse_pos[1] <= PLAYABLE_HEIGHT:
                    if is_position_valid(mouse_pos, plants):
                        if inventory.items[inventory.selected_fruit] > 0:
                            tree_type = predicted_tree_type
                            tree, fruit = tree_fruit_pairs[tree_names.index(tree_type)]
                            attributes = tree_attributes[tree_fruit_pairs.index((tree, fruit))]
                            plants.append(Plant(tree, fruit, mouse_pos, attributes))
                            inventory.remove_selected_fruit()
                            predict_next_tree(inventory.selected_fruit)  # Predict the next tree after planting
                else:
                    # Check if Luminara button was clicked
                    luminara_button_rect = pygame.Rect(SCREEN_WIDTH - 120, PLAYABLE_HEIGHT + 10, 110, 50)
                    if luminara_button_rect.collidepoint(mouse_pos):
                        if inventory.items["etherealpear"] >= LUMINARA_COST:
                            inventory.items["etherealpear"] -= LUMINARA_COST
                            luminaras.append(Luminara())
                    # Check if Speed Boost button was clicked
                    speed_boost_button_rect = pygame.Rect(SCREEN_WIDTH - 240, PLAYABLE_HEIGHT + 10, 110, 50)
                    if speed_boost_button_rect.collidepoint(mouse_pos):
                        if inventory.items["shimmeringapple"] >= SPEED_BOOST_COST:
                            inventory.items["shimmeringapple"] -= SPEED_BOOST_COST
                            apply_speed_boost()
                    # Check if Lure button was clicked
                    lure_button_rect = pygame.Rect(SCREEN_WIDTH - 360, PLAYABLE_HEIGHT + 10, 110, 50)
                    if lure_button_rect.collidepoint(mouse_pos):
                        if inventory.items["flamefruit"] >= LURE_COST:
                            inventory.items["flamefruit"] -= LURE_COST
                            place_lure()
                    # Check if Ripple clone button was clicked
                    ripple_clone_button_rect = pygame.Rect(SCREEN_WIDTH - 480, PLAYABLE_HEIGHT + 10, 110, 50)
                    if ripple_clone_button_rect.collidepoint(mouse_pos):
                        if inventory.items["gleamberry"] >= RIPPLE_COST:
                            inventory.items["gleamberry"] -= RIPPLE_COST
                            temporary_ripples.append(RippleClone())
            elif event.button == 3:
                x_offset, selected = 10, False
                for fruit in fruit_images.keys():
                    if x_offset <= mouse_pos[0] <= x_offset + FRUIT_SIZE[0] and PLAYABLE_HEIGHT + 10 <= mouse_pos[1] <= PLAYABLE_HEIGHT + FRUIT_SIZE[1] + 10:
                        inventory.set_selected_fruit(fruit)
                        selected = True
                        break
                    x_offset += 50
                if not selected:
                    for plant in plants:
                        if plant.is_clicked(mouse_pos) and plant.fruit_visible:
                            while plant.fruit_positions:
                                inventory.collect_fruit(list(fruit_images.keys())[tree_images.index(plant.tree)])
                                plant.fruit_positions.pop(0)
                            plant.fruit_visible, plant.harvested = False, True
                            plant.respawn_start_time = time.time()
                            if plant.harvest_count >= plant.max_harvests:
                                plants.remove(plant)
                            break
    return True

class RippleClone(Ripple):
    def __init__(self):
        super().__init__()
        self.spawn_time = time.time()

    def update(self):
        super().update()
        if time.time() - self.spawn_time >= 15:
            temporary_ripples.remove(self)

def apply_speed_boost():
    current_time = time.time()
    for obj in [ripple] + luminaras + temporary_ripples:
        if obj.speed < MAX_SPEED:
            obj.speed += 1
            obj.speed_boost_timer = current_time + SPEED_BOOST_DURATION
        else:
            obj.speed_boost_timer += SPEED_BOOST_DURATION

def place_lure():
    lure_pos = (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, PLAYABLE_HEIGHT - 50))
    lures.append(Lure(lure_pos))

def update_game():
    if game_over:
        return
    for plant in plants:
        plant.update()
    if nyx:
        nyx.update()
    if ripple:
        ripple.update()
    for luminara in luminaras:
        luminara.update()
    for temp_ripple in temporary_ripples:
        temp_ripple.update()
    for lure in lures:
        lure.update()

    check_win_loss_condition()

def check_win_loss_condition():
    global game_over
    if nyx_melon_count >= LOSS_CONDITION and luminara_melon_count >= WIN_CONDITION:
        display_message("Nyx and Luminara share a Moonbeam Melon", PURPLE)
        game_over = True
    elif nyx_melon_count >= LOSS_CONDITION:
        display_message("Nyx Stole the Moonbeam Melons", RED)
        game_over = True
    elif luminara_melon_count >= WIN_CONDITION:
        display_message("50 Moonbeam Melons Harvested", NEON_GREEN)
        game_over = True

def display_message(message, color):
    font = pygame.font.SysFont(None, 55)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()

def render_game():
    screen.fill(BLACK)
    screen.blit(background, ((SCREEN_WIDTH - background.get_width()) // 2, UNPLAYABLE_HEIGHT))
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, UNPLAYABLE_HEIGHT))
    draw_statistics(screen)
    for plant in plants:
        plant.draw(screen)
    if nyx:
        nyx.draw(screen)
    if ripple:
        ripple.draw(screen)
    for luminara in luminaras:
        luminara.draw(screen)
    for temp_ripple in temporary_ripples:
        temp_ripple.draw(screen)
    for lure in lures:
        lure.draw(screen)
    draw_inventory(screen, inventory)
    cursor_surface = create_cursor_surface(next_tree_color)
    screen.blit(cursor_surface, pygame.mouse.get_pos())
    pygame.display.flip()

def draw_statistics(screen):
    font = pygame.font.SysFont(None, 30)
    nyx_melons_text = font.render(f"Nyx: {nyx_melon_count}/50", True, WHITE)
    nyx_speed_text = font.render(f"Nyx Speed: {nyx.speed}", True, WHITE)
    screen.blit(nyx_melons_text, (10, 10))
    screen.blit(nyx_speed_text, (200, 10))  # Display side by side


running = True
while running:
    running = handle_events()
    check_melon_timers()
    update_game()
    render_game()

pygame.quit()
sys.exit()
