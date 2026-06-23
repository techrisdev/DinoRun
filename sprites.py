import pygame
from constants import *
import traceback
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Versuche das Bild zu laden, ansonsten ein grünes Rechteck
        try:
            self.image = PLAYER_IMAGE.convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except:
            traceback.print_exc()
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.math.Vector2(0, 0) # X ist links/rechts, Y ist oben/unten
        self.speed = 4
        self.gravity = 0.7
        self.jump_speed = -14
        
        self.lives = 3              # Start-Leben
        self.has_fireball = False   # Kann Feuerball schießen
        self.powerup_timer = 0       # Zählt die Zeit der Superpower runter
        self.fireball_request = False
        self.is_invincible = False
    
    def apply_gravity(self):
        # Zieht den Spieler jede Sekunde ein Stück nach unten
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        # Gibt einen Stoß nach oben
        self.direction.y = self.jump_speed



    # W muss erst released werden damit es nicht gespammed werden kann und der Player nicht an Blöcken hängen bleiben kann
    w_is_pressed = False

    def update(self):
        # Tasten abfragen für WASD
        keys = pygame.key.get_pressed()

        
        # A und D für links und rechts
        if keys[pygame.K_d]: 
            self.direction.x = 1

            # Animation für laufen
            if random.randint(0,1) == 1:
                self.image = PLAYER_WALKING_1
            else:
                self.image = PLAYER_WALKING_2
            
            self.image = self.image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        elif keys[pygame.K_a]: 
            self.direction.x = -1
        else: 
            self.direction.x = 0

        # Sicherstellen, dass die Maske immer zum aktuellen Bild passt
        self.mask = pygame.mask.from_surface(self.image)
        
        
        # W zum Springen (nur wenn man auf dem Boden steht und W released wurde)
        if not self.w_is_pressed:
            if keys[pygame.K_w] and self.direction.y == 0:
                self.jump()
                self.w_is_pressed = True

        if not keys[pygame.K_w]:
            self.w_is_pressed = False
        
        # Space zum Schießen, wenn Powerup aktiv ist
        if keys[pygame.K_SPACE] and self.has_fireball and not self.fireball_request:
            self.fireball_request = True
        if not keys[pygame.K_SPACE]:
            self.fireball_request = False

        # Powerup-Timer
        if self.has_fireball:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.has_fireball = False
                self.is_invincible = False

    # W muss erst released werden damit es nicht gespammed werden kann und der Player nicht an Blöcken hängen bleiben kann
    w_is_pressed = False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        if enemy_type == "exploder":
            self.image = EXPLODER_IMAGE.convert_alpha()
        elif enemy_type == "jumper":
            self.image = JUMPER_IMAGE.convert_alpha()
        else:
            self.image = ENEMY_IMAGE.convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 1
        self.direction = -1
        self.v_speed = 0
        self.gravity = 0.6 if enemy_type == "jumper" else 0.8
        self.jump_strength = -13 if enemy_type == "jumper" else 0
        self.world_x = x  # Weltposition (wird für Horizontal-Bewegung verwendet)
        self.near_player_timer = 0
        self.explosion_radius = TILE_SIZE * 3
        self.has_exploded = False

    def apply_gravity(self):
        """Wendet Schwerkraft an."""
        self.v_speed += self.gravity
        self.rect.y += self.v_speed

    def check_explode(self, player):
        if self.enemy_type != "exploder" or self.has_exploded:
            return False
        proximity_rect = player.rect.inflate(TILE_SIZE * 3, TILE_SIZE * 3)
        if self.rect.colliderect(proximity_rect):
            self.near_player_timer += 1
        else:
            self.near_player_timer = 0

            # Nach 45 Frames explodiert der Gegner jetzt später
        if self.near_player_timer >= 45:
            self.has_exploded = True
            return True
        return False

    def update(self, x_shift):
        if not self.enemy_type == "jumper":
            self.rect.x += self.speed * self.direction
        self.apply_gravity()
        self.rect.x += x_shift


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = FIREBALL_IMAGE.convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = direction if direction != 0 else 1
        self.speed = 10

    def update(self, x_shift):
        self.rect.x += self.speed * self.direction
        self.rect.x += x_shift


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Die Bodenblöcke (Berge)
        self.image = TILE_IMAGE.convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, x_shift):
        self.rect.x += x_shift

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Tödliche Stacheln
        self.image = SPIKES_IMAGE.convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, x_shift):
        self.rect.x += x_shift

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = POWERUP_IMAGE.convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, x_shift):
        self.rect.x += x_shift

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = GOAL_IMAGE.convert_alpha() if hasattr(GOAL_IMAGE, 'convert_alpha') else GOAL_IMAGE.copy()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, x_shift):
        self.rect.x += x_shift