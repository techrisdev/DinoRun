import pygame
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent

# --- GRUNDEINSTELLUNGEN ---
SCREEN_WIDTH = 1920   # Breite des Fensters
SCREEN_HEIGHT = 1080  # Höhe des Fensters
TILE_SIZE = 40       # Größe eines Quadrats (Boden, Spieler, Gegner)
FPS = 60              # Bilder pro Sekunde (Sorgt für flüssiges Spiel)

# Farben (RGB Werte)
SKY_BLUE = (135, 206, 235)  # Hintergrundfarbe
RED = (255, 0, 0)           # Standardfarbe für Gegner
GOLD = (255, 215, 0)        # Farbe für das Superpower-Item
DARK_GREY = (50, 50, 50)    # Farbe für die Spikes

IMAGE_PATH = BASE_PATH / "images"

PLAYER_IMAGE = pygame.image.load(str(IMAGE_PATH / "player.png"))
ENEMY_IMAGE = pygame.image.load(str(IMAGE_PATH / "enemy.png"))
EXPLODER_IMAGE = pygame.image.load(str(IMAGE_PATH / "exploderenemy.png"))
JUMPER_IMAGE = pygame.image.load(str(IMAGE_PATH / "jumper.png"))

PLAYER_WALKING_1 = pygame.image.load(str(IMAGE_PATH / "dinowalking1.png"))
PLAYER_WALKING_2 = pygame.image.load(str(IMAGE_PATH / "dinowalking2.png"))
SPIKES_IMAGE = pygame.image.load(str(IMAGE_PATH / "spikes.png"))
POWERUP_IMAGE = pygame.image.load(str(IMAGE_PATH / "powerup.png"))
POWEREDUPPLAYER_IMAGE = pygame.image.load(str(IMAGE_PATH / "poweredupplayer.png"))
BACKGROUND_IMAGE = pygame.image.load(str(IMAGE_PATH / "background.png"))
FIREBALL_IMAGE = pygame.image.load(str(IMAGE_PATH / "fireball.png"))
TILE_IMAGE = pygame.image.load(str(IMAGE_PATH / "gras squared.png"))
try:
    GOAL_IMAGE = pygame.image.load(str(IMAGE_PATH / "goal.png"))
except Exception:
    # Fallback: Ein goldenes Rechteck als Ziel
    GOAL_IMAGE = pygame.Surface((TILE_SIZE, TILE_SIZE))
    GOAL_IMAGE.fill(GOLD)
