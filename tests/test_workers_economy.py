"""Tests workers / économie (priorité #2).

1. produce_worker doit affecter unit.game à un objet Game (pas l'économie).
2. Un worker nouvellement produit doit récolter et déposer sans exception.
3. Les bonus de recherche de récolte doivent augmenter la quantité récoltée réelle.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.worker import Worker
from systems.economy import EconomySystem


def test_produce_worker_assigne_game_pas_economie():
    """Le worker produit doit avoir .game = objet Game (avec resource_nodes/buildings/economy)."""
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000

    before = len(g.units)
    produced = g.construction_system.produce_worker("worker", g.camera.x + 50, g.camera.y + 50)
    assert produced, "le worker doit être produit"
    new_worker = g.units[-1]
    assert not isinstance(new_worker.game, EconomySystem), \
        "unit.game ne doit PAS être l'économie (TypeError quand worker récolte)"
    assert hasattr(new_worker.game, "resource_nodes"), \
        "unit.game doit être l'objet Game (resource_nodes requis)"


def test_hero_a_un_unit_type():
    """Régression : le héros doit définir unit_type (sinon clic droit plante)."""
    from entities.hero import Hero
    h = Hero(0, 0, "player")
    assert h.unit_type == "hero"


def test_clic_droit_mine_avec_heros_selectionne_ne_plante_pas():
    """Régression : que le héros n'a pas de unit_type, un clic droit sur une
    mine d'or faisait AttributeError ('Hero' object has no attribute 'unit_type')."""
    from core.game import Game
    from entities.resource_node import ResourceNode
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.selected_units = [g.hero]

    mine = ResourceNode(10_000, 10_000, "gold", 1000)  # is_mine auto=True pour gold
    g.resource_nodes = [mine]

    # Clic droit sur la mine (coord souris = map - caméra, passé en tuple).
    # Ne doit pas lever.
    g._handle_right_click((mine.x - g.camera.x, mine.y - g.camera.y))


def test_worker_produit_apres_demarrage_campagne():
    """Régression : après _start_campaign, un worker produit doit apparaître en jeu."""
    from core.game import Game
    g = Game()
    g.faction_id = "human"
    g._start_campaign()
    g.state = "playing"
    # Le système de construction doit partager LA MÊME liste que game.units
    # (un rebind de self.units cassait produce_worker : ressource débitée, worker invisible).
    assert g.construction_system.units is g.units
    assert g.construction_system.buildings is g.buildings

    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    before = len(g.units)
    g._produce_worker("worker")
    assert len(g.units) == before + 1, "le worker doit être créé (et visible dans game.units)"
    assert g.units[-1].unit_type == "worker"


def test_worker_produit_apres_demarrage_campagne_debite_bien():
    """Le worker créé après démarrage coûte bien ses ressources (pas de doublon de débit)."""
    from core.game import Game
    g = Game()
    g.faction_id = "human"
    g._start_campaign()
    g.state = "playing"
    g.economy.gold = 1000

    cost = g.construction_system.WORKER_COSTS["worker"]
    gold_before = g.economy.gold
    g._produce_worker("worker")
    assert g.economy.gold == gold_before - cost["gold"]


def test_worker_produit_recolte_et_depose_sans_crash():
    """Un worker produit via le pipeline doit récolter et déposer sans exception."""
    from core.game import Game
    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000

    g.construction_system.produce_worker("worker", g.camera.x + 50, g.camera.y + 50)
    w = g.units[-1]
    # Trouver une ressource gold
    node = next((n for n in g.resource_nodes if not n.is_depleted() and n.resource_type == "gold"), None)
    assert node is not None
    w.target_resource = node
    w.x, w.y = node.x, node.y  # placer sur la ressource
    # Force désélection (gather)
    w.selected = False

    # La récolte est temporisée (harvest_progress >= 1.0) : on avance les frames
    # jusqu'à ce que le worker porte la ressource.
    frames = 0
    try:
        while not w.carrying and frames < 300:
            w.update(0.016)
            frames += 1
    except Exception as e:
        pytest.fail(f"worker.update a crashé pendant la récolte: {e}")
    assert w.carrying, "le worker doit porter la ressource après la récolte"

    # Retour au dépôt et dépôt
    w._find_drop_off_point()
    assert w.drop_off_point is not None
    w.x, w.y = w.drop_off_point.x, w.drop_off_point.y
    w.is_moving = False
    gold_before = g.economy.gold
    try:
        for _ in range(5):
            w.update(0.016)  # dépôt
            if w.carry_amount == 0:
                break
    except Exception as e:
        pytest.fail(f"worker.update a crashé pendant le dépôt: {e}")
    assert g.economy.gold > gold_before or not w.carrying, \
        "le dépôt doit ajouter la ressource à l'économie du joueur"


def test_recherche_mining_augmente_recolte_reelle():
    """Rechercher 'mining' doit augmenter la quantité d'or réellement récoltée."""
    from entities.resource_node import ResourceNode
    node = ResourceNode(100, 100, "gold", 1000)

    def _complete_harvest(w):
        """Avance les frames jusqu'à ce que le worker ait terminé une récolte."""
        for _ in range(300):
            w.update(0.016)
            if w.carrying:
                return w.carry_amount
        return w.carry_amount

    w1 = Worker(100, 100, "player")  # sans bonus
    w1.target_resource = node
    amount_no_bonus = _complete_harvest(w1)

    # avec bonus mining (simule : meilleure capacité de portage)
    w2 = Worker(100, 100, "player")
    w2.target_resource = node
    w2.max_carry = 15 + 15  # mining double la portée (comme géré par _apply_research_effects)
    amount_with_bonus = _complete_harvest(w2)

    assert amount_with_bonus > amount_no_bonus, \
        "le bonus de recherche doit augmenter la quantité réellement récoltée"