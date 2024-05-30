import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and configuration
config = {
    "width": 800,
    "height": 600,
    "playable_height": 540,  # Leave space for inventory at the bottom
    "enemy_health": {"enemy": 100, "bossenemy": 500, "malakar": 5000},
    "enemy_damages": {
        "enemy": lambda lvl: 1 + lvl // 4,
        "bossenemy": lambda lvl: 10 + lvl // 2,
        "malakar": lambda lvl: 10 + lvl,
        "nightcrawler": lambda lvl: 1 + lvl // 4  # Ensure this key is present
    },
    "enemy_sizes": {"enemy": (67, 67), "bossenemy": (134, 134), "malakar": (268, 268)},
}

# Set up the display
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
    "moonbeammelon": pygame.transform.scale(load_image("moonbeammelon.png"), (45, 45)),
}

# Colors
WHITE, GREEN, RED, BLUE, BLACK = (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 0, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.default_image = images["luminara"]
        self.invuln_image = images["luminarainvuln"]
        self.image = self.default_image
        self.rect = self.image.get_rect(center=(config["width"] // 2, config["playable_height"] // 2))
        self.base_speed, self.permanent_speed_boost = 5, 0
        self.base_damage, self.permanent_damage_boost = 20, 0
        self.speed, self.damage = self.base_speed, self.base_damage
        self.experience, self.level = 0, 1
        self.health, self.max_health = 100, 100
        self.inventory = {fruit: 0 for fruit in ["gleamberry", "shimmeringapple", "etherealpear", "flamefruit", "moonbeammelon"]}
        self.invulnerable, self.last_hit = False, pygame.time.get_ticks()
        self.invuln_end_time, self.melon_end_time, self.last_regen_time = 0, 0, pygame.time.get_ticks()
        self.special_attack_ready, self.special_attack_time = True, 0
        self.flamefruit_end_time, self.flamefruit_active = 0, False
        self.flamefruit_position, self.speed_boost_end_time = None, 0
        self.damage_reduction, self.permanent_damage_reduction = 0, 0
        self.timed_effects = {"damage_reduction": []}

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
            self.speed = self.base_speed + self.permanent_speed_boost + 1
        elif fruit.name == "etherealpear":
            self.experience += 150
            self.health = min(self.health + 20, self.max_health)
        elif fruit.name == "flamefruit":
            self.experience += 100
            self.flamefruit_end_time = pygame.time.get_ticks() + 3000
            self.flamefruit_active = True
            self.flamefruit_position = fruit.rect.center
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
        if not self.invulnerable and pygame.time.get_ticks() - self.last_hit > 1000:
            self.health -= max(enemydamage - (self.damage_reduction + self.permanent_damage_reduction), 0)
            self.speed = max(self.speed - 1, 1)
            self.last_hit = pygame.time.get_ticks()

    def special_attack(self):
        if self.special_attack_ready:
            for sprite in all_sprites:
                if isinstance(sprite, (NightCrawler, BossEnemy, Malakar)):
                    distance = math.hypot(self.rect.centerx - sprite.rect.centerx, self.rect.centery - sprite.rect.centery)
                    if distance <= config["width"] // 5:
                        sprite.health -= 500
                        sprite.speed = 0
                        sprite.freeze_end_time = pygame.time.get_ticks() + 2000
                        sprite.original_color = sprite.image.copy()
                        sprite.image.fill(RED, special_flags=pygame.BLEND_MULT)
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

        self.damage_reduction = sum(10 for end_time in self.timed_effects["damage_reduction"] if current_time <= end_time)
        self.timed_effects["damage_reduction"] = [end_time for end_time in self.timed_effects["damage_reduction"] if current_time <= end_time]

        if current_time > self.speed_boost_end_time:
            self.speed = self.base_speed + self.permanent_speed_boost

        if current_time - self.last_regen_time > 5000 and self.health < self.max_health:
            self.health += 1
            self.last_regen_time = current_time

        if not self.special_attack_ready and current_time > self.special_attack_time:
            self.special_attack_ready = True

        if self.flamefruit_active and current_time > self.flamefruit_end_time:
            self.flamefruit_active = False

# Fruit class
class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.image = images[name]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name

# Ripple class
class Ripple(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = images["ripple"]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1

    def update(self):
        nearest_enemy = min(enemies, key=lambda enemy: math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery), default=None)
        nearest_boss = min(bossenemies, key=lambda bossenemy: math.hypot(self.rect.centerx - bossenemy.rect.centerx, self.rect.centery - bossenemy.rect.centery), default=None)
        nearest_malakar = min(malakar_group, key=lambda malakar: math.hypot(self.rect.centerx - malakar.rect.centerx, self.rect.centery - malakar.rect.centery), default=None)
        nearest_target = min(
            (nearest_enemy, nearest_boss, nearest_malakar),
            key=lambda target: math.hypot(self.rect.centerx - target.rect.centerx, self.rect.centery - target.rect.centery) if target else float('inf')
        )
        if nearest_target:
            dx, dy = nearest_target.rect.centerx - self.rect.centerx, nearest_target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance != 0:
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            if self.rect.colliderect(nearest_target.rect):
                nearest_target.health -= 10000
                if nearest_target.health <= 0:
                    nearest_target.kill()
                self.kill()

# Enemy classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image_key):
        super().__init__()
        self.image = pygame.transform.scale(load_image(f"{image_key}.png"), config["enemy_sizes"][image_key])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = config["enemy_health"][image_key]
        self.speed = random.uniform(0.5, 1.5)
        self.aggro_radius = config["width"] // 5
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

        dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx, dy = dx / distance, dy / distance

        if self.rect.colliderect(player.rect):
            player.take_damage(config["enemy_damages"][self.__class__.__name__.lower()](player.level))
        elif player.flamefruit_active and player.flamefruit_position:
            dx, dy = player.flamefruit_position[0] - self.rect.x, player.flamefruit_position[1] - self.rect.y
            distance = math.hypot(dx, dy)
            if distance != 0:
                dx, dy = dx / distance, dy / distance
        else:
            if player.rect.x - self.rect.x:
                self.rect.x += self.speed * dx
            if player.rect.y - self.rect.y:
                self.rect.y += self.speed * dy

class NightCrawler(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "enemy")

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "bossenemy")

class Malakar(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "malakar")

# Additional functions
def spawn_ripple(position):
    ripple = Ripple(*position)
    all_sprites.add(ripple)

def draw_inventory(surface, player):
    pygame.draw.rect(surface, BLUE, (0, config["playable_height"], config["width"], config["height"] - config["playable_height"]))
    x_offset, y_offset = 10, config["playable_height"] + 10
    for fruit, image in fruit_names_images:
        surface.blit(image, (x_offset, y_offset))
        draw_text(surface, str(player.inventory[fruit]), 18, x_offset + 30, y_offset, WHITE)
        x_offset += 50
    if player.invulnerable:
        draw_text(surface, 'Status: Invulnerable', 18, x_offset + 30, config["playable_height"] + 10, GREEN)

def draw_legend(surface):
    legend_text = ["Arrow Keys: Move", "Spacebar: Attack", "N: Special Attack", "P: Pause"]
    x, y = config["width"] - 150, config["height"] - 50
    for line in legend_text:
        draw_text(surface, line, 18, x, y, WHITE)
        y += 20

def draw_health_bar(surface, x, y, health, max_health, width, height, border=2):
    if health < 0:
        health = 0
    fill = (health / max_health) * width
    outline_rect, fill_rect = pygame.Rect(x, y, width, height), pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, RED if health > max_health * 0.1 else WHITE, fill_rect)
    pygame.draw.rect(surface, BLUE, outline_rect, border)

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont(None, size)
    text_surface, text_rect = font.render(text, True, color), font.render(text, True, color).get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

# Create player and groups
player = Player()
all_sprites = pygame.sprite.Group(player)
fruits, enemies, bossenemies, malakar_group = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

fruit_names_images = [("gleamberry", images["gleamberry"]), ("shimmeringapple", images["shimmeringapple"]), ("etherealpear", images["etherealpear"]), ("flamefruit", images["flamefruit"]), ("moonbeammelon", images["moonbeammelon"])]

for _ in range(10):
    name, image = random.choice(fruit_names_images)
    fruit = Fruit(random.randint(0, config["width"] - 30), random.randint(0, config["playable_height"] - 30), name)
    fruits.add(fruit)
    all_sprites.add(fruit)

for _ in range(10):
    enemy = NightCrawler(random.randint(0, config["width"] - 45), random.randint(0, config["playable_height"] - 45))
    enemies.add(enemy)
    all_sprites.add(enemy)

# Main game loop
running, paused, game_won, clock = True, False, False, pygame.time.Clock()

fruit_spawn_time, enemy_spawn_time, bossenemy_spawn_time = pygame.time.get_ticks(), pygame.time.get_ticks(), pygame.time.get_ticks()
malakar_spawn_allowed_time, ripple_spawn_allowed_time = pygame.time.get_ticks() + 30000, 0
show_fruit_name, fruit_name, fruit_name_time = False, "", 0

def show_menu():
    screen.fill(BLACK)
    draw_text(screen, "Elysian Grove Adventure", 50, config["width"] // 2, config["height"] // 4, WHITE)
    draw_text(screen, "Press S to Start", 30, config["width"] // 2, config["height"] // 2, WHITE)
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
    screen.fill(BLACK)
    upgrades = [
        ("Increase Max Health with Gleam Berry", "gleamberry", lambda: setattr(player, 'max_health', player.max_health + 10)),
        ("Increase Speed with Shimmering Apple", "shimmeringapple", lambda: setattr(player, 'permanent_speed_boost', player.permanent_speed_boost + 1)),
        ("Increase Level with Ethereal Pear", "etherealpear", lambda: setattr(player, 'level', player.level + 1)),
        ("Increase Damage Reduction with Flamefruit", "flamefruit", lambda: setattr(player, 'permanent_damage_reduction', player.permanent_damage_reduction + 5)),
        ("Increase Damage with Moonbeam Melon", "moonbeammelon", lambda: setattr(player, 'permanent_damage_boost', player.permanent_damage_boost + 5)),
    ]
    draw_text(screen, "Upgrade Menu", 50, config["width"] // 2, config["height"] // 4, WHITE)
    for i, (text, fruit, _) in enumerate(upgrades):
        draw_text(screen, f'Press {i + 1} to {text}', 30, config["width"] // 2, config["height"] // 2 - 60 + 30 * i, WHITE)
    draw_text(screen, "Press P to Resume Game", 30, config["width"] // 2, config["height"] // 2 + 90, WHITE)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                for i, (_, fruit, upgrade) in enumerate(upgrades):
                    if event.key == pygame.K_1 + i and player.inventory[fruit] > 0:
                        upgrade()
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
            name, image = random.choice(fruit_names_images)
            fruit = Fruit(random.randint(0, config["width"] - 30), random.randint(0, config["playable_height"] - 30), name)
            fruits.add(fruit)
            all_sprites.add(fruit)
            fruit_spawn_time = current_time

        if current_time - enemy_spawn_time >= 2000:
            enemy = NightCrawler(random.randint(0, config["width"] - 45), random.randint(0, config["playable_height"] - 45))
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

    screen.blit(images["background"], (0, 0))
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

    draw_text(screen, f'Speed: {player.speed}', 18, config["width"] - 100, 10, WHITE)
    draw_text(screen, f'Damage: {player.damage}', 18, config["width"] - 100, 30, WHITE)
    draw_text(screen, f'Damage Reduction: {player.damage_reduction}', 18, config["width"] - 100, 50, WHITE)

    draw_text(screen, f'Level: {player.level}', 18, 50, 10, WHITE)
    draw_text(screen, f'Experience: {player.experience}', 18, 150, 10, WHITE)
    draw_text(screen, f'Health: {int(player.health)}', 18, 250, 10, WHITE)

    if player.health <= 0:
        draw_text(screen, 'GAME OVER', 50, config["width"] // 2, config["height"] // 2, RED)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    if player.level >= 100:
        draw_text(screen, 'YOU WIN', 50, config["width"] // 2, config["height"] // 2, GREEN)
        pygame.display.flip()
        pygame.time.wait(3000)
        running, game_won = False, True

    if show_fruit_name and current_time - fruit_name_time < 1000:
        draw_text(screen, f'Collected: {fruit_name}', 30, config["width"] // 2, config["playable_height"] + 10, GREEN)
    else:
        show_fruit_name = False

    if player.invulnerable:
        draw_text(screen, 'Status: Invulnerable', 18, config["width"] // 2, config["playable_height"] + 30, GREEN)

    if paused:
        draw_text(screen, 'PAUSED', 50, config["width"] // 2, config["height"] // 2, BLUE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
