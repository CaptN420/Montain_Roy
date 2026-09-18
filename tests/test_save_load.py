"""Tests sauvegarde / chargement (priorité #3).

Bug documentés:
- La sauvegarde n'inclut pas: campagne, faction, tech tree, ressources ennemies,
  nœuds de ressources, constructions en cours, statistiques.
- Au chargement, les bâtiments sont tous recréés comme TownHall (perte du vrai type).
- Les workers ne sont pas réattachés à l'objet Game.
- Pas de version de format de sauvegarde.
"""
import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.building import Farm, Barracks, TownHall, Dock
from entities.unit_types import Worker, Warrior
from systems.campaign import Campaign, create_default_campaign
from core.save_system import SaveSystem


@pytest.fixture
def save_dir(tmp_path):
    d = os.path.join(str(tmp_path), "saves")
    os.makedirs(d, exist_ok=True)
    return d


def make_game(save_dir):
    from core.game import Game
    g = Game()
    g._apply_faction("elf")
    g.state = "playing"
    g.save_system = SaveSystem(save_dir)
    g.economy.gold = 500
    g.economy.wood = 400
    g.economy.food = 300
    g.enemy_economy.gold = 123
    g.enemy_economy.wood = 234
    g.enemy_economy.food = 345
    return g


def test_sauvegarde_conserve_faction_et_ressources(save_dir):
    """La sauvegarde doit contenir faction, ressources joueur ET ennemies."""
    g = make_game(save_dir)
    g.save_system.save_game(g, "t_save")
    data = g.save_system.load_game("t_save")

    assert data.get("faction_id") == "elf", "la faction doit être sauvegardée"
    assert data["resources"]["gold"] == 500
    assert data.get("enemy_resources", {}).get("gold") == 123, \
        "les ressources ennemies doivent être sauvegardées"


def test_chargement_restaure_vrais_types_batiments(save_dir):
    """Charger doit restaurer le vrai type de chaque bâtiment (pas que TownHall)."""
    g = make_game(save_dir)
    # Vider et ajouter des bâtiments variés
    g.buildings = []
    g.buildings.append(TownHall(100, 100, "player"))
    g.buildings.append(Barracks(200, 100, "player"))
    g.buildings.append(Farm(300, 100, "player"))
    g.buildings.append(Dock(400, 100, "enemy"))
    g.save_system.save_game(g, "t_buildings")

    g2 = make_game(save_dir)
    g2._load_save("t_buildings")
    types = [b.building_type for b in g2.buildings]
    assert "farm" in types, "les fermes doivent être restaurées comme Farm"
    assert "dock" in types, "les quais doivent être restaurés comme Dock (pas TownHall)"
    assert "town_hall" in types


def test_chargement_retablit_campagne(save_dir):
    """Charger doit restaurer la campagne et la mission en cours."""
    g = make_game(save_dir)
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.missions[0] if g.campaign.missions else None
    # Marquer une mission comme complétée et avancer l'index
    if g.campaign.missions:
        g.campaign.completed_missions.append(g.campaign.missions[0].mission_id)
        g.campaign.current_mission_index = 1
    g.save_system.save_game(g, "t_camp")

    g2 = make_game(save_dir)
    g2._load_save("t_camp")
    assert g2.campaign is not None, "la campagne doit être restaurée"
    assert len(g2.campaign.missions) == len(g.campaign.missions), \
        "les missions de la campagne doivent être restaurées"
    assert g2.campaign.current_mission_index == 1, \
        "l'index de mission en cours doit être restauré"
    assert g2.campaign.completed_missions == g.campaign.completed_missions, \
        "les missions complétées doivent être restaurées"


def test_chargement_reattache_workers_au_game(save_dir):
    """Après chargement, chaque worker unit doit référencer le Game (game != économie)."""
    g = make_game(save_dir)
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    # forcer un worker existant avec game=None puis sauvegarder
    for u in g.units:
        if hasattr(u, "unit_type") and u.unit_type == "worker":
            u.game = None
    g.save_system.save_game(g, "t_workers")

    g2 = make_game(save_dir)
    g2._load_save("t_workers")
    workers = [u for u in g2.units if getattr(u, "unit_type", "") == "worker"]
    for w in workers:
        assert w.game is not None, "le worker doit être réattaché au Game"
        from systems.economy import EconomySystem
        assert not isinstance(w.game, EconomySystem), \
            "le worker.game ne doit pas être l'économie"


def test_sauvegarde_a_une_version_de_format(save_dir):
    """La sauvegarde doit indiquer sa version de format."""
    g = make_game(save_dir)
    g.save_system.save_game(g, "t_version")
    data = g.save_system.load_game("t_version")
    assert "version" in data, "la sauvegarde doit avoir une version"
    assert data["version"] == "2.0", "la version actuelle doit être 2.0"


def test_chargement_restaure_tech_tree(save_dir):
    """Charger doit restaurer l'arbre technologique (recherches terminées et en cours)."""
    g = make_game(save_dir)
    g.economy.gold = 1000; g.economy.wood = 1000; g.economy.food = 1000
    # marquer une recherche terminée + une en cours
    g.tech_tree.get_technology("mining").researched = True
    g.tech_tree.unlocked_techs.append("mining")
    started = g.tech_tree.start_research("iron_working", g.economy)
    g.tech_tree.update(5.0)
    g.save_system.save_game(g, "t_tech")

    g2 = make_game(save_dir)
    g2._load_save("t_tech")
    assert getattr(g2.tech_tree, "technologies", None) is not None
    assert g2.tech_tree.unlocked_techs == ["mining"], \
        "les recherches terminées doivent être restaurées"
    assert g2.tech_tree.current_research is not None, \
        "la recherche en cours doit être restaurée"


def test_chargement_restaure_constructions_en_cours(save_dir):
    """Charger doit restaurer les chantiers de construction en cours."""
    g = make_game(save_dir)
    g.economy.gold = 1000; g.economy.wood = 1000; g.economy.food = 1000
    # Forcer toute la carte en herbe (la carte réelle a eau/montagne aléatoires)
    from map.tile import Tile, TileType
    for yy in range(g.game_map.height):
        g.game_map.tiles[yy] = [Tile(xx, yy, TileType.GRASS) for xx in range(g.game_map.width)]
    g.construction_system._game_map = g.game_map
    g.construction_system._all_nodes = []
    tx, ty = 20, 20
    g.selected_building_type = "farm"
    g._place_building(tx * 32 + 16, ty * 32 + 16)
    assert g.construction_system.construction_sites, "un chantier doit exister"
    g.save_system.save_game(g, "t_sites")

    g2 = make_game(save_dir)
    g2._load_save("t_sites")
    assert len(g2.construction_system.construction_sites) == 1, \
        "les constructions en cours doivent être restaurées"