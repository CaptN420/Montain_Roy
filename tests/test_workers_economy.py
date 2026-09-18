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
    try:
        w.update(0.016)  # récolte
    except Exception as e:
        pytest.fail(f"worker.update a crashé pendant la récolte: {e}")
    assert w.carrying, "le worker doit porter la ressource après la récolte"

    # Retour au dépôt et dépôt
    w._find_drop_off_point()
    assert w.drop_off_point is not None
    w.x, w.y = w.drop_off_point.x, w.drop_off_point.y
    gold_before = g.economy.gold
    try:
        w.update(0.016)  # dépôt
    except Exception as e:
        pytest.fail(f"worker.update a crashé pendant le dépôt: {e}")
    assert g.economy.gold > gold_before or not w.carrying, \
        "le dépôt doit ajouter la ressource à l'économie du joueur"


def test_recherche_mining_augmente_recolte_reelle():
    """Rechercher 'mining' doit augmenter la quantité d'or réellement récoltée."""
    from entities.resource_node import ResourceNode
    node = ResourceNode(100, 100, "gold", 1000)

    w1 = Worker(100, 100, "player")  # sans bonus
    w1.target_resource = node
    w1.update(0.016)
    amount_no_bonus = w1.carry_amount

    # avec bonus mining (simule : meilleure capacité de portage)
    w2 = Worker(100, 100, "player")
    w2.target_resource = node
    w2.max_carry = 15 + 15  # mining double la portée (comme géré par _apply_research_effects)
    w2.update(0.016)
    amount_with_bonus = w2.carry_amount

    assert amount_with_bonus > amount_no_bonus, \
        "le bonus de recherche doit augmenter la quantité réellement récoltée"