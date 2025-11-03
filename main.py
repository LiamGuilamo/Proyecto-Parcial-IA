#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maze Runner - Un juego basado en mecánicas de Berzerk
Archivo principal de ejecución

Uso: python main.py [--windowed]

El juego corre a pantalla completa por defecto.
Usa --windowed para ejecutar en ventana.
"""

import sys
import os

# Agregar el directorio de scripts al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.game import Game

def main():
    """Función principal"""
    # Verificar argumentos
    fullscreen = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "--windowed":
            fullscreen = False
    
    # Crear e iniciar el juego
    game = Game(fullscreen=fullscreen)
    game.run()

if __name__ == "__main__":
    main()
