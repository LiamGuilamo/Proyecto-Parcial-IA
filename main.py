import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from game import Game

def main():
    """Funcion Principal"""
    fullscreen = True
    if len(sys.argv)  > 1:
        if sys.argv[1] == "--windowed":
            fullscreen = False

    #crear e iniciar el juego
    game = Game(fullscreen=fullscreen)
    game.run()

if __name__ == "__main__":
    main() 