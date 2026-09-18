"""
Mountain_Roy - Tile (Tuile)
Étape 2: Système de carte
"""

from enum import Enum
import pygame


class TileType(Enum):
    """Types de tuiles disponibles."""
    GRASS = "grass"
    FOREST = "forest"
    WATER = "water"
    MOUNTAIN = "mountain"
    PATH = "path"
    GOLD_DEPOSIT = "gold_deposit"
    WOOD_TREE = "wood_tree"


class Tile:
    """Représente une tuile de la carte."""
    
    def __init__(self, x: int, y: int, tile_type: TileType):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        
        # Collision (impassable)
        self.passable = tile_type in [TileType.GRASS, TileType.PATH]
        
        # Resources (peut être récolté)
        self.has_resource = tile_type in [TileType.GOLD_DEPOSIT, TileType.WOOD_TREE]
        self.resource_amount = 100 if tile_type == TileType.GOLD_DEPOSIT else 50
        
    def get_color(self) -> tuple:
        """Retourne la couleur de la tuile."""
        from settings import COLORS
        
        colors = {
            TileType.GRASS: COLORS["grass"],
            TileType.FOREST: COLORS["forest"],
            TileType.WATER: COLORS["water"],
            TileType.MOUNTAIN: COLORS["mountain"],
            TileType.PATH: COLORS["path"],
            TileType.GOLD_DEPOSIT: COLORS["gold"],
            TileType.WOOD_TREE: COLORS["wood"],
        }
        return colors.get(self.tile_type, COLORS["grass"])
    
    def to_tuple(self) -> tuple:
        """Retourne la tuile comme tuple pour le stockage."""
        return (self.x, self.y, self.tile_type.value)
    
    @classmethod
    def from_tuple(cls, data: tuple) -> "Tile":
        """Crée une tuile depuis un tuple."""
        x, y, type_str = data
        return cls(x, y, TileType(type_str))
