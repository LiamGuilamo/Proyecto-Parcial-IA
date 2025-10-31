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