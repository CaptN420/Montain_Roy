"""
Mountain_Roy - Game Map (Carte de jeu)
Étape 2: Génération et gestion de la carte
"""

import random
import pygame
from map.tile import Tile, TileType
from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE


class GameMap:
    """Gère la carte du jeu."""
    
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tiles = [[None for _ in range(self.width)] for _ in range(self.height)]
        self._generate_map()
    
    def _generate_map(self):
        """Génère une carte avec validation de connectivité et équilibre des ressources."""
        # Remplir avec de l'herbe
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = Tile(x, y, TileType.GRASS)
        
        # Ajouter des chemins (lignes horizontales et verticales) - plus larges
        for y in range(self.height):
            if random.random() < 0.4:
                for x in range(self.width):
                    self.tiles[y][x] = Tile(x, y, TileType.PATH)
        
        for x in range(self.width):
            if random.random() < 0.4:
                for y in range(self.height):
                    self.tiles[y][x] = Tile(x, y, TileType.PATH)
        
        # Zones de ressources équilibrées (quadrants)
        self._add_resource_zones()
        
        # Ajouter des obstacles avec validation
        self._add_obstacles_balanced()
    
    def _add_resource_zones(self):
        """Ajoute des zones de ressources équilibrées dans chaque quadrant."""
        qw = self.width // 2
        qh = self.height // 2
        
        # Quadrants: (x_start, y_start)
        quadrants = [
            (0, 0, "gold"),      # Haut-gauche: or
            (qw, 0, "wood"),     # Haut-droite: bois
            (0, qh, "wood"),     # Bas-gauche: bois
            (qw, qh, "gold"),    # Bas-droite: or
        ]
        
        for qx, qy, resource_type in quadrants:
            # Zone de 8x6 tuiles
            for dy in range(6):
                for dx in range(8):
                    tx = qx + dx
                    ty = qy + dy
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        if resource_type == "gold":
                            self.tiles[ty][tx] = Tile(tx, ty, TileType.GOLD_DEPOSIT)
                        else:
                            self.tiles[ty][tx] = Tile(tx, ty, TileType.WOOD_TREE)
    
    def _add_obstacles_balanced(self):
        """Ajoute des obstacles (forêts, montagnes, eau) de façon équilibrée."""
        # Forêts: 8% de la carte, évite les zones de ressources
        for _ in range(int(self.width * self.height * 0.08)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Évite les quadrants de ressources (coins)
            if not self._is_resource_zone(x, y):
                self.tiles[y][x] = Tile(x, y, TileType.FOREST)
        
        # Montagnes: 4% de la carte
        for _ in range(int(self.width * self.height * 0.04)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not self._is_resource_zone(x, y):
                self.tiles[y][x] = Tile(x, y, TileType.MOUNTAIN)
        
        # Eau: 3% de la carte (lacs)
        for _ in range(int(self.width * self.height * 0.03)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not self._is_resource_zone(x, y):
                self.tiles[y][x] = Tile(x, y, TileType.WATER)
    
    def _is_resource_zone(self, x, y):
        """Vérifie si une tuile est dans une zone de ressources."""
        qw = self.width // 2
        qh = self.height // 2
        
        # Quadrants de ressources (coins)
        if x < qw and y < qh:  # Haut-gauche
            return True
        if x >= qw and y < qh:  # Haut-droite
            return True
        if x < qw and y >= qh:  # Bas-gauche
            return True
        if x >= qw and y >= qh:  # Bas-droite
            return True
        
        return False
    
    def get_tile(self, x: int, y: int) -> Tile:
        """Récupère une tuile aux coordonnées données."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def is_passable(self, x: int, y: int) -> bool:
        """Vérifie si une tuile est traversable."""
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        return tile.passable
    
    def find_passable_position(self, x: int, y: int, radius: int = 100) -> tuple:
        """Trouve une position passable proche d'un point."""
        for r in range(radius, 0, -5):
            for angle in range(0, 360, 15):
                tx = int(x + r * pygame.math.Vector2(angle, 0).rotate(0).x // TILE_SIZE)
                ty = int(y + r * pygame.math.Vector2(angle, 0).rotate(0).y // TILE_SIZE)
                tile_x = int(tx // TILE_SIZE)
                tile_y = int(ty // TILE_SIZE)
                if self.is_passable(tile_x, tile_y):
                    return (tile_x * TILE_SIZE + TILE_SIZE // 2, 
                            tile_y * TILE_SIZE + TILE_SIZE // 2)
        # Fallback: centre de la carte
        cx = (self.width * TILE_SIZE) // 2
        cy = (self.height * TILE_SIZE) // 2
        return (cx, cy)
    
    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Dessine la carte visible."""
        # Convertir en int pour éviter les erreurs avec range()
        camera_x = int(camera_x)
        camera_y = int(camera_y)
        
        # Calculer les tuiles visibles
        start_x = max(0, camera_x // TILE_SIZE)
        end_x = min(self.width, (camera_x + screen.get_width()) // TILE_SIZE + 1)
        start_y = max(0, camera_y // TILE_SIZE)
        end_y = min(self.height, (camera_y + screen.get_height()) // TILE_SIZE + 1)
        
        # Dessiner chaque tuile visible
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                color = tile.get_color()
                
                # Position écran
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                
                pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                
                # Bordure subtile
                pygame.draw.rect(screen, (0, 0, 0, 20), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
