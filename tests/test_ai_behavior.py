"""Tests du comportement économique/défensif de l'IA ennemie.

Vérifie : récolte par les workers seuls, combat par les unités de combat
seules, défense des nodes de ressources, production qui paie les vraies
ressources + cap de population.
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from entities.worker import Worker
from entities.unit_types import Warrior
from entities.unit import Unit
from systems.ai import EnemyAI


# --------------------------------------------------------------- fixtures
class RecordingMovement:
    """Enregistre les ordres de déplacement/attaque émis par l'IA."""
    def __init__(self):
        self.attack_orders = []  # (attacker, target)
        self.move_orders = []    # (unit, x, y)

    def attack_target(self, unit, target):
        self.attack_orders.append((unit, target))

    def move_to(self, unit, x, y):
        self.move_orders.append((unit, x, y))


def _w(x, y, faction="enemy"):
    w = Worker(x, y, faction)
    return w


def _combat(x, y, faction="enemy", unit_type="warrior"):
    u = Warrior(x, y, faction)
    u.unit_type = unit_type
    return u


def _player(x, y):
    return Unit(x, y, "player")


def _node(x, y, depleted=False):
    return SimpleNamespace(x=x, y=y, is_depleted=lambda: depleted)


def _game(**over):
    """Construit un game fantôme réaliste pour l'IA."""
    econ = SimpleNamespace(gold=500, wood=500, food=500,
                           get_max_population=lambda buildings: 25)
    ghost = SimpleNamespace(
        units=[],
        buildings=[],
        resource_nodes=[],
        enemy_economy=econ,
        economy=econ,
        movement_system=RecordingMovement(),
    )
    for k, v in over.items():
        setattr(ghost, k, v)
    return ghost


# ----------------------------------------------------------- récolte
def test_gather_assigns_workers_pas_de_combat():
    worker = _w(50, 50)
    warrior = _combat(60, 60)          # target par défaut None
    game = _game(units=[worker, warrior], resource_nodes=[_node(100, 100)])
    ai = EnemyAI(game)
    ai._gather_resources(0.016)
    # Le worker est assigné à la mine...
    assert worker.target_resource is not None
    # ...mais PAS le guerrier (l'ancien code l'y envoyait car target is None).
    assert getattr(warrior, "target_resource", None) is None


def test_gather_ignore_worker_deja_assignee():
    worker = _w(50, 50)
    node = _node(100, 100)
    worker.target_resource = node
    game = _game(units=[worker], resource_nodes=[_node(200, 200)])
    ai = EnemyAI(game)
    ai._gather_resources(0.016)
    assert worker.target_resource is node, "ne pas réassigner un worker occupé"


def test_gather_ignore_worker_qui_porte():
    worker = _w(50, 50)
    worker.carrying = True
    game = _game(units=[worker, _w(200, 200)], resource_nodes=[_node(300, 300)])
    ai = EnemyAI(game)
    ai._gather_resources(0.016)
    # Le worker qui porte ne doit pas être réassigné ; l'autre peut l'être.
    assert worker.target_resource is None


# ----------------------------------------------------------- attaque
def test_attack_combat_uniquement():
    attacker = _combat(0, 0)
    worker = _w(10, 0)
    target = _player(300, 0)
    game = _game(units=[attacker, worker, target])
    ai = EnemyAI(game)
    ai._attack_player()
    attackers_ordered = [a for a, t in game.movement_system.attack_orders]
    assert attacker in attackers_ordered, "l'unité de combat part attaquer"
    assert worker not in attackers_ordered, "le worker NE doit PAS partir au combat"


# ----------------------------------------------------------- défense des nodes
def test_defend_reagit_a_une_menace_pres_dun_node():
    defender = _combat(0, 0)
    node = _node(500, 500)                 # node ennemi éloigné de l'armée
    player_raider = _player(510, 510)      # menace à < 250 du node
    game = _game(units=[defender, player_raider], resource_nodes=[node],
                 buildings=[SimpleNamespace(faction="enemy", building_type="town_hall", x=100, y=100)])
    ai = EnemyAI(game)
    ai._defend_base()
    skills = game.movement_system.attack_orders
    assert skills, "l'IA doit défendre le node menacé"
    assert player_raider in [t for a, t in skills], "la menace (raider) doit être attaquée"


def test_defend_n_envoie_pas_le_worker_au_combat():
    defender = _combat(0, 0)
    worker = _w(5, 0)
    node = _node(500, 500)
    player_raider = _player(510, 510)
    game = _game(units=[defender, worker, player_raider], resource_nodes=[node],
                 buildings=[SimpleNamespace(faction="enemy", building_type="town_hall", x=100, y=100)])
    ai = EnemyAI(game)
    ai._defend_base()
    ordered = [a for a, t in game.movement_system.attack_orders]
    assert worker not in ordered, "le worker ne doit pas défendre (il récolte)"


def test_defend_ignore_menace_loin_de_tout_interest():
    defender = _combat(0, 0)
    node = _node(500, 500)
    player_far = _player(2000, 2000)       # trop loin de tout point ennemi
    game = _game(units=[defender, player_far], resource_nodes=[node],
                 buildings=[SimpleNamespace(faction="enemy", building_type="town_hall", x=100, y=100)])
    ai = EnemyAI(game)
    ai._defend_base()
    assert game.movement_system.attack_orders == [], "aucune défense si pas de menace proche"


# ----------------------------------------------------------- production
def test_produce_paye_les_vraies_ressources():
    econ = SimpleNamespace(gold=500, wood=500, food=500,
                           get_max_population=lambda buildings: 25)
    game = _game(units=[],
                 buildings=[SimpleNamespace(building_type="barracks", faction="enemy", x=0, y=0)],
                 economy=econ, enemy_economy=econ)
    before = len(game.units)
    ai = EnemyAI(game)
    ai._produce_units()
    assert len(game.units) == before + 1, "une unité doit être produite"
    # knight (le plus cher abordable) : 100 or, 50 bois, 20 nourriture.
    assert econ.gold == 400
    assert econ.wood == 450
    assert econ.food == 480


def test_produce_descend_sur_unit_moins_chere_si_inabordable():
    # 79 or : knight(100) et mage(80) inabordables -> archer(40) OK
    econ = SimpleNamespace(gold=79, wood=500, food=500,
                           get_max_population=lambda buildings: 25)
    game = _game(units=[],
                 buildings=[SimpleNamespace(building_type="barracks", faction="enemy", x=0, y=0)],
                 economy=econ, enemy_economy=econ)
    ai = EnemyAI(game)
    ai._produce_units()
    produced = [u for u in game.units if u.faction == "enemy"][-1]
    assert produced.unit_type == "archer", "doit produire l'arc (40 or) abordable"
    assert econ.gold == 39
    assert econ.wood == 480  # 500 - 20


def test_produce_bloque_a_cap_de_population():
    econ = SimpleNamespace(gold=5000, wood=5000, food=5000,
                           get_max_population=lambda buildings: 1)  # cap très bas
    units = [_combat(0, 0)]  # population >= cap
    game = _game(units=units,
                 buildings=[SimpleNamespace(building_type="barracks", faction="enemy", x=0, y=0)],
                 economy=econ, enemy_economy=econ)
    before = len(game.units)
    ai = EnemyAI(game)
    ai._produce_units()
    assert len(game.units) == before, "aucune production au-delà du cap"
    assert econ.gold == 5000, "ressources intactes quand la prod est bloquée"


def test_produce_sans_caserne_ne_fait_rien():
    econ = SimpleNamespace(gold=5000, wood=5000, food=5000,
                           get_max_population=lambda buildings: 25)
    game = _game(units=[], buildings=[], economy=econ, enemy_economy=econ)
    before = len(game.units)
    ai = EnemyAI(game)
    ai._produce_units()
    assert len(game.units) == before


def test_produit_nouvelle_unite_a_game_reference():
    econ = SimpleNamespace(gold=500, wood=500, food=500,
                           get_max_population=lambda buildings: 25)
    game = _game(units=[],
                 buildings=[SimpleNamespace(building_type="barracks", faction="enemy", x=0, y=0)],
                 economy=econ, enemy_economy=econ)
    ai = EnemyAI(game)
    ai._produce_units()
    new_unit = game.units[-1]
    assert new_unit.game is game, "l'unité produite doit référencer le Game (synergie/récolte)"


# --------------------------------------------------------------- héros IA
def _hero_game(buildings, gold=5000, wood=5000, food=5000):
    econ = SimpleNamespace(gold=gold, wood=wood, food=food,
                           get_max_population=lambda b: 99)
    game = _game(units=[SimpleNamespace(faction="enemy", x=0, y=0, unit_type="worker",
                                        hp=100, target_resource=None)],
                 buildings=buildings, economy=econ, enemy_economy=econ)
    game.faction_id = "human"
    game.construction_system = SimpleNamespace(
        validate_build_position=lambda *a, **k: (True, ""))
    return game


def _enemy_heroes(game):
    return [u for u in game.units
            if getattr(u, "faction", "") == "enemy"
            and getattr(u, "unit_type", "").startswith("hero_")]


def test_ai_construit_un_herohall_quand_il_a_deja_une_caserne():
    from entities.building import HeroHall
    from entities.building import Barracks
    barracks = Barracks(0, 0, "enemy")
    game = _hero_game([barracks])
    ai = EnemyAI(game)
    gold = game.enemy_economy.gold
    ai._build_structures()
    halls = [b for b in game.buildings if getattr(b, "building_type", "") == "hero_hall"
             and b.faction == "enemy"]
    assert isinstance(halls[0], HeroHall), "l'IA doit construire un bâtiment à héros"
    # 180 or / 120 bois / 40 nourriture
    assert game.enemy_economy.gold == gold - 180
    assert game.enemy_economy.wood == 5000 - 120


def test_ai_invoque_3_heros_ennemis():
    from entities.building import HeroHall
    hall = HeroHall(200, 200, "enemy")
    game = _hero_game([hall])
    ai = EnemyAI(game)
    ai._manage_heroes()
    ai._manage_heroes()
    ai._manage_heroes()

    heroes = _enemy_heroes(game)
    assert len(heroes) == 3, "l'IA doit pouvoir invoquer ses 3 héros"
    assert len({h.unit_type for h in heroes}) == 3
    assert all(h.faction == "enemy" for h in heroes)


def test_ai_paye_les_heros_invoques():
    from entities.building import HeroHall
    from entities.hero_types import HERO_SUMMON_COSTS, HERO_ORDER
    hall = HeroHall(200, 200, "enemy")
    game = _hero_game([hall])
    gold_before = game.enemy_economy.gold
    ai = EnemyAI(game)
    ai._manage_heroes()  # warrior d'abord
    assert game.enemy_economy.gold == gold_before - HERO_SUMMON_COSTS["warrior"]["gold"]


def test_ai_ne_dedouble_pas_heros_vivant():
    from entities.building import HeroHall
    hall = HeroHall(200, 200, "enemy")
    game = _hero_game([hall])
    ai = EnemyAI(game)
    for _ in range(3):
        ai._manage_heroes()
    count = len(_enemy_heroes(game))
    gold = game.enemy_economy.gold
    ai._manage_heroes()  # un 4e tick : rien à invoquer
    assert len(_enemy_heroes(game)) == count
    assert game.enemy_economy.gold == gold


def test_ai_sans_herohall_n_invoque_pas():
    game = _hero_game([SimpleNamespace(building_type="barracks", faction="enemy",
                                       x=0, y=0, hp=100)])
    ai = EnemyAI(game)
    ai._manage_heroes()
    assert _enemy_heroes(game) == []