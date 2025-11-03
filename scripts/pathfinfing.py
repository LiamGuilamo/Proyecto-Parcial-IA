# Implementación de A* Pathfinding desde cero
import heapq
import math

class Node:
    """Nodo en la grilla para A*"""
    def __init__(self, position, parent=None):
        self.position = position  # (x, y)
        self.parent = parent
        self.g = 0  # Costo desde el inicio
        self.h = 0  # Heurística (distancia estimada al objetivo)
        self.f = 0  # f = g + h
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.position == other.position

class AStar:
    """Algoritmo A* para pathfinding"""
    
    def __init__(self, grid, tile_size):
        """
        grid: matriz 2D donde 0 = pasable, 1 = obstáculo
        tile_size: tamaño de cada celda
        """
        self.grid = grid
        self.tile_size = tile_size
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
    
    def heuristic(self, pos1, pos2):
        """heuristica de distancia"""
        return abs(pos1[0] - pos2[0] + abs(pos1[1] - pos2[1]))
    
    def get_neighbors(self, position):
        """Obtiene vecinos válidos de una posición"""
        neighbors = []
        x, y = position
        
        # 4 direcciones (arriba, abajo, izquierda, derecha)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Verificar límites
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                # Verificar si no es obstáculo
                if self.grid[ny][nx] == 0:
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def find_path(self, start, goal):
        """
        Encuentra el camino más corto de start a goal
        Returns: Lista de posiciones [start, ..., goal] o lista vacía si no hay camino
        """
        start_node = Node(start)
        goal_node = Node(goal)
        
        open_list = []
        closed_set = set()

        heapq.heappush(open_list, start_node)
        
        while open_list:
            current_node = heapq.heappop(open_list)
            
            if current_node.position == goal_node.position:
                # Reconstruir camino
                path = []
                node = current_node
                while node:
                    path.append(node.position)
                    node = node.parent
                return path[::-1]  # Invertir para obtener start -> goal
            
            closed_set.add(current_node.position)
            
            for neighbor_pos in self.get_neighbors(current_node.position):
                if neighbor_pos in closed_set:
                    continue
                
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = current_node.g + 1
                neighbor_node.h = self.heuristic(neighbor_pos, goal)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                
                # Verificar si ya existe en open_list con mejor f
                existing = None
                for node in open_list:
                    if node.position == neighbor_pos:
                        existing = node
                        break
                
                if existing is None or neighbor_node.f < existing.f:
                    if existing:
                        open_list.remove(existing)
                    heapq.heappush(open_list, neighbor_node)
        
        return []  # No hay camino disponible
    
    def get_grid_coords(self, pixel_pos):
        """Convierte coordenadas de píxeles a coordenadas de grilla"""
        return (pixel_pos[0] // self.tile_size, pixel_pos[1] // self.tile_size)
    
    def get_pixel_coords(self, grid_pos):
        """Convierte coordenadas de grilla a coordenadas de píxeles"""
        return (grid_pos[0] * self.tile_size, grid_pos[1] * self.tile_size)

            