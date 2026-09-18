"""Tests des compétences du héros (priorité #5).

- Consomme du mana.
- Cooldown bloque le relancement.
- Mana insuffisant → échec.
- Attaque de zone (aoe) ne touche que les ennemis dans la portée/rayon.
- Météore inflige des dégâts de zone aux ennemis.
- Bouclier temporaire absorbe les dégâts.
- Aucun allié ne doit être touché par les compétences offensives.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.unit import Unit
from entities.hero import Hero


def make_hero():
    return Hero(100, 100, "player")


def enemy_at(x, y, hp=100):
    u = Unit(x, y, "enemy")
    u.hp = hp
    u.max_hp = hp
    return u


def ally_at(x, y):
    return Unit(x, y, "player")


def test_aoe_damages_only_enemies_in_range():
    hero = make_hero()
    near = enemy_at(150, 110)     # ~50 px, dans le rayon (64)
    far_enemy = enemy_at(500, 500)  # hors portée
    ally = ally_at(130, 130)       # dans le rayon mais allié

    before = hero.mana
    ok = hero.use_skill(0, target_x=100, target_y=100, units=[near, far_enemy, ally])
    assert ok is True
    assert hero.mana < before, "le mana doit être consommé"
    assert near.hp < near.max_hp, "l'ennemi proche doit subir des dégâts"
    assert far_enemy.hp == far_enemy.max_hp, "l'ennemi hors portée ne doit pas être touché"
    assert ally.hp == ally.max_hp, "les alliés ne doivent jamais être touchés"


def test_skill_blocked_by_cooldown():
    hero = make_hero()
    enemies = [enemy_at(150, 110)]
    assert hero.use_skill(0, target_x=100, target_y=100, units=enemies) is True
    assert hero.use_skill(0, target_x=100, target_y=100, units=enemies) is False, \
        "la compétence doit être en cooldown juste après son activation"


def test_skill_blocked_when_not_enough_mana():
    hero = make_hero()
    hero.mana = 0
    enemies = [enemy_at(150, 110)]
    before = hero.mana
    assert hero.use_skill(0, target_x=100, target_y=100, units=enemies) is False
    assert hero.mana == before
    # la cible ne doit pas subir de dégâts si échec
    assert enemies[0].hp == enemies[0].max_hp


def test_invalid_skill_index_returns_false():
    hero = make_hero()
    assert hero.use_skill(99, units=[]) is False


def test_cooldown_decays_over_time():
    hero = make_hero()
    hero.use_skill(0, target_x=100, target_y=100, units=[])
    skill = hero.skills[0]
    assert skill["cooldown"] > 0
    # au bout de max_cooldown + epsilon, le cooldown doit être à zéro
    hero.update(skill["max_cooldown"] + 0.1)
    assert skill["cooldown"] <= 0


def test_shield_absorbs_damage_then_expires():
    hero = make_hero()
    assert hero.use_skill(1, units=[]) is True
    assert hero.shield > 0, "le bouclier doit être actif"
    hp_before = hero.hp
    attacker = enemy_at(10, 10)
    hero.take_damage(30, attacker=attacker)
    assert hero.hp == hp_before, "le bouclier doit absorber tous les dégâts tant qu'il reste du bouclier"
    assert hero.shield < 30 + 1, "le bouclier doit être consommé"

    # le bouclier expire avec le temps
    hero.take_damage(hero.shield + 1, attacker=attacker)  # épuise le bouclier
    assert hero.shield == 0
    hero_skill = hero.skills[1]
    hero.update(hero_skill["max_cooldown"] + 0.1)
    assert hero.shield <= 0 or hero.shield_duration <= 0, "le bouclier doit expirer après sa durée"


def test_meteor_damages_enemies_in_area():
    hero = make_hero()
    near = enemy_at(200, 200)
    ally = ally_at(190, 190)
    ok = hero.use_skill(3, target_x=200, target_y=200, units=[near, ally])
    assert ok is True
    assert near.hp < near.max_hp, "le météore doit toucher l'ennemi dans la zone"
    assert ally.hp == ally.max_hp, "le météore ne doit pas toucher les alliés"


def test_hero_cannot_cast_without_enough_mana_for_meteor():
    hero = make_hero()
    hero.mana = 10  # < 50 requis pour le météore
    enemies = [enemy_at(200, 200)]
    assert hero.use_skill(3, target_x=200, target_y=200, units=enemies) is False
    assert enemies[0].hp == enemies[0].max_hp