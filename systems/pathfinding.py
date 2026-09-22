"""
Mountain_Roy - Pathfinding (A* Algorithm)
Étape 4: Système de pathfinding
"""

import heapq
from map.game_map import GameMap


class Pathfinder:
    """Algorithme A* pour le pathfinding."""

    def __init__(self, game_map: GameMap):
        self.game_map = game_map
        # Tuiles occupées par des obstacles dynamiques (murs). Set de (x, y).
        # Mis à jour par le jeu quand un mur est construit/détruit.
        self.blocked_cells = set()

    def set_blocked(self, cells):
        """Remplace l'ensemble des cellules bloquées (tuiles (x, y))."""
        self.blocked_cells = set(cells)

    def add_blocked(self, x, y):
        self.blocked_cells.add((x, y))

    def remove_blocked(self, x, y):
        self.blocked_cells.discard((x, y))

    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int) -> list:
        """Trouve un chemin entre deux points."""
        # Convertir en coordonnées grille
        start_tile_x = int(start_x / 32)
        start_tile_y = int(start_y / 32)
        end_tile_x = int(end_x / 32)
        end_tile_y = int(end_y / 32)
        
        # Vérifier si les points sont valides
        if not self._is_valid_tile(start_tile_x, start_tile_y):
            return []
        if not self._is_valid_tile(end_tile_x, end_tile_y):
            return []
        
        # A* algorithm
        open_set = [(0, start_tile_x, start_tile_y)]
        came_from = {}
        g_score = {(start_tile_x, start_tile_y): 0}
        f_score = {(start_tile_x, start_tile_y): self._heuristic(start_tile_x, start_tile_y, end_tile_x, end_tile_y)}
        
        while open_set:
            _, current_x, current_y = heapq.heappop(open_set)
            
            # On a atteint la destination
            if current_x == end_tile_x and current_y == end_tile_y:
                return self._reconstruct_path(came_from, (current_x, current_y))
            
            # Voisins (8 directions)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy
                
                if not self._is_valid_tile(neighbor_x, neighbor_y):
                    continue
                
                # Interdire les diagonales qui coupent un coin bloqué : (x+dx, y)
                # et (x, y+dy) doivent tous deux être passables.
                if dx != 0 and dy != 0:
                    if not self._is_valid_tile(current_x + dx, current_y):
                        continue
                    if not self._is_valid_tile(current_x, current_y + dy):
                        continue
                
                # Coût du mouvement (diagonale plus cher)
                movement_cost = 1.4 if dx != 0 and dy != 0 else 1.0
                tentative_g = g_score[(current_x, current_y)] + movement_cost
                
                if (neighbor_x, neighbor_y) not in g_score or tentative_g < g_score[(neighbor_x, neighbor_y)]:
                    came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                    g_score[(neighbor_x, neighbor_y)] = tentative_g
                    f = tentative_g + self._heuristic(neighbor_x, neighbor_y, end_tile_x, end_tile_y)
                    f_score[(neighbor_x, neighbor_y)] = f
                    heapq.heappush(open_set, (f, neighbor_x, neighbor_y))
        
        # Pas de chemin trouvé
        return []
    
    def _heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Heuristique Manhattan."""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _is_valid_tile(self, x: int, y: int) -> bool:
        """Vérifie si une tuile est valide et traversable."""
        if not self.game_map.is_passable(x, y):
            return False
        if (x, y) in self.blocked_cells:
            return False
        return True
    
    def _reconstruct_path(self, came_from: dict, current: tuple) -> list:
        """Reconstruit le chemin depuis came_from."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
