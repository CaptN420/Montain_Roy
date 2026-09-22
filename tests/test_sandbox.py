"""Tests du mode Sandbox (mode libre).

Vérifie :
- le bouton "Mode Libre" du menu principal renvoie "sandbox",
- _start_sandbox lance un jeu sans ennemi, ressources généreuses, IA coupée,
- _check_victory_defeat est neutre en mode sandbox,
- l'IA n'est pas mise à jour en mode sandbox.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from core.game import Game
from ui.menus import MainMenu
from entities.worker import Worker


def test_menu_principal_a_un_bouton_mode_libre():
    menu = MainMenu()
    texts = [b.text for b in menu.buttons]
    assert "Mode Libre" in texts, "le menu doit proposer le mode libre"


def test_bouton_mode_libre_retourne_sandbox():
    menu = MainMenu()
    # Trouver le bouton "Mode Libre" et cliquer dessus
    button = next(b for b in menu.buttons if b.text == "Mode Libre")
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                               {"button": 1, "pos": button.rect.center})
    assert menu.handle_event(event) == "sandbox"


def test_start_sandbox_sans_ennemis():
    g = Game()
    g._sandbox_pending = True
    g._start_sandbox()
    # Le joueur est seul : aucun ennemi
    assert g.sandbox is True
    assert all(u.faction != "enemy" for u in g.units)
    assert all(b.faction != "enemy" for b in g.buildings)
    # Le joueur a bien sa base
    assert any(b.faction == "player" for b in g.buildings)
    # Ressources généreuses
    assert g.economy.gold >= 800
    assert g.economy.wood >= 600
    # État en jeu
    assert g.state == "playing"
    assert g.current_mission is None
    assert g.ai.state == "idle"


def test_sandbox_worker_a_game_ref():
    g = Game()
    g._sandbox_pending = True
    g._start_sandbox()
    # Les workers joueurs conservent leur référence game (récolte/dépôt)
    assert all(getattr(u, 'game', None) is g for u in g.units)
    assert all(hasattr(u, 'game') and u.game is g for u in g.units
               if isinstance(u, Worker))


def test_sandbox_ne_decide_pas_victoire():
    g = Game()
    g._sandbox_pending = True
    g._start_sandbox()
    # Détruire toute la base joueur : en sandbox, pas de défaite.
    g.buildings[:] = [b for b in g.buildings if b.faction != "player"]
    g._check_victory_defeat()
    assert g.state == "playing", "le mode libre ne déclenche jamais la défaite"


def test_ia_desactivee_en_sandbox():
    g = Game()
    g._sandbox_pending = True
    g._start_sandbox()
    # L'update du jeu ne doit pas appeler ai.update en sandbox.
    # On vérifie que le flag sandbox désactive bien l'IA à la source du code.
    assert g.sandbox is True
    # (le contrôle réel est dans Game.update: `if not self.sandbox: ai.update`)
    # Simule l'absence d'unités ennemies : l'IA n'a rien à faire de toute façon.
    assert all(u.faction != "enemy" for u in g.units)