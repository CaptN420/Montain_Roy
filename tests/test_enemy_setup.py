"""Tests du camp ennemi configurable par mission (difficulté croissante).

Vérifie : initialize_enemy_base lit la config de la mission courante, accepte une
config explicite, retombe sur DEFAULT_ENEMY_CONFIG sans mission, produit une
difficulté croissante entre missions, serialise enemy_config, et donne aux
workers ennemis la référence au Game.
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from systems.ai import EnemyAI, DEFAULT_ENEMY_CONFIG
from systems.campaign import Mission, Objective, create_default_campaign


def _ghost(mission_cfg=None):
    """Game fantôme : mission avec (ou sans) enemy_config."""
    mission = SimpleNamespace(enemy_config=mission_cfg)
    return SimpleNamespace(
        current_mission=mission,
        units=[],
        buildings=[],
        enemy_economy=SimpleNamespace(gold=0, wood=0, food=0),
    )


def _want():
    return {"town_hall": True, "barracks": False, "farms": 1, "collection": False,
            "towers": 1, "workers": 2, "warriors": 5,
            "gold": 999, "wood": 888, "food": 777}


def _enemy_counts(game):
    eunits = [u for u in game.units if u.faction == "enemy"]
    workers = [u for u in eunits if getattr(u, "unit_type", "") == "worker"]
    warriors = [u for u in eunits if getattr(u, "unit_type", "") == "warrior"]
    ebuildings = [b for b in game.buildings if b.faction == "enemy"]
    return workers, warriors, ebuildings


def test_initialize_from_mission_config():
    game = _ghost(_want())
    ai = EnemyAI(game)
    ai.initialize_enemy_base()
    workers, warriors, ebuildings = _enemy_counts(game)

    assert len(workers) == 2
    assert len(warriors) == 5
    assert len(ebuildings) == 3  # town hall + 1 ferme + 1 tour (pas de caserne/cabane)
    assert game.enemy_economy.gold == 999
    assert game.enemy_economy.wood == 888
    assert game.enemy_economy.food == 777


def test_workers_ennemis_ont_reference_game():
    game = _ghost(_want())
    ai = EnemyAI(game)
    ai.initialize_enemy_base()
    eworkers = [u for u in game.units if u.faction == "enemy" and u.unit_type == "worker"]
    assert eworkers, "des workers ennemis doivent exister"
    assert all(w.game is game for w in eworkers), "workers ennemis -> .game = Game (récolte)"


def test_config_explicite_prioritaire_sur_mission():
    game = _ghost({})  # mission sans config utile
    ai = EnemyAI(game)
    ai.initialize_enemy_base({"town_hall": False, "barracks": False, "farms": 0,
                              "collection": False, "towers": 0, "workers": 0,
                              "warriors": 1, "gold": 5, "wood": 5, "food": 5})
    workers, warriors, ebuildings = _enemy_counts(game)
    assert len(warriors) == 1
    assert len(workers) == 0
    assert len(ebuildings) == 0
    assert game.enemy_economy.gold == 5


def test_default_sans_config():
    game = _ghost(None)
    ai = EnemyAI(game)
    ai.initialize_enemy_base()
    workers, warriors, ebuildings = _enemy_counts(game)
    assert len(workers) == DEFAULT_ENEMY_CONFIG["workers"]
    assert len(warriors) == DEFAULT_ENEMY_CONFIG["warriors"]
    # town hall + caserne + 3 fermes + cabane (collection True par défaut)
    assert len(ebuildings) >= 1
    assert any(b.building_type == "town_hall" for b in ebuildings)


def test_default_assigns_ressources():
    game = _ghost(None)
    ai = EnemyAI(game)
    ai.initialize_enemy_base()
    assert game.enemy_economy.gold == DEFAULT_ENEMY_CONFIG["gold"]


def test_difficulte_croissante_entre_missions():
    c = create_default_campaign()
    warriors = [m.enemy_config["warriors"] for m in c.missions]
    assert warriors == sorted(warriors) and len(set(warriors)) == len(warriors), \
        "le nombre de guerriers ennemis doit croître à chaque mission"
    # Mission 4 nettement plus forte que mission 1
    assert c.missions[3].enemy_config["warriors"] > c.missions[0].enemy_config["warriors"]
    assert c.missions[3].enemy_config["towers"] >= c.missions[0].enemy_config["towers"]


def test_enemy_config_est_serialisee():
    m = Mission("mi", "M", "D")
    m.add_objective(Objective("o", "Obj", "kill", 3))
    m.enemy_config = {"workers": 6, "warriors": 9, "farms": 4, "gold": 400}

    restored = Mission.from_dict(m.to_dict())
    assert restored.enemy_config == m.enemy_config


def test_mission_sans_enemy_config_se_serialise_sans_enemy_config():
    m = Mission("mi", "M", "D")
    d = m.to_dict()
    assert "enemy_config" in d and d["enemy_config"] == {}
    restored = Mission.from_dict(d)
    assert restored.enemy_config == {}