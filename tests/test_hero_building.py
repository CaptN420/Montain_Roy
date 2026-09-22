"""Tests du bâtiment à héros (HeroHall) et de l'invocation des 3 héros/faction.

Valide : plus de héros gratuit, hero_hall constructible par toutes les factions,
les 3 héros coexistent (invoqués, coût chacun), pas de doublon d'un héros vivant,
refus sans ressources, identité des héros (unit_type/nom/stats), et round-trip
via create_unit (pour la sauvegarde).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

from entities.building import HeroHall


def _game(faction="human"):
    from core.game import Game
    g = Game()
    g._apply_faction(faction)
    g.state = "playing"
    g.economy.gold = 5000
    g.economy.wood = 5000
    g.economy.food = 5000
    return g


def _select_hall(g, x=100, y=100):
    hall = HeroHall(x, y, "player")
    g._selected_building = hall
    return hall


# ---------------------------------------------------------------- héros gratuit
def test_heros_gratuit_supprime():
    g = _game()
    assert g.hero is None, "plus de héros gratuit au départ"
    assert not any(getattr(u, "unit_type", "") in ("hero",) for u in g.units)


# ---------------------------------------------------------------- constructible
def test_herohall_constructible_par_toutes_factions():
    from systems.factions import get_factions
    for fid in get_factions():
        g = _game(fid)
        assert "hero_hall" in g.construction_system.get_available_buildings()


def test_create_herohall_retourne_le_bon_type():
    g = _game()
    b = g.construction_system._create_building("hero_hall", 500, 500, "player")
    assert b is not None and b.building_type == "hero_hall"
    assert isinstance(b, HeroHall)


# ---------------------------------------------------------------- identité
def test_chaque_faction_a_3_heros_uniques():
    from entities.hero_types import faction_hero_types, HERO_IDENTITY
    for fid, roles in HERO_IDENTITY.items():
        types = faction_hero_types(fid)
        assert len(types) == 3
        assert len(set(types)) == 3, "unit_type distincts par faction"
        names = [info[1] for info in roles.values()]
        assert len(set(names)) == 3


def test_hero_injecte_stats_de_faction():
    from entities.hero_types import create_faction_hero
    # Le nain augmente l'armure ; l'orc les dégâts.
    dwarf = create_faction_hero("dwarf", "warrior", 0, 0)
    orc = create_faction_hero("orc", "warrior", 0, 0)
    assert dwarf.armor > orc.armor
    assert orc.damage > dwarf.damage
    assert dwarf.unit_type.startswith("hero_")


def test_create_unit_reconstruit_le_heros():
    from entities.unit_types import create_unit
    from entities.hero import Hero
    h = create_unit("hero_swordmaster", 10, 10, "player")
    assert isinstance(h, Hero)
    assert h.unit_type == "hero_swordmaster"
    assert h.faction_id == "human"
    assert h.name == "Lionel"


# ---------------------------------------------------------------- invocation
def test_invocation_sans_batiment_ne_fait_rien():
    g = _game()
    gold_before = g.economy.gold
    n_units = len(g.units)
    g._summon_hero(0)
    assert len(g.units) == n_units, "aucune unité sans bâtiment à héros"
    assert g.economy.gold == gold_before


def test_invoque_3_heros_coexistants():
    g = _game()
    _select_hall(g)
    n_units = len(g.units)
    for i in range(3):
        g._summon_hero(i)
    heroes = [u for u in g.units if u.unit_type.startswith("hero_")]
    assert len(heroes) == 3, "les 3 héros coexistent"
    assert len({h.unit_type for h in heroes}) == 3
    assert len(g.units) == n_units + 3


def test_invocation_debite_le_cout():
    from entities.hero_types import HERO_SUMMON_COSTS
    g = _game()
    _select_hall(g)
    before = g.economy.gold
    g._summon_hero(0)  # warrior
    assert g.economy.gold == before - HERO_SUMMON_COSTS["warrior"]["gold"]


def test_invocation_refuse_le_doublon_vivant():
    g = _game()
    _select_hall(g)
    g._summon_hero(0)
    count = len(g.units)
    gold_after_first = g.economy.gold
    g._summon_hero(0)  # même héros déjà vivant
    assert len(g.units) == count, "pas de doublon"
    assert g.economy.gold == gold_after_first


def test_invocation_refuse_sans_ressources():
    g = _game()
    _select_hall(g)
    g.economy.gold = 10
    g._summon_hero(0)
    assert not any(u.unit_type.startswith("hero_") for u in g.units)
    assert g.economy.gold == 10


# ---------------------------------------------------------------- round-trip
def test_heros_roundtrip_to_dict_create_unit():
    from entities.hero_types import create_faction_hero
    from entities.unit_types import create_unit
    h = create_faction_hero("elf", "archer", 30, 40)
    d = h.to_dict()

    restored = create_unit(d["unit_type"], d["x"], d["y"], d["faction"])
    assert restored.unit_type == h.unit_type
    assert restored.faction_id == "elf"
    assert len(restored.skills) == len(h.skills) == 4


# ---------------------------------------------------------------- HUD
def test_hud_affiche_panneau_invocation_heros_sans_crash():
    g = _game()
    hall = _select_hall(g)
    # Panneau initial (aucun héros)
    g.hud.draw_production_buttons(g.economy, g.selected_units, hall,
                                  g.production_system, g.faction, g)
    # Après avoir invoqué un héros (état "Présent")
    g._summon_hero(0)
    g.hud.draw_production_buttons(g.economy, g.selected_units, hall,
                                  g.production_system, g.faction, g)


def test_selected_hero_parmi_plusieurs():
    g = _game()
    _select_hall(g)
    for i in range(3):
        g._summon_hero(i)
    heroes = [u for u in g.units if u.unit_type.startswith("hero_")]
    # Sélectionner uniquement le 3e héros
    g.selected_units = [heroes[2]]
    assert g._selected_hero() is heroes[2]
    assert len(g._player_heroes()) == 3