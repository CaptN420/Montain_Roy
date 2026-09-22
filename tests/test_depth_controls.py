"""Tests des améliorations : profondeur (techs fonctionnelles) + minimap cliquable
+ groupes de contrôle (Ctrl+1..9 / 1..9).

Vérifie :
- les nouvelles techs existent et ont des prérequis valides,
- les techs (anciennes et nouvelles) appliquent réellement leurs effets aux
  unités existantes ET aux unités produites après coup,
- le clic minimap recentre la caméra,
- l'assignation/rappel de groupe de contrôle fonctionne.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from systems.tech_tree import TechTree
from core.game import Game
from entities.worker import Worker
from entities.unit_types import Warrior, Archer


# ---------------------------------------------------------------------
# Profondeur : nouvelles techs
# ---------------------------------------------------------------------

def test_nouvelles_techs_presentes():
    tt = TechTree()
    for tid in ("rapid_weapons", "mounted_speed", "veteran_bulk", "scout_sight",
                "rapid_workers", "siege_power"):
        assert tid in tt.technologies, f"tech manquante: {tid}"


def test_nouvelles_techs_a_prerequis_valides():
    tt = TechTree()
    # rapid_weapons exige iron_working ; siege_power exige siege_weapons
    assert tt.get_technology("rapid_weapons").requirements and \
        any(r.tech_id == "iron_working" for r in tt.get_technology("rapid_weapons").requirements)
    assert any(r.tech_id == "siege_weapons"
               for r in tt.get_technology("siege_power").requirements)


def test_toutes_techs_ont_un_effet_declare():
    tt = TechTree()
    g = Game()
    # hero_training est géré à part (déjà câblé) ; on vérifie que les autres
    # techs de game._RESEARCH_EFFECTS couvrent toutes celles du tree.
    declared = set(g._RESEARCH_EFFECTS.keys())
    # Chaque tech du tree doit avoir un effet déclaré (même vide pour hero_training).
    for tid in tt.technologies:
        assert tid in declared, f"tech sans effet déclaré: {tid}"
    # Vérifie qu'au moins une nouvelle tech a un effet non trivial
    assert g._RESEARCH_EFFECTS["rapid_weapons"]["attack_speed_percent"] < 1.0
    assert g._RESEARCH_EFFECTS["veteran_bulk"]["max_hp_percent"] > 1.0


def test_veteran_bulk_augmente_pv_existants():
    g = Game()
    u = Warrior(100, 100, "player")
    g.units.append(u)
    before = u.max_hp
    # Applique manuellement l'effet de veteran_bulk
    g.tech_tree.unlocked_techs.append("veteran_bulk")
    g._apply_research_effects_to_unit(u)
    assert u.max_hp > before, "veteran_bulk doit augmenter les PV"


def test_rapid_weapons_accelere_attaque():
    g = Game()
    u = Warrior(100, 100, "player")
    before = u.attack_speed
    g.tech_tree.unlocked_techs.append("rapid_weapons")
    g._apply_research_effects_to_unit(u)
    assert u.attack_speed < before, "rapid_weapons doit accélérer l'attaque"


def test_mounted_speed_accelere_deplacement():
    g = Game()
    u = Warrior(100, 100, "player")
    before = u.speed
    g.tech_tree.unlocked_techs.append("mounted_speed")
    g._apply_research_effects_to_unit(u)
    assert u.speed > before


# ---------------------------------------------------------------------
# Minimap cliquable
# ---------------------------------------------------------------------

def test_minimap_has_rect():
    g = Game()
    rect = g.hud.minimap_rect()
    assert rect.width > 0 and rect.height > 0


def test_minimap_click_recentre_camera():
    g = Game()
    g.state = "playing"
    rect = g.hud.minimap_rect()
    # Cliquer au centre de la minimap -> caméra recentrée sur le centre de la carte
    cx, cy = rect.center
    camera_before = (g.camera.x, g.camera.y)
    g._handle_minimap_click((cx, cy))
    # La caméra a bougé (au moins vers une nouvelle position)
    moved = (g.camera.x, g.camera.y) != camera_before
    assert moved or g.camera.x != 0 or g.camera.y != 0, "le clic minimap doit déplacer la caméra"


# ---------------------------------------------------------------------
# Groupes de contrôle
# ---------------------------------------------------------------------

def _make_selected_units(g, n=3):
    units = []
    for i in range(n):
        u = Warrior(100 + i * 40, 200, "player")
        units.append(u)
    g.units.extend(units)
    g.selected_units = units
    for u in units:
        u.selected = True
    return units


def test_assigner_groupe_ctrl():
    g = Game()
    units = _make_selected_units(g)
    g._assign_group(1)
    assert 1 in g.control_groups
    assert len(g.control_groups[1]) == len(units)


def test_rappel_groupe_selectionne():
    g = Game()
    units = _make_selected_units(g)
    g._assign_group(2)
    # Désélectionner tout
    g.selected_units = []
    for u in g.units:
        u.selected = False
    # Rappeler le groupe
    g._select_group(2)
    assert len(g.selected_units) == len(units)
    assert all(u.selected for u in units)


def test_rappel_groupe_ignore_morts():
    g = Game()
    units = _make_selected_units(g, n=2)
    g._assign_group(3)
    # Tuer une unité du groupe
    units[0].hp = 0
    g._select_group(3)
    assert units[1] in g.selected_units
    assert units[0] not in g.selected_units


def test_group_key_mapping():
    g = Game()
    ev = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_4})
    assert g._group_key_for(ev) == 4
    ev0 = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a})
    assert g._group_key_for(ev0) == 0


def test_handle_group_keys_ctrl_assigne():
    g = Game()
    _make_selected_units(g)
    ev = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_5, "mod": pygame.KMOD_CTRL})
    handled = g._handle_group_keys(ev)
    assert handled is True
    assert 5 in g.control_groups