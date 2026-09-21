"""Tests du délai de mission (échec par temps).

Vérifie : mission avec time_limit -> défaites passés le délai (statut FAILED),
aucun échec avant le délai, mission sans time_limit (0) = illimité, et
sérialisation de time_limit.
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from systems.campaign import Mission, MissionStatus


def _game_with_mission(time_limit):
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    m = Mission("mt", "Mission temps", "D")
    m.time_limit = time_limit
    g.current_mission = m
    return g, m


def test_defaite_quand_le_delai_est_depasse():
    g, m = _game_with_mission(10)
    g.mission_timer = 12
    g._check_victory_defeat()
    assert g.state == "defeat"
    assert m.status == MissionStatus.FAILED


def test_pas_de_defaite_avant_le_delai():
    g, m = _game_with_mission(10)
    g.mission_timer = 9
    g._check_victory_defeat()
    assert g.state == "playing", "avant le délai, la partie continue"
    assert m.status == MissionStatus.PENDING


def test_time_limit_zero_est_illimite():
    g, m = _game_with_mission(0)
    g.mission_timer = 10_000
    g._check_victory_defeat()
    assert g.state == "playing", "time_limit=0 -> aucune échéance"
    assert m.status == MissionStatus.PENDING


def test_sans_mission_pas_d_echance():
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.current_mission = None  # pas de délai possible
    g.mission_timer = 99999
    g._check_victory_defeat()
    assert g.state == "playing"


def test_time_limit_serialise():
    m = Mission("mt", "M", "D")
    m.time_limit = 600
    restored = Mission.from_dict(m.to_dict())
    assert restored.time_limit == 600


def test_time_limit_defaut_zero_a_la_deserialisation():
    m = Mission("mt", "M", "D")  # time_limit par défaut 0
    d = m.to_dict()
    assert d["time_limit"] == 0
    restored = Mission.from_dict(d)
    assert restored.time_limit == 0