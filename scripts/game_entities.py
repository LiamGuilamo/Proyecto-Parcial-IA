# Entidades del juego (Jugador, Enemigos, Proyectiles) - VERSIÓN CORREGIDA
import pygame
import math
import random
from constants import *
from behavior_tree import *

class Player:
    """Clase del jugador"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.direction = DIRECTIONS["NONE"]
        self.lives = 3
        self.score = 0
        self.respawn_invulnerability = 120  # Frames de invulnerabilidad
        self.invulnerability_counter = self.respawn_invulnerability
    
    def handle_input(self, keys, gamepad=None):
        """Procesa entrada del jugador"""
        self.direction = DIRECTIONS["NONE"]
        
        # Entrada por teclado
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = DIRECTIONS["UP"]
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = DIRECTIONS["DOWN"]
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.direction == DIRECTIONS["UP"]:
                self.direction = DIRECTIONS["UP_LEFT"]
            elif self.direction == DIRECTIONS["DOWN"]:
                self.direction = DIRECTIONS["DOWN_LEFT"]
            else:
                self.direction = DIRECTIONS["LEFT"]
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.direction == DIRECTIONS["UP"]:
                self.direction = DIRECTIONS["UP_RIGHT"]
            elif self.direction == DIRECTIONS["DOWN"]:
                self.direction = DIRECTIONS["DOWN_RIGHT"]
            else:
                self.direction = DIRECTIONS["RIGHT"]
        
        # Entrada por gamepad (si está disponible)
        if gamepad:
            try:
                joy = pygame.joystick.Joystick(0)
                axes = joy.get_numaxes()
                
                # Stick analógico izquierdo para movimiento
                if axes >= 2:
                    x_axis = joy.get_axis(0)
                    y_axis = joy.get_axis(1)
                    
                    if abs(x_axis) > 0.5 or abs(y_axis) > 0.5:
                        self.direction = (int(x_axis), int(y_axis))
                        if self.direction == (0, 0):
                            self.direction = DIRECTIONS["NONE"]
            except:
                pass
    
    def shoot(self, bullets, sound_manager):
        """Dispara un proyectil"""
        if self.shoot_cooldown <= 0:
            # Disparar en la dirección actual
            if self.direction != DIRECTIONS["NONE"]:
                dx, dy = self.direction
                bullet = Bullet(self.x, self.y, dx, dy, is_player=True)
                bullets.append(bullet)
                self.shoot_cooldown = SHOOT_COOLDOWN
                if sound_manager:
                    sound_manager.play_sound("shoot")
    
    def update(self, maze, bullets, sound_manager, gamepad=None):
        """Actualiza el estado del jugador"""
        keys = pygame.key.get_pressed()
        self.handle_input(keys, gamepad)
        
        # Movimiento
        if self.direction != DIRECTIONS["NONE"]:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # Colisión con muros
            if maze.is_walkable(new_x, new_y) and maze.is_walkable(new_x + self.width, new_y + self.height):
                self.x = new_x
                self.y = new_y
        
        # Disparo
        if keys[pygame.K_SPACE]:
            self.shoot(bullets, sound_manager)
        
        # Actualizar cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Actualizar invulnerabilidad
        if self.invulnerability_counter > 0:
            self.invulnerability_counter -= 1
    
    def draw(self, screen):
        """Dibuja el jugador"""
        # Si está en invulnerabilidad, parpadear
        if self.invulnerability_counter > 0 and self.invulnerability_counter % 10 < 5:
            color = CYAN
        else:
            color = GREEN
        
        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)
    
    def check_exit(self, maze):
        """Verifica si el jugador ha salido de la mazmorra"""
        player_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        
        # Comprobar si está fuera de los límites
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            return True
        return False
    
    def reset_position(self, maze=None):
        if maze:
        # Buscar un punto aleatorio que sea transitable
           while True:
               new_x = random.randint(1, maze.width - 2) * TILE_SIZE + TILE_SIZE // 2
               new_y = random.randint(1, maze.height - 2) * TILE_SIZE + TILE_SIZE // 2
               if maze.is_walkable(new_x, new_y):
                  self.x = new_x
                  self.y = new_y
                  break
        else: 
        # Si no hay referencia al maze, usar posición por defecto
            self.x = SCREEN_WIDTH // 4
            self.y = SCREEN_HEIGHT // 2
  
        self.invulnerability_counter = self.respawn_invulnerability


class Bullet:
    """Clase de proyectil"""
    
    def __init__(self, x, y, dx, dy, is_player=True):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_player = is_player
        self.speed = BULLET_SPEED
        self.size = 4
    
    def update(self, maze):
        """Actualiza la posición del proyectil"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
        # Comprobar colisión con muros
        if not maze.is_walkable(int(self.x), int(self.y)):
            return False  # Eliminar proyectil
        
        # Comprobar si salió de la pantalla
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            return False
        
        return True
    
    def draw(self, screen):
        """Dibuja el proyectil"""
        color = YELLOW if self.is_player else RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Enemy:
    """Clase de enemigo con Behavior Tree y A*"""
    
    def __init__(self, x, y, enemy_type=1):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = ENEMY_SPEED
        self.enemy_type = enemy_type  # 1, 2, 3 - diferentes comportamientos
        self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN + random.randint(0, 30)
        self.direction = DIRECTIONS["NONE"]
        self.vision_range = 300  # AUMENTADO: Rango de visión en píxeles
        self.shoot_range = 250   # AUMENTADO: Rango de disparo en píxeles
        self.path = []
        self.path_counter = 0
        self.patrol_target = None
        self.patrol_timer = 0
        
        # Comportamiento
        self.player = None
        self.bullets = None
        self.sound_manager = None
        
        # Behavior Tree
        self.behavior_tree = self.create_behavior_tree()
    
    def create_behavior_tree(self):
        """Crea el árbol de comportamiento del enemigo"""
        if self.enemy_type == 1:
            # Tipo 1: Patrulla y dispara si ve al jugador
            root = BTSelector()
            
            # Rama 1: Si puede disparar, disparar
            shoot_sequence = BTSequence()
            shoot_sequence.add_child(BTCondition(self.condition_can_see_player))
            shoot_sequence.add_child(BTCondition(self.condition_can_shoot))
            shoot_sequence.add_child(BTAction(self.action_shoot_at_player))
            
            # Rama 2: Si ve al jugador, perseguir
            chase_sequence = BTSequence()
            chase_sequence.add_child(BTCondition(self.condition_can_see_player))
            chase_sequence.add_child(BTAction(self.action_move_towards_player))
            
            # Rama 3: Patrullar
            patrol_action = BTAction(self.action_patrol)
            
            root.add_child(shoot_sequence)
            root.add_child(chase_sequence)
            root.add_child(patrol_action)
            
            return BehaviorTree(root)
        
        else:
            # Tipo 2 y 3: Más agresivos
            root = BTPriority()
            
            # Prioridad 1: Atacar si es posible
            attack_seq = BTSequence()
            attack_seq.add_child(BTCondition(self.condition_can_see_player))
            attack_seq.add_child(BTCondition(self.condition_can_shoot))
            attack_seq.add_child(BTAction(self.action_shoot_at_player))
            
            # Prioridad 2: Perseguir
            chase_seq = BTSequence()
            chase_seq.add_child(BTCondition(self.condition_can_see_player))
            chase_seq.add_child(BTAction(self.action_move_towards_player))
            
            # Prioridad 3: Patrullar
            patrol = BTAction(self.action_patrol)
            
            root.add_child(attack_seq)
            root.add_child(chase_seq)
            root.add_child(patrol)
            
            return BehaviorTree(root)
    
    # Condiciones del Behavior Tree
    def condition_can_see_player(self, agent=None):
        """Verifica si el enemigo puede ver al jugador"""
        if self.player is None:
            return False
        
        # Calcular distancia al jugador
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # CORRECIÓN: Retorna True si está dentro del rango de visión
        return distance < self.vision_range
    
    def condition_can_shoot(self, agent=None):
        """Verifica si puede disparar"""
        return self.shoot_cooldown <= 0
    
    def condition_is_player_close(self, agent=None):
        """Verifica si el jugador está cerca"""
        if self.player is None:
            return False
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        return dist < self.shoot_range
    
    # Acciones del Behavior Tree
    def action_move_towards_player(self, agent=None):
        """Acción: moverse hacia el jugador"""
        if self.player is None:
            return BT_FAILURE
        
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            # Normalizar dirección
            self.direction = (int(dx / dist * 2), int(dy / dist * 2))
        
        return BT_SUCCESS
    
    def action_shoot_at_player(self, agent=None):
        """Acción: disparar al jugador"""
        if self.player is None or self.bullets is None:
            return BT_FAILURE
        
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # Solo disparar si está en rango y puede ver
        if 0 < dist < self.shoot_range:
            # Normalizar dirección del disparo
            bullet_dx = dx / dist
            bullet_dy = dy / dist
            bullet = Bullet(self.x, self.y, bullet_dx, bullet_dy, is_player=False)
            self.bullets.append(bullet)
            self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
            if self.sound_manager:
                self.sound_manager.play_sound("enemy_shoot")
            return BT_SUCCESS
        
        return BT_FAILURE
    
    def action_patrol(self, agent=None):
        """Acción: patrullar aleatoriamente"""
        self.patrol_timer -= 1
        
        if self.patrol_timer <= 0:
            # Elegir nueva dirección aleatoria
            angle = random.random() * 2 * math.pi
            self.direction = (int(math.cos(angle) * 2), int(math.sin(angle) * 2))
            self.patrol_timer = random.randint(30, 100)
        
        return BT_SUCCESS
    
    def update(self, player, maze, bullets, sound_manager):
        """Actualiza el estado del enemigo"""
        self.player = player
        self.bullets = bullets
        self.sound_manager = sound_manager
        
        # Ejecutar Behavior Tree - ESTO EJECUTA LAS CONDICIONES Y ACCIONES
        self.behavior_tree.tick(self)
        
        # Movimiento basado en la dirección decidida por el BT
        if self.direction != DIRECTIONS["NONE"]:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if maze.is_walkable(new_x, new_y) and maze.is_walkable(new_x + self.width, new_y + self.height):
                self.x = new_x
                self.y = new_y
        
        # Actualizar cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def draw(self, screen):
        """Dibuja el enemigo"""
        colors = [RED, pygame.Color("orange"), pygame.Color("purple")]
        color = colors[min(self.enemy_type - 1, len(colors) - 1)]
        
        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)
        
        # DEBUG: Dibujar rango de visión (opcional - comentar para versión final)
        # pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.vision_range), 1)

class EvilOtto:
    """Enemigo especial - Evil Otto (indestructible)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.speed = ENEMY_SPEED * 0.8
        self.active = False
        self.time_until_spawn = EVIL_OTTO_SPAWN_TIME
    
    def update(self, player, maze):
        """Actualiza a Evil Otto"""
        if not self.active:
            self.time_until_spawn -= 1
            if self.time_until_spawn <= 0:
                self.active = True
                print("¡EVIL OTTO HA APARECIDO!")
        
        if self.active and player:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                # Evil Otto puede atravesar muros
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
    
    def draw(self, screen):
        """Dibuja a Evil Otto"""
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
            # Dibujar ojos
            pygame.draw.circle(screen, BLACK, (int(self.x) - 5, int(self.y) - 3), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x) + 5, int(self.y) - 3), 2)
    
    def check_collision(self, player):
        """Verifica colisión con el jugador"""
        if not self.active:
            return False
        
        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        return dist < (self.radius + player.width // 2)


    

        
