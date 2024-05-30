import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
PLAYABLE_HEIGHT = HEIGHT - 60  # Leave space for inventory at the bottom
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elysian Grove Adventure")

# Load character images with error handling
def load_image(name):
    try:
        image = pygame.image.load(name)
        return image.convert_alpha()  # Ensure transparency is handled correctly
    except pygame.error as message:
        print(f"Cannot load image: {name}")
        raise SystemExit(message)

# Load images
images = {
    "luminara": pygame.transform.scale(load_image("luminara.png"), (90, 90)),
    "luminarainvuln": pygame.transform.scale(load_image("luminarainvuln.png"), (90, 90)),
    "enemy": pygame.transform.scale(load_image("enemy.png"), (67, 67)),
    "bossenemy": pygame.transform.scale(load_image("bossenemy.png"), (134, 134)),
    "malakar": pygame.transform.scale(load_image("malakar.png"), (268, 268)),
    "background": load_image("background.png"),
    "ripple": pygame.transform.scale(load_image("ripple.png"), (45, 45)),
    "gleamberry": pygame.transform.scale(load_image("gleamberry.png"), (45, 45)),
    "shimmeringapple": pygame.transform.scale(load_image("shimmeringapple.png"), (45, 45)),
    "etherealpear": pygame.transform.scale(load_image("etherealpear.png"), (45, 45)),
    "flamefruit": pygame.transform.scale(load_image("flamefruit.png"), (45, 45)),
    "moonbeammelon": pygame.transform.scale(load_image("moonbeammelon.png"), (45, 45))
}

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Player(BaseSprite):
    def __init__(self):
        super().__init__(WIDTH // 2, PLAYABLE_HEIGHT // 2, images["luminara"])
        self.default_image = self.image
        self.invuln_image = images["luminarainvuln"]
        self.base_speed = 5
        self.permanent_speed_boost = 0
        self.speed = self.base_speed
        self.base_damage = 20
        self.permanent_damage_boost = 0
        self.damage = self.base_damage
        self.experience = 0
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.inventory = {
            "gleamberry": 0,
            "shimmeringapple": 0,
            "etherealpear": 0,
            "flamefruit": 0,
            "moonbeammelon": 0
        }
        self.invulnerable = False
        self.last_hit = pygame.time.get_ticks()
        self.invuln_end_time = 0
        self.melon_end_time = 0
        self.last_regen_time = pygame.time.get_ticks()
        self.special_attack_ready = True
        self.special_attack_time = 0
        self.flamefruit_end_time = 0
        self.flamefruit_active = False
        self.flamefruit_position = None
        self.speed_boost_end_time = 0
        self.damage_reduction = 0
        self.permanent_damage_reduction = 0
        self.damage_reduction_end_times = []

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, PLAYABLE_HEIGHT - self.rect.height))

    def collect_fruit(self, fruit):
        self.inventory[fruit.name] += 1
        if fruit.name == "gleamberry":
            self.health = min(self.health + 10, self.max_health)
            spawn_ripple(fruit.rect.center)
        elif fruit.name == "shimmeringapple":
            self.speed_boost_end_time = pygame.time.get_ticks() + 12000
            self.speed = (self.base_speed + self.permanent_speed_boost) * 2
        elif fruit.name == "etherealpear":
            self.experience += 150
            self.health = min(self.health + 20, self.max_health + 20)
            self.max_health += 5
        elif fruit.name == "flamefruit":
            self.experience += 100
            self.flamefruit_end_time = pygame.time.get_ticks() + 3000
            self.flamefruit_active = True
            self.flamefruit_position = fruit.rect.center
            if self.level > 50:
                self.damage_reduction += 10
                self.damage_reduction_end_times.append(pygame.time.get_ticks() + 5000)
        elif fruit.name == "moonbeammelon":
            self.experience += 200
            self.damage = (self.base_damage + self.permanent_damage_boost) * 5
            self.melon_end_time = pygame.time.get_ticks() + 9000
            self.invulnerable = True
            self.image = self.invuln_image
            self.invuln_end_time = pygame.time.get_ticks() + 2000

        self.experience += 100
        if self.experience >= 1000:
            self.level += 1
            self.experience = 0

        return fruit.name

    def attack(self, enemy):
        damage_dealt = max(self.damage, 0)
        enemy.health -= damage_dealt
        if enemy.health <= 0:
            enemy.kill()
            self.experience += 50
            if isinstance(enemy, BossEnemy):
                self.experience += 500
            if isinstance(enemy, Malakar):
                self.experience += 1000
                global malakar_spawn_allowed_time
                malakar_spawn_allowed_time = pygame.time.get_ticks() + 15000

    def take_damage(self, enemydamage):
        if not self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit > 1000:
                self.health -= max(enemydamage - (self.damage_reduction + self.permanent_damage_reduction), 0)
                self.speed = max(self.speed - 1, 1)
                self.last_hit = current_time

    def special_attack(self):
        if self.special_attack_ready:
            for sprite in all_sprites:
                if isinstance(sprite, (NightCrawler, BossEnemy, Malakar)):
                    distance = math.hypot(self.rect.centerx - sprite.rect.centerx, self.rect.centery - sprite.rect.centery)
                    if distance <= WIDTH // 5:
                        sprite.health -= 500
                        sprite.freeze()
                        if sprite.health <= 0:
                            sprite.kill()
                            self.experience += 50
                            if isinstance(sprite, BossEnemy):
                                self.experience += 500
                            if isinstance(sprite, Malakar):
                                self.experience += 1000
                                global malakar_spawn_allowed_time
                                malakar_spawn_allowed_time = pygame.time.get_ticks() + 15000
            self.special_attack_ready = False
            self.special_attack_time = pygame.time.get_ticks() + 30000

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.invulnerable and current_time > self.invuln_end_time:
            self.invulnerable = False
            self.image = self.default_image

        if current_time > self.melon_end_time:
            self.damage = self.base_damage + self.permanent_damage_boost

        self.damage_reduction = sum(10 for end_time in self.damage_reduction_end_times if current_time <= end_time)
        self.damage_reduction_end_times = [end_time for end_time in self.damage_reduction_end_times if current_time <= end_time]

        if current_time > self.speed_boost_end_time:
            self.speed = self.base_speed + self.permanent_speed_boost

        if current_time - self.last_regen_time > 5000 and self.health < self.max_health:
            self.health += 1
            self.last_regen_time = current_time

        if not self.special_attack_ready and current_time > self.special_attack_time:
            self.special_attack_ready = True

        if self.flamefruit_active and current_time > self.flamefruit_end_time:
            self.flamefruit_active = False

class Enemy(BaseSprite):
    def __init__(self, x, y, image, health, speed_range, aggro_radius):
        super().__init__(x, y, image)
        self.health = health
        self.speed = random.uniform(*speed_range)
        self.aggro_radius = aggro_radius
        self.freeze_end_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time < self.freeze_end_time:
            self.speed = 0
            self.image.fill(RED, special_flags=pygame.BLEND_MULT)
        else:
            self.speed = random.uniform(0.5, 1.5)
            if hasattr(self, 'original_color'):
                self.image = self.original_color

        if pygame.sprite.collide_circle_ratio(self.aggro_radius / self.rect.width)(self, player):
            self.move_towards(player.rect.center)
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(self.calculate_damage())

        elif player.flamefruit_active and player.flamefruit_position:
            self.move_towards(player.flamefruit_position)

    def move_towards(self, target):
        dx, dy = target[0] - self.rect.centerx, target[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def calculate_damage(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def freeze(self):
        self.speed = 0
        self.freeze_end_time = pygame.time.get_ticks() + 2000
        self.original_color = self.image.copy()
        self.image.fill(RED, special_flags=pygame.BLEND_MULT)

class NightCrawler(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, images["enemy"], 100, (0.5, 1.5), WIDTH // 5)

    def calculate_damage(self):
        return 1 + player.level // 4

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, images["bossenemy"], 500, (0.5, 1.5), WIDTH // 5)

    def calculate_damage(self):
        return 10 + player.level // 2

class Malakar(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, images["malakar"], 5000, (0.5, 1.5), WIDTH // 2)

    def calculate_damage(self):
        return 10 + player.level

class Fruit(BaseSprite):
    def __init__(self, x, y, name):
        super().__init__(x, y, images[name])
        self.name = name

class Ripple(BaseSprite):
    def __init__(self, x, y):
        super().__init__(x, y, images["ripple"])
        self.speed = 1

    def update(self):
        nearest_enemy = min(
            enemies.sprites() + bossenemies.sprites() + malakar_group.sprites(),
            key=lambda enemy: math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery),
            default=None
        )
        if nearest_enemy:
            self.move_towards(nearest_enemy.rect.center)
            if pygame.sprite.collide_rect(self, nearest_enemy):
                nearest_enemy.health -= 10000
                if nearest_enemy.health <= 0:
                    nearest_enemy.kill()
                self.kill()

    def move_towards(self, target):
        dx, dy = target[0] - self.rect.centerx, target[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

def spawn_ripple(position):
    ripple = Ripple(*position)
    all_sprites.add(ripple)

def draw_inventory(surface, player):
    pygame.draw.rect(surface, BLUE, (0, PLAYABLE_HEIGHT, WIDTH, HEIGHT - PLAYABLE_HEIGHT))
    x_offset, y_offset = 10, PLAYABLE_HEIGHT + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, WHITE)
        x_offset += 50

def draw_legend(surface):
    legend_text = ["Arrow Keys: Move", "Spacebar: Attack", "N: Special Attack", "P: Pause"]
    x, y = WIDTH - 150, HEIGHT - 50
    for line in legend_text:
        draw_text(surface, line, 18, x, y, WHITE)
        y += 20

def draw_health_bar(surface, x, y, health, max_health, width, height, border=2):
    fill = max(health, 0) / max_health * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, RED if health > max_health * 0.1 else WHITE, fill_rect)
    pygame.draw.rect(surface, BLUE, outline_rect, border)

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

def increase_max_health():
    player.max_health += 10

def increase_speed():
    player.permanent_speed_boost += 1

def increase_level():
    player.level += 1

def increase_damage_reduction():
    player.permanent_damage_reduction += 5

def increase_damage():
    player.permanent_damage_boost += 5

player = Player()
all_sprites = pygame.sprite.Group()
fruits = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bossenemies = pygame.sprite.Group()
malakar_group = pygame.sprite.Group()
all_sprites.add(player)

fruit_images = {
    "gleamberry": images["gleamberry"],
    "shimmeringapple": images["shimmeringapple"],
    "etherealpear": images["etherealpear"],
    "flamefruit": images["flamefruit"],
    "moonbeammelon": images["moonbeammelon"]
}

for _ in range(10):
    name = random.choice(list(fruit_images.keys()))
    fruit = Fruit(random.randint(0, WIDTH - 30), random.randint(0, PLAYABLE_HEIGHT - 30), name)
    fruits.add(fruit)
    all_sprites.add(fruit)

for _ in range(10):
    enemy = NightCrawler(random.randint(0, WIDTH - 45), random.randint(0, PLAYABLE_HEIGHT - 45))
    enemies.add(enemy)
    all_sprites.add(enemy)

running, paused, game_won = True, False, False
clock = pygame.time.Clock()

fruit_spawn_time, enemy_spawn_time = pygame.time.get_ticks(), pygame.time.get_ticks()
bossenemy_spawn_time, malakar_spawn_allowed_time = pygame.time.get_ticks(), pygame.time.get_ticks() + 30000
show_fruit_name, fruit_name, fruit_name_time = False, "", 0

def show_menu():
    screen.fill(BLACK)
    draw_text(screen, "Elysian Grove Adventure", 50, WIDTH // 2, HEIGHT // 4, WHITE)
    draw_text(screen, "Press S to Start", 30, WIDTH // 2, HEIGHT // 2, WHITE)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return

def show_upgrade_menu():
    screen.fill(BLACK)
    options = [
        ("Increase Max Health with Gleam Berry", "gleamberry", increase_max_health),
        ("Increase Speed with Shimmering Apple", "shimmeringapple", increase_speed),
        ("Increase Level with Ethereal Pear", "etherealpear", increase_level),
        ("Increase Damage Reduction with Flamefruit", "flamefruit", increase_damage_reduction),
        ("Increase Damage with Moonbeam Melon", "moonbeammelon", increase_damage)
    ]
    for i, (text, fruit, action) in enumerate(options):
        draw_text(screen, f"Press {i + 1} to {text}", 30, WIDTH // 2, HEIGHT // 2 - 60 + i * 30, WHITE)
    draw_text(screen, "Press P to Resume Game", 30, WIDTH // 2, HEIGHT // 2 + 90, WHITE)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    index = event.key - pygame.K_1
                    fruit = options[index][1]
                    if player.inventory[fruit] > 0:
                        action()
                        player.inventory[fruit] -= 1

show_menu()

while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    show_upgrade_menu()
            if event.key == pygame.K_n and not paused:
                player.special_attack()

    if not paused and not game_won and player.health > 0:
        keys = pygame.key.get_pressed()
        dx, dy = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        collected_fruits = pygame.sprite.spritecollide(player, fruits, True)
        for fruit in collected_fruits:
            fruit_name = player.collect_fruit(fruit)
            show_fruit_name, fruit_name_time = True, current_time

        enemies_hit = pygame.sprite.spritecollide(player, enemies, False)
        bossenemies_hit = pygame.sprite.spritecollide(player, bossenemies, False)
        malakar_hit = pygame.sprite.spritecollide(player, malakar_group, False)
        if keys[pygame.K_SPACE]:
            for enemy in enemies_hit:
                player.attack(enemy)
            for bossenemy in bossenemies_hit:
                player.attack(bossenemy)
            for malakar in malakar_hit:
                player.attack(malakar)

        if current_time - fruit_spawn_time >= 2000:
            name = random.choice(list(fruit_images.keys()))
            fruit = Fruit(random.randint(0, WIDTH - 30), random.randint(0, PLAYABLE_HEIGHT - 30), name)
            fruits.add(fruit)
            all_sprites.add(fruit)
            fruit_spawn_time = current_time

        if current_time - enemy_spawn_time >= 2000:
            enemy = NightCrawler(random.randint(0, WIDTH - 45), random.randint(0, PLAYABLE_HEIGHT - 45))
            enemies.add(enemy)
            all_sprites.add(enemy)
            enemy_spawn_time = current_time

        if len(bossenemies) < 3 and current_time - bossenemy_spawn_time >= 5000:
            bossenemy = BossEnemy(random.randint(0, WIDTH - 90), random.randint(0, PLAYABLE_HEIGHT - 90))
            bossenemies.add(bossenemy)
            all_sprites.add(bossenemy)
            bossenemy_spawn_time = current_time

        if len(bossenemies) == 0 and len(malakar_group) == 0 and current_time > malakar_spawn_allowed_time:
            malakar = Malakar(random.randint(0, WIDTH - 90), random.randint(0, PLAYABLE_HEIGHT - 90))
            malakar_group.add(malakar)
            all_sprites.add(malakar)

        all_sprites.update()

    screen.blit(images["background"], (0, 0))
    all_sprites.draw(screen)
    draw_inventory(screen, player)
    draw_legend(screen)

    for enemy in enemies:
        draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 10, enemy.health, 100, 40, 5)
    for bossenemy in bossenemies:
        draw_health_bar(screen, bossenemy.rect.x, bossenemy.rect.y - 10, bossenemy.health, 500, 40, 5)
    for malakar in malakar_group:
        draw_health_bar(screen, malakar.rect.x, malakar.rect.y - 10, malakar.health, 5000, 40, 5)

    draw_health_bar(screen, player.rect.x - 10, player.rect.y - 15, player.health, player.max_health, 60, 10, 2)
    draw_text(screen, f'Speed: {player.speed}', 18, WIDTH - 100, 10, WHITE)
    draw_text(screen, f'Damage: {player.damage}', 18, WIDTH - 100, 30, WHITE)
    draw_text(screen, f'Damage Reduction: {player.damage_reduction}', 18, WIDTH - 100, 50, WHITE)
    draw_text(screen, f'Level: {player.level}', 18, 50, 10, WHITE)
    draw_text(screen, f'Experience: {player.experience}', 18, 150, 10, WHITE)
    draw_text(screen, f'Health: {int(player.health)}', 18, 250, 10, WHITE)

    if player.health <= 0:
        draw_text(screen, 'GAME OVER', 50, WIDTH // 2, HEIGHT // 2, RED)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    if player.level >= 100:
        draw_text(screen, 'YOU WIN', 50, WIDTH // 2, HEIGHT // 2, GREEN)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
        game_won = True

    if show_fruit_name and current_time - fruit_name_time < 1000:
        draw_text(screen, f'Collected: {fruit_name}', 30, WIDTH // 2, PLAYABLE_HEIGHT + 10, GREEN)
    else:
        show_fruit_name = False

    if player.invulnerable:
        draw_text(screen, 'Status: Invulnerable', 18, WIDTH // 2, PLAYABLE_HEIGHT + 30, GREEN)

    if paused:
        draw_text(screen, 'PAUSED', 50, WIDTH // 2, HEIGHT // 2, BLUE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
