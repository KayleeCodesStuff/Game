import pygame
import random
import time
import sys
import cProfile
import pstats
from typing import List, Tuple, Dict

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
TILE_SIZE = 40
INVENTORY_HEIGHT = 100
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT
MAZE_WIDTH = (SCREEN_WIDTH // TILE_SIZE) - 1
MAZE_HEIGHT = (PLAY_AREA_HEIGHT // TILE_SIZE) - 2
FPS = 60
SCREEN_PLAY_AREA_HEIGHT = SCREEN_HEIGHT - INVENTORY_HEIGHT

# Type aliases
Position = List[int]
Wall = Tuple[int, int, pygame.Surface]

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Maze Game')
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 64)
        
        self.player_pos = [2 * TILE_SIZE, 2 * TILE_SIZE]
        self.player_speed = 3
        self.nightcrawler_pos = None
        self.nightcrawler_speed = 5
        self.nightcrawler_target = None
        
        self.start_time = time.time()
        self.elapsed_time = 0
        self.found_ripple = False
        self.lost_game = False
        
        self.maze, self.maze_walls = self.generate_maze()
        self.ripple_pos = self.find_valid_position()
        self.outer_walls = self.create_outer_walls()
        
        self.fruit_positions = {}
        self.tree_timers = {}
        self.additional_tree_destruction_time = 0
        self.flamefruit_effect_end_time = 0
        self.last_fruit_spawn_time = self.start_time
        
        self.load_images()
        self.inventory, self.egg_counts, self.inventory_slots = self.load_inventory_data()

    def load_images(self):
        self.luminara_img = self.load_and_scale('luminara.png')
        self.background_img = self.load_image('background.png')
        self.ripple_img = self.load_and_scale('ripple.png')
        self.outer_wall_img = self.load_and_scale('tree5.png')
        self.nightcrawler_img = self.load_and_scale('nightcrawler.png')
        self.tree_images = [self.load_and_scale(f'tree{i}.png') for i in range(8)]
        self.fruit_images = {name: pygame.transform.scale(self.load_image(f"{name}.png"), (45, 45)) 
                             for name in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}

    @staticmethod
    def load_and_scale(image_path: str) -> pygame.Surface:
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return pygame.Surface((TILE_SIZE, TILE_SIZE))

    @staticmethod
    def load_image(image_path: str) -> pygame.Surface:
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_PLAY_AREA_HEIGHT))
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            return pygame.Surface((SCREEN_WIDTH, SCREEN_PLAY_AREA_HEIGHT))

    def generate_maze(self) -> Tuple[List[List[int]], List[Wall]]:
        maze = self.create_maze(MAZE_WIDTH, MAZE_HEIGHT)
        walls = [(x, y, random.choice(self.tree_images)) for y in range(len(maze)) for x in range(len(maze[y])) if maze[y][x] == 1]
        return maze, walls

    @staticmethod
    def create_maze(width: int, height: int) -> List[List[int]]:
        maze = [[1] * width for _ in range(height)]

        def carve_passages(x: int, y: int):
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

    @staticmethod
    def create_outer_walls() -> List[Tuple[int, int]]:
        return (
            [(x, 0) for x in range(MAZE_WIDTH + 2)] +
            [(x, MAZE_HEIGHT + 1) for x in range(MAZE_WIDTH + 2)] +
            [(MAZE_WIDTH + 1, y) for y in range(1, MAZE_HEIGHT + 1)]
        )

    def find_valid_position(self) -> Position:
        while True:
            x, y = random.randint(1, MAZE_WIDTH - 2), random.randint(1, MAZE_HEIGHT - 2)
            if self.maze[y][x] == 0 and (x, y) not in self.outer_walls:
                return [x, y]

    def is_colliding_with_walls(self, next_pos: Position) -> bool:
        inner_margin = TILE_SIZE * 0.1
        inner_rect = pygame.Rect(next_pos[0] + inner_margin, next_pos[1] + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)
        return any(inner_rect.colliderect(pygame.Rect((x + 1) * TILE_SIZE + inner_margin, (y + 1) * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y, _) in self.maze_walls) or \
               any(inner_rect.colliderect(pygame.Rect(x * TILE_SIZE + inner_margin, y * TILE_SIZE + inner_margin, TILE_SIZE * 0.8, TILE_SIZE * 0.8)) for (x, y) in self.outer_walls)

    @staticmethod
    def move_towards_target(pos: Position, target: Position, speed: float) -> Position:
        dx, dy = target[0] - pos[0], target[1] - pos[1]
        dist = (dx**2 + dy**2) ** 0.5
        if dist != 0:
            dx, dy = dx / dist, dy / dist
        return [pos[0] + dx * speed, pos[1] + dy * speed]

    def draw_game(self):
        self.screen.blit(self.background_img, (0, 0))
        self.draw_walls()
        self.draw_inventory()
        self.draw_game_objects()
        self.draw_ui()

    def draw_walls(self):
        for (x, y, img) in self.maze_walls:
            if (x, y) in self.tree_timers:
                timer = self.tree_timers[(x, y)]
                dark_factor = int(255 * (timer['start'] - time.time()) / (3 + self.additional_tree_destruction_time))
                dark_factor = max(0, min(255, dark_factor))
                img = self.darken_image(img, dark_factor)
            self.screen.blit(img, ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
        for (x, y) in self.outer_walls:
            self.screen.blit(self.outer_wall_img, (x * TILE_SIZE, y * TILE_SIZE))

    def draw_inventory(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        self.draw_inventory_items()

    def draw_game_objects(self):
        self.screen.blit(self.ripple_img, ((self.ripple_pos[0] + 1) * TILE_SIZE, (self.ripple_pos[1] + 1) * TILE_SIZE))
        for pos, (fruit_type, img) in self.fruit_positions.items():
            self.screen.blit(img, (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
        self.screen.blit(self.luminara_img, (self.player_pos[0], self.player_pos[1]))
        if self.nightcrawler_pos:
            self.screen.blit(self.nightcrawler_img, (self.nightcrawler_pos[0], self.nightcrawler_pos[1]))

    def draw_ui(self):
        timer_text = self.font.render(f'Time: {self.elapsed_time}s', True, (255, 255, 255))
        self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
        instructions = self.font.render('Use arrow keys to move', True, (255, 255, 255))
        self.screen.blit(instructions, (10, SCREEN_HEIGHT - 20))
        speed_text = self.font.render(f'Player Speed: {self.player_speed}  Nightcrawler Speed: {self.nightcrawler_speed}  Blight Speed: {self.additional_tree_destruction_time + 3}', True, (255, 255, 255))
        self.screen.blit(speed_text, (10, 10))

    @staticmethod
    def darken_image(image: pygame.Surface, factor: int) -> pygame.Surface:
        dark_image = image.copy()
        dark_image.fill((0, 0, 0, factor), special_flags=pygame.BLEND_RGBA_MULT)
        return dark_image

    def apply_fruit_effect(self, fruit_type: str, current_time: float):
        if self.inventory.get(fruit_type, 0) > 0:
            if fruit_type == "gleamberry":
                self.additional_tree_destruction_time += 1
                print("Gleaming Berry used! Blight effect increased.")
            elif fruit_type == "shimmeringapple":
                self.player_speed += 1
                print("Shimmering Apple used! Player speed increased.")
            elif fruit_type == "etherealpear":
                self.nightcrawler_speed = max(1, self.nightcrawler_speed - 0.5)
                print("Ethereal Pear used! Nightcrawler speed decreased.")
            elif fruit_type == "flamefruit":
                self.nightcrawler_target = self.player_pos.copy()
                self.flamefruit_effect_end_time = current_time + 5
                print("Flame Fruit used! Nightcrawler lured to Luminara's position for 5 seconds.")
            elif fruit_type == "moonbeammelon":
                self.ripple_pos = self.find_valid_position()
                print("Moonbeam Melon used! Ripple moved to a new position.")
            self.inventory[fruit_type] -= 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        keys = pygame.key.get_pressed()
        next_pos = self.player_pos.copy()
        if keys[pygame.K_LEFT]:
            next_pos[0] -= self.player_speed
        if keys[pygame.K_RIGHT]:
            next_pos[0] += self.player_speed
        if keys[pygame.K_UP]:
            next_pos[1] -= self.player_speed
        if keys[pygame.K_DOWN]:
            next_pos[1] += self.player_speed

        current_time = time.time()
        if keys[pygame.K_1]:
            self.apply_fruit_effect("gleamberry", current_time)
        if keys[pygame.K_2]:
            self.apply_fruit_effect("flamefruit", current_time)
        if keys[pygame.K_3]:
            self.apply_fruit_effect("shimmeringapple", current_time)
        if keys[pygame.K_4]:
            self.apply_fruit_effect("etherealpear", current_time)
        if keys[pygame.K_5]:
            self.apply_fruit_effect("moonbeammelon", current_time)

        if not (self.found_ripple or self.lost_game):
            if 0 <= next_pos[0] < SCREEN_WIDTH and TILE_SIZE <= next_pos[1] < PLAY_AREA_HEIGHT and not self.is_colliding_with_walls(next_pos):
                self.player_pos = next_pos

        return True

    def update_game_state(self, current_time: float):
        if current_time > self.flamefruit_effect_end_time:
            self.nightcrawler_target = [(self.ripple_pos[0] + 1) * TILE_SIZE, (self.ripple_pos[1] + 1) * TILE_SIZE]

        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], TILE_SIZE, TILE_SIZE)
        ripple_rect = pygame.Rect((self.ripple_pos[0] + 1) * TILE_SIZE, (self.ripple_pos[1] + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if player_rect.colliderect(ripple_rect):
            print("Ripple found")
            self.found_ripple = True

        self.update_nightcrawler(current_time)
        self.update_fruits(current_time)
        self.update_tree_timers(current_time)

        if not (self.found_ripple or self.lost_game):
            self.elapsed_time = int(current_time - self.start_time)

    def update_nightcrawler(self, current_time: float):
        if not self.nightcrawler_pos and current_time >= self.start_time + 5:
            self.nightcrawler_pos = [coord * TILE_SIZE for coord in self.find_valid_position()]
            self.nightcrawler_target = [(self.ripple_pos[0] + 1) * TILE_SIZE, (self.ripple_pos[1] + 1) * TILE_SIZE]
        if self.nightcrawler_pos and not self.found_ripple and not self.lost_game:
            self.nightcrawler_pos = self.move_towards_target(self.nightcrawler_pos, self.nightcrawler_target, self.nightcrawler_speed)
            nightcrawler_rect = pygame.Rect(self.nightcrawler_pos[0], self.nightcrawler_pos[1], TILE_SIZE, TILE_SIZE)

            for (x, y, img) in self.maze_walls:
                wall_rect = pygame.Rect((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if nightcrawler_rect.colliderect(wall_rect):
                    if (x, y) not in self.tree_timers:
                        self.tree_timers[(x, y)] = {'start': current_time + 3 + self.additional_tree_destruction_time, 'img': img}
                    break

            if nightcrawler_rect.colliderect(pygame.Rect((self.ripple_pos[0] + 1) * TILE_SIZE, (self.ripple_pos[1] + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                print("Nightcrawler reached the ripple")
                self.lost_game = True

    def update_fruits(self, current_time: float):
        if not (self.found_ripple or self.lost_game) and current_time - self.last_fruit_spawn_time >= 2:
            fruit_type = random.choice(list(self.fruit_images.keys()))
            fruit_pos = self.find_valid_position()
            while (fruit_pos[0], fruit_pos[1]) in self.fruit_positions or (fruit_pos[0], fruit_pos[1]) in [(x, y) for x, y, _ in self.maze_walls]:
                fruit_pos = self.find_valid_position()
            self.fruit_positions[tuple(fruit_pos)] = (fruit_type, self.fruit_images[fruit_type])
            self.last_fruit_spawn_time = current_time

        if self.found_ripple or self.lost_game:
            self.fruit_positions.clear()

        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], TILE_SIZE, TILE_SIZE)
        for pos, (fruit_type, img) in list(self.fruit_positions.items()):
            fruit_rect = pygame.Rect(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(fruit_rect):
                self.inventory[fruit_type] = self.inventory.get(fruit_type, 0) + 1
                del self.fruit_positions[pos]

    def update_tree_timers(self, current_time: float):
        to_remove = []
        for (x, y) in self.tree_timers:
            if current_time >= self.tree_timers[(x, y)]['start']:
                self.maze_walls = [(wx, wy, wimg) for (wx, wy, wimg) in self.maze_walls if not (wx == x and wy == y)]
                to_remove.append((x, y))
        for key in to_remove:
            del self.tree_timers[key]

    def run(self):
        running = True
        while running:
            try:
                current_time = time.time()
                running = self.handle_events()
                self.update_game_state(current_time)
                self.draw_game()

                if self.found_ripple:
                    won_text = self.large_font.render('Found Ripple', True, (0, 255, 0))
                    self.screen.blit(won_text, (SCREEN_WIDTH // 2 - won_text.get_width() // 2, SCREEN_HEIGHT // 2 - won_text.get_height() // 2))

                if self.lost_game:
                    lost_text = self.large_font.render('Ripple Taken by Malakar', True, (255, 0, 0))
                    self.screen.blit(lost_text, (SCREEN_WIDTH // 2 - lost_text.get_width() // 2, SCREEN_HEIGHT // 2 - lost_text.get_height() // 2))

                pygame.display.flip()
                self.clock.tick(FPS)

            except Exception as e:
                print(f"Exception in game loop: {e}")
                running = False

        self.save_inventory_data()
        print("Exiting the game loop")

    def load_inventory_data(self):
        # Implement this method to load inventory data
        return {}, {}, {}

    def save_inventory_data(self):
        # Implement this method to save inventory data
        pass

    def draw_inventory_items(self):
        # Implement this method to draw inventory items
        pass

def main():
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        game = Game()
        game.run()
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
            