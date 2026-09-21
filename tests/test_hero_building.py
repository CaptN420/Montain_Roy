"""Tests du bâtiment à héros (HeroHall) et du recrutement.

Valide : héros plus gratuit au départ, hero_hall constructible par toutes les
factions, et la logique de recrutement (sans bâtiment, création + coût, refus
si héros vivant, refus sans ressources, résurrection après mort).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from entities.building import HeroHall
from entities.hero import Hero


def _game(faction="human"):
    from core.game import Game
    g = Game()
    g._apply_faction(faction)
    g.state = "playing"
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    return g


def _select_hall(g, x=100, y=100):
    hall = HeroHall(x, y, "player")
    g._selected_building = hall
    return hall


# ---------------------------------------------------------------- héros gratuit
def test_heros_gratuit_supprime():
    g = _game()
    assert g.hero is None, "plus de héros gratuit au départ"
    assert not any(getattr(u, "unit_type", "") == "hero" for u in g.units)


# ---------------------------------------------------------------- constructible
def test_herohall_constructible_par_toutes_factions():
    from systems.factions import get_factions
    for fid in get_factions():
        g = _game(fid)
        avail = g.construction_system.get_available_buildings()
        assert "hero_hall" in avail, f"hero_hall doit être constructible pour {fid}"


def test_create_herohall_retourne_le_bon_type():
    g = _game()
    b = g.construction_system._create_building("hero_hall", 500, 500, "player")
    assert b is not None and b.building_type == "hero_hall"
    assert isinstance(b, HeroHall)


# ---------------------------------------------------------------- recrutement
def test_recrutement_sans_batiment_ne_fait_rien():
    g = _game()
    gold_before = g.economy.gold
    g._recruit_hero()
    assert g.hero is None
    assert g.economy.gold == gold_before, "aucun débit sans bâtiment à héros"


def test_recrutement_cree_le_heros_et_debite():
    g = _game()
    _select_hall(g)
    gold_before = g.economy.gold
    g._recruit_hero()

    assert g.hero is not None
    assert g.hero in g.units, "le héros doit apparaître parmi les unités"
    assert g.economy.gold == gold_before - g.HERO_RECRUIT_COST["gold"]


def test_recrutement_ignore_heros_deja_vivant():
    g = _game()
    _select_hall(g)
    g._recruit_hero()
    count_after_first = len(g.units)
    gold_after_first = g.economy.gold

    g._recruit_hero()  # héros toujours vivant -> refus
    assert len(g.units) == count_after_first, "pas de second héros"
    assert g.economy.gold == gold_after_first, "pas de second débit"


def test_recrutement_refuse_sans_ressources():
    g = _game()
    _select_hall(g)
    g.economy.gold = 10  # < 250, bois/nourriture OK
    g._recruit_hero()
    assert g.hero is None, "pas de héros sans ressources"
    assert g.economy.gold == 10, "ressources intactes quand le recrutement échoue"


def test_recrutement_ressuscite_le_heros_mort():
    g = _game()
    _select_hall(g)
    g._recruit_hero()
    hero = g.hero

    # Simuler la mort : le héros est retiré de units et hp à 0.
    g.units.remove(hero)
    hero.hp = 0
    count_before_revive = len(g.units)

    g._recruit_hero()
    assert g.hero is hero, "on ressuscite le même héros (niveau/XP conservés)"
    assert hero in g.units
    assert hero.hp == hero.max_hp
    assert len(g.units) == count_before_revive + 1, "réajout une seule fois"