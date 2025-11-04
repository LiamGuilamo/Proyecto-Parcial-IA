# ARQUITECTURA DEL PROYECTO

## Diagrama de Capas

```
┌─────────────────────────────────────────────────────────┐
│              PRESENTACIÓN / INTERFAZ                    │
│  (Rendering, Menús, HUD, Input Handling)               │
│  Módulos: menu.py, constants.py (colores)              │
└────────────┬──────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────┐
│           LÓGICA DE JUEGO / GAME LOOP                │
│  (Game.update(), Game.draw(), Game.handle_input())   │
│  Módulo: game.py                                      │
└────────────┬──────────────────────────────────────────┘
             │
    ┌────────┴─────────────┬──────────────┬──────────────┐
    │                      │              │              │
┌───▼──────┐  ┌──────────┐  ┌──────┐  ┌─────────┐  ┌────────────┐
│ ENTIDADES│  │  MUNDO   │  │ SONIDO│  │BEHAVIORS│  │PATHFINDING│
│          │  │          │  │      │  │ TREE    │  │           │
│-Player   │  │ - Maze   │  │Sound │  │ -BTNode │  │ -AStar    │
│-Enemy    │  │ - Grid   │  │Manager│  │ -Action │  │ -Heuristic│
│-Bullet   │  │ - Collis │  │      │  │-Condition│ │-Find Path │
│-EvilOtto │  │          │  │      │  │-Sequence│  │           │
└──────────┘  └──────────┘  └──────┘  └─────────┘  └────────────┘

Módulos:      Módulos:       Módulos: Módulos:       Módulos:
game_entities maze.py       sound_   behavior_tree  pathfinding
                           manager   .py            .py
```

## Dependencias Entre Módulos

```
main.py
  └── game.py
       ├── constants.py
       ├── menu.py
       │    └── constants.py
       ├── maze.py
       │    ├── constants.py
       │    └── (pygame)
       ├── game_entities.py
       │    ├── constants.py
       │    ├── behavior_tree.py
       │    │    └── constants.py
       │    └── (pygame, math, random)
       ├── pathfinding.py
       │    └── (heapq)
       ├── sound_manager.py
       │    └── (pygame)
       └── (pygame, random, math)
```

## Flujo de Datos en un Frame

```
┌─────────────────────────────────────────────────┐
│  Inicio del Frame (60 FPS = 16.67ms)           │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  1. HANDLE INPUT                               │
│  - Procesar teclado                            │
│  - Procesar gamepad                            │
│  - Eventos de ventana (close, key, etc)        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  2. UPDATE                                     │
│  ┌──────────────────────────────────────────┐  │
│  │ Player.update()                          │  │
│  │ - Aplicar input al movimiento            │  │
│  │ - Procesar disparo                       │  │
│  │ - Actualizar cooldown                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Para cada Enemy.update():                │  │
│  │ - behavior_tree.tick()                   │  │
│  │   ├─ Evaluar condiciones (¿ver jugador?)│  │
│  │   ├─ Ejecutar acciones (moverse, etc)   │  │
│  │   └─ Si necesita pathfinding:           │  │
│  │       └─ AStar.find_path()              │  │
│  │ - Actualizar posición                    │  │
│  │ - Disparar si es necesario               │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ EvilOtto.update()                        │  │
│  │ - Seguir al jugador                      │  │
│  │ - Aumentar contador de spawn             │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Actualizar Bullets                       │  │
│  │ - Mover proyectiles                      │  │
│  │ - Detectar colisiones con muros          │  │
│  │ - Remover si salen de pantalla           │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ Detectar Colisiones                      │  │
│  │ - Proyectiles jugador ↔ Enemigos        │  │
│  │ - Proyectiles enemigos ↔ Jugador        │  │
│  │ - EvilOtto ↔ Jugador                    │  │
│  │ - Enemigos ↔ Jugador                    │  │
│  │ - Actualizar puntuación                  │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  3. DRAW                                       │
│  - Limpiar pantalla                            │
│  - Dibujar maze                                │
│  - Dibujar jugador                             │
│  - Dibujar enemigos                            │
│  - Dibujar EvilOtto                            │
│  - Dibujar bullets                             │
│  - Dibujar HUD (puntos, vidas, etc)            │
│  - Actualizar pantalla (flip)                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  4. FRAME RATE CONTROL                        │
│  - Esperar hasta alcanzar 60 FPS              │
└────────────────┬────────────────────────────────┘
                 │
                 └─► Siguiente Frame
```

## Máquina de Estados del Juego

```
               ┌─────────────┐
               │    MENU     │◄─────────────┐
               └──────┬──────┘              │
                      │ Jugar              │ ESC
                      │                    │
                ┌─────▼──────────┐         │
                │  MENU OPCIONES │         │
                └─────┬──────────┘         │
                      │ Seleccionar       │
                      │                    │
               ┌──────▼───────────┐        │
               │   PLAYING        │        │
               │ (Loop principal) │        │
               └──────┬───────────┘        │
                 ┌────┴────┐               │
    Escapar      │          │ Game Over   │
    Nivel        │          │ (0 vidas)   │
    ┌───────────┬┴──┐      ┌┴──────────┐  │
    │   VICTORY │   └─────►│ GAME_OVER ├──┘
    │ (siguiente├──────────┤ (retry)   │
    │   nivel)  │          └───────────┘
    └───────────┘
```

## Estructura de Datos Principales

### Maze (Laberinto)
```python
Maze
├── width: int (32)
├── height: int (24)
├── grid: List[List[int]]  # 0=pasable, 1=muro
├── exit_points: List[Tuple]  # Puntos de salida
└── methods
    ├── generate()
    ├── is_walkable(x, y)
    ├── is_wall_at(x, y)
    └── draw(screen, color)
```

### Player
```python
Player
├── x, y: float  # Posición
├── width, height: int  # Dimensiones
├── speed: float  # Velocidad
├── direction: Tuple  # Dirección actual
├── lives: int  # Vidas restantes
├── score: int  # Puntuación
├── shoot_cooldown: int  # Cooldown de disparo
└── methods
    ├── handle_input(keys, gamepad)
    ├── update(maze, bullets, sound_manager)
    ├── shoot(bullets, sound_manager)
    ├── draw(screen)
    ├── check_exit(maze)
    └── reset_position()
```

### Enemy
```python
Enemy
├── x, y: float  # Posición
├── enemy_type: int  # 1, 2, 3 - Dificultad
├── behavior_tree: BehaviorTree  # Sistema de IA
├── path: List  # Camino calculado por A*
├── shoot_cooldown: int
├── methods
    ├── create_behavior_tree()
    ├── can_see_player()
    ├── can_shoot()
    ├── move_towards_player()  # Usa A*
    ├── shoot_at_player()
    ├── patrol()
    ├── update(player, maze, bullets, sound_manager)
    └── draw(screen)
```

### BehaviorTree
```python
BehaviorTree
├── root: BTNode
└── methods
    └── tick(agent) → (SUCCESS | FAILURE | RUNNING)

BTNode (base)
├── tick(agent) [virtual]

BTSequence
├── children: List[BTNode]
├── tick(agent): ejecuta todos, falla si alguno falla

BTSelector
├── children: List[BTNode]
├── tick(agent): para en el primero que tenga éxito

BTAction
├── action_func: Callable
├── tick(agent): ejecuta función

BTCondition
├── condition_func: Callable
├── tick(agent): verifica condición
```

### AStar
```python
AStar
├── grid: List[List[int]]  # Mapa del laberinto
├── tile_size: int
├── methods
    ├── heuristic(pos1, pos2) → float
    ├── get_neighbors(pos) → List[pos]
    ├── find_path(start, goal) → List[pos]
    ├── get_grid_coords(pixel_pos) → grid_pos
    └── get_pixel_coords(grid_pos) → pixel_pos

Node
├── position: Tuple(x, y)
├── parent: Node
├── g, h, f: float  # Costos
└── operators
    ├── __lt__(other)  # Para heap
    └── __eq__(other)
```

## Optimizaciones Implementadas

1. **Render Mínimo**: Solo dibuja objetos visibles
2. **Pathfinding bajo demanda**: A* solo calcula cuando cambia objetivo
3. **Colisiones AABB**: Detección rápida con rectángulos
4. **Heap para A***: O(log n) en lugar de O(n)
5. **Soundeffects síncronos**: No genera lag
6. **FPS limitado**: 60 FPS constante con clock.tick()

## Requisitos de Memoria

| Componente | Tamaño |
|-----------|--------|
| Maze grid (32x24) | ~5 KB |
| Player | ~1 KB |
| Enemy (c/u) | ~500 B |
| Bullet (c/u) | ~200 B |
| BT nodes | ~100 B (c/u) |
| **Total típico** | **< 10 MB** |

## Benchmarks Esperados

| Operación | Tiempo |
|-----------|--------|
| Generate Maze | ~5 ms |
| A* search (5x5) | ~1-2 ms |
| BT tick | ~0.1 ms (x10 enemigos) |
| Render frame | ~8-10 ms |
| Total frame | ~14-16 ms (60 FPS) |

Este diseño modular permite:
✓ Fácil mantenimiento
✓ Pruebas unitarias
✓ Extensibilidad
✓ Rendimiento
✓ Claridad del código
