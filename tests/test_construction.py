"""Tests construction / placement (priorité #4).

- can_build() doit refuser hors carte, terrain non constructible, bâtiment existant,
  chantier existant, ressource, unité.
- Aucun coût ne doit être débité pour une construction invalide.
- Sans builder/worker disponible: comportement explicite sans perte de ressources.
- Pas de chantiers superposés.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.building import Farm, Barracks
from systems.economy import EconomySystem
from systems.construction import ConstructionSystem, BuildingProgress
from map.game_map import GameMap
from map.tile import Tile, TileType
from entities.worker import Worker
from entities.resource_node import ResourceNode


class FakeMap(GameMap):
    """Carte contrôlée pour les tests."""
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        # tout en herbe
        self.tiles = [[Tile(x, y, TileType.GRASS) for x in range(width)] for y in range(height)]

    def _generate_map(self):
        pass


@pytest.fixture
def cs():
    econ = EconomySystem()
    econ.gold = 1000
    econ.wood = 1000
    econ.food = 1000
    units = []
    buildings = []
    system = ConstructionSystem(econ, units, buildings)
    return system, econ


def make_buildable(system, w, h):
    """Étend le système avec les données de carte/nœuds."""
    system._game_map = FakeMap(w, h)
    system._all_nodes = []
    return system

def test_can_build_refuse_hors_carte(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    ok, reason = system.validate_build_position("farm", 5000, 5000)
    assert ok is False
    assert reason

def test_can_build_refuse_terrain_non_constructible(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    system._game_map.tiles[50][50] = Tile(50, 50, TileType.WATER)
    x, y = 50 * 32 + 16, 50 * 32 + 16
    ok, reason = system.validate_build_position("farm", x, y)
    assert ok is False
    assert "eau" in reason or "constructible" in reason or "non" in reason.lower()

def test_can_build_refuse_batiment_existant(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    system.buildings.append(Farm(100, 100, "player"))
    ok, reason = system.validate_build_position("farm", 100, 100)
    assert ok is False
    assert "bâtiment" in reason

def test_can_build_refuse_chantiere_close(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    site = BuildingProgress("farm", 100, 100, "player")
    system.construction_sites.append(site)
    ok, reason = system.validate_build_position("farm", 100, 100)
    assert ok is False
    assert "chantier" in reason

def test_construction_invalide_ne_debite_rien(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    system._game_map.tiles[50][50] = Tile(50, 50, TileType.WATER)
    x, y = 50 * 32 + 16, 50 * 32 + 16
    gold_before = econ.gold
    started = system.start_construction("farm", x, y)
    assert started is False
    assert econ.gold == gold_before, "aucun coût ne doit être débité si invalide"

def test_construction_valide_debite_une_fois(cs):
    system, econ = cs
    make_buildable(system, 128, 128)
    gold_before = econ.gold
    started = system.start_construction("farm", 100, 100)
    assert started is True
    assert econ.gold < gold_before, "le coût doit être débité pour une construction valide"