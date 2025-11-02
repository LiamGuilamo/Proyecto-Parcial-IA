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
        self.respawn_invulnerability = 120
        self.invulnerability_counter = self.respawn_invulnerability

    def handle_input(self, keys, gamepad=None):
        """entrada del jugador"""
        self.direction = DIRECTIONS["NONE"]

        #entrada por teclado
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

        #gamepad
        if gamepad:
            try:
                joy = pygame.joystick.Joystick(0)
                axes = joy.get_numaxes()

                #stick analogico izquierdo
                if axes  >= 2:
                    x_axis = joy.get_axis(0)
                    y_axis = joy.get_axis(1)

                    if abs(x_axis)  > 0.5 or abs(y_axis)  > 0.5:
                        self.direction = (int(x_axis), int(y_axis))
                        if self.direction == (0, 0):
                            self.direction = DIRECTIONS["NONE"]
            
            except:
                pass

    def shoot(self, bullets, sound_manager):
        """dispara un proyectil"""
        if self.shoot_cooldown <= 0:
            #dispara en la direccion actual
            if self.direction != DIRECTIONS["NONE"]:
                dx, dy = self.direction
                bullet = Bullet(self.x, self.y, dx, dy, is_player=True)
                bullets.append(bullet)
                self.shoot_cooldown = SHOOT_COOLDOWN
                if sound_manager:
                    sound_manager.play_sound("shoot")

    def update(self, maze, bullets, sound_manager, gamepad=None):
        """estado del jugador"""
        keys = pygame.key.get_pressed()
        self.handle_input(keys, gamepad)

        #movimiento
        if self.direction != DIRECTIONS["NONE"]:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            #colision con muros
            if maze.is_walkable(new_x, new_y) and maze.is_walkable(new_x + self.width, new_y + self.height):
                self.x = new_x
                self.y = new_y

        #disparo
        if keys[pygame.K_SPACE]:
            self.shoot(bullets, sound_manager)

        #cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1 
        
        #vulnerabilidad
        if self.invulnerability_counter > 0:
            self.invulnerability_counter -= 1
        
    def draw(self, screen):
        """dibuja el jugador"""
        # si esta en vulnerabilidad, parpadear
        if self. invulnerability_counter > 0 and self.invulnerability_counter % 10 < 5:
            color = CYAN
        else:
            color = GREEN

        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)

    def check_exit(self, maze):
        """verificar si el jugador salio de la mazmorra"""
        player_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

        #comprobar limites
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            return True
        return False
    
    def reset_position(self):
        """resetea la posicion del jugador al inicio"""
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.invulnerability_counter = self.respawn_invulnerability

class Bullet:
    """clase de proyectil"""

    def __init__(self, x, y, dx, dy, is_player=True):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.is_player = is_player
        self.speed = BULLET_SPEED
        self.size = 4
    
    def update(self,maze):
        """actuliza la posicion del proyectil"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        #comprobar colision con muros
        if not maze.is_walkable(self.x, self.y):
            return False #delete proyectil
        
        #comprobar si salio de pantalla
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            return False

        return True

    def draw(self, screen):
        """dibuja el proyectil""" 
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
        self.enemy_type = enemy_type
        self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN + random.randint(0, 30)
        self.direction = DIRECTIONS["NONE"]
        self.vision_range = 300
        self.shoot_range = 250
        self.path = []
        self.path_counter = 0
        self.patrol_target = None
        self.patrol_timer = 0

        #comportamiento
        self.player = None
        self,bullets = None
        self.sound_manager = None

        #behavior
        self.behavior_tree = self.create_behavior_treee()
    
    def create_behavior_tree(self):
        """Arbol de comportamiento (enemigo)"""
        if self.enemy_type == 1:
            #perseguir y disparar si ve al jugador
            root = BTSelector()

            #rama 1: si puede disparar, dispare
            shoot_sequence = BTSequence()
            shoot_sequence.add_child(BTCondition(self.condition_can_see_player))
            shoot_sequence.add_child(BTCondition(self.condition_can_shoot))
            shoot_sequence.add_child(BTAction(self.action_shoot_at_player))

            #rama 2: si ve al jugador, persiguelo
            chase_sequence = BTSequence()
            chase_sequence.add_child(BTCondition(self.condition_can_see_player))
            chase_sequence.add_child(BTAction(self.action_move_towards_player))

            #rama 3: patrullar
            action_patrol = BTAction(self.action_patrol)

            root.add_child(shoot_sequence)
            root.add_child(chase_sequence)
            root.add_child(action_patrol)

            return BehaviorTree(root)
        
        else:
            #tipo 2 y 3: mas agresivos 
            root = BTPriority()

            #Atacar si es posible
            attack_seq = BTSequence()
            attack_seq.add_child(BTCondition(self.condition_can_see_player))
            attack_seq.add_child(BTCondition(self.condition_can_shoot))
            attack_seq.add_child(BTAction(self.action_shoot_at_player))

            #perseguir
            chase_seq = BTSequence()
            chase_seq.add_child(BTCondition(self.condition_can_see_player))
            chase_seq.add_child(BTAction(self.action_move_towards_player))

            #patrullar
            patrol = BTAction(self.action_patrol)

            root.add_child(attack_seq)
            root.add_child(chase_seq)
            root.add_child(patrol)

            return BehaviorTree(root)
        
    #condiciones del behavior Tree
    def condition_can_see_player(self, agent=None):
        """cerifica si el enemigo puede ver al jugador"""
        if self.player is None:
            return False
        
        #distancia del jugador 
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        #retornar true si esta dentro del rango de vision
        return distance < self.vision_range
    
    def condition_can_shoot(self, agent=None):
        """verifica si el jugador se encuentra cerca"""
        if self.player is None:
            return False
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        return dist < self.shoot_range
    
    #acciones del behavior tree
    def action_move_towards_player(self, agent=None):
        """moverse hacia el jugador"""
        if self.player is None:
            return BT_FAILURE
        
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist > 0:
            #normalizar direccion
            self.direction = (int(dx / dist * 2), int(dy / dist * 2))

            return BT_SUCCESS
        
        def action_shoot_at_player(self, agent=None):
            """accion disparar al jugador"""
            if self.player is None or self.bullets is None:
                return BT_FAILURE
            
            dx = self.player.x - self.x
            dy = self.player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)

            #solo disparar si esta en el rango
            if 0 < dist < self.shoot_range:
                #direcciones del disparador 
                bullet_dx = int(dx / dist)
                bullet_dy = int (dy / dist)
                bullet = Bullet(self.x, self.y, bullet_dx, bullet_dy, is_player=False)
                self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
                if self.sound_manager:
                    self.sound_manager.play_sound("enemy_shoot")
                return BT_SUCCESS
            
            return BT_FAILURE
        
        def action_patrol(self, agent=None):
            """patrullar aleatoriamente"""
            self.patrol_timer -= 1

            if self.patrol_timer <= 0:
                #elegir nueva direccion 
                angle = random.random() * 2 * math.pi
                self.direction = (int(math.cos(angle) * 2), int(math.sin(angle) * 2))
                self.patrol_timer = random.randint(30, 100)
        
        return BT_SUCCESS
    
    def update(self, player, maze, bullets, sound_manager):
        """actualizar el estado del enemigo"""
        self.player = player
        self.bullets = bullets
        self.sound_manager = sound_manager

        #ejecutar behavior tree
        self.behavior_tree.tick(self)

        #movimiento basado en la direccion
        if self.direction != DIRECTIONS["NONE"]:
            dx, dy = self.direction
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            if maze.is_walkable(new_x, new_y) and maze.is_walkable(new_x + self.width, new_y + self.height):
                self.x = new_x
                self.y = new_y

        #actualizar cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        """dibuja el enemigo"""
        colors = [RED, pygame.Color("orange"), pygame.Color("purpple")]
        colors = colors[min(self.enemy_type - 1, len(colors) - 1)]

        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)

        #debug: dibujar rango de vision


class EvilOtto:
    """Enemigo especial"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.speed = ENEMY_SPEED * 1.5
        self.active = False
        self.time_untill_spawn = EVIL_OTTO_SPAWN_TIME

    def update(self, player, maze):
        """actualizacion de Evil Otto"""
        if not self.active:
            self.time_untill_spawn -= 1
            if self.time_untill_spawn <= 0: 
                self.active = True
                print("EVIL OTTO HA APARECIDO")

        if self.active and player:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > 0: 
                # Evil Otto puede atravesar muro
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, screen):
        """EVIL OTTO"""
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int( self.y)), self.radius)
            #ojos
            pygame.draw.circle(screen, BLACK, (int(self.x) - 5, int(self.y) - 3), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x) + 5, int(self.y) - 3), 2)

    def check_collision(self, player):
        """verifica colision con el jugador"""
        if not self.active:
            return False

        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        return dist < (self.radius + player.width // 2)

    
            


        

    

        
