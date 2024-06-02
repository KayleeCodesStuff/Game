import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
INVENTORY_HEIGHT = SCREEN_HEIGHT // 5
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT
MAZE_WIDTH = (SCREEN_WIDTH // TILE_SIZE) - 2
MAZE_HEIGHT = (PLAY_AREA_HEIGHT // TILE_SIZE) - 2
FPS = 60

def load_and_scale(image_path):
    """Load and scale image to the defined TILE_SIZE."""
    return pygame.transform.scale(pygame.image.load(image_path), (TILE_SIZE, TILE_SIZE))

# Load images
luminara_img = load_and_scale('luminara.png')
background_img = pygame.image.load('background.png')
ripple_img = load_and_scale('ripple.png')
outer_wall_img = load_and_scale('tree5.png')
nightcrawler_img = load_and_scale('nightcrawler.png')
tree_images = [load_and_scale(f'tree{i}.png') for i in range(8)]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Maze Game')

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Player setup
player_pos = [2 * TILE_SIZE, 2 * TILE_SIZE]
player_speed = 5

# Timer setup
start_time = time.time()

# Tree destruction tracking
tree_timers = {}

def create_maze(width, height):
    """Create a random maze using DFS algorithm."""
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
    """Generate the maze and store wall positions."""
    maze = create_maze(MAZE_WIDTH, MAZE_HEIGHT)
    walls = [(x, y, random.choice(tree_images)) for y in range(len(maze)) for x in range(len(maze[y])) if maze[y][x] == 1]
    return maze, walls

maze, maze_walls = generate_maze()
maze[1][1] = 0

def find_valid_position(maze):
    """Find a valid position within the maze."""
    while True:
        x, y = random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)
        if maze[y][x] == 0:
            return [x, y]

ripple_pos = find_valid_position(maze)

# Add outer walls
outer_walls = [(x, 0) for x in range(MAZE_WIDTH + 2)] + [(x, MAZE_HEIGHT + 1) for x in range(MAZE_WIDTH + 2)] + [(0, y) for y in range(MAZE_HEIGHT + 2)] + [(MAZE_WIDTH + 1, y) for y in range(MAZE_HEIGHT + 2)]

def darken_image(image, factor):
    """Darken the image by a given factor."""
    dark_image = image.copy()
    dark_image.fill((0, 0, 0, factor), special_flags=pygame.BLEND_RGBA_MULT)
    return dark_image

def is_colliding_with_walls(next_pos):
    """Check if the next position collides with any walls."""
    inner_margin = TILE_SIZE * 0.1
    inner_rect = pygame.Rect(next_pos[0] + inner_margin, next_pos[1] + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)
    return any(inner_rect.colliderect(pygame.Rect((x + 1) * TILE_SIZE + inner_margin, (y + 1) * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y, _) in maze_walls) or any(inner_rect.colliderect(pygame.Rect(x * TILE_SIZE + inner_margin, y * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y) in outer_walls)

def move_towards_target(pos, target, speed):
    """Move the character towards the target position."""
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    dist = (dx**2 + dy**2) ** 0.5
    if dist != 0:
        dx, dy = dx / dist, dy / dist
    next_pos = [pos[0] + dx * speed, pos[1] + dy * speed]
    if not is_colliding_with_walls(next_pos):
        pos = next_pos
    return pos

def draw_game():
    """Draw the game screen."""
    screen.blit(background_img, (0, 0))
    for (x, y, img) in maze_walls:
        if (x, y) in tree_timers:
            timer = tree_timers[(x, y)]
            dark_factor = int(255 * (timer['start'] - time.time()) / 3)
            dark_factor = max(0, min(255, dark_factor))
            img = darken_image(img, dark_factor)
        screen.blit(img, ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
    for (x, y) in outer_walls:
        screen.blit(outer_wall_img, (x * TILE_SIZE, y * TILE_SIZE))
    screen.blit(ripple_img, ((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE))
    screen.blit(luminara_img, (player_pos[0], player_pos[1]))
    if nightcrawler_pos:
        screen.blit(nightcrawler_img, (nightcrawler_pos[0], nightcrawler_pos[1]))

    elapsed_time = int(time.time() - start_time)
    timer_text = font.render(f'Time: {elapsed_time}s', True, (255, 255, 255))
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

    instructions = font.render('Use arrow keys to move', True, (255, 255, 255))
    screen.blit(instructions, (10, SCREEN_HEIGHT - 40))

    inventory_text = font.render('Inventory:', True, (255, 255, 255))
    screen.blit(inventory_text, (10, SCREEN_HEIGHT - INVENTORY_HEIGHT + 10))
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - INVENTORY_HEIGHT, SCREEN_WIDTH, INVENTORY_HEIGHT))

# Main game loop
running, found_ripple, lost_game = True, False, False
nightcrawler_pos = None
nightcrawler_speed = 3
nightcrawler_spawn_time = start_time + 5
clock = pygame.time.Clock()

while running:
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

    if 0 <= next_pos[0] < SCREEN_WIDTH and 0 <= next_pos[1] < PLAY_AREA_HEIGHT - TILE_SIZE and not is_colliding_with_walls(next_pos):
        player_pos = next_pos

    player_rect = pygame.Rect(player_pos[0], player_pos[1], TILE_SIZE, TILE_SIZE)
    ripple_rect = pygame.Rect((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    if player_rect.colliderect(ripple_rect):
        found_ripple = True

    if not nightcrawler_pos and time.time() >= nightcrawler_spawn_time:
        nightcrawler_pos = [coord * TILE_SIZE for coord in find_valid_position(maze)]

    if nightcrawler_pos and not found_ripple and not lost_game:
        nightcrawler_pos = move_towards_target(nightcrawler_pos, [(ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE], nightcrawler_speed)
        nightcrawler_rect = pygame.Rect(nightcrawler_pos[0], nightcrawler_pos[1], TILE_SIZE, TILE_SIZE)

        for (x, y, img) in maze_walls:
            wall_rect = pygame.Rect((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if nightcrawler_rect.colliderect(wall_rect):
                if (x, y) not in tree_timers:
                    tree_timers[(x, y)] = {'start': time.time() + 3, 'img': img}
                break

        if nightcrawler_rect.colliderect(ripple_rect):
            lost_game = True

    current_time = time.time()
    to_remove = []
    for (x, y) in tree_timers:
        timer = tree_timers[(x, y)]
        if current_time >= timer['start']:
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

pygame.quit()
