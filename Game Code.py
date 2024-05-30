import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Configuration dictionary
config = {
    "width": 800,
    "height": 600,
    "playable_height": 540,
    "colors": {
        "white": (255, 255, 255),
        "green": (0, 255, 0),
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "black": (0, 0, 0),
    },
    "player": {
        "base_speed": 5,
        "base_damage": 20,
        "health": 100,
        "max_health": 100,
    },
    "enemy_health": {
        "enemy": 100,
        "bossenemy": 500,
        "malakar": 5000,
    },
    "enemy_damages": {
        "enemy": lambda level: 1 + level // 4,
        "bossenemy": lambda level: 10 + level // 2,
        "malakar": lambda level: 10 + level,
    }
}

# Screen dimensions
screen = pygame.display.set_mode((config["width"], config["height"]))
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
luminara_img = load_image("luminara.png")
luminara_img = pygame.transform.scale(luminara_img, (90, 90))
luminara_invuln_img = pygame.transform.scale(load_image("luminarainvuln.png"), (90, 90))
enemy_img = load_image("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (67, 67))
bossenemy_img = load_image("bossenemy.png")
bossenemy_img = pygame.transform.scale(bossenemy_img, (134, 134))
malakar_img = pygame.transform.scale(load_image("malakar.png"), (268, 268))
background_img = load_image("background.png")
ripple_img = load_image("ripple.png")
ripple_img = pygame.transform.scale(ripple_img, (45, 45))

# Load fruit images
fruit_images = {
    "gleamberry": pygame.transform.scale(load_image("gleamberry.png"), (45, 45)),
    "shimmeringapple": pygame.transform.scale(load_image("shimmeringapple.png"), (45, 45)),
    "etherealpear": pygame.transform.scale(load_image("etherealpear.png"), (45, 45)),
    "flamefruit": pygame.transform.scale(load_image("flamefruit.png"), (45, 45)),
    "moonbeammelon": pygame.transform.scale(load_image("moonbeammelon.png"), (45, 45)),
}

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.default_image = image
        self.invuln_image = luminara_invuln_img
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.center = (config["width"] // 2, config["playable_height"] // 2)
        self.base_speed = config["player"]["base_speed"]
        self.permanent_speed_boost = 0
        self.speed = self.base_speed
        self.base_damage = config["player"]["base_damage"]
        self.permanent_damage_boost = 0
        self.damage = self.base_damage
        self.experience = 0
        self.level = 1
        self.health = config["player"]["health"]
        self.max_health = config["player"]["max_health"]
        self.inventory = {key: 0 for key in fruit_images.keys()}
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
        self.rect.x = max(0, min(self.rect.x + dx * self.speed, config["width"] - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + dy * self.speed, config["playable_height"] - self.rect.height))

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
                    if distance <= config["width"] // 5:
                        sprite.health -= 500
                        sprite.speed = 0
                        sprite.freeze_end_time = pygame.time.get_ticks() + 2000
                        sprite.image.fill(config["colors"]["red"], special_flags=pygame.BLEND_MULT)
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

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image_key):
        super().__init__()
        self.image = globals()[f"{image_key}_img"]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = config["enemy_health"][image_key]
        self.speed = random.uniform(0.5, 1.5)
        self.aggro_radius = config["width"] // 5
        self.freeze_end_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time < self.freeze_end_time:
            self.speed = 0
            self.image.fill(config["colors"]["red"], special_flags=pygame.BLEND_MULT)
        else:
            self.speed = random.uniform(0.5, 1.5)
        if pygame.sprite.collide_circle_ratio(self.aggro_radius / self.rect.width)(self, player):
            dx = (player.rect.x - self.rect.x) / math.hypot(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
            dy = (player.rect.y - self.rect.y) / math.hypot(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(config["enemy_damages"][self.__class__.__name__.lower()](player.level))

# Boss Enemy class
class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "bossenemy")
        self.aggro_radius = config["width"] // 5

# Malakar class
class Malakar(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "malakar")
        self.aggro_radius = config["width"] // 2

# Fruit class
class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.image = fruit_images[name]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name

# Ripple class
class Ripple(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ripple_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1

    def update(self):
        nearest_enemy = min((sprite for sprite in all_sprites if isinstance(sprite, (Enemy, BossEnemy, Malakar))),
                            key=lambda enemy: math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery),
                            default=None)
        if nearest_enemy:
            dx = (nearest_enemy.rect.x - self.rect.x) / math.hypot(nearest_enemy.rect.x - self.rect.x, nearest_enemy.rect.y - self.rect.y)
            dy = (nearest_enemy.rect.y - self.rect.y) / math.hypot(nearest_enemy.rect.x - self.rect.x, nearest_enemy.rect.y - self.rect.y)
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            if pygame.sprite.collide_rect(self, nearest_enemy):
                nearest_enemy.health -= 10000
                if nearest_enemy.health <= 0:
                    nearest_enemy.kill()
                self.kill()

# Additional functions
def spawn_ripple(position):
    ripple = Ripple(*position)
    all_sprites.add(ripple)

def draw_inventory(surface, player):
    pygame.draw.rect(surface, config["colors"]["blue"], (0, config["playable_height"], config["width"], config["height"] - config["playable_height"]))
    x_offset, y_offset = 10, config["playable_height"] + 10
    for fruit, image in fruit_images.items():
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, config["colors"]["white"])
        x_offset += 50
    if player.invulnerable:
        draw_text(surface, 'Status: Invulnerable', 18, x_offset + 30, config["playable_height"] + 10, config["colors"]["green"])

def draw_legend(surface):
    legend_text = ["Arrow Keys: Move", "Spacebar: Attack", "N: Special Attack", "P: Pause"]
    x, y = config["width"] - 150, config["height"] - 50
    for line in legend_text:
        draw_text(surface, line, 18, x, y, config["colors"]["white"])
        y += 20

def draw_health_bar(surface, x, y, health, max_health, width, height, border=2):
    health = max(0, health)
    fill = (health / max_health) * width
    outline_rect, fill_rect = pygame.Rect(x, y, width, height), pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, config["colors"]["red"] if health > max_health * 0.1 else config["colors"]["white"], fill_rect)
    pygame.draw.rect(surface, config["colors"]["blue"], outline_rect, border)

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

# Create player and groups
player = Player(luminara_img)
all_sprites = pygame.sprite.Group(player)
fruits = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bossenemies = pygame.sprite.Group()
malakar_group = pygame.sprite.Group()

fruit_names = list(fruit_images.keys())
for _ in range(10):
    fruit = Fruit(random.randint(0, config["width"] - 30), random.randint(0, config["playable_height"] - 30), random.choice(fruit_names))
    fruits.add(fruit)
    all_sprites.add(fruit)

for _ in range(10):
    enemy = Enemy(random.randint(0, config["width"] - 45), random.randint(0, config["playable_height"] - 45), "enemy")
    enemies.add(enemy)
    all_sprites.add(enemy)

# Main game loop
running, paused, game_won = True, False, False
clock = pygame.time.Clock()
fruit_spawn_time, enemy_spawn_time, bossenemy_spawn_time = pygame.time.get_ticks(), pygame.time.get_ticks(), pygame.time.get_ticks()
malakar_spawn_allowed_time = pygame.time.get_ticks() + 30000
show_fruit_name, fruit_name, fruit_name_time = False, "", 0

# Main menu
def show_menu():
    screen.fill(config["colors"]["black"])
    draw_text(screen, "Elysian Grove Adventure", 50, config["width"] // 2, config["height"] // 4, config["colors"]["white"])
    draw_text(screen, "Press S to Start", 30, config["width"] // 2, config["height"] // 2, config["colors"]["white"])
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                waiting = False

def show_upgrade_menu():
    upgrades = [
        ("Increase Max Health with Gleam Berry", "gleamberry", lambda: setattr(player, 'max_health', player.max_health + 10)),
        ("Increase Speed with Shimmering Apple", "shimmeringapple", lambda: setattr(player, 'permanent_speed_boost', player.permanent_speed_boost + 1)),
        ("Increase Level with Ethereal Pear", "etherealpear", lambda: setattr(player, 'level', player.level + 1)),
        ("Increase Damage Reduction with Flamefruit", "flamefruit", lambda: setattr(player, 'permanent_damage_reduction', player.permanent_damage_reduction + 5)),
        ("Increase Damage with Moonbeam Melon", "moonbeammelon", lambda: setattr(player, 'permanent_damage_boost', player.permanent_damage_boost + 5)),
    ]
    screen.fill(config["colors"]["black"])
    draw_text(screen, "Upgrade Menu", 50, config["width"] // 2, config["height"] // 4, config["colors"]["white"])
    for i, (text, fruit, func) in enumerate(upgrades, start=1):
        draw_text(screen, f"Press {i} to {text}", 30, config["width"] // 2, config["height"] // 2 - 60 + i * 30, config["colors"]["white"])
    draw_text(screen, "Press P to Resume Game", 30, config["width"] // 2, config["height"] // 2 + 90, config["colors"]["white"])
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                for i, (text, fruit, func) in enumerate(upgrades, start=1):
                    if event.key == getattr(pygame, f'K_{i}') and player.inventory[fruit] > 0:
                        func()
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
        dx, dy = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]), (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        player.move(dx, dy)

        collected_fruits = pygame.sprite.spritecollide(player, fruits, True)
        for fruit in collected_fruits:
            player.collect_fruit(fruit)
            show_fruit_name, fruit_name, fruit_name_time = True, fruit.name, current_time

        enemies_hit = pygame.sprite.spritecollide(player, enemies, False)
        bossenemies_hit = pygame.sprite.spritecollide(player, bossenemies, False)
        malakar_hit = pygame.sprite.spritecollide(player, malakar_group, False)
        if keys[pygame.K_SPACE]:
            for enemy in enemies_hit + bossenemies_hit + malakar_hit:
                player.attack(enemy)

        if current_time - fruit_spawn_time >= 2000:
            fruit = Fruit(random.randint(0, config["width"] - 30), random.randint(0, config["playable_height"] - 30), random.choice(fruit_names))
            fruits.add(fruit)
            all_sprites.add(fruit)
            fruit_spawn_time = current_time

        if current_time - enemy_spawn_time >= 2000:
            enemy = Enemy(random.randint(0, config["width"] - 45), random.randint(0, config["playable_height"] - 45), "enemy")
            enemies.add(enemy)
            all_sprites.add(enemy)
            enemy_spawn_time = current_time

        if len(bossenemies) < 3 and current_time - bossenemy_spawn_time >= 5000:
            bossenemy = BossEnemy(random.randint(0, config["width"] - 90), random.randint(0, config["playable_height"] - 90))
            bossenemies.add(bossenemy)
            all_sprites.add(bossenemy)
            bossenemy_spawn_time = current_time

        if len(bossenemies) == 0 and len(malakar_group) == 0 and current_time > malakar_spawn_allowed_time:
            malakar = Malakar(random.randint(0, config["width"] - 90), random.randint(0, config["playable_height"] - 90))
            malakar_group.add(malakar)
            all_sprites.add(malakar)

        all_sprites.update()

    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_inventory(screen, player)
    draw_legend(screen)
    for enemy in enemies:
        draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 10, enemy.health, config["enemy_health"]["enemy"], 40, 5)
    for bossenemy in bossenemies:
        draw_health_bar(screen, bossenemy.rect.x, bossenemy.rect.y - 10, bossenemy.health, config["enemy_health"]["bossenemy"], 40, 5)
    for malakar in malakar_group:
        draw_health_bar(screen, malakar.rect.x, malakar.rect.y - 10, malakar.health, config["enemy_health"]["malakar"], 40, 5)
    draw_health_bar(screen, player.rect.x - 10, player.rect.y - 15, player.health, player.max_health, 60, 10, 2)
    draw_text(screen, f'Speed: {player.speed}', 18, config["width"] - 100, 10, config["colors"]["white"])
    draw_text(screen, f'Damage: {player.damage}', 18, config["width"] - 100, 30, config["colors"]["white"])
    draw_text(screen, f'Damage Reduction: {player.damage_reduction}', 18, config["width"] - 100, 50, config["colors"]["white"])
    draw_text(screen, f'Level: {player.level}', 18, 50, 10, config["colors"]["white"])
    draw_text(screen, f'Experience: {player.experience}', 18, 150, 10, config["colors"]["white"])
    draw_text(screen, f'Health: {int(player.health)}', 18, 250, 10, config["colors"]["white"])
    if player.health <= 0:
        draw_text(screen, 'GAME OVER', 50, config["width"] // 2, config["height"] // 2, config["colors"]["red"])
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    if player.level >= 100:
        draw_text(screen, 'YOU WIN', 50, config["width"] // 2, config["height"] // 2, config["colors"]["green"])
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
        game_won = True
    if show_fruit_name and current_time - fruit_name_time < 1000:
        draw_text(screen, f'Collected: {fruit_name}', 30, config["width"] // 2, config["playable_height"] + 10, config["colors"]["green"])
    else:
        show_fruit_name = False
    if player.invulnerable:
        draw_text(screen, 'Status: Invulnerable', 18, config["width"] // 2, config["playable_height"] + 30, config["colors"]["green"])
    if paused:
        draw_text(screen, 'PAUSED', 50, config["width"] // 2, config["height"] // 2, config["colors"]["blue"])
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
