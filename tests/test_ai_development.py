"""Tests du développement de l'IA ennemie.

Vérifie que l'IA se développe pour inquiéter le joueur :
- produit des workers supplémentaires (économie en croissance),
- construit des fermes pour lever le cap de population,
- construit des casernes supplémentaires et des tours défensives,
- attaque de façon proactive dès que son armée atteint sa cible (pas besoin
  de dominer le joueur).
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.worker import Worker
from entities.unit_types import Warrior
from entities.unit import Unit
from entities.building import TownHall, Farm, Tower, Barracks
from systems.ai import EnemyAI


def _w(x, y, faction="enemy"):
    return Worker(x, y, faction)


def _combat(x, y, faction="enemy", unit_type="warrior"):
    u = Warrior(x, y, faction)
    u.unit_type = unit_type
    u.game = None
    return u


def _building(btype, x, y, faction="enemy"):
    return SimpleNamespace(building_type=btype, faction=faction, x=x, y=y,
                           hp=100)


class _RecMove:
    def __init__(self):
        self.attack_orders = []

    def attack_target(self, unit, target):
        self.attack_orders.append((unit, target))


def _game(workers=4, combat_units=0, farms=3, gold=1000, wood=1000, food=1000,
          with_construction=True, units=None, buildings=None):
    econ = SimpleNamespace(gold=gold, wood=wood, food=food,
                           get_max_population=lambda buildings: 10 + 5 * sum(
                               1 for b in buildings if b.building_type == "farm"))
    if units is None:
        units = [_w(i, 100) for i in range(workers)]
        units += [_combat(i, 200) for i in range(combat_units)]
    else:
        units = list(units)
    if buildings is None:
        buildings = [_building("town_hall", 0, 0)] + \
                    [_building("farm", i, 0) for i in range(farms)]
    else:
        buildings = list(buildings)
    ghost = SimpleNamespace(
        units=units,
        buildings=buildings,
        resource_nodes=[],
        enemy_economy=econ,
        economy=econ,
        movement_system=_RecMove(),
        construction_system=SimpleNamespace(
            validate_build_position=lambda *a, **k: (True, "")),
    )
    for u in units:
        u.game = ghost
    return ghost


def test_produit_des_workers_supplementaires():
    game = _game(workers=4)
    ai = EnemyAI(game)
    before = len([u for u in game.units if u.unit_type == "worker"])
    ai._produce_workers()
    after = len([u for u in game.units if u.unit_type == "worker"])
    assert after == before + 1, "l'IA doit produire un worker de plus"
    # 30 or / 15 bois / 5 nourriture débités
    assert game.enemy_economy.gold == 1000 - 30


def test_produit_workers_avec_reference_jeu():
    game = _game(workers=4)
    ai = EnemyAI(game)
    ai._produce_workers()
    new_worker = [u for u in game.units if u.unit_type == "worker"][-1]
    assert new_worker.game is game, "worker doit référencer le Game (récolte)"


def test_ne_produit_pas_worker_sans_or():
    game = _game(workers=4, gold=50)  # réserve < 120
    ai = EnemyAI(game)
    before = len(game.units)
    ai._produce_workers()
    assert len(game.units) == before


def test_ne_produit_pas_worker_a_cap_pop():
    # cap 10+5*0=10, 10 workers dejà -> plus de production
    game = _game(workers=10, farms=0)
    ai = EnemyAI(game)
    before = len(game.units)
    ai._produce_workers()
    assert len(game.units) == before


def test_construit_des_fermes_pour_lever_pop():
    # pop=10 (cap très bas), 0 ferme -> doit construire une ferme
    game = _game(workers=10, farms=0, gold=5000, wood=5000)
    ai = EnemyAI(game)
    farms_before = len([b for b in game.buildings if b.building_type == "farm"])
    ai._build_farms_as_needed()
    farms_after = len([b for b in game.buildings if b.building_type == "farm"])
    assert farms_after == farms_before + 1, "l'IA doit agrandir son cap de pop"
    assert isinstance([b for b in game.buildings if b.building_type == "farm"][-1], Farm)


def test_n_ajoute_pas_de_ferme_si_pop_confortable():
    game = _game(workers=4, farms=3)  # cap 25, pop 4 -> pas besoin
    ai = EnemyAI(game)
    farms_before = len([b for b in game.buildings if b.building_type == "farm"])
    ai._build_farms_as_needed()
    farms_after = len([b for b in game.buildings if b.building_type == "farm"])
    assert farms_after == farms_before


def test_construit_casernes_supplementaires():
    game = _game(workers=4, gold=5000, wood=5000, food=5000)
    # On active la cible à 2 casernes (normal)
    ai = EnemyAI(game)
    ai.dev["barracks"] = 2
    before = len([b for b in game.buildings if b.building_type == "barracks"])
    ai._build_extra_barracks()
    after = len([b for b in game.buildings if b.building_type == "barracks"])
    assert after == before + 1


def test_construit_tours_defensives():
    game = _game(workers=4, combat_units=3, gold=5000, wood=5000)
    ai = EnemyAI(game)
    ai.dev["towers"] = 2
    before = len([b for b in game.buildings if b.building_type == "tower"])
    ai._build_towers()
    after = len([b for b in game.buildings if b.building_type == "tower"])
    assert after == before + 1
    assert isinstance([b for b in game.buildings if b.building_type == "tower"][-1], Tower)


def test_pas_de_tour_sans_armee():
    game = _game(workers=4, combat_units=0, gold=5000, wood=5000)
    ai = EnemyAI(game)
    ai.dev["towers"] = 2
    before = len([b for b in game.buildings if b.building_type == "tower"])
    ai._build_towers()
    assert len([b for b in game.buildings if b.building_type == "tower"]) == before


def test_attack_proactive_sans_dominer():
    # 10 unités de combat vs 10 unités au joueur : l'IA attaque car >= cible
    game = _game(workers=4, combat_units=10)
    players = [Unit(i, 500, "player") for i in range(10)]
    game.units += players
    ai = EnemyAI(game)
    ai.dev["army"] = 8
    ai.state = "gather"
    ai._choose_state()
    assert ai.state == "attack", "l'IA doit attaquer dès que son armée atteint la cible"


def test_attaque_agressive_des_23_de_la_cible():
    # Normal : seuil agressif = ~2/3 (max(3, int(7*0.66)=4)). 5 unités -> attaquer.
    game = _game(workers=8, combat_units=5)
    players = [Unit(i, 500, "player") for i in range(5)]
    game.units += players
    ai = EnemyAI(game)  # difficulty normal -> army 7, seuil 4
    assert ai.dev["army"] == 7
    ai.state = "gather"
    ai._choose_state()
    assert ai.state == "attack", "seuil agressif (2/3) déclenché avec 5 unités"


# --------------------------------------------------------------- tactique
def test_cible_strategique_production_prioritaire():
    # La production joueur prime sur l'hôtel de ville et les unités.
    player_barracks = SimpleNamespace(building_type="barracks", faction="player",
                                      x=200, y=200, hp=100)
    player_th = SimpleNamespace(building_type="town_hall", faction="player",
                                x=300, y=300, hp=100)
    game = _game(workers=4, combat_units=3)
    game.buildings += [player_barracks, player_th]
    game.enemy_economy = game.economy
    ai = EnemyAI(game)
    target = ai._strategic_player_target()
    assert target is player_barracks, "un bâtiment de production est prioritaire"


def test_cible_strategique_repli_sur_hotel_de_ville():
    player_th = SimpleNamespace(building_type="town_hall", faction="player",
                                x=50, y=50, hp=100)
    game = _game(workers=4, combat_units=3)
    game.buildings += [player_th]
    ai = EnemyAI(game)
    target = ai._strategic_player_target()
    assert target is player_th, "sans production, l'hôtel de ville est la cible"


def test_cible_strategique_repli_sur_armee_joueur():
    game = _game(workers=4, combat_units=3)
    players = [Unit(100, 100, "player") for _ in range(3)]
    game.units += players
    ai = EnemyAI(game)
    target = ai._strategic_player_target()
    assert target in players, "sans bâtiment, une unité joueur est la cible"


def test_attaque_concentre_larmee_sur_une_seule_cible():
    # Toute l'armée doit être ordonnée d'attaquer LA MÊME cible (concentration).
    enemy_units = [_combat(0, i * 10) for i in range(4)]
    player_th = SimpleNamespace(building_type="town_hall", faction="player",
                                x=500, y=500, hp=100)
    game = _game(units=enemy_units,
                 buildings=[_building("town_hall", 0, 0), player_th],
                 gold=5000, wood=5000)
    for u in enemy_units:
        u.game = game
    ai = EnemyAI(game)
    ai.dev["garrison"] = 0  # pas de garnison pour ce test
    ai._attack_player()
    orders = game.movement_system.attack_orders
    assert len(orders) == len(enemy_units), "toute l'armée doit être ordonnée"
    targets = {id(t) for _, t in orders}
    assert len(targets) == 1 and id(player_th) in targets, \
        "l'armée doit se concentrer sur la cible stratégique unique"


def test_attaque_garde_une_garnison_en_defense():
    enemy_units = [_combat(0, i * 10) for i in range(6)]
    player_th = SimpleNamespace(building_type="town_hall", faction="player",
                                x=500, y=500, hp=100)
    game = _game(units=enemy_units,
                 buildings=[_building("town_hall", 100, 100), player_th],
                 gold=5000, wood=5000)
    for u in enemy_units:
        u.game = game
    ai = EnemyAI(game)
    ai.dev["garrison"] = 2
    ai._attack_player()
    orders = game.movement_system.attack_orders
    attack_count = len(orders)
    assert attack_count == 4, f"garnison de 2 doit rester : {attack_count} attaquent"


def test_develop_produit_workers_puis_construit():
    game = _game(workers=4, gold=5000, wood=5000, food=5000, farms=0)
    ai = EnemyAI(game)
    ai.dev["workers"] = 8
    ai._develop()
    # Premier appel : il reste < 8 workers -> produit un worker
    workers = sum(1 for u in game.units if u.unit_type == "worker")
    assert workers == 5
    # Une fois les workers au max, il passe à la construction
    game2 = _game(workers=8, gold=5000, wood=5000, food=5000, farms=0)
    ai2 = EnemyAI(game2)
    ai2.dev["workers"] = 8
    ai2._develop()
    assert any(b.building_type == "farm" for b in game2.buildings), \
        "workers comblés -> la prochaine étape est de construire une ferme"