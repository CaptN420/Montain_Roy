"""Test du système de Pathfinding (A*)\n"""

import sys
sys.path.insert(0, 'C:/Users/celes/Documents/Hermes-Workspace/Mountain_Roy')

from systems.pathfinding import Pathfinder
from map.game_map import GameMap

class MockGameMap:
    def __init__(self):
        # Grille 10x10
        self.grid = [[True] * 10 for _ in range(10)]
        # Ajouter des obstacles au milieu
        for y in range(3, 7):
            self.grid[5][y] = False

    def is_passable(self, x, y):
        if 0 <= x < 10 and 0 <= y < 10:
            return self.grid[y][x]
        return False

def test_pathfinding():
    print("=" * 50)
    print("TEST : Pathfinding A*")
    print("=" * 50)

    game_map = MockGameMap()
    pathfinder = Pathfinder(game_map)

    # Test 1: Chemin simple
    path = pathfinder.find_path(0, 0, 2, 2)
    print(f"Chemin (0,0) -> (2,2) : {path}")
    assert len(path) > 0, "Le chemin devrait être trouvé"

    # Test 2: Contournement d'obstacle
    # L'obstacle est à x=5, y=3 à 6.
    # On part de (0, 5) pour aller à (9, 5). Le chemin devrait contourner x=5.
    path = pathfinder.find_path(0, 5, 9, 5)
    print(f"Chemin (0,5) -> (9,5) avec obstacle : {path}")
    assert len(path) > 0, "Le chemin devrait contourner l'obstacle"
    
    # Vérifier qu'il ne passe pas par (5, 5)
    for p in path:
        assert p != (5, 5), f"Le chemin passe par un obstacle à {p}"
    
    print("✓ Pathfinding fonctionne correctement")

if __name__ == "__main__":
    test_pathfinding()
