"""
Mountain_Roy - Formation System (Système de Formation)
Étape 15: Unités en formation
"""

import pygame
import math


class Formation:
    """Gère les formations de unités."""
    
    def __init__(self, formation_type: str = "line"):
        self.type = formation_type
        self.offsets = []
        self._calculate_offsets()
    
    def _calculate_offsets(self):
        """Calcule les décalages pour la formation."""
        spacing = 40  # Distance entre les unités
        
        if self.type == "line":
            # Formation en ligne
            for i in range(-3, 4):
                self.offsets.append((i * spacing, 0))
        
        elif self.type == "column":
            # Formation en colonne
            for i in range(-3, 4):
                self.offsets.append((0, i * spacing))
        
        elif self.type == "triangle":
            # Formation en triangle
            positions = [
                (0, -spacing),      # Pointe
                (-spacing, 0),      # Gauche
                (spacing, 0),       # Droite
                (-spacing // 2, spacing // 2),  # Gauche bas
                (spacing // 2, spacing // 2),   # Droite bas
            ]
            self.offsets = positions
        
        elif self.type == "circle":
            # Formation en cercle
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                radius = spacing
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                self.offsets.append((x, y))
        
        elif self.type == "diamond":
            # Formation en diamant
            positions = [
                (0, -spacing),      # Haut
                (-spacing // 2, -spacing // 2),  # Gauche haut
                (spacing // 2, -spacing // 2),   # Droite haut
                (-spacing, 0),      # Gauche
                (spacing, 0),       # Droite
                (0, spacing),       # Bas
            ]
            self.offsets = positions
    
    def get_offset(self, index: int) -> tuple:
        """Récupère le décalage pour une unité."""
        if not self.offsets:
            return (0, 0)
        return self.offsets[index % len(self.offsets)]


class FormationManager:
    """Gère les formations des unités sélectionnées."""
    
    def __init__(self):
        self.formations = {
            "line": Formation("line"),
            "column": Formation("column"),
            "triangle": Formation("triangle"),
            "circle": Formation("circle"),
            "diamond": Formation("diamond"),
        }
        self.current_formation = "line"
    
    def set_formation(self, formation_type: str):
        """Change la formation."""
        if formation_type in self.formations:
            self.current_formation = formation_type
    
    def apply_formation(self, units: list, target_x: int, target_y: int):
        """Applique la formation aux unités."""
        for i, unit in enumerate(units):
            offset = self.formations[self.current_formation].get_offset(i)
            
            # Calculer la position cible avec le décalage
            new_x = target_x + offset[0]
            new_y = target_y + offset[1]
            
            # Déplacer l'unité
            unit.is_moving = True
            unit.move_target = (new_x, new_y)
    
    def get_formation_names(self) -> list:
        """Retourne les noms des formations disponibles."""
        return list(self.formations.keys())


class UnitAvoidance:
    """Gère l'évitement de collision entre unités."""
    
    def __init__(self):
        self.separation_distance = 30
    
    def apply_separation(self, unit, all_units: list):
        """Applique la séparation aux unités proches."""
        dx, dy = 0, 0
        count = 0
        
        for other in all_units:
            if other == unit:
                continue
            
            other_dx = other.x - unit.x
            other_dy = other.y - unit.y
            distance = math.sqrt(other_dx ** 2 + other_dy ** 2)
            
            if distance < self.separation_distance and distance > 0:
                # Repousser l'unité
                dx -= other_dx / distance
                dy -= other_dy / distance
                count += 1
        
        if count > 0:
            # Normaliser et appliquer
            dx /= count
            dy /= count
            length = math.sqrt(dx ** 2 + dy ** 2)
            
            if length > 0:
                unit.x += dx / length * 2
                unit.y += dy / length * 2
    
    def update(self, units: list):
        """Met à jour l'évitement pour toutes les unités."""
        for unit in units:
            self.apply_separation(unit, units)
