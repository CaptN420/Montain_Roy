"""Tests du refacteur unit/économie commité (7afc3eb).

Couvre les 4 surfaces ajoutées/déplacées :
1. Synergie Archer   (range_mult +20% derrière mur/tour alliée)
2. Synergie Chevalier (damage_mult +15% avec 2+ chevaliers alliés proches)
3. Application des synergies dans le combat (Unit.update)
4. Validation de la population avant production/spawn
5. Rendu HUD des compétences héros ([Esp]/[Q]/[E]/[R] + mana)
6. Placement IA via validate_build_position
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest

from entities.unit import Unit
from entities.unit_types import Archer, Knight, Warrior, create_unit
from entities.hero import Hero
from entities.building import Barracks
from systems.ai import EnemyAI
from ui.hud import HUD


# ---------------------------------------------------------------- Synergies
def _game(buildings=(), units=()):
    return SimpleNamespace(buildings=list(buildings), units=list(units))


def _wall(x, y, faction="player", building_type="wall"):
    return SimpleNamespace(x=x, y=y, faction=faction, building_type=building_type)


# ---------- Archer
def test_archer_gagne_portee_derriere_mur_allie():
    archer = Archer(0, 0, "player")
    wall = _wall(50, 0)  # distance 50 < 128
    bonus = archer.get_synergy_bonus(_game(buildings=[wall], units=[]))
    assert bonus["range_mult"] == pytest.approx(1.2)
    assert bonus["damage_mult"] == pytest.approx(1.0)


def test_archer_sans_mur_pas_de_bonus():
    archer = Archer(0, 0, "player")
    bonus = archer.get_synergy_bonus(_game(units=[]))
    assert bonus["range_mult"] == pytest.approx(1.0)


def test_archer_mur_trop_loin_pas_de_bonus():
    archer = Archer(0, 0, "player")
    far_wall = _wall(300, 0)  # > 128
    bonus = archer.get_synergy_bonus(_game(buildings=[far_wall], units=[]))
    assert bonus["range_mult"] == pytest.approx(1.0)


def test_archer_mur_ennemi_pas_de_bonus():
    archer = Archer(0, 0, "player")
    enemy_wall = _wall(50, 0, faction="enemy")
    bonus = archer.get_synergy_bonus(_game(buildings=[enemy_wall], units=[]))
    assert bonus["range_mult"] == pytest.approx(1.0)


def test_archer_tower_allie_compte_comme_mur():
    archer = Archer(0, 0, "player")
    tower = _wall(30, 0, building_type="tower")
    bonus = archer.get_synergy_bonus(_game(buildings=[tower], units=[]))
    assert bonus["range_mult"] == pytest.approx(1.2)


# ---------- Chevalier
def test_knight_gagne_degats_avec_deux_chevaliers_proches():
    knight = Knight(0, 0, "player")
    k2 = Knight(10, 0, "player")
    k3 = Knight(0, 10, "player")  # tous à < 64
    bonus = knight.get_synergy_bonus(_game(units=[k2, k3]))
    assert bonus["damage_mult"] == pytest.approx(1.15)
    assert bonus["range_mult"] == pytest.approx(1.0)


def test_knight_un_seul_chevalier_pas_de_bonus():
    knight = Knight(0, 0, "player")
    k2 = Knight(10, 0, "player")
    bonus = knight.get_synergy_bonus(_game(units=[k2]))
    assert bonus["damage_mult"] == pytest.approx(1.0)


def test_knight_chevaliers_ennemis_ne_comptent_pas():
    knight = Knight(0, 0, "player")
    e2 = Knight(10, 0, "enemy")
    e3 = Knight(0, 10, "enemy")
    bonus = knight.get_synergy_bonus(_game(units=[e2, e3]))
    assert bonus["damage_mult"] == pytest.approx(1.0)


def test_knight_chevaliers_loin_ne_comptent_pas():
    knight = Knight(0, 0, "player")
    far = Knight(200, 0, "player")  # > 64
    bonus = knight.get_synergy_bonus(_game(units=[far]))
    assert bonus["damage_mult"] == pytest.approx(1.0)


# ---------- Application en combat (Unit.update)
def _target_at(x, y):
    t = Unit(x, y, "enemy")
    t.hp = 100
    t.max_hp = 100
    return t


def test_synergie_archer_etend_portee_effective_en_combat():
    # Archer portée de base 128 ; portée boostée 153.6 (avec mur allié < 128)
    archer = Archer(0, 0, "player")
    wall = _wall(50, 0)
    archer.game = _game(buildings=[wall], units=[])
    archer.attack_timer = archer.attack_speed  # attaque immédiatement

    target = _target_at(140, 0)  # >128 mais <=153.6 : hors portée de base
    archer.target = target
    before = target.hp
    archer.update(0.016)
    assert target.hp < before, "l'archer doit frapper dans la portée boostée"


def test_archer_sans_synergie_ne_touche_pas_a_portee_boostee():
    archer = Archer(0, 0, "player")
    archer.game = None  # pas de synergie
    archer.attack_timer = archer.attack_speed

    target = _target_at(140, 0)
    archer.target = target
    before = target.hp
    archer.update(0.016)
    assert target.hp == before, "sans synergie, la portée reste 128 -> hors de portée"


def test_synergie_chevalier_augmente_degats_en_combat():
    knight = Knight(0, 0, "player")
    k2 = Knight(10, 0, "player")
    k3 = Knight(0, 10, "player")
    knight.game = _game(units=[k2, k3])
    knight.attack_timer = knight.attack_speed

    target = _target_at(30, 0)
    knight.target = target
    before = target.hp
    knight.update(0.016)
    dealt = before - target.hp
    # 25 * 1.15 - 0 = 28.75
    assert dealt == pytest.approx(28.75, abs=0.01)


def test_chevalier_sans_synergie_degats_normaux():
    knight = Knight(0, 0, "player")
    knight.game = None
    knight.attack_timer = knight.attack_speed

    target = _target_at(30, 0)
    target.hp = 200
    knight.target = target
    before = target.hp
    knight.update(0.016)
    dealt = before - target.hp
    assert dealt == pytest.approx(25.0, abs=0.01)


# ---------------------------------------------------------------- Population
def test_max_population_croit_avec_les_fermes():
    from entities.building import Farm
    from systems.economy import EconomySystem
    ec = EconomySystem()
    assert ec.get_max_population([]) == 10
    assert ec.get_max_population([Farm(0, 0, "player")]) == 15
    assert ec.get_max_population([Farm(0, 0, "player"), Farm(60, 0, "player")]) == 20


def test_production_refusee_population_max():
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"

    # Garantir que le gate de faction passe (caserne + warrior dans le roster)
    g.buildings.append(Barracks(0, 0, "player"))
    ok, reason = g.faction.can_produce("warrior", g.buildings, g.tech_tree.unlocked_techs)
    assert ok, f"le gate faction doit passer pour tester le gate population : {reason}"

    # Remplir la population jusqu'au cap
    max_pop = g.economy.get_max_population(g.buildings or [])
    player_count = len([u for u in g.units if getattr(u, "faction", "player") == "player"])
    for i in range(max_pop - player_count + 1):
        u = Unit(100 + i, 100, "player")
        g.units.append(u)

    ok, reason = g._can_produce_unit("warrior")
    assert not ok
    assert "population" in reason.lower()


def test_spawn_bloque_a_population_max_sans_spawner():
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.buildings.append(Barracks(0, 0, "player"))

    max_pop = g.economy.get_max_population(g.buildings or [])
    player_count = len([u for u in g.units if getattr(u, "faction", "player") == "player"])
    for i in range(max_pop - player_count + 1):
        g.units.append(Unit(100 + i, 100, "player"))
    before = len(g.units)
    g._spawn_unit("warrior")
    assert len(g.units) == before, "_spawn_unit ne doit rien spawner au-delà du cap"


# ---------------------------------------------------------------- HUD
def test_hud_dessine_competences_du_heros_sans_crash():
    hud = HUD(200, 200)
    hero = Hero(100, 100, "player")
    hud.draw_skill_buttons(hero)  # ne doit pas lever d'exception


def test_hud_none_et_heros_sans_skills_court_circuit():
    hud = HUD(200, 200)
    hud.draw_skill_buttons(None)          # héros absent
    hud.draw_skill_buttons(Warrior(0, 0))  # pas d'attribut .skills


# ---------------------------------------------------------------- IA placement
def _ghost_game(cs):
    ec = SimpleNamespace(gold=1000, wood=1000, food=1000)
    return SimpleNamespace(
        enemy_economy=ec,
        units=[SimpleNamespace(faction="enemy", x=0, y=0)],
        buildings=[],
        construction_system=cs,
    )


def test_ai_refuse_placement_invalide_sans_depenser():
    # validate_build_position retourne toujours False -> l'IA ne doit rien construire
    cs = SimpleNamespace(validate_build_position=lambda *a, **k: (False, "Une unité est déjà là"))
    game = _ghost_game(cs)
    ai = EnemyAI(game)
    ai._build_structures()
    assert len(game.buildings) == 0, "aucun bâtiment ne doit être placé sur position invalide"
    assert game.enemy_economy.gold == 1000, "ressources IA intactes quand le placement échoue"


def test_ai_construit_sur_position_valide_et_paye():
    cs = SimpleNamespace(validate_build_position=lambda *a, **k: (True, ""))
    game = _ghost_game(cs)
    ai = EnemyAI(game)
    ai._build_structures()
    assert len(game.buildings) == 1, "un bâtiment doit être placé sur position valide"
    # Barracks : 150 or, 100 bois, 20 nourriture
    assert game.enemy_economy.gold == 850
    assert game.enemy_economy.wood == 900
    assert game.enemy_economy.food == 980


# ---------------------------------------------------------------- create_unit
def test_create_unit_assigne_game_apres_construction():
    game = _game()
    unit = create_unit("warrior", 10, 10, "player", game=game)
    assert unit.game is game


def test_create_unit_sans_game_laisse_game_a_None():
    unit = create_unit("archer", 10, 10, "player")
    assert getattr(unit, "game", None) is None


def test_armure_appliquee_une_seule_fois_en_combat():
    """Régression : take_damage applique déjà l'armure, les appelants ne doivent PAS
    la retrancher aussi (double application faisait 15 vs armure 8 -> 1 dégât)."""
    from entities.unit_types import Warrior, Knight
    attacker = Warrior(0, 0, "player")
    attacker.attack_timer = attacker.attack_speed
    target = Knight(50, 0, "enemy")  # armure 8, hp 200
    attacker.target = target
    before = target.hp
    attacker.update(0.016)
    dealt = before - target.hp
    assert dealt == 15 - 8, f"armure appliquée une fois : {dealt} != 7"