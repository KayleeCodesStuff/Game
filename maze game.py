import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
INVENTORY_HEIGHT = SCREEN_HEIGHT // 5  # Make the inventory area taller
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT
MAZE_WIDTH = (SCREEN_WIDTH // TILE_SIZE) - 2  # Adjust for outer walls
MAZE_HEIGHT = (PLAY_AREA_HEIGHT // TILE_SIZE) - 2  # Adjust for outer walls
FPS = 60

# Load Images
luminara_img = pygame.image.load('luminara.png')
background_img = pygame.image.load('background.png')
ripple_img = pygame.image.load('ripple.png')
outer_wall_img = pygame.image.load('tree5.png')

# Tree images
tree_images = [pygame.image.load(f'tree{i}.png') for i in range(8)]

# Resize images to TILE_SIZE
luminara_img = pygame.transform.scale(luminara_img, (TILE_SIZE, TILE_SIZE))
ripple_img = pygame.transform.scale(ripple_img, (TILE_SIZE, TILE_SIZE))
outer_wall_img = pygame.transform.scale(outer_wall_img, (TILE_SIZE, TILE_SIZE))
tree_images = [pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) for img in tree_images]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Maze Game')

# Font
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Player setup
player_pos = [2 * TILE_SIZE, 2 * TILE_SIZE]
player_speed = 5
score = 0

# Timer setup
start_time = time.time()

# Function to create a random maze using DFS algorithm
def create_maze(width, height):
    maze = [[1] * width for _ in range(height)]
    
    def carve_passages(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[ny - dy // 2][nx - dx // 2] = 0  # Ensure path is two tiles wide
                maze[y + dy // 2][x + dx // 2] = 0
                carve_passages(nx, ny)
    
    maze[1][1] = 0
    carve_passages(1, 1)
    return maze

# Create the maze and store wall positions
def generate_maze():
    maze = create_maze(MAZE_WIDTH, MAZE_HEIGHT)
    maze_walls = []

    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:
                maze[y][x] = random.choice(tree_images)
                maze_walls.append((x, y, maze[y][x]))

    return maze, maze_walls

maze, maze_walls = generate_maze()

# Ensure start and end points are clear
maze[1][1] = 0
ripple_pos = [MAZE_WIDTH-2, MAZE_HEIGHT-2]

# Add outer walls
outer_walls = []
for x in range(MAZE_WIDTH + 2):
    outer_walls.append((x, 0))
    outer_walls.append((x, MAZE_HEIGHT + 1))
for y in range(MAZE_HEIGHT + 2):
    outer_walls.append((0, y))
    outer_walls.append((MAZE_WIDTH + 1, y))

# Function to draw the maze
def draw_maze():
    for (x, y, img) in maze_walls:
        screen.blit(img, ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
    for (x, y) in outer_walls:
        screen.blit(outer_wall_img, (x * TILE_SIZE, y * TILE_SIZE))

# Function to draw the timer
def draw_timer():
    elapsed_time = int(time.time() - start_time)
    timer_text = font.render(f'Time: {elapsed_time}s', True, (255, 255, 255))
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

# Function to draw instructions
def draw_instructions():
    instructions = font.render('Use arrow keys to move', True, (255, 255, 255))
    screen.blit(instructions, (10, SCREEN_HEIGHT - 40))

# Function to draw the inventory
def draw_inventory():
    inventory_text = font.render('Inventory:', True, (255, 255, 255))
    screen.blit(inventory_text, (10, SCREEN_HEIGHT - INVENTORY_HEIGHT + 10))
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - INVENTORY_HEIGHT, SCREEN_WIDTH, INVENTORY_HEIGHT))

# Check for collisions with walls
def is_colliding_with_walls(next_pos, walls):
    next_rect = pygame.Rect(next_pos[0], next_pos[1], TILE_SIZE, TILE_SIZE)
    for (x, y, img) in walls:
        wall_rect = pygame.Rect((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if next_rect.colliderect(wall_rect):
            return True
    for (x, y) in outer_walls:
        wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if next_rect.colliderect(wall_rect):
            return True
    return False

# Main game loop
running = True
found_ripple = False
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get pressed keys
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

    # Check for collisions with walls and screen edges
    if (
        0 <= next_pos[0] < SCREEN_WIDTH and
        0 <= next_pos[1] < PLAY_AREA_HEIGHT - TILE_SIZE and
        not is_colliding_with_walls(next_pos, maze_walls)
    ):
        player_pos = next_pos

    # Check if player reaches the ripple
    if player_pos[0] // TILE_SIZE == ripple_pos[0] + 1 and player_pos[1] // TILE_SIZE == ripple_pos[1] + 1:
        found_ripple = True

    # Draw everything
    screen.blit(background_img, (0, 0))
    draw_maze()
    screen.blit(ripple_img, ((ripple_pos[0] + 1) * TILE_SIZE, (ripple_pos[1] + 1) * TILE_SIZE))
    screen.blit(luminara_img, (player_pos[0], player_pos[1]))
    draw_timer()
    draw_instructions()
    draw_inventory()
    
    # Display score
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Display "Found Ripple" message if ripple is found
    if found_ripple:
        ripple_text = large_font.render('Found Ripple', True, (0, 255, 0))
        screen.blit(ripple_text, (SCREEN_WIDTH // 2 - ripple_text.get_width() // 2, SCREEN_HEIGHT // 2 - ripple_text.get_height() // 2))
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
