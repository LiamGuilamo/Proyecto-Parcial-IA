# Generador y manager de mazmorras
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Maze:
    """Generador de mazmorras tipo Berzerk"""
    
    def __init__(self):
        self.width = SCREEN_WIDTH // TILE_SIZE
        self.height = SCREEN_HEIGHT // TILE_SIZE
        self.grid = None
        self.exit_points = []
        self.generate()
    
    def generate(self):
        """Genera una mazmorra nueva"""
        # Inicializar grid (0 = pasable, 1 = pared)
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Crear muros en los bordes
        for x in range(self.width):
            self.grid[0][x] = 1
            self.grid[self.height - 1][x] = 1
        
        for y in range(self.height):
            self.grid[y][0] = 1
            self.grid[y][self.width - 1] = 1
        
        # Crear muros internos aleatorios
        for y in range(2, self.height - 2):
            for x in range(2, self.width - 2):
                if random.random() < 0.15:  # 15% de probabilidad
                    self.grid[y][x] = 1
        
        # Definir puntos de salida (uno en cada lado)
        self.exit_points = [
            (self.width // 2, 0),      # Arriba
            (self.width // 2, self.height - 1),  # Abajo
            (0, self.height // 2),     # Izquierda
            (self.width - 1, self.height // 2)   # Derecha
        ]
        
        # Asegurar que los puntos de salida son accesibles
        for ex, ey in self.exit_points:
            self.grid[ey][ex] = 0
    
    def is_walkable(self, x, y):
        """Verifica si una posición es transitible"""
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == 0
        return False
    
    def is_wall_at(self, x, y):
        """Verifica si hay una pared en una posición"""
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == 1
        return True
    
    def get_exit_point(self):
        """Obtiene un punto de salida aleatorio"""
        if not self.exit_points:
            return (self.width // 2, self.height // 2)
        ex, ey = random.choice(self.exit_points)
        return (ex * TILE_SIZE + TILE_SIZE // 2, ey * TILE_SIZE + TILE_SIZE // 2)
    
    def get_random_walkable_position(self):
        """Obtiene una posición aleatoria transitible"""
        while True:
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.grid[y][x] == 0:
                return (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
    
    def draw(self, screen, wall_color):
        """Dibuja la mazmorra en la pantalla"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, wall_color, rect)

import pygame
