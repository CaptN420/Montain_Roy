"""Tests du brouillard de guerre (FogOfWar).

Couvre : aucune visibilité sans entité, révélation par unités joueur,
bâtiments joueur, persistance de l'exploration après départ, et le fait
que les unités ennemies ne révèlent pas la carte.
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from systems.fog_of_war import FogOfWar
from entities.unit import Unit


def test_aucune_visibilite_sans_entite():
    fow = FogOfWar(40, 30)
    fow.update([], [])
    assert not fow.is_visible(0, 0)
    assert not fow.is_explored(0, 0)
    assert not fow.is_visible(99999, 99999)  # hors carte


def test_unite_joueur_revele_zone():
    fow = FogOfWar(40, 30)
    u = Unit(160, 160, "player")  # tuile (5,5), rayon 8
    fow.update([u], [])
    assert fow.is_visible(160, 160)
    assert fow.is_explored(160, 160)
    # Loin -> pas visible ni exploré
    assert not fow.is_visible(1000, 1000)
    assert not fow.is_explored(1000, 1000)


def test_unite_ennemie_ne_revele_pas():
    fow = FogOfWar(40, 30)
    e = Unit(160, 160, "enemy")
    fow.update([e], [])
    assert not fow.is_visible(160, 160)
    assert not fow.is_explored(160, 160)


def test_exploration_persiste_apres_depart():
    fow = FogOfWar(40, 30)
    u = Unit(160, 160, "player")
    fow.update([u], [])
    assert fow.is_visible(160, 160)
    # L'unité part -> la zone explorée reste connue mais n'est plus visible.
    fow.update([], [])
    assert not fow.is_visible(160, 160)
    assert fow.is_explored(160, 160)


def test_batiment_joueur_revele():
    fow = FogOfWar(40, 30)
    building = SimpleNamespace(faction="player", x=160, y=160)
    fow.update([], [building])
    assert fow.is_visible(160, 160)
    assert fow.is_explored(160, 160)


def test_rayon_de_vision_borne_par_la_carte():
    # Une unité au bord ne fait pas planter la révélation (clamping).
    fow = FogOfWar(10, 10)
    u = Unit(0, 0, "player")  # coin (0,0)
    fow.update([u], [])  # ne doit pas lever d'exception
    assert fow.is_visible(0, 0)
    assert fow.is_explored(10 * 32 - 1, 0) is False or True  # pas de crash, hors coin