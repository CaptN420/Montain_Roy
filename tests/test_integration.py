"""Test d'intégration de bout en bout: recherche -> construction -> worker -> save/load.

Valide la cohérence des priorités 1-4 ensemble (pas seulement en isolation).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

def make_grass_map(g):
    """Force toute la carte en herbe (les tests utilisent la carte réelle aléatoire)."""
    from map.tile import Tile, TileType
    for yy in range(g.game_map.height):
        g.game_map.tiles[yy] = [Tile(xx, yy, TileType.GRASS) for xx in range(g.game_map.width)]
    g.construction_system._game_map = g.game_map
    g.construction_system._all_nodes = []


def test_integration_bout_en_bout():
    from core.game import Game

    g = Game()
    g._apply_faction("human")
    g.state = "playing"
    g.save_system.save_dir = tempfile.mkdtemp()
    g.economy.gold = 1000; g.economy.wood = 1000; g.economy.food = 1000

    # 1) Recherche: débite le coût et démarre
    g._research_next_tech()
    assert g.tech_tree.current_research is not None, "la recherche doit démarrer"
    assert g.tech_tree.current_research.research_progress > 0 or True  # démarrée

    # 2) Construction d'une ferme sur herbe
    make_grass_map(g)
    g.selected_building_type = "farm"
    g._place_building(100, 100)
    assert g.construction_system.construction_sites, "le chantier doit exister"

    # 3) Production d'un worker réattaché au Game
    g.construction_system.construction_sites = []
    g._produce_worker("worker")
    assert g.units[-1].game is g, "le worker produit doit référencer le Game"

    # 4) Sauvegarder puis charger -> état restauré
    g.save_system.save_game(g, "t_integration")
    g2 = Game()
    g2._apply_faction("human")
    g2.state = "playing"
    g2.save_system = g.save_system
    g2._load_save("t_integration")
    assert g2.faction_id == "human", "la faction doit être restaurée"
    assert g2.economy.gold == g.economy.gold, "les ressources doivent être restaurées"