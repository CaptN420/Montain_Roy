"""Tests campagne + UX (priorité #6).

Objectifs:
1. Nouveau type d'objectif 'destroy_building' pour la mission Conquête :
   mis à jour à la destruction d'un bâtiment ENNEMI, jamais à la construction.
2. Message UI explicite quand la recherche exige un bâtiment de recherche
   (nom + coût) au lieu du simple print console.
3. File de production visible (progression) + indicateurs d'ordres
   (déplacement / attaque / récolte / construction).
4. Raisons précises quand une action est bloquée.
5. Tutoriel contextuel minimal affiché une seule fois.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest
from types import SimpleNamespace

from systems.campaign import create_default_campaign, Mission, Objective
from systems.economy import EconomySystem
from systems.construction import ProductionSystem
from ui.hud import HUD


def make_game():
    from core.game import Game
    g = Game()
    g.state = "playing"
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    return g


# ============================================================
# 1. OBJECTIF destroy_building (mission Conquête)
# ============================================================

def test_mission_conquete_utilise_objectif_destroy_building():
    """La mission 4 (Conquête) doit utiliser le type 'destroy_building'."""
    campaign = create_default_campaign()
    mission_4 = next(m for m in campaign.missions if m.mission_id == "mission_4")
    assert any(obj.type == "destroy_building" for obj in mission_4.objectives), (
        "Conquête doit utiliser un objectif destroy_building, pas build"
    )
    # Aucun objectif 'build' ne doit rester dans cette mission
    assert not any(obj.type == "build" for obj in mission_4.objectives)


def test_destroy_building_progresse_a_destruction_batiment_ennemi():
    """Détruire un bâtiment ENNEMI doit incrémenter l'objectif destroy_building."""
    g = make_game()
    g.campaign = create_default_campaign()
    g.current_mission = next(m for m in g.campaign.missions if m.mission_id == "mission_4")
    obj = next(o for o in g.current_mission.objectives if o.type == "destroy_building")
    assert obj.current == 0

    g._handle_building_destroyed(SimpleNamespace(faction="enemy"))
    assert obj.current == 1, "la destruction d'un bâtiment ennemi doit incrémenter"
    assert g.stats["enemies_killed"] == 1


def test_destroy_building_ne_progresse_pas_si_batiment_joueur():
    """Détruire un bâtiment JOUEUR ne doit pas incrémenter destroy_building."""
    g = make_game()
    g.current_mission = next(m for m in g.campaign.missions if m.mission_id == "mission_4")
    obj = next(o for o in g.current_mission.objectives if o.type == "destroy_building")

    g._handle_building_destroyed(SimpleNamespace(faction="player"))
    assert obj.current == 0, "un bâtiment joueur détruit ne compte pas"


def test_destroy_building_n_est_pas_marque_par_la_construction():
    """Construire des bâtiments ne doit PAS compléter l'objectif destroy_building."""
    g = make_game()
    g.current_mission = next(m for m in g.campaign.missions if m.mission_id == "mission_4")
    obj = next(o for o in g.current_mission.objectives if o.type == "destroy_building")

    # Simuler plein de bâtiments joueur — _check_mission_objectives ('build') ne doit pas le compléter
    class FakeB:
        faction = "player"
    g.buildings = [FakeB() for _ in range(10)]
    g._check_mission_objectives()
    assert obj.current == 0, "construire ne doit pas faire progresser destroy_building"
    assert not obj.is_completed()


# ============================================================
# 2. MESSAGE UI pour la recherche exigée (bâtiment + coût)
# ============================================================

def test_research_requirement_message_inclut_batiment_et_cout():
    """Le message doit nommer le bâtiment de recherche et son coût."""
    g = make_game()
    msg = g._research_requirement_message()
    assert "Recherche" in msg
    assert ("académie" in msg.lower() or "Académie" in msg)
    assert "or" in msg
    # Un chiffre (le coût) doit être présent
    assert any(ch.isdigit() for ch in msg)


def test_recherche_sans_batiment_affiche_message_ui():
    """Appuyer sur T sans bâtiment de recherche sélectionné affiche un message UI."""
    g = make_game()
    g._selected_building = None
    assert g.ui_message is None
    g._handle_research_key()
    assert g.ui_message is not None, "un message UI doit être affiché"
    assert "Recherche" in g.ui_message


# ============================================================
# 3. FILE DE PRODUCTION + INDICATEURS D'ORDRES
# ============================================================

class _Econ(EconomySystem):
    def __init__(self):
        super().__init__()
        self.gold = 500
        self.wood = 500
        self.food = 500


def test_production_queue_track_progression():
    """Lancer une production doit créer une entrée en file, pas une unité immédiate."""
    econ = _Econ()
    units = []
    ps = ProductionSystem(econ, units)
    assert ps.enqueue("warrior", 0, 0) is True
    assert len(units) == 0, "l'unité ne doit pas apparaître immédiatement"
    assert len(ps.queue) == 1
    assert ps.queue[0]["progress"] == 0.0

    # Journée complète → l'unité apparaît, la file se vide
    spawned = ps.update(ps.queue[0]["total"] + 0.1)
    assert len(spawned) == 1
    assert len(units) == 1
    assert len(ps.queue) == 0


def test_production_queue_respecte_ordre():
    """La file doit produire dans l'ordre (FIFO)."""
    econ = _Econ()
    units = []
    ps = ProductionSystem(econ, units)
    ps.enqueue("warrior", 0, 0)   # time 5.0
    ps.enqueue("scout", 10, 10)   # time 4.0 — devrait sortir APRÈS le warrior
    ps.update(ps.queue[0]["total"] + 0.1)  # ne termine que le warrior
    assert len(units) == 1
    assert units[0].unit_type == "warrior", "la file doit être FIFO"


def test_production_queue_refuse_sans_ressources():
    """Produire sans ressources suffisantes doit être refusé (pas d'entrée en file)."""
    econ = _Econ()
    econ.gold = 0
    econ.wood = 0
    econ.food = 0
    ps = ProductionSystem(econ, [])
    assert ps.enqueue("warrior", 0, 0) is False
    assert len(ps.queue) == 0


def _fake_unit(**kwargs):
    defaults = dict(construction_target=None, target_resource=None, target=None, is_moving=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_order_indicator_attaque():
    assert HUD.order_text(_fake_unit(target=object())) == "Attaque"


def test_order_indicator_recolte():
    assert HUD.order_text(_fake_unit(target_resource=object())) == "Récolte"


def test_order_indicator_construction():
    assert HUD.order_text(_fake_unit(construction_target=object())) == "Construction"


def test_order_indicator_deplacement():
    assert HUD.order_text(_fake_unit(is_moving=True)) == "Déplacement"


def test_order_indicator_inactif():
    assert HUD.order_text(_fake_unit()) == ""


# ============================================================
# 4. RAISONS PRÉCISES QUAND UNE ACTION EST BLOQUÉE
# ============================================================

def test_raison_ressources_insuffisantes():
    """_can_produce_unit doit donner la raison 'ressources insuffisantes'."""
    g = make_game()
    g.faction = None  # contourne la vérification faction
    g.economy.gold = 0
    g.economy.wood = 0
    g.economy.food = 0
    ok, reason = g._can_produce_unit("warrior")
    assert ok is False
    assert "ressource" in reason


def test_raison_preconditions_batiment_manquant():
    """Sans la caserne, produire un guerrier doit donner une raison de prérequis."""
    g = make_game()
    faction = type("F", (), {
        "can_produce": lambda self, utype, buildings, researched:
            (False, "Caserne requise") if utype != "worker" else (True, ""),
    })()
    g.faction = faction
    g.buildings = []  # pas de caserne
    ok, reason = g._can_produce_unit("warrior")
    assert ok is False
    assert reason  # une raison précise doit exister


def test_raison_population_maximale():
    """Produire au-delà de la population max doit donner une raison précise."""
    from entities.building import Farm
    g = make_game()
    g.faction = None
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    # Un seul bâtiment joueur → population max faible
    g.buildings = [Farm(0, 0, "player")]
    from types import SimpleNamespace as SN
    g.units = []
    for _ in range(60):  # bien au-delà de la pop max
        g.units.append(SN(faction="player"))
    ok, reason = g._can_produce_unit("warrior")
    assert ok is False
    assert "population" in reason or "pop" in reason


def test_raison_construction_bloquee_affichee_au_placement():
    """Placement d'un bâtiment sur terrain invalide doit donner une raison précise."""
    from systems.construction import ConstructionSystem
    from systems.economy import EconomySystem
    from map.game_map import GameMap
    from map.tile import Tile, TileType

    class FlatMap(GameMap):
        def __init__(self, w=64, h=64):
            self.width, self.height = w, h
            self.tiles = [[Tile(x, y, TileType.GRASS) for x in range(w)] for y in range(h)]
        def _generate_map(self):
            pass

    econ = EconomySystem()
    econ.gold = 1000; econ.wood = 1000; econ.food = 1000
    cs = ConstructionSystem(econ, [], [])
    cs._game_map = FlatMap()
    cs._all_nodes = []
    cs._available_buildings = None

    g = make_game()
    g.construction_system = cs
    g.economy = econ
    g.selected_building_type = "farm"
    # Position sur de l'eau → invalide
    cs._game_map.tiles[20][20] = Tile(20, 20, TileType.WATER)
    x, y = 20 * 32 + 16, 20 * 32 + 16
    g._place_building(x, y)
    assert g.ui_message is not None, "un message de raison doit être affiché"
    assert "eau" in g.ui_message.lower() or "impossible" in g.ui_message.lower() or \
           "constructible" in g.ui_message.lower()


# ============================================================
# 5. TUTORIEL CONTEXTUEL MINIMAL
# ============================================================

def test_tutoriel_affiche_une_seule_fois():
    """Chaque tutoriel doit apparaître une seule fois."""
    g = make_game()
    assert g._show_tutorial("gather", "Récoltez") is True
    assert g.tutorial_shown.get("gather") is True
    assert g.ui_message is not None
    # Deuxième fois : ne doit pas s'afficher à nouveau
    g.ui_message = None
    assert g._show_tutorial("gather", "Récoltez") is False
    assert g.ui_message is None


def test_tutoriels_independants():
    """Les différents tutoriels (récolte/construction/recherche/combat) sont indépendants."""
    g = make_game()
    g._show_tutorial("gather", "G")
    g._show_tutorial("build", "B")
    assert g.tutorial_shown["gather"] is True
    assert g.tutorial_shown["build"] is True
    assert g._show_tutorial("research", "R") is True
    assert g._show_tutorial("combat", "C") is True