"""
Mountain_Roy - Fog of War System (Brouillard de guerre)
Étape 7: Système de brouillard de guerre
"""

import pygame
import math


class FogOfWar:
    """Gère le brouillard de guerre."""
    
    def __init__(self, map_width: int, map_height: int):
        self.map_width = map_width
        self.map_height = map_height
        
        # Grille de vision (en tuiles)
        # 0 = jamais exploré, 1 = exploré mais pas visible, 2 = actuellement visible
        self.explored = [[0 for _ in range(map_width)] for _ in range(map_height)]
        self.visible = [[False for _ in range(map_width)] for _ in range(map_height)]
        
        # Rayon de vision par défaut
        self.vision_radius = 8  # tuiles
        
    def update(self, units: list, buildings: list):
        """Met à jour la vision basée sur les unités et bâtiments."""
        # Réinitialiser la visibilité
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.visible[y][x] = False
        
        # Mettre à jour pour chaque entité visible
        entities = []
        for unit in units:
            if unit.faction == "player":
                entities.append({
                    'x': int(unit.x / 32),
                    'y': int(unit.y / 32),
                    'radius': self.vision_radius
                })
        
        for building in buildings:
            if building.faction == "player":
                entities.append({
                    'x': int(building.x / 32),
                    'y': int(building.y / 32),
                    'radius': self.vision_radius
                })
        
        # Pour chaque entité, marquer les tuiles visibles
        for entity in entities:
            self._reveal_area(entity['x'], entity['y'], entity['radius'])
    
    def _reveal_area(self, center_x: int, center_y: int, radius: int):
        """Révèle une zone autour d'un point."""
        # Cercle de vision
        for y in range(max(0, center_y - radius), min(self.map_height, center_y + radius)):
            for x in range(max(0, center_x - radius), min(self.map_width, center_x + radius)):
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= radius:
                    self.visible[y][x] = True
                    self.explored[y][x] = 1  # Marquer comme exploré
    
    def is_visible(self, x: int, y: int) -> bool:
        """Vérifie si une position est visible."""
        tile_x = int(x / 32)
        tile_y = int(y / 32)
        
        if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
            return self.visible[tile_y][tile_x]
        return False
    
    def is_explored(self, x: int, y: int) -> bool:
        """Vérifie si une position a été explorée."""
        tile_x = int(x / 32)
        tile_y = int(y / 32)
        
        if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
            return self.explored[tile_y][tile_x] > 0
        return False
    
    def draw(self, screen, game_map, camera):
        """Dessine le brouillard de guerre."""
        # Pour chaque tuile, vérifier si elle est visible
        for y in range(self.map_height):
            for x in range(self.map_width):
                if not self.explored[y][x]:
                    # Jamais exploré - noir
                    screen_x = x * 32 - camera.x
                    screen_y = y * 32 - camera.y
                    
                    # Dessiner seulement si visible à l'écran
                    if (0 <= screen_x < screen.get_width() and 
                        0 <= screen_y < screen.get_height()):
                        pygame.draw.rect(screen, (0, 0, 0), 
                                       (screen_x, screen_y, 32, 32))
                elif not self.visible[y][x]:
                    # Exploré mais pas visible - gris foncé
                    screen_x = x * 32 - camera.x
                    screen_y = y * 32 - camera.y
                    
                    if (0 <= screen_x < screen.get_width() and 
                        0 <= screen_y < screen.get_height()):
                        pygame.draw.rect(screen, (50, 50, 50), 
                                       (screen_x, screen_y, 32, 32))
