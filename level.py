import pygame
from constants import *
from sprites import Player, Enemy, Tile, Spike, Powerup, Goal, Fireball

class Level:
    def __init__(self, level_data, surface, level_number=1, level_name=""):
        # Das Fenster, auf dem gezeichnet wird
        self.display_surface = surface
        self.level_data = level_data
        self.level_number = level_number
        self.level_name = level_name
        
        # Initialisierung der Kamera-Verschiebung
        # world_shift ist die Delta-Verschiebung pro Frame
        self.world_shift = 0
        # camera_x ist die kumulierte Kameraposition für den Hintergrund
        self.camera_x = 0
        
        # Level-Completion Flag
        self.level_completed = False
        
        # Game Over Flag
        self.game_over = False
        
        # Timer für das Level
        self.start_time = pygame.time.get_ticks()  # Zeit in Millisekunden

        # Hilfsvariable um die Startposition des players zu behalten
        self.player_start_coordinates = (100,100)
        
        # Level-Objekte erstellen
        self.setup_level()

        # Hilfvariable um Zeit anzuhalten wenn completed
        self.level_completed_time = ""

        

    def setup_level(self):
        """Erstellt alle Sprites basierend auf der level_map."""
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        self.explosions = []
        
        # PlayerGroupSingle ist eine spezielle Gruppe für nur ein Objekt (den Spieler)
        self.player_group = pygame.sprite.GroupSingle()
        
        for row_index, row in enumerate(self.level_data):
            for col_index, cell in enumerate(row):
                x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
                
                if cell == 'X': 
                    self.tiles.add(Tile(x, y))
                elif cell == 'P':
                    self.player_start_coordinates = (x,y)
                    self.player = Player(x, y)
                    self.player_group.add(self.player)
                elif cell == 'E': 
                    self.enemies.add(Enemy(x, y, "normal"))
                elif cell == 'J': 
                    self.enemies.add(Enemy(x, y, "jumper"))
                elif cell == 'O': 
                    self.enemies.add(Enemy(x, y, "exploder"))
                elif cell == 'S': 
                    self.spikes.add(Spike(x, y))
                elif cell == 'G': 
                    # Superpower Item
                    self.powerups.add(Powerup(x, y))
                elif cell == 'Z':
                    # Ziel
                    self.goals.add(Goal(x, y))

        if not hasattr(self, 'player'):
            raise ValueError('Level enthält keinen Spielerstart (P). Bitte füge ein P in die Level-Datei ein.')

    def scroll_x(self):
        """Berechnet, ob das Level verschoben werden muss, wenn der Spieler den Rand erreicht."""
        player = self.player
        player_x = player.rect.centerx
        direction_x = player.direction.x
        screen_width = self.display_surface.get_width()
        left_boundary = screen_width / 4
        right_boundary = screen_width - left_boundary

        if player_x < left_boundary and direction_x < 0:
            self.world_shift = left_boundary - player_x
            player.rect.centerx = left_boundary
        elif player_x > right_boundary and direction_x > 0:
            self.world_shift = right_boundary - player_x
            player.rect.centerx = right_boundary
        else:
            self.world_shift = 0

        self.camera_x += self.world_shift

    def check_enemy_collision(self):
        """Prüft direkte Kollisionen mit Gegnern."""
        if self.player.is_invincible:
            return False
        if pygame.sprite.spritecollideany(self.player, self.enemies, collided=pygame.sprite.collide_rect):
            self.reset_player()
            return True
        return False

    def horizontal_collision(self):
        """Prüft Kollisionen mit Wänden während der Seitwärtsbewegung des Spielers."""
        player = self.player

        # Bewegung anwenden
        player.rect.x += player.direction.x * player.speed

        # für player: Kollisionen mit Tiles
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0: # Läuft nach links (A)
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0: # Läuft nach rechts (D)
                    player.rect.right = sprite.rect.left

        # Direkter Treffer mit Gegnern nach Bewegung
        return self.check_enemy_collision()

    def enemy_horizontal_collision(self):
        """Prüft Gegner-Wandkollisionen: Richtung umkehren bei Wand-Hit"""
        for enemy in self.enemies.sprites():
            if enemy.enemy_type == "jumper":
                continue  # Jumper werden nicht horizontal bewegt
            
            # Auf Wand-Kollisionen prüfen
            for tile in self.tiles.sprites():
                if enemy.rect.colliderect(tile.rect):
                    # Richtung umkehren wenn Wand getroffen
                    enemy.direction = -enemy.direction
                    break

    def check_vertical_enemy_collision(self, previous_bottom):
        """Prüft Kollisionen mit Gegnern bei vertikaler Bewegung."""
        for enemy in self.enemies.sprites():
            if self.player.rect.colliderect(enemy.rect):
                landed_on_enemy = (
                    previous_bottom <= enemy.rect.top + (TILE_SIZE // 2)
                    and self.player.rect.bottom >= enemy.rect.top + 1
                    and self.player.direction.y >= -1
                )
                if landed_on_enemy:
                    self.enemies.remove(enemy)
                    self.player.rect.bottom = enemy.rect.top
                    self.player.direction.y = self.player.jump_speed // 2
                    return True
                self.reset_player()
                return True
        return False

    def vertical_collision(self):
        """Prüft Kollisionen mit Boden/Decke und wendet Schwerkraft an."""
        player = self.player
        previous_bottom = player.rect.bottom
        player.apply_gravity() # Schwerkraft zieht nach unten
        
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0: # Fällt nach unten
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0 # Fall stoppen
                elif player.direction.y < 0: # Springt gegen Decke (W)
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0 # Kopf gestoßen

        self.check_vertical_enemy_collision(previous_bottom)

    def enemy_vertical_collision(self):
        """Prüft Kollisionen der Gegner mit Boden/Decke."""
        for enemy in self.enemies.sprites():
            for sprite in self.tiles.sprites():
                if sprite.rect.colliderect(enemy.rect):
                    if enemy.v_speed > 0: # Fällt nach unten
                        enemy.rect.bottom = sprite.rect.top
                        enemy.v_speed = 0 # Fall stoppen
                        
                        # Jumper springt wenn es auf dem Boden landet
                        if enemy.enemy_type == "jumper":
                            enemy.v_speed = enemy.jump_strength
                    elif enemy.v_speed < 0: # Springt gegen Decke
                        enemy.rect.top = sprite.rect.bottom
                        enemy.v_speed = 0 # Kopf gestoßen

    def damage_and_items(self):
        """Verwaltet Leben, Tod durch Spikes/Gegner und Powerups."""
        p = self.player
        
        # Schaden nur prüfen, wenn nicht unbesiegbar
        if not p.is_invincible:
            for enemy in self.enemies.sprites():
                if p.rect.colliderect(enemy.rect):
                    # Check ob Spieler VON OBEN auf Feind springt (nicht von der Seite)
                    player_horizontal_over_enemy = (p.rect.centerx > enemy.rect.left and p.rect.centerx < enemy.rect.right)
                    player_above_enemy = p.rect.bottom <= enemy.rect.top + (TILE_SIZE // 4)
                    landing_on_enemy = player_horizontal_over_enemy and player_above_enemy and p.direction.y >= 0
                    
                    if landing_on_enemy:
                        self.enemies.remove(enemy)
                        p.direction.y = p.jump_speed // 2
                        p.rect.bottom = enemy.rect.top
                        break
                    else:
                        # Von der Seite oder von unten getroffen
                        self.reset_player()
                        return

            for spike in self.spikes.sprites():
                if p.rect.colliderect(spike.rect):
                    self.reset_player()
                    return

        # Spieler fällt aus der Karte -> Game Over
        if p.rect.top > self.display_surface.get_height():
            p.lives = 0
            self.set_game_over()

        # Superpower (Gold) einsammeln
        if pygame.sprite.spritecollide(p, self.powerups, True, collided=pygame.sprite.collide_mask):
            self.play_sound("powerup")

            p.is_invincible = True
            p.has_fireball = True
            p.powerup_timer = 300 # Ca. 5 Sekunden bei 60 FPS
        
        # Ziel berührt?
        if pygame.sprite.spritecollide(p, self.goals, False, collided=pygame.sprite.collide_mask):
            self.play_sound("won")
            self.level_completed = True

        # Feuerball abfeuern, wenn gedrückt
        if p.fireball_request:
            self.spawn_fireball()
            p.fireball_request = False

    def reset_player(self):
        """Setzt den Spieler bei Tod zurück und zieht ein Leben ab."""
        self.player.lives -= 1
        print(f"Leben übrig: {self.player.lives}")

        self.play_sound("death")
        
        if self.player.lives <= 0:
            self.set_game_over()
        else:
            self.camera_x = 0
            self.world_shift = 0
            self.player.rect.topleft = self.player_start_coordinates # Teleport zum Start (oder Checkpoint,  nicht verfügbar)

    # Hilfsfunktion um den sound zu spielen
    def set_game_over(self):
        self.play_sound("gameover")
        self.game_over = True
    
    def get_elapsed_time(self):
        """Gibt die verstrichene Zeit in Millisekunden zurück."""
        return pygame.time.get_ticks() - self.start_time
    
    def format_time(self, milliseconds):
        """Formatiert Millisekunden zu MM:SS Format."""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw_sprite_borders(self, sprite_group):
        """Zeichnet Ränder und Schatten um Sprites herum."""
        border_color = (0, 0, 0)  # Schwarzer Rand
        border_width = 2
        shadow_offset_x = 3
        shadow_offset_y = 3
        
        for sprite in sprite_group.sprites():
            # Schatten zeichnen (dunkelgrauer Rahmen unter dem Sprite)
            shadow_surface = pygame.Surface((sprite.rect.width + 4, sprite.rect.height + 4), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 80))  # Schwarzes Rechteck mit 80 Alpha
            self.display_surface.blit(shadow_surface, (sprite.rect.x - 2 + shadow_offset_x, sprite.rect.y - 2 + shadow_offset_y))
            
            # Rand zeichnen um das Sprite
            pygame.draw.rect(self.display_surface, border_color, sprite.rect, border_width)
    
    def draw_hud(self):
        """Zeichnet das HUD mit Leben, Powerup-Status und Zeit oben auf dem Bildschirm."""
        font = pygame.font.Font(None, 40)
        
        # Leben anzeigen
        lives_text = font.render(f"Leben: {self.player.lives}", True, (255, 0, 0))
        lives_rect = lives_text.get_rect(topleft=(20, 20))
        self.display_surface.blit(lives_text, lives_rect)

        # Level-Anzeige
        level_label = f"Level {self.level_number}"
        if self.level_name:
            level_label += f" ({self.level_name})"
        level_text = font.render(level_label, True, (255, 255, 255))
        level_rect = level_text.get_rect(topleft=(20, 70))
        self.display_surface.blit(level_text, level_rect)
        
        # Powerup-Status anzeigen
        power_status = "Aktiv" if self.player.has_fireball else "Keins"
        power_color = (255, 215, 0) if self.player.has_fireball else (200, 200, 200)
        power_text = font.render(f"Powerup: {power_status}", True, power_color)
        power_rect = power_text.get_rect(midtop=(self.display_surface.get_width() / 2, 20))
        self.display_surface.blit(power_text, power_rect)
        
        # Zeit anzeigen
        elapsed_ms = self.get_elapsed_time()
        time_str = self.format_time(elapsed_ms)
        time_text = font.render(f"Zeit: {time_str}", True, (255, 255, 255))
        time_rect = time_text.get_rect(topright=(self.display_surface.get_width() - 20, 20))
        self.display_surface.blit(time_text, time_rect)



    def draw_level_completed(self):
        """Zeichnet einen vollbildschirm 'Level Completed' Text mit der verstrichenen Zeit."""

        # Schwarzer Hintergrund
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.display_surface.blit(overlay, (0, 0))
        
        if self.level_completed_time == "":
            # Verstrichene Zeit berechnen
            elapsed_ms = self.get_elapsed_time()
            self.level_completed_time = self.format_time(elapsed_ms)
        
        # Text rendern
        font_large = pygame.font.Font(None, 100)
        font_small = pygame.font.Font(None, 60)
        
        text_main = font_large.render("LEVEL COMPLETED!", True, (255, 215, 0))
        text_time = font_small.render(f"Zeit: {self.level_completed_time}", True, (255, 255, 255))
        
        center_x = self.display_surface.get_rect().centerx
        center_y = self.display_surface.get_rect().centery
        
        # Haupttext
        text_main_rect = text_main.get_rect(center=(center_x, center_y - 120))
        self.display_surface.blit(text_main, text_main_rect)

        # Level-Text
        level_label = f"Level {self.level_number}"
        if self.level_name:
            level_label += f" ({self.level_name})"
        text_level = font_small.render(f"Abgeschlossen: {level_label}", True, (255, 255, 255))
        text_level_rect = text_level.get_rect(center=(center_x, center_y))
        self.display_surface.blit(text_level, text_level_rect)

        # Zeit-Text
        text_time_rect = text_time.get_rect(center=(center_x, center_y + 80))
        self.display_surface.blit(text_time, text_time_rect)

        # Eingabehinweis
        text_next = font_small.render("Drücke ENTER für das nächste Level", True, (200, 200, 200))
        text_next_rect = text_next.get_rect(center=(center_x, center_y + 160))
        self.display_surface.blit(text_next, text_next_rect)
    
    def handle_exploding_enemies(self):
        """Löst Explosionen aus, wenn explodierende Gegner lange nahe dem Spieler sind."""
        for enemy in self.enemies.copy():
            if enemy.check_explode(self.player):
                explosion_center = enemy.rect.center
                self.explosions.append({
                    'pos': explosion_center,
                    'timer': FPS // 2,
                    'radius': enemy.explosion_radius
                })
                self.enemies.remove(enemy)
                
                # Schaden an Player, wenn er zu nah ist
                if pygame.math.Vector2(self.player.rect.center).distance_to(explosion_center) < enemy.explosion_radius:
                    self.reset_player()
                
                # Normale Gegner in Explosionsradius zerstören
                for other in self.enemies.copy():
                    if pygame.math.Vector2(other.rect.center).distance_to(explosion_center) < enemy.explosion_radius:
                        self.enemies.remove(other)

    def draw_explosions(self):
        

        for explosion in self.explosions[:]:
            alpha = int(255 * (explosion['timer'] / (FPS // 2)))
            radius = explosion['radius']
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 120, 0, alpha), (radius, radius), radius)
            self.display_surface.blit(surf, (explosion['pos'][0] - radius, explosion['pos'][1] - radius))

            self.play_sound("explosion")
            explosion['timer'] -= 1
            if explosion['timer'] <= 0:
                self.explosions.remove(explosion)

    def spawn_fireball(self):
        # Sound Effect Spiele
        self.play_sound("fire")

        direction = 1 if self.player.direction.x >= 0 else -1
        spawn_x = self.player.rect.centerx + (direction * TILE_SIZE)
        spawn_y = self.player.rect.centery
        fireball = Fireball(spawn_x, spawn_y, direction)
        self.fireballs.add(fireball)

    def handle_fireballs(self):
        for fireball in self.fireballs.copy():
            # Remove if off-screen
            if fireball.rect.right < 0 or fireball.rect.left > self.display_surface.get_width():
                self.fireballs.remove(fireball)
                continue
            # Collision with enemies
            for enemy in self.enemies.copy():
                if fireball.rect.colliderect(enemy.rect):
                    if enemy.enemy_type in ["normal", "jumper"]:
                        self.enemies.remove(enemy)
                    self.fireballs.remove(fireball)
                    break
            # collision with tiles stops fireball
            for tile in self.tiles.sprites():
                if tile.rect.colliderect(fireball.rect):
                    if fireball in self.fireballs:
                        self.fireballs.remove(fireball)
                    break

    def draw_game_over(self):
        """Zeichnet einen vollbildschirm 'Game Over' Screen."""
        # Schwarzer Hintergrund
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.display_surface.blit(overlay, (0, 0))
        
        # Text rendern
        font_large = pygame.font.Font(None, 120)
        font_small = pygame.font.Font(None, 60)
        
        text_main = font_large.render("GAME OVER", True, (255, 0, 0))
        text_lives = font_small.render("Alle Leben aufgebraucht!", True, (255, 255, 255))
        
        center_x = self.display_surface.get_rect().centerx
        center_y = self.display_surface.get_rect().centery
        
        # Haupttext
        text_main_rect = text_main.get_rect(center=(center_x, center_y - 50))
        self.display_surface.blit(text_main, text_main_rect)
        
        # Leben-Text
        text_lives_rect = text_lives.get_rect(center=(center_x, center_y + 80))
        self.display_surface.blit(text_lives, text_lives_rect)

        # Neustart-Hinweis
        text_restart = font_small.render("Drücke ENTER zum Neustarten", True, (200, 200, 200))
        text_restart_rect = text_restart.get_rect(center=(center_x, center_y + 160))
        self.display_surface.blit(text_restart, text_restart_rect)

    def play_sound(self, name: str):
        music_path = BASE_PATH / "sounds" / str(name + ".mp3")
        if music_path.exists():
            sound = pygame.mixer.Sound(music_path)
            sound.set_volume(0.5)
            sound.play()

    def run(self):
        """Die Haupt-Update-Methode für das Level, die in main.py aufgerufen wird."""
        
        # 1. Spieler-Logik (Bewegung & Kollisionen)
        # Nur wenn Level noch nicht abgeschlossen oder Game Over
        if not self.level_completed and not self.game_over:
            self.player_group.update() # Eingabe (WASD) verarbeiten
            self.horizontal_collision()
            self.vertical_collision()
            self.scroll_x()

            self.enemies.update(self.world_shift)
            self.enemy_vertical_collision()  # Gegner-Kollisionen mit Boden
            self.enemy_horizontal_collision()  # Gegner-Wandkollisionen
            self.fireballs.update(self.world_shift)

            self.damage_and_items()
            self.handle_fireballs()
            self.handle_exploding_enemies()

        # 2. Level-Objekte zeichnen und aktualisieren
        # Alle Gruppen außer dem Spieler erhalten 'self.world_shift' zum Scrollen
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.draw_sprite_borders(self.tiles)  # Ränder für Boden
        
        self.spikes.update(self.world_shift)
        self.spikes.draw(self.display_surface)
        self.draw_sprite_borders(self.spikes)  # Ränder für Spikes
        
        self.powerups.update(self.world_shift)
        self.powerups.draw(self.display_surface)
        self.draw_sprite_borders(self.powerups)  # Ränder für Powerups
        
        self.goals.update(self.world_shift)
        self.goals.draw(self.display_surface)
        self.draw_sprite_borders(self.goals)  # Ränder für Ziele
        
        self.fireballs.draw(self.display_surface)
        self.draw_sprite_borders(self.fireballs)
        
        self.enemies.draw(self.display_surface)
        self.draw_sprite_borders(self.enemies)  # Ränder für Gegner
        self.draw_explosions()

        # 4. Spieler zeichnen
        self.player_group.draw(self.display_surface)
        self.draw_sprite_borders(self.player_group)  # Ränder für Spieler
        
        # 5. HUD zeichnen (Leben und Zeit) - außer wenn Level abgeschlossen oder Game Over
        if not self.level_completed and not self.game_over:
            self.draw_hud()
        
        # 6. Wenn Level abgeschlossen, Fullscreen-Nachricht anzeigen
        if self.level_completed:
            self.draw_level_completed()
        
        # 7. Wenn Game Over, Game Over Screen anzeigen
        if self.game_over:
            self.draw_game_over()