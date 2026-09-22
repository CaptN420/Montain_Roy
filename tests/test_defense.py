"""Tests du système de défense.

Vérifie :
- les tours tirent réellement sur les ennemis à portée (et pas sur les alliés),
- les tours ne tirent pas sur une cible hors portée,
- les murs bloquent le pathfinding (obstacles dynamiques),
- la synchronisation _update_defenses met à jour les cellules bloquées du
  pathfinder à chaque frame.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from core.game import Game
from entities.building import Tower, Wall
from entities.unit_types import Warrior
from entities.unit import Unit
from systems.pathfinding import Pathfinder


def _enemy(n=3, x=200, y=200):
    return [Warrior(x + i * 20, y, "enemy") for i in range(n)]


def _player_ally(x=100, y=100):
    return Warrior(x, y, "player")


def test_tour_tire_sur_ennemi_a_portee():
    g = Game()
    g.state = "playing"
    tower = Tower(500, 500, "player")
    g.buildings.append(tower)
    enemies = _enemy(x=520, y=500)  # à <128 de la tour
    g.units.extend(enemies)
    hp_before = enemies[0].hp
    # Lancer plusieurs frames pour dépasser le cooldown de 1s
    for _ in range(70):
        g._tower_fire(tower, 1.0 / 60)
    assert enemies[0].hp < hp_before, "la tour doit infliger des dégâts"


def test_tour_ignore_cible_hors_portee():
    g = Game()
    tower = Tower(500, 500, "player")
    far = Warrior(5000, 5000, "enemy")  # bien au-delà de 128
    g.units.append(far)
    hp_before = far.hp
    for _ in range(70):
        g._tower_fire(tower, 1.0 / 60)
    assert far.hp == hp_before, "pas de dégâts hors portée"


def test_tour_ne_tire_pas_sur_allie():
    g = Game()
    tower = Tower(500, 500, "player")
    ally = Warrior(510, 500, "player")
    g.units.append(ally)
    ally.take_damage = lambda dmg, attacker=None: None  # neutralise
    hp_before = ally.hp
    for _ in range(70):
        g._tower_fire(tower, 1.0 / 60)
    assert ally.hp == hp_before


def test_mur_bloque_le_chemin():
    pf = Pathfinder.__new__(Pathfinder)

    class FakeMap:
        def is_passable(self, x, y):
            return 0 <= x < 20 and 0 <= y < 20

    pf.game_map = FakeMap()
    pf.blocked_cells = set()
    # Pas de mur : chemin direct trouvé
    assert pf.find_path(0 * 32, 0 * 32, 3 * 32, 0 * 32)
    # Un mur barre la ligne : le chemin doit contourner ou échouer
    pf.add_blocked(2, 0)
    path = pf.find_path(0 * 32, 0 * 32, 3 * 32, 32)
    assert path, "un chemin alternatif doit exister (contournement)"


def test_mur_bloque_ligne_droite():
    pf = Pathfinder.__new__(Pathfinder)

    class FakeMap:
        def is_passable(self, x, y):
            return 0 <= x < 20 and 0 <= y < 5

    pf.game_map = FakeMap()
    pf.blocked_cells = set()
    # Une rangée complète de murs sur y=2 bloque le passage.
    for x in range(20):
        pf.add_blocked(x, 2)
    path = pf.find_path(1 * 32, 0 * 32, 1 * 32, 4 * 32)
    assert path == [], "une rangée de murs complète doit bloquer le déplacement"


def test_update_defenses_synchronise_les_murs():
    g = Game()
    wall = Wall(64, 64, "player")  # tuile (2,2)
    g.buildings.append(wall)
    g._update_defenses(0.016)
    assert (2, 2) in g.pathfinder.blocked_cells, "le mur doit bloquer sa tuile"


def test_update_defenses_enleve_mur_detruit():
    g = Game()
    wall = Wall(64, 64, "player")
    g.buildings.append(wall)
    g._update_defenses(0.016)
    assert (2, 2) in g.pathfinder.blocked_cells
    # Détruire le mur
    wall.hp = 0
    g._update_defenses(0.016)
    assert (2, 2) not in g.pathfinder.blocked_cells, "mur détruit = passage libre"