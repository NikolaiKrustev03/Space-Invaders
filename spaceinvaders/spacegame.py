import math
import random
from typing import List

import pygame

pygame.init()

# Screen
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Color constants
black = (0, 0, 0)
white = (255, 255, 255)

# Background
background = pygame.image.load('aRTU1s.png')
background_scaledown = pygame.transform.scale(background, (screen_width, screen_height))

# Title and Icons
pygame.display.set_caption("Space Invaders")
icon_player = pygame.image.load('space_invaders.png')
pygame.display.set_icon(icon_player)
icon_enemy = pygame.image.load('enemy.png')
icon_bullet = pygame.image.load('bullet.png')
bullet_rotated = pygame.transform.rotate(icon_bullet, 45)
bullet_scaledown = pygame.transform.scale(bullet_rotated,
                                          (bullet_rotated.get_width() // 3, bullet_rotated.get_height() // 3))

# Variables
clock = pygame.time.Clock()
dt = 0
player_speed = 300
enemy_hit_count = 0
num_enemies = 5
highscore_count = 0
font = pygame.font.Font(None, 36)
font_game_over = pygame.font.Font(None, 100)
game_over_count = 5
bg_y = 0


class BaseCharacter:
    def __init__(self, x_y: List, base_character_image):
        self.x_y = x_y
        self.character_img = base_character_image


# Player
class Player(BaseCharacter):
    def __init__(self, x_y: List, player_image):
        super().__init__(x_y, player_image)


# Enemy
class Enemy(BaseCharacter):
    def __init__(self, x_y: List, enemy_image, direction):
        super().__init__(x_y, enemy_image)
        self.direction = direction


# Bullet
class Bullet(BaseCharacter):
    def __init__(self, x_y: List, bullet_image, bullet_state):
        super().__init__(x_y, bullet_image)
        self.bullet_state = bullet_state


# Define functions
def character_creation(character_img, x_y: List[int]):
    screen.blit(character_img, x_y)


def enemy_hit(enemy: Enemy):
    global enemy_hit_count
    global game_over_count
    enemy.x_y[0] += player_speed // 1.5 * dt * enemy.direction

    # Define hitboxes
    enemy_hitbox = pygame.Rect(enemy.x_y[0], enemy.x_y[1], 64, 64)
    player_hitbox = pygame.Rect(player.x_y[0], player.x_y[1], 64, 64)

    # Check if the enemy hits the player
    if enemy_hitbox.colliderect(player_hitbox):
        enemy.x_y = [random.randint(0, screen_width - 64), random.randint(0, 150)]
        game_over_count -= 1
    # Check if the enemy goes below the map
    elif enemy.x_y[1] > screen_height:
        enemy.x_y = [random.randint(0, screen_width - 64), 0]
        game_over_count -= 1
    # Check if the enemy reaches the screen boundaries
    elif enemy.x_y[0] <= 0 or enemy.x_y[0] >= screen_width - 64:
        enemy.direction *= -1
        enemy.x_y[1] += 50


def fire_bullet():
    if bullet.bullet_state == "ready":
        bullet.bullet_state = "fire"
        bullet.x_y = [player.x_y[0] + 20, player.x_y[1] - 10]


def collision(enemy_x_y: List[int], bullet_x_y: List[int]):
    enemy_x, enemy_y = enemy_x_y[0], enemy_x_y[1]
    bullet_x, bullet_y = bullet_x_y[0], bullet_x_y[1]

    if (
            bullet.bullet_state == "fire" and
            bullet_x < enemy_x + 64 and
            bullet_x + 64 > enemy_x and
            bullet_y < enemy_y + 64 and
            bullet_y + 64 > enemy_y
    ):
        bullet.x_y = [player.x_y[0] + 20, player.x_y[1] - 10]
        bullet.bullet_state = "ready"
        return True

    return False

# Initialise sprites
player = Player([screen_width / 2, screen_height - 100], icon_player)
enemies = [Enemy([random.randint(0, screen_width - 64), random.randint(0, 150)], icon_enemy, 1) for _ in
           range(num_enemies)]
bullet = Bullet([player.x_y[0] + 20, player.x_y[1] - 10], bullet_scaledown, "ready")


def game():
    running = True
    while running:
        global highscore_count, bg_y, dt, game_over_count, enemies
        # Background scrolling
        bg_y += player_speed * dt
        if bg_y > background_scaledown.get_height():
            bg_y = 0  # Reset to the top for seamless looping

        # Draw the background
        screen.blit(background_scaledown, (0, bg_y))
        screen.blit(background_scaledown, (0, bg_y - background_scaledown.get_height()))
        high_score = font.render(f"Kills: {highscore_count}", True, white)
        game_over = font_game_over.render(f"Game Over.", True, white)
        lives_left = font.render(f"Lives left: {game_over_count}", True, white)
        restart = font_game_over.render("Press R to restart", True, white)
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.x_y[1] -= player_speed * dt
        if keys[pygame.K_s]:
            player.x_y[1] += player_speed * dt
        if keys[pygame.K_a]:
            player.x_y[0] -= player_speed * dt
        if keys[pygame.K_d]:
            player.x_y[0] += player_speed * dt

        if keys[pygame.K_SPACE]:
            fire_bullet()

        # Bullet state changes, fires
        if bullet.bullet_state == "fire":
            character_creation(bullet.character_img, bullet.x_y)
            bullet.x_y[1] -= player_speed * 1.2 * dt

        # Bullet reloads
        if bullet.x_y[1] < -100:
            bullet.x_y = [player.x_y[0] + 20, player.x_y[1] - 10]
            bullet.bullet_state = "ready"
        if game_over_count <= 0:
            for enemy in enemies:
                enemy.x_y[0], enemy.x_y[1] = 100, 100
            player.x_y[0], player.x_y[1] = screen_width // 2, screen_height // 2
            screen.blit(game_over, (400, 400))
            screen.blit(restart, (400, 500))
            if keys[pygame.K_r]:
                game_over_count = 5
                enemies = [Enemy([random.randint(0, screen_width - 64), random.randint(0, 150)], icon_enemy, 1) for _ in
                           range(num_enemies)]
                game()
        else:
            for enemy in enemies:
                enemy_hit(enemy)
                character_creation(enemy.character_img, enemy.x_y)
                is_collision = collision(enemy.x_y, bullet.x_y)
                screen.blit(lives_left, (10, 70))
                if is_collision:
                    enemy.x_y[0], enemy.x_y[1] = random.randint(0, 150), random.randint(0, 150)
                    bullet.x_y = [player.x_y[0] + 20, player.x_y[1] - 10]
                    bullet.bullet_state = "ready"
                    highscore_count += 1

        player.x_y[0] = max(0, min(player.x_y[0], screen_width - 64))
        player.x_y[1] = max(700 - 64, min(player.x_y[1], 800 - 64))

        screen.blit(high_score, (10, 10))
        character_creation(player.character_img, player.x_y)

        pygame.display.update()


game()
