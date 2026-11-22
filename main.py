"""
Modern Military Tower Defence
Application Entrypoint.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
