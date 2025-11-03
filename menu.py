#sistema de menu
import pygame
from constants import *

class Menu:
    """sistema de menu"""

    def __init__(self,screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.selected_option = 0
        self.options = ["jugar", "salir"]

    def handle_input(self, keys):
        """procesa entrada del menu"""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_option = (self.selected_option + 1) % len(self.options)

    def draw(self, screen):
        """dibuja el menu"""
        screen.fill(BLACK)

        #titl
        title = self.font_large.render("maze runner", True, CYAN)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        #subtitulos
        subtitle = self.font_small.render("basado en ber", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(subtitle, subtitle_rect)

        #opciones
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = YELLOW
                text = "> " + option + " <"
            else:
                color = WHITE
                text = option

            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.text.get_rect(center=(self.screen_width // 2, 350 + i * 100))
            screen.blit(option_text, option_rect)

        #controles
        controls_text = self.font_small.render("ARRIBA/ABAJO para seleccionar, espacio para confirmar", True, GRAY)
        controls_rect = controls_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        screen.blit(controls_text, controls_rect)

    def get_selected(self):
        """retornar las opciones"""
        return self.options[self.selected_option]
    
class GameOverMenu:
    """menu"""

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, score=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.score = score
        self.selected_option = 0
        self.options = ["Reintentar", "Menú Principal"]

    def handle_input(self, keys):
        """Procesa entrada"""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_option = (self.selected_option + 1) % len(self.options)
    
    def draw(self, screen):
        """Dibuja el menú de Game Over"""
        screen.fill(BLACK)
        
        # Título
        title = self.font_large.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)

        # Puntuación
        score_text = self.font_medium.render(f"Puntuación: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 250))
        screen.blit(score_text, score_rect)
        
        # Opciones
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = YELLOW
                text = "> " + option + " <"
            else:
                color = WHITE
                text = option
            
            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, 400 + i * 80))
            screen.blit(option_text, option_rect)
    
    def get_selected(self):
        """Retorna la opción seleccionada"""
        return self.options[self.selected_option]
    
class VictoryMenu:
    """Menú de Victoria"""
    
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, score=0, level=1):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.score = score
        self.level = level
        self.selected_option = 0
        self.options = ["Siguiente Nivel", "Menú Principal"]
    
    def handle_input(self, keys):
        """Procesa entrada"""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_option = (self.selected_option + 1) % len(self.options)
    
    def draw(self, screen):
        """Dibuja el menú de Victoria"""
        screen.fill(BLACK)

        # Título
        title = self.font_large.render("¡ESCAPASTE!", True, GREEN)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)
        
        # Información
        level_text = self.font_medium.render(f"Nivel: {self.level}", True, CYAN)
        level_rect = level_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(level_text, level_rect)
        
        score_text = self.font_medium.render(f"Puntuación: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 280))
        screen.blit(score_text, score_rect)
        
        # Opciones
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = YELLOW
                text = "> " + option + " <"
            else:
                color = WHITE
                text = option
            
            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, 400 + i * 80))
            screen.blit(option_text, option_rect)
    
    def get_selected(self):
        """Retorna la opción seleccionada"""
        return self.options[self.selected_option]

        

        
    



        