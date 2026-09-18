"""
Mountain_Roy - Camera (Caméra)
Étape 2: Système de caméra RTS
"""

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    """Gère la caméra du jeu."""
    
    def __init__(self, map_width: int, map_height: int):
        self.x = 0
        self.y = 0
        self.map_width = map_width
        self.map_height = map_height
        self.zoom = 1.0
        self.zoom_speed = 0.1

        # Limites de la caméra (en pixels)
        self.min_x = 0
        self.min_y = 0
        self.max_x = max(0, map_width - SCREEN_WIDTH)
        self.max_y = max(0, map_height - SCREEN_HEIGHT)
    
    def move(self, dx: int, dy: int):
        """Déplace la caméra."""
        self.x += dx
        self.y += dy
        
        # Limiter aux bords de la carte
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))
    
    def zoom_in(self):
        """Zoom avant."""
        if self.zoom < 2.0:
            self.zoom += self.zoom_speed
    
    def zoom_out(self):
        """Zoom arrière."""
        if self.zoom > 0.5:
            self.zoom -= self.zoom_speed
    
    def update_bounds(self):
        """Mets à jour les limites de la caméra."""
        self.max_x = max(0, self.map_width - SCREEN_WIDTH)
        self.max_y = max(0, self.map_height - SCREEN_HEIGHT)
    
    def screen_to_map(self, screen_x: int, screen_y: int) -> tuple:
        """Convertit les coordonnées écran en coordonnées carte."""
        map_x = screen_x + self.x
        map_y = screen_y + self.y
        return (map_x, map_y)
    
    def map_to_screen(self, map_x: int, map_y: int) -> tuple:
        """Convertit les coordonnées carte en coordonnées écran."""
        screen_x = map_x - self.x
        screen_y = map_y - self.y
        return (screen_x, screen_y)
