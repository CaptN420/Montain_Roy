"""Tests pathfinding + movement + separation (priorité #5).

- Le pathfinding A* doit éviter les tuiles impassables (eau/montagne/forêt).
- Pas de diagonales à travers les coins bloqués.
- MovementSystem suit le chemin par points de passage, se re-route si bloqué.
- Une unité ne doit JAMAIS se trouver sur une tuile impassable.
- La séparation de deux unités convergent (pas d'oscillation, reste en carte).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from map.game_map import GameMap
from map.tile import Tile, TileType
from entities.unit import Unit
from systems.pathfinding import Pathfinder
from systems.movement import MovementSystem
from systems.collision import CollisionSystem


class ControlledMap(GameMap):
    """Carte contrôlée pour les tests (tout herbe, modifiable)."""
    def __init__(self, width=32, height=32):
        self.width = width
        self.height = height
        self.tiles = [[Tile(x, y, TileType.GRASS) for x in range(width)] for y in range(height)]

    def _generate_map(self):
        pass

    def block(self, tx, ty, tile_type=TileType.MOUNTAIN):
        self.tiles[ty][tx] = Tile(tx, ty, tile_type)


def tile_center(tx, ty):
    return (tx * 32 + 16, ty * 32 + 16)


def make_system(width=32, height=32):
    pmap = ControlledMap(width, height)
    return pmap, MovementSystem(pmap, Pathfinder(pmap))


# ---------------------------------------------------------------------------
# Pathfinding
# ---------------------------------------------------------------------------
def test_pathfinding_returns_path_to_reachable_target():
    pmap = ControlledMap()
    path = Pathfinder(pmap).find_path(16, 16, tile_center(5, 5)[0], tile_center(5, 5)[1])
    assert path, "un chemin doit exister si la cible est atteignable"
    assert path[0] == (0, 0)
    assert path[-1] == (5, 5)


def test_pathfinding_avoids_impassable_tiles():
    pmap = ControlledMap()
    # Mur vertical d'eau en x=3 avec une brèche passable à y=5, pour forcer un détour.
    for y in range(pmap.height):
        if y != 5:  # laisser une brèche
            pmap.block(3, y, TileType.WATER)
    start = tile_center(0, 5)
    end = tile_center(30, 5)
    path_tiles = Pathfinder(pmap).find_path(start[0], start[1], end[0], end[1])
    assert path_tiles, "il doit exister un chemin contournant l'eau"
    # aucun point du chemin ne doit être sur une tuile impassable
    for (tx, ty) in path_tiles:
        assert pmap.is_passable(tx, ty), f"chemin traverse une tuile impassable ({tx},{ty})"


def test_pathfinding_returns_empty_when_target_on_impassable():
    pmap = ControlledMap()
    pmap.block(5, 5, TileType.WATER)
    ex, ey = tile_center(5, 5)
    path = Pathfinder(pmap).find_path(16, 16, ex, ey)
    assert path == []


def test_pathfinding_no_diagonal_through_blocked_corner():
    """Un pas diagonal (0,0)->(1,1) doit être interdit si (1,0) ou (0,1) est bloqué."""
    pmap = ControlledMap()
    # bloque (1,0) mais laisse (0,1) passé : le coin diagonal (0,0)->(1,1) est coupé
    pmap.block(1, 0, TileType.MOUNTAIN)
    path_tiles = Pathfinder(pmap).find_path(16, 16, tile_center(1, 1)[0], tile_center(1, 1)[1])
    assert path_tiles, "un chemin alternatif (détour) doit exister"
    # Aucun pas du chemin ne doit être une diagonale traversant un coin bloqué.
    for (a, b), (c, d) in zip(path_tiles, path_tiles[1:]):
        dx, dy = c - a, d - b
        if dx != 0 and dy != 0:  # pas diagonal
            orthogonal_a_open = pmap.is_passable(a + dx, b)
            orthogonal_b_open = pmap.is_passable(a, b + dy)
            assert orthogonal_a_open and orthogonal_b_open, \
                f"pas diagonal {a,b}->{c,d} coupe un coin bloqué"
    # Le détour doit être moins direct que le raccourci interdit.
    assert path_tiles[0] == (0, 0) and path_tiles[-1] == (1, 1)


# ---------------------------------------------------------------------------
# MovementSystem (intégration du pathfinding)
# ---------------------------------------------------------------------------
def test_unit_follows_path_avoiding_obstacle():
    pmap, ms = make_system()
    # Mur vertical d'eau avec une brèche en y=6, pour forcer un contournement.
    for y in range(pmap.height):
        if y != 6:
            pmap.block(10, y, TileType.WATER)
    unit = Unit(16, 16, "player")
    unit.speed = 200
    end = tile_center(25, 16)
    ms.move_to(unit, end[0], end[1])
    assert unit.is_moving and unit.path

    for _ in range(2000):
        ms.update(unit, 1 / 60)
        if not unit.is_moving:
            break
        # jamais sur une tuile impassable pendant le trajet
        tx, ty = int(unit.x // 32), int(unit.y // 32)
        assert pmap.is_passable(tx, ty), f"unité entrée dans une tuile impassable ({tx},{ty})"

    assert not unit.is_moving, "l'unité doit atteindre sa cible"
    assert abs(unit.x - end[0]) <= 10 and abs(unit.y - end[1]) <= 10


def test_unit_reroutes_when_path_blocked():
    """Si un obstacle apparaît sur le chemin, l'unité se re-route et n'entre pas dedans."""
    pmap, ms = make_system()
    unit = Unit(16, 16, "player")
    unit.speed = 200
    end = tile_center(20, 16)
    ms.move_to(unit, end[0], end[1])
    assert unit.path

    # Après quelques frames, on bloque le prochain point de passage sur la route.
    for _ in range(5):
        ms.update(unit, 1 / 60)
    if unit.path:
        nx, ny = unit.path[0]
        pmap.block(int(nx // 32), int(ny // 32), TileType.MOUNTAIN)

    for _ in range(2000):
        ms.update(unit, 1 / 60)
        if not unit.is_moving:
            break
        tx, ty = int(unit.x // 32), int(unit.y // 32)
        assert pmap.is_passable(tx, ty), "l'unité ne doit jamais entrer dans l'obstacle après re-routage"

    assert not unit.is_moving, "l'unité doit atteindre sa cible malgré le blocage en cours de route"
    assert abs(unit.x - end[0]) <= 10 and abs(unit.y - end[1]) <= 10


def test_update_without_any_order_does_nothing():
    pmap, ms = make_system()
    unit = Unit(16, 16, "player")
    ms.update(unit, 1 / 60)  # ne doit pas lever d'exception ni bouger
    assert unit.x == 16 and unit.y == 16


# ---------------------------------------------------------------------------
# Séparation des unités (convergence sans oscillation)
# ---------------------------------------------------------------------------
def make_units_at(x1, y1, x2, y2):
    u1 = Unit(x1, y1, "player")
    u2 = Unit(x2, y2, "player")
    return u1, u2


def test_separation_converges_without_oscillation():
    pmap = ControlledMap()
    cs = CollisionSystem()
    cs.game_map = pmap
    cs.separation_distance = 25
    min_d = cs.separation_distance + 16 + 16  # radius unité + radius + separation

    u1, u2 = make_units_at(400, 400, 420, 400)  # overlapping
    dists = []
    for _ in range(30):
        cs.resolve_all_collisions([u1, u2])
        dists.append(((u1.x - u2.x) ** 2 + (u1.y - u2.y) ** 2) ** 0.5)

    assert dists[-1] >= min_d - 1.0, "les unités doivent converger au-delà de la distance minimale"
    # Ne doit pas osciller : la distance ne doit pas redescendre après convergence stabilité
    assert dists[-1] >= dists[0], "la distance ne doit pas avoir rétréci (oscillation) après la première séparation"


def test_separation_never_pushes_units_out_of_map():
    pmap = ControlledMap(width=8, height=8)  # 256x256 px
    cs = CollisionSystem()
    cs.game_map = pmap
    cs.separation_distance = 25

    u1, u2 = make_units_at(20, 20, 22, 22)  # en haut à gauche, chevauchés
    for _ in range(50):
        cs.resolve_all_collisions([u1, u2])
        for u in (u1, u2):
            assert 0 <= u.x <= pmap.width * 32, f"unité sortie de la carte en x={u.x}"
            assert 0 <= u.y <= pmap.height * 32, f"unité sortie de la carte en y={u.y}"