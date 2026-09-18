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
        
        # Appliquer les dégâts
        actual_damage = max(1, attacker.damage - target.armor)
        target.take_damage(actual_damage)
        
        # Effet visuel simple (sera amélioré plus tard)
        self._draw_attack_effect(attacker, target)
        
        return True
    
    def _draw_attack_effect(self, attacker, target):
        """Dessine un effet visuel simple pour l'attaque."""
        # Ligne entre l'attaquant et la cible
        pass  # Sera implémenté dans le rendu
    
    def check_dead_units(self, units: list) -> list:
        """Retire les unités mortes et retourne la liste mise à jour."""
        alive_units = [u for u in units if u.is_alive()]
        return alive_units
