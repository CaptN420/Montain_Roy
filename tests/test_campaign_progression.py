"""Tests victoire/défaite, progression de campagne et objectif 'survive'.

Corrige/couvre :
- Défaite quand le joueur n'a plus de bâtiment.
- Victoire quand tous les ennemis (unités + bâtiments) sont détruits + récompenses.
- Anti-cascade : recréer un camp ennemi pour la mission suivante (sinon victoire en chaîne).
- Traversée complète des 4 missions de la campagne par défaut.
- Objectif 'survive' : rempli uniquement à la durée cible (ancien code additionnait
  le timer à chaque frame et complétait l'objectif en quelques secondes).
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((200, 200))

import pytest


def _make_game():
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    return g


def _kill_enemies(g):
    g.units = [u for u in g.units if u.faction != "enemy"]
    g.buildings = [b for b in g.buildings if b.faction != "enemy"]


def test_defeat_quand_plus_de_batiment_joueur():
    g = _make_game()
    g.buildings = [b for b in g.buildings if b.faction != "player"]
    g._check_victory_defeat()
    assert g.state == "defeat"


def test_victoire_sur_derniere_mission_donne_recompenses():
    from systems.campaign import create_default_campaign
    g = _make_game()
    g.campaign = create_default_campaign()
    g.campaign.current_mission_index = 3  # mission_4 = dernière
    g.current_mission = g.campaign.start_next_mission()

    _kill_enemies(g)
    gold_before = g.economy.gold
    g._check_victory_defeat()

    assert g.state == "victory", "dernière mission rendue -> victoire"
    assert g.campaign.is_campaign_complete()
    # mission_4 : 500 or, 300 bois, 200 nourriture
    assert g.economy.gold == gold_before + 500


def test_victoire_avance_a_la_mission_suivante_et_recree_lenemi():
    """Anti-cascade : la mission 2 a de nouveau un camp ennemi à affronter."""
    from systems.campaign import create_default_campaign
    g = _make_game()
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.start_next_mission()
    assert g.current_mission.mission_id == "mission_1"

    _kill_enemies(g)
    g._check_victory_defeat()

    assert g.state == "mission_screen", "pas encore la dernière mission -> écran mission"
    assert g.current_mission.mission_id == "mission_2"
    assert g.campaign.completed_missions == [0]
    # Le camp ennemi a été recréé : la mission 2 ne démarre pas sur une victoire instantanée.
    enemy_units = [u for u in g.units if u.faction == "enemy"]
    enemy_buildings = [b for b in g.buildings if b.faction == "enemy"]
    assert enemy_units or enemy_buildings, "le camp ennemi doit être recréé pour la mission suivante"


def test_pas_de_cascade_apres_deux_victoires():
    """Deux missions consécutives gagnées : la 3e a encore un ennemi (pas de victoire directe)."""
    from systems.campaign import create_default_campaign
    g = _make_game()
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.start_next_mission()

    # Gagner mission_1
    _kill_enemies(g)
    g._check_victory_defeat()
    assert g.current_mission.mission_id == "mission_2"
    # Gagner mission_2 : détruire le camp recréé
    _kill_enemies(g)
    g._check_victory_defeat()
    assert g.current_mission.mission_id == "mission_3"
    assert [u for u in g.units if u.faction == "enemy"] or \
           [b for b in g.buildings if b.faction == "enemy"]


def test_campagne_parcourt_toutes_les_missions():
    from systems.campaign import create_default_campaign
    c = create_default_campaign()
    assert len(c.missions) == 4

    expected = ["mission_1", "mission_2", "mission_3", "mission_4"]
    for i, mid in enumerate(expected):
        m = c.start_next_mission()
        assert m.mission_id == mid
        c.complete_current_mission()
        assert c.current_mission_index == i + 1

    assert c.is_campaign_complete()


def test_victoire_atteignable_en_detruisant_la_base_ennemie():
    """Régression 'game unwinnable' : l'IA re-produit/re-construit à l'infini, donc
    exiger 0 unité ET 0 bâtiment ennemis restait inatteignable. Victoire = base
    (town_hall) ennemie détruite, même si des unités ennemies survivent."""
    from core.game import Game
    from systems.campaign import create_default_campaign
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.start_next_mission()

    # On garde des unités et bâtiments ennemis, mais on détruit le town_hall.
    enemy_units_before = [u for u in g.units if u.faction == "enemy"]
    assert enemy_units_before, "des unités ennemies doivent exister (bloquait l'ancienne victoire)"
    g.buildings[:] = [b for b in g.buildings
                      if not (b.faction == "enemy" and b.building_type == "town_hall")]

    g._check_victory_defeat()
    # Victoire -> avance à la mission 2 (même s'il restait des unités ennemies).
    assert g.current_mission.mission_id == "mission_2"
    assert g.state == "mission_screen"


def test_avance_de_mission_purge_les_ennemis_survivants():
    """Après victoire (base détruite), on ne doit pas cumuler les ennemis survivants
    de l'ancienne mission avec la nouvelle base."""
    from core.game import Game
    from systems.campaign import create_default_campaign
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.start_next_mission()

    # Conserver des unités ennemies + détruire la base
    surviving = [u for u in g.units if u.faction == "enemy"]
    assert len(surviving) > 0
    g.buildings[:] = [b for b in g.buildings
                      if not (b.faction == "enemy" and b.building_type == "town_hall")]
    g._check_victory_defeat()

    # La nouvelle base ennemie est recréée et propre : pas d'accumulation.
    new_enemy = [u for u in g.units if u.faction == "enemy"]
    for old in surviving:
        assert old not in new_enemy, "les survivants de la mission précédente ne doivent plus être en jeu"


def test_mission1_camp_ennemi_vient_de_la_config():
    """Nouvelle partie : le camp ennemi de mission 1 vient de enemy_config (3 guerriers)."""
    from core.game import Game
    g = Game()
    g.faction_id = "human"
    g._start_campaign()
    assert g.current_mission.mission_id == "mission_1"

    ewarriors = [u for u in g.units if u.faction == "enemy" and u.unit_type == "warrior"]
    eworkers = [u for u in g.units if u.faction == "enemy" and u.unit_type == "worker"]
    cfg = g.current_mission.enemy_config
    assert len(ewarriors) == cfg["warriors"]
    assert len(eworkers) == cfg["workers"]
    # Coût : la config fait foi (avant : le setup inline de __init__ créait 0 guerrier).
    assert len(ewarriors) >= 1


def test_objectif_survive_rempli_a_la_duree_cible():
    from systems.campaign import Mission, Objective
    from core.game import Game
    g = Game()
    g.state = "playing"

    m = Mission("m_survive", "S", "D")
    m.add_objective(Objective("surv", "Survivre", "survive", 120))
    g.current_mission = m

    # Avant la durée cible, l'objectif n'est PAS complété (ancien code le complétait vite).
    g.mission_timer = 30
    g._check_mission_objectives()
    assert not m.objectives[0].completed

    # À la durée (ou au-delà), l'objectif est rempli, sans attendre l'accumulation.
    g.mission_timer = 121
    g._check_mission_objectives()
    assert m.objectives[0].completed


def test_objectif_survive_ignore_les_fractions():
    from systems.campaign import Mission, Objective
    from core.game import Game
    g = Game()
    g.state = "playing"
    m = Mission("ms", "S", "D")
    m.add_objective(Objective("s", "Survivre", "survive", 10))
    g.current_mission = m
    g.mission_timer = 9.7
    g._check_mission_objectives()
    assert not m.objectives[0].completed
    g.mission_timer = 10.0
    g._check_mission_objectives()
    assert m.objectives[0].completed