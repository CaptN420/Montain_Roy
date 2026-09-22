"""
Mountain_Roy - Combat System (Système de combat)
Étape 4: Logique de combat
"""

import pygame


class CombatSystem:
    """Gère les combats entre unités."""
    
    def __init__(self):
        pass
    
    def find_target(self, unit, units: list, range_threshold: float = None) -> object:
        """Trouve la cible la plus proche d'une unité."""
        if range_threshold is None:
            range_threshold = unit.range
        
        closest_unit = None
        min_distance = range_threshold
        
        for other in units:
            if other == unit or other.faction == unit.faction:
                continue
            
            dx = other.x - unit.x
            dy = other.y - unit.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_unit = other
        
        return closest_unit
    
    def attack(self, attacker, target):
        """Effectue une attaque."""
        if target.hp <= 0:
            return False
        
        # take_damage applique déjà l'armure : on passe les dégâts bruts.
        target.take_damage(attacker.damage)
        
        # Effet visuel simple (sera amélioré plus tard)
        self._draw_attack_effect(attacker, target)
        
        return True
    
    def _draw_attack_effect(self, attacker, target, screen=None, camera_x=0, camera_y=0):
        """Dessine un effet visuel simple pour l'attaque."""
        if screen is None:
            return
        # Ligne flash entre l'attaquant et la cible
        import pygame
        sx1 = int(attacker.x - camera_x)
        sy1 = int(attacker.y - camera_y)
        sx2 = int(target.x - camera_x)
        sy2 = int(target.y - camera_y)
        pygame.draw.line(screen, (255, 255, 100), (sx1, sy1), (sx2, sy2), 2)
    
    def check_dead_units(self, units: list) -> list:
        """Retire les unités mortes et retourne la liste mise à jour."""
        alive_units = [u for u in units if u.is_alive()]
        return alive_units
