"""
Mountain_Roy - Collision System (Système de collision)
Étape 14: Prévention du stacking des unités + collisions avec forêts
"""

import math


class CollisionSystem:
    """Gère les collisions entre unités et obstacles (forêts)."""
    
    def __init__(self):
        self.separation_distance = 25  # Distance minimale entre unités
        self.resource_nodes = []  # Liste des nœuds de ressources (obstacles)
        self.game_map = None  # Optionnel : pour borner les unités dans la carte
    
    def resolve_collision(self, unit, all_units: list, resource_nodes: list = None):
        """Résout la collision d'une unité avec les autres et les obstacles."""
        if resource_nodes:
            self.resource_nodes = resource_nodes

        # Collision avec les forêts (obstacles) - sauf si mode bucheron
        if not getattr(unit, 'can_cut_trees', False):
            self._check_forest_collision(unit)

        # Collision avec autres unités (sauf workers portant des ressources)
        is_worker_carrying = (getattr(unit, 'unit_type', None) == 'worker' and getattr(unit, 'carrying', False))
        for other in all_units:
            if other == unit:
                continue
            # Workers porteurs ne poussent pas les autres (et vice versa)
            other_carrying = (getattr(other, 'unit_type', None) == 'worker' and getattr(other, 'carrying', False))
            if is_worker_carrying and other_carrying:
                continue

            dx = other.x - unit.x
            dy = other.y - unit.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Distance minimale entre les centres (rayons + séparation)
            min_distance = unit.radius + other.radius + self.separation_distance
            
            if distance < min_distance:
                if distance > 0:
                    # Pousser l'unité courante complètement hors du chevauchement.
                    # Un push complet (facteur 1.0) fait converger la paire à la
                    # distance minimale dans cette itération et évite l'oscillation
                    # d'un push fractionnaire répété à chaque frame.
                    overlap = min_distance - distance
                    nx = dx / distance
                    ny = dy / distance
                    # nx/ny pointent de l'unité courante vers l'autre : on pousse
                    # l'unité courante dans la direction OPPOSÉE (loin de l'autre).
                    unit.x -= nx * overlap
                    unit.y -= ny * overlap
                else:
                    # Centres exactement superposés : écarter légèrement et de façon déterminée.
                    unit.x += 1.0
                    unit.y += 1.0
        
        self._clamp_to_bounds(unit)

    def _clamp_to_bounds(self, unit):
        """Empêche une unité de sortir des limites de la carte."""
        if self.game_map is None:
            return
        width_px = self.game_map.width * 32
        height_px = self.game_map.height * 32
        r = getattr(unit, 'radius', 16)
        unit.x = max(r, min(width_px - r, unit.x))
        unit.y = max(r, min(height_px - r, unit.y))
    
    def _check_forest_collision(self, unit):
        """Vérifie la collision avec les forêts."""
        for node in self.resource_nodes:
            if node.resource_type != "wood" or node.is_depleted():
                continue

            dx = node.x - unit.x
            dy = node.y - unit.y
            distance = math.sqrt(dx**2 + dy**2)

            # Éviter division par zéro si l'unité est exactement sur l'arbre
            if distance == 0:
                # Pousser dans une direction aléatoire
                import random
                angle = random.uniform(0, 2 * math.pi)
                unit.x += math.cos(angle) * (node.radius + unit.radius)
                unit.y += math.sin(angle) * (node.radius + unit.radius)
                continue

            # Collision avec l'arbre (rayon + rayon unité)
            if distance < node.radius + unit.radius:
                # Pousser l'unité hors de l'arbre
                push_x = (dx / distance) * (node.radius + unit.radius - distance)
                push_y = (dy / distance) * (node.radius + unit.radius - distance)
                unit.x += push_x
                unit.y += push_y
    
    def resolve_all_collisions(self, units: list):
        """Résout toutes les collisions entre unités."""
        for unit in units:
            self.resolve_collision(unit, units)
    
    def can_place_unit(self, x: int, y: int, radius: int, existing_units: list) -> bool:
        """Vérifie si on peut placer une unité à cette position."""
        for unit in existing_units:
            dx = unit.x - x
            dy = unit.y - y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            min_distance = unit.radius + radius + self.separation_distance
            if distance < min_distance:
                return False
        
        return True
    
    def find_safe_position(self, x: int, y: int, radius: int, existing_units: list, max_attempts: int = 10) -> tuple:
        """Trouve une position sûre pour placer une unité."""
        for attempt in range(max_attempts):
            offset_x = (attempt % 4) * 20
            offset_y = (attempt // 4) * 20
            
            test_x = x + offset_x
            test_y = y + offset_y
            
            if self.can_place_unit(test_x, test_y, radius, existing_units):
                return (test_x, test_y)
        
        # Si aucune position sûre trouvée, retourner la position originale
        return (x, y)
