import pygame
import random
import time
import sys
import cProfile
import pstats
from game import load_inventory_data, save_inventory_data, draw_inventory
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
TILE_SIZE = 40
INVENTORY_HEIGHT = 100
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT
MAZE_WIDTH = (SCREEN_WIDTH // TILE_SIZE) - 1  # Exclude left and right border walls
MAZE_HEIGHT = (PLAY_AREA_HEIGHT // TILE_SIZE) - 2  # Exclude top and bottom border wall
FPS = 60

# Adjust the screen dimensions to exclude the inventory height
SCREEN_PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT

def load_and_scale(image_path):
    try:
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return pygame.Surface((TILE_SIZE, TILE_SIZE))  # Return a blank surface as a placeholder

def load_image(image_path):
    try:
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_PLAY_AREA_HEIGHT))
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return pygame.Surface((SCREEN_WIDTH, SCREEN_PLAY_AREA_HEIGHT))  # Return a blank surface as a placeholder

# Load images
luminara_img = load_and_scale('luminara.png')
background_img = load_image('background.png')
ripple_img = load_and_scale('ripple.png')
outer_wall_img = load_and_scale('tree5.png')
nightcrawler_img = load_and_scale('nightcrawler.png')
tree_images = [load_and_scale(f'tree{i}.png') for i in range(8)]
fruit_images = {name: pygame.transform.scale(load_image(f"{name}.png"), (45, 45)) for name in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Maze Game')

flamefruit_effect_end_time = 0
gleamberry_cooldown_end_time = 0
gleamberry_remaining_cooldown = 0

font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 64)

player_pos = [2 * TILE_SIZE, 2 * TILE_SIZE]
player_speed = 3

start_time = time.time()
elapsed_time = 0

tree_timers = {}
additional_tree_destruction_time = 0

# Initialize inventory and egg counts
inventory, egg_counts, inventory_slots = load_inventory_data()

def create_maze(width, height):
    maze = [[1] * width for _ in range(height)]

    def carve_passages(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[ny - dy // 2][nx - dx // 2] = 0
                maze[y + dy // 2][x + dx // 2] = 0
                carve_passages(nx, ny)

    maze[1][1] = 0
    carve_passages(1, 1)
    return maze

def generate_maze():
    maze = create_maze(MAZE_WIDTH, MAZE_HEIGHT)
    walls = [(x, y, random.choice(tree_images)) for y in range(len(maze)) for x in range(len(maze[y])) if maze[y][x] == 1]
    return maze, walls

maze, maze_walls = generate_maze()
maze[1][1] = 0

outer_walls = (
    [(x, 0) for x in range(MAZE_WIDTH + 2)] +  # Top wall
    [(x, MAZE_HEIGHT + 1) for x in range(MAZE_WIDTH + 2)] +  # Bottom wall
    [(MAZE_WIDTH + 1, y) for y in range(1, MAZE_HEIGHT + 1)]  # Right wall
)

def find_valid_position():
    while True:
        x, y = random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)
        if maze[y][x] == 0 and (x, y) not in outer_walls:
            return [x, y]

ripple_pos = find_valid_position()

def darken_image(image, factor):
    dark_image = image.copy()
    dark_image.fill((0, 0, 0, factor), special_flags=pygame.BLEND_RGBA_MULT)
    return dark_image

def is_colliding_with_walls(next_pos):
    inner_margin = TILE_SIZE * 0.1
    inner_rect = pygame.Rect(next_pos[0] + inner_margin, next_pos[1] + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)
    return any(inner_rect.colliderect(pygame.Rect((x + 1) * TILE_SIZE + inner_margin, (y + 1) * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y, _) in maze_walls) or any(inner_rect.colliderect(pygame.Rect(x * TILE_SIZE + inner_margin, y * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y) in outer_walls)

def move_towards_target(pos, target, speed):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    dist = (dx**2 + dy**2) ** 0.5
    if dist != 0:
        dx, dy = dx / dist, dy / dist
    next_pos = [pos[0] + dx * speed, pos[1] + dy * speed]
    if not is_colliding_with_walls(next_pos):
        pos = next_pos
    return pos

def draw_game():
    screen.blit(background_img, (0, 0))  # Ensure this covers the play area correctly
    for (x, y, img) in maze_walls:
        if (x, y) in tree_timers:
            timer = tree_timers[(x, y)]
            dark_factor = int(255 * (timer['start'] - time.time()) / (3 + additional_tree_destruction_time))
            dark_factor = max(0, min(255, dark_factor))
            img = darken_image(img, dark_factor)
        screen.blit(img, ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
    for (x, y) in outer_walls:
        # Drawing outer walls
        screen.blit(outer_wall_img, (x * TILE_SIZE, y * TILE_SIZE))

    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))  # Draw inventory background
    draw_inventory(screen, inventory, egg_counts, inventory_slots)

    # Display ripple and fruits
    screen.blit(ripple_img, ((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE))
    for pos, (fruit_type, img) in fruit_positions.items():
        screen.blit(img, (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))

    # Display player and other game elements
    screen.blit(luminara_img, (player_pos[0], player_pos[1]))
    if nightcrawler_pos:
        screen.blit(nightcrawler_img, (nightcrawler_pos[0], nightcrawler_pos[1]))

    # Display timer and other UI elements
    timer_text = font.render(f'Time: {elapsed_time}s', True, (255, 255, 255))
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
    instructions = font.render('Use arrow keys to move', True, (255, 255, 255))
    screen.blit(instructions, (10, SCREEN_HEIGHT - 20))

    # Display player speed, nightcrawler speed, and blight speed in one row
    speed_text = font.render(f'Player Speed: {player_speed}  Nightcrawler Speed: {nightcrawler_speed}  Blight Speed: {additional_tree_destruction_time + 3}', True, (255, 255, 255))
    screen.blit(speed_text, (10, 10))


def find_valid_nightcrawler_position():
    while True:
        x, y = random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)
        if maze[y][x] == 0 and (x, y) not in [(x, y) for x, y, _ in maze_walls] and (x, y) not in outer_walls:
            return [x, y]
def apply_fruit_effect(fruit_type):
    global player_speed, nightcrawler_target, nightcrawler_speed, additional_tree_destruction_time, flamefruit_effect_end_time, ripple_pos
def apply_fruit_effect(fruit_type, current_time):
    global player_speed, nightcrawler_target, nightcrawler_speed, additional_tree_destruction_time, flamefruit_effect_end_time, ripple_pos
    global moonbeam_cooldown_end_time

    if inventory.get(fruit_type, 0) > 0:
        if fruit_type == "gleamberry":
            additional_tree_destruction_time += 1
            print("Gleaming Berry used! Blight effect increased.")           
        elif fruit_type == "shimmeringapple":
            player_speed += 1
            print("Shimmering Apple used! Player speed increased.")
        elif fruit_type == "etherealpear":
            nightcrawler_speed = max(1, nightcrawler_speed - 0.5)
            print("Ethereal Pear used! Nightcrawler speed decreased.")
        elif fruit_type == "flamefruit":
            nightcrawler_target = player_pos.copy()  # Target Luminara's position at the moment
            flamefruit_effect_end_time = current_time + 5
            print("Flame Fruit used! Nightcrawler lured to Luminara's position for 5 seconds.")
        elif fruit_type == "moonbeammelon":
            moonbeam_cooldown_end_time = current_time + 30  # 30 seconds cooldown
            ripple_pos = find_valid_position()  # Change ripple position
            print("Moonbeam Melon used! Ripple moved to a new position.")
            if current_time < moonbeam_cooldown_end_time:
                print("Moonbeam Melon is on cooldown.")
                return
        inventory[fruit_type] -= 1


def main():
    global player_pos, player_speed, start_time, elapsed_time, found_ripple, lost_game
    global nightcrawler_pos, nightcrawler_speed, nightcrawler_target_time, nightcrawler_spawn_time
    global last_fruit_spawn_time, fruit_positions, additional_tree_destruction_time, tree_timers
    global maze_walls, ripple_pos, outer_walls, flamefruit_effect_end_time, nightcrawler_target

    # Initialize global variables
    player_pos = [2 * TILE_SIZE, 2 * TILE_SIZE]
    player_speed = 3
    start_time = time.time()
    elapsed_time = 0
    found_ripple = False
    lost_game = False
    nightcrawler_pos = None
    nightcrawler_speed = 5
    nightcrawler_target_time = 0
    nightcrawler_spawn_time = start_time + 5
    last_fruit_spawn_time = start_time
    fruit_positions = {}
    tree_timers = {}
    additional_tree_destruction_time = 0

    # Initialize maze and walls
    maze, maze_walls = generate_maze()
    maze[1][1] = 0
    ripple_pos = find_valid_position()
    outer_walls = [(x, 1) for x in range(MAZE_WIDTH + 2)] + [(x, MAZE_HEIGHT + 1) for x in range(MAZE_WIDTH + 2)] + [(0, y) for y in range(2, MAZE_HEIGHT + 2)] + [(MAZE_WIDTH + 1, y) for y in range(2, MAZE_HEIGHT + 2)]

    running = True
    clock = pygame.time.Clock()

    while running:
        try:
            current_time = time.time()  # Update current time at the beginning of each loop iteration

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            next_pos = player_pos.copy()
            if keys[pygame.K_LEFT]:
                next_pos[0] -= player_speed
            if keys[pygame.K_RIGHT]:
                next_pos[0] += player_speed
            if keys[pygame.K_UP]:
                next_pos[1] -= player_speed
            if keys[pygame.K_DOWN]:
                next_pos[1] += player_speed
            if keys[pygame.K_1]:
                apply_fruit_effect("gleamberry", current_time)
            if keys[pygame.K_2]:
                apply_fruit_effect("flamefruit", current_time)
            if keys[pygame.K_3]:
                apply_fruit_effect("shimmeringapple", current_time)
            if keys[pygame.K_4]:
                apply_fruit_effect("etherealpear", current_time)
            if keys[pygame.K_5]:
                apply_fruit_effect("moonbeammelon", current_time)

            if not (found_ripple or lost_game):
                if 0 <= next_pos[0] < SCREEN_WIDTH and TILE_SIZE <= next_pos[1] < PLAY_AREA_HEIGHT and not is_colliding_with_walls(next_pos):
                    player_pos = next_pos

            # Update nightcrawler target based on flamefruit effect
            if current_time > flamefruit_effect_end_time:
                nightcrawler_target = [(ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE]

            player_rect = pygame.Rect(player_pos[0], player_pos[1], TILE_SIZE, TILE_SIZE)
            ripple_rect = pygame.Rect((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(ripple_rect):
                print("Ripple found")
                found_ripple = True

            if not nightcrawler_pos and current_time >= nightcrawler_spawn_time:
                nightcrawler_pos = [coord * TILE_SIZE for coord in find_valid_nightcrawler_position()]
                nightcrawler_target = [(ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE]
            if nightcrawler_pos and not found_ripple and not lost_game:
                nightcrawler_pos = move_towards_target(nightcrawler_pos, nightcrawler_target, nightcrawler_speed)
                nightcrawler_rect = pygame.Rect(nightcrawler_pos[0], nightcrawler_pos[1], TILE_SIZE, TILE_SIZE)

                # Check for collision with walls or other elements as needed
                for (x, y, img) in maze_walls:
                    wall_rect = pygame.Rect((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if nightcrawler_rect.colliderect(wall_rect):
                        if (x, y) not in tree_timers:
                            tree_timers[(x, y)] = {'start': current_time + 3 + additional_tree_destruction_time, 'img': img}
                        break

                if nightcrawler_rect.colliderect(pygame.Rect((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                    print("Nightcrawler reached the ripple")
                    lost_game = True

            if not (found_ripple or lost_game):
                elapsed_time = int(current_time - start_time)

            if not (found_ripple or lost_game) and current_time - last_fruit_spawn_time >= 2:
                fruit_type = random.choice(list(fruit_images.keys()))
                fruit_pos = find_valid_position()
                while (fruit_pos[0], fruit_pos[1]) in fruit_positions or (fruit_pos[0], fruit_pos[1]) in [(x, y) for x, y, _ in maze_walls]:
                    fruit_pos = find_valid_position()
                fruit_positions[tuple(fruit_pos)] = (fruit_type, fruit_images[fruit_type])
                last_fruit_spawn_time = current_time

            if found_ripple or lost_game:
                fruit_positions.clear()

            for pos, (fruit_type, img) in list(fruit_positions.items()):
                fruit_rect = pygame.Rect(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_rect.colliderect(fruit_rect):
                    inventory[fruit_type] += 1
                    del fruit_positions[pos]

            to_remove = []
            for (x, y) in tree_timers:
                if current_time >= tree_timers[(x, y)]['start']:
                    maze_walls = [(wx, wy, wimg) for (wx, wy, wimg) in maze_walls if not (wx == x and wy == y)]
                    to_remove.append((x, y))
            for key in to_remove:
                del tree_timers[key]

            draw_game()

            if found_ripple:
                won_text = large_font.render('Found Ripple', True, (0, 255, 0))
                screen.blit(won_text, (SCREEN_WIDTH // 2 - won_text.get_width() // 2, SCREEN_HEIGHT // 2 - won_text.get_height() // 2))

            if lost_game:
                lost_text = large_font.render('Ripple Taken by Malakar', True, (255, 0, 0))
                screen.blit(lost_text, (SCREEN_WIDTH // 2 - lost_text.get_width() // 2, SCREEN_HEIGHT // 2 - lost_text.get_height() // 2))

            pygame.display.flip()
            clock.tick(FPS)

        except Exception as e:
            print(f"Exception in game loop: {e}")
            running = False

    save_inventory_data()  # Save the inventory data before quitting
    print("Exiting the game loop")


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        main()
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        pygame.quit()
        sys.exit()
