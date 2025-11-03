# Clase principal del juego
import pygame
import random
import math
from constants import *
from maze import Maze
from game_entities import Player, Enemy, Bullet, EvilOtto
from pathfinding import AStar
from sound_manager import SoundManager
from menu import Menu, GameOverMenu, VictoryMenu

class Game:
    """Clase principal del juego"""
    
    def __init__(self, fullscreen=True):
        pygame.init()
        
        if fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Maze Runner - Escape the Maze")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Estado del juego
        self.game_state = GAME_STATE_MENU
        self.level = 1
        
        # Componentes del juego
        self.maze = None
        self.player = None
        self.enemies = []
        self.bullets = []
        self.evil_otto = None
        
        # Managers
        self.sound_manager = SoundManager()
        self.a_star = None
        
        # Menús
        self.menu = Menu()
        self.game_over_menu = None
        self.victory_menu = None
        
        # Gamepad
        self.gamepad_available = pygame.joystick.get_count() > 0
        if self.gamepad_available:
            self.gamepad = pygame.joystick.Joystick(0)
        
        # FPS
        self.fps_clock = pygame.time.Clock()
    
    def start_new_game(self):
        """Inicia un nuevo juego"""
        self.level = 1
        self.game_state = GAME_STATE_PLAYING
        self.setup_level()
    
    def setup_level(self):
        """Configura un nuevo nivel"""
        self.maze = Maze()
        self.a_star = AStar(self.maze.grid, TILE_SIZE)
        
        # Crear jugador
        exit_point = self.maze.get_exit_point()
        self.player = Player(exit_point[0], exit_point[1])
        
        # Crear enemigos
        self.enemies = []
        num_enemies = 3 + self.level
        for i in range(num_enemies):
            pos = self.maze.get_random_walkable_position()
            enemy_type = 1 + (i % 3)
            enemy = Enemy(pos[0], pos[1], enemy_type)
            self.enemies.append(enemy)
        
        # Crear Evil Otto
        self.evil_otto = EvilOtto(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.evil_otto.time_until_spawn = EVIL_OTTO_SPAWN_TIME + (self.level * 50)
        
        # Limpiar proyectiles
        self.bullets = []
    
    def handle_input(self):
        """Procesa entrada del usuario"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GAME_STATE_PLAYING:
                        self.game_state = GAME_STATE_MENU
                    else:
                        self.running = False
                
                if event.key == pygame.K_SPACE:
                    if self.game_state == GAME_STATE_MENU:
                        if self.menu.get_selected() == "Jugar":
                            self.start_new_game()
                        else:
                            self.running = False
                    
                    elif self.game_state == GAME_STATE_GAME_OVER:
                        if self.game_over_menu.get_selected() == "Reintentar":
                            self.start_new_game()
                        else:
                            self.game_state = GAME_STATE_MENU
                    
                    elif self.game_state == GAME_STATE_VICTORY:
                        if self.victory_menu.get_selected() == "Siguiente Nivel":
                            self.level += 1
                            self.setup_level()
                            self.game_state = GAME_STATE_PLAYING
                        else:
                            self.game_state = GAME_STATE_MENU
        
        keys = pygame.key.get_pressed()
        
        if self.game_state == GAME_STATE_MENU:
            self.menu.handle_input(keys)
        
        elif self.game_state == GAME_STATE_PLAYING:
            # Entrada del jugador
            if self.player:
                self.player.handle_input(keys, self.gamepad_available)
        
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.game_over_menu.handle_input(keys)
        
        elif self.game_state == GAME_STATE_VICTORY:
            self.victory_menu.handle_input(keys)
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.game_state == GAME_STATE_PLAYING:
            # Actualizar jugador
            self.player.update(self.maze, self.bullets, self.sound_manager, self.gamepad_available)
            
            # Actualizar enemigos
            for enemy in self.enemies:
                enemy.update(self.player, self.maze, self.bullets, self.sound_manager)
            
            # Actualizar Evil Otto
            self.evil_otto.update(self.player, self.maze)
            
            # Actualizar proyectiles
            self.bullets = [b for b in self.bullets if b.update(self.maze)]
            
            # Colisiones: proyectiles del jugador con enemigos
            player_bullets = [b for b in self.bullets if b.is_player]
            for bullet in player_bullets:
                for enemy in self.enemies:
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < 16:
                        self.bullets.remove(bullet)
                        self.enemies.remove(enemy)
                         
                        self.sound_manager.play_sound("explosion")
                        break
            
            # Colisiones: proyectiles de enemigos con jugador
            enemy_bullets = [b for b in self.bullets if not b.is_player]
            for bullet in enemy_bullets:
                if self.player.invulnerability_counter <= 0:
                    dist = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                    if dist < 12:
                        self.bullets.remove(bullet)
                        self.player.lives -= 1
                        self.sound_manager.play_sound("hit")
                        
                        if self.player.lives <= 0:
                            self.game_state = GAME_STATE_GAME_OVER
                            self.game_over_menu = GameOverMenu(score=self.player.score)
                        else:
                            self.player.reset_position()
                        break
            
            # Colisión con Evil Otto
            if self.evil_otto.check_collision(self.player):
                if self.player.invulnerability_counter <= 0:
                    self.player.lives -= 1
                    self.sound_manager.play_sound("hit")
                    
                    if self.player.lives <= 0:
                        self.game_state = GAME_STATE_GAME_OVER
                        self.game_over_menu = GameOverMenu(score=self.player.score)
                    else:
                        self.player.reset_position()
            
            # Colisión con enemigos
            for enemy in self.enemies:
                dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if dist < 16 and self.player.invulnerability_counter <= 0:
                    self.player.lives -= 1
                    self.sound_manager.play_sound("hit")
                    
                    if self.player.lives <= 0:
                        self.game_state = GAME_STATE_GAME_OVER
                        self.game_over_menu = GameOverMenu(score=self.player.score)
                    else:
                        self.player.reset_position()
                    break
            
            # Verificar si el jugador escapó
            if self.player.check_exit(self.maze):
                self.player.score += POINTS_ROOM_CLEAR_BONUS
                self.game_state = GAME_STATE_VICTORY
                self.victory_menu = VictoryMenu(score=self.player.score, level=self.level)
                self.sound_manager.play_sound("explosion")
            
            # Ganancia de vidas
            if self.player.score > 0 and self.player.score % POINTS_LIVES_GAINED_AT == 0:
                # Limitar a 5 vidas máximo
                if self.player.lives < 5:
                    self.player.lives += 1
                    self.sound_manager.play_sound("shoot")
    
    def draw(self):
        """Dibuja el juego"""
        self.screen.fill(BLACK)
        
        if self.game_state == GAME_STATE_MENU:
            self.menu.draw(self.screen)
        
        elif self.game_state == GAME_STATE_PLAYING:
            # Dibujar mazmorra
            self.maze.draw(self.screen, DARK_GRAY)
            
            # Dibujar jugador
            self.player.draw(self.screen)
            
            # Dibujar enemigos
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Dibujar Evil Otto
            self.evil_otto.draw(self.screen)
            
            # Dibujar proyectiles
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            # Dibujar HUD
            self.draw_hud()
        
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.game_over_menu.draw(self.screen)
        
        elif self.game_state == GAME_STATE_VICTORY:
            self.victory_menu.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Dibuja la interfaz de usuario"""
        font = pygame.font.Font(None, 32)
        
        # Puntuación
        score_text = font.render(f"Puntuación: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Vidas
        lives_text = font.render(f"Vidas: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 40))
        
        # Nivel
        level_text = font.render(f"Nivel: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, 10))
        
        # Enemigos restantes
        enemies_text = font.render(f"Enemigos: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 200, 40))
        
        # Evil Otto
        if self.evil_otto.active:
            otto_text = font.render("¡EVIL OTTO!", True, RED)
            self.screen.blit(otto_text, (SCREEN_WIDTH // 2 - 80, 10))
    
    def run(self):
        """Loop principal del juego"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
