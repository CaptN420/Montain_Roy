"""
Mountain_Roy - Movement System (Système de mouvement)
Étape 4: Déplacement des unités

Priorité #5: intégration du pathfinding A*. Les unités suivent un itinéraire
par points de passage, se re-routent si un obstacle apparaît, et ne traversent
jamais une tuile impassable.
"""

import pygame
from entities.unit import Unit
from systems.pathfinding import Pathfinder

TILE = 32


def is_diagonal(dx, dy):
    return dx != 0 and dy != 0


class MovementSystem:
    """Gère le déplacement des unités via un chemin A*."""

    def __init__(self, game_map, pathfinder=None):
        self.game_map = game_map
        self.pathfinder = pathfinder or Pathfinder(game_map)
        self.arrival_distance = 5

    def move_to(self, unit: Unit, target_x: int, target_y: int):
        """Déplace une unité vers une position en calculant un chemin A*."""
        unit.is_moving = True
        unit.move_target = (target_x, target_y)
        unit.path = self._compute_path(unit.x, unit.y, target_x, target_y)

    def _compute_path(self, start_x: float, start_y: float, end_x: float, end_y: float) -> list:
        """Calcule une liste de points de passage (pixels) du point de départ à la cible."""
        start_tile = (int(start_x // TILE), int(start_y // TILE))
        end_tile = (int(end_x // TILE), int(end_y // TILE))

        if start_tile == end_tile:
            return [(float(end_x), float(end_y))]

        path_tiles = self.pathfinder.find_path(start_x, start_y, end_x, end_y)
        if not path_tiles:
            # Aucun chemin : on tente quand même la cible directe (l'update se
            # chargera de ne pas entrer dans une tuile impassable).
            return [(float(end_x), float(end_y))]

        waypoints = []
        for tx, ty in path_tiles:
            if (tx, ty) == start_tile and len(path_tiles) > 1:
                continue  # ne pas reculer sur la tuile de départ
            waypoints.append((float(tx * TILE + 16), float(ty * TILE + 16)))

        # Toujours terminer sur la position exacte demandée.
        if waypoints:
            waypoints[-1] = (float(end_x), float(end_y))
        else:
            waypoints = [(float(end_x), float(end_y))]
        return waypoints

    def attack_target(self, unit: Unit, target_unit: Unit):
        """Ordre d'attaquer une unité ennemie."""
        unit.is_moving = False
        unit.target = target_unit

    def update(self, unit: Unit, dt: float):
        """Met à jour le mouvement et le combat d'une unité."""
        self._move_along_path(unit, dt)

        # Vérifier si l'unité peut attaquer
        if unit.target and hasattr(unit.target, 'hp') and unit.target.hp > 0:
            dx = unit.target.x - unit.x
            dy = unit.target.y - unit.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= unit.range + getattr(unit.target, 'radius', 0):
                # Attaquer
                unit.attack_timer += dt
                if unit.attack_timer >= unit.attack_speed:
                    unit.attack_timer = 0
                    unit.target.take_damage(unit.damage, attacker=unit)
            else:
                # Poursuivre la cible (avec pathfinding)
                unit.is_moving = True
                unit.move_target = (unit.target.x, unit.target.y)
                unit.path = self._compute_path(unit.x, unit.y, unit.target.x, unit.target.y)
        else:
            unit.target = None

    def _move_along_path(self, unit: Unit, dt: float):
        """Avance l'unité le long de son chemin, point de passage après point."""
        if not (unit.is_moving and unit.move_target):
            return

        # Re-route si le premier point de passage est devenu impassable.
        if unit.path:
            sx, sy = int(unit.path[0][0] // TILE), int(unit.path[0][1] // TILE)
            if not self.game_map.is_passable(sx, sy):
                unit.path = self._compute_path(unit.x, unit.y, unit.move_target[0], unit.move_target[1])

        if not unit.path:
            unit.is_moving = False
            unit.move_target = None
            return

        step = unit.path[0]
        dx = step[0] - unit.x
        dy = step[1] - unit.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.arrival_distance:
            unit.path.pop(0)
            if not unit.path:
                unit.x, unit.y = unit.move_target
                unit.is_moving = False
                unit.move_target = None
            return

        move_dist = unit.speed * dt
        if move_dist >= distance:
            unit.x, unit.y = step
            unit.path.pop(0)
            if not unit.path:
                unit.is_moving = False
                unit.move_target = None
            return

        unit.x += (dx / distance) * move_dist
        unit.y += (dy / distance) * move_dist