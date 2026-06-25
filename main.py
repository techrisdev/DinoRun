import sys
import random
from pathlib import Path

import pygame
from constants import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 720), pygame.FULLSCREEN)
        pygame.display.set_caption("Dino Run")
        self.clock = pygame.time.Clock()

        self.base_path = BASE_PATH
        self.level_folder = self.base_path / "levels"
        self.level_folder.mkdir(exist_ok=True)

        self.level_files = sorted(
            self.level_folder.glob("*.txt"),
            key=lambda path: int(''.join([c for c in path.stem if c.isdigit()]) or 0)
        )
        if not self.level_files:
            raise FileNotFoundError(f"Keine Level-Dateien im Ordner '{self.level_folder}' gefunden.")

        # Zufällige Hintergrundmusik laden

        music_number = random.randint(1, 2)

        music_path = self.base_path / "music" / ("music" + str(music_number) + ".mp3")
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1)  # -1 = Endlosschleife

        self.current_level_index = 0
        self.game_completed = False
        self.load_level()

    def load_level(self):
        level_path = self.level_files[self.current_level_index]
        with open(level_path, encoding="utf-8") as f:
            level_data = [line.rstrip("\n") for line in f]

        self.level = Level(level_data, self.screen, self.current_level_index + 1, level_path.stem)

    def restart_level(self):
        self.load_level()

    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index >= len(self.level_files):
            self.current_level_index = 0
        self.load_level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.game_completed:
                        pygame.quit()
                        sys.exit()
                    elif self.level.game_over:
                        self.restart_level()
                    elif self.level.level_completed:
                        if self.current_level_index == len(self.level_files) - 1:
                            # Level 10 (letzte Level) komplett - Game Completed!
                            self.game_completed = True
                        else:
                            self.next_level()

            # Hintergrund kacheln, damit die Kamera unendlich weit scrollen kann
            bg_width = BACKGROUND_IMAGE.get_width()
            screen_width = self.screen.get_width()
            offset_x = int(self.level.camera_x % bg_width)
            if offset_x > 0:
                offset_x -= bg_width
            for x in range(offset_x, screen_width, bg_width):
                self.screen.blit(BACKGROUND_IMAGE, (x, 0))

            if self.game_completed:
                self.draw_game_completed()
            else:
                self.level.run()           # Level-Logik ausführen
            
            pygame.display.update()    # Monitor aktualisieren
            self.clock.tick(FPS)       # Auf 60 Bilder begrenzen

    def draw_game_completed(self):
        """Zeichnet den Game Completed Screen."""
        font_big = pygame.font.Font(None, 80)
        font_small = pygame.font.Font(None, 50)
        
        title = font_big.render("SPIEL FERTIG!", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)
        
        message = font_small.render("Alle 10 Level geschafft!", True, (255, 255, 255))
        message_rect = message.get_rect(center=(self.screen.get_width() // 2, 280))
        self.screen.blit(message, message_rect)
        
        exit_text = font_small.render("ENTER um zu beenden", True, (100, 255, 100))
        exit_rect = exit_text.get_rect(center=(self.screen.get_width() // 2, 400))
        self.screen.blit(exit_text, exit_rect)

if __name__ == "__main__":
    game = Game()
    game.run()