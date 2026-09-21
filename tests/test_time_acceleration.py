"""Tests de l'accélération du temps (fast-forward).

Vérifie : valeur par défaut 1, cycler 1->2->4->8->16->1 (boucle), set_time_scale
n'accepte que les valeurs valides, et effective_dt multiplie bien le dt.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from core.game import Game


@pytest.fixture()
def g():
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    return g


def test_vitesse_defaut_est_1(g):
    assert g.time_scale == 1


def test_cycle_parcourt_les_echelles_puis_revient(g):
    expected = [2, 4, 8, 16, 1, 2, 4]
    for want in expected:
        g._cycle_time_scale()
        assert g.time_scale == want


def test_set_time_scale_valide(g):
    g.set_time_scale(8)
    assert g.time_scale == 8
    g.set_time_scale(1)
    assert g.time_scale == 1


def test_set_time_scale_ignore_valeur_invalide(g):
    g.time_scale = 4
    g.set_time_scale(3)   # pas dans (1,2,4,8,16)
    assert g.time_scale == 4
    g.set_time_scale(-2)
    assert g.time_scale == 4


def test_effective_dt_multiplie(g):
    g.time_scale = 4
    assert g.effective_dt(0.016) == pytest.approx(0.064)
    g.time_scale = 1
    assert g.effective_dt(0.016) == pytest.approx(0.016)


def test_echelles_max_16(g):
    assert g.TIME_SCALES[-1] == 16
    g.time_scale = 16
    g._cycle_time_scale()   # 16 -> 1
    assert g.time_scale == 1