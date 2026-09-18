"""
Mountain_Roy - Main Entry Point
Étape 1: Lancement du jeu
"""

import os
import sys

# Force window positioning and disable scaling
os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_VIDEO_HIGHDPI_DISABLED'] = '1'
os.environ['SDL_VIDEO_DPI_SCALE'] = '1.0'

# Try to set DPI awareness BEFORE pygame init
try:
    import ctypes
    windll = ctypes.windll
    # PROCESS_SYSTEM_DPI_AWARE = 1
    result = windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from core.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
