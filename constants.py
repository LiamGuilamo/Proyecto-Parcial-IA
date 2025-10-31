import pygame

#pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32

#colores
BLACK =(0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN =(0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

#configuracion
FPS = 60
PLAYER_SPEED = 4
ENEMY_SPEED = 2
BULLET_SPEED = 6
SHOOT_COOLDOWN = 20
ENEMY_SHOOT_COOLDOWN = 30
EVIL_OTTO_SPAWN_TIME = 300

#Tipos de nodos 
BT_SUCCESS = "success"
BT_FAILURE = "failure"
BT_RUNNING = "running"

#direccion
DIRECTIONS = {
     "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP_LEFT": (-1, -1),
    "UP_RIGHT": (1, -1),
    "DOWN_LEFT": (-1, 1),
    "DOWN_RIGHT": (1, 1),
    "NONE": (0, 0)
}
#Estados del juego
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"
GAME_STATE_VICTORY = "victory"


# Puntos
POINTS_DESTROY_ENEMY = 100
POINTS_ROOM_CLEAR_BONUS = 500
POINTS_LIVES_GAINED_AT = 1000

n