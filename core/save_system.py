"""
Mountain_Roy - Save System (Système de Sauvegarde)
Étape 9: Sauvegarde et chargement de partie
"""

import json
import os
import pygame
from datetime import datetime


class SaveSystem:
    """Gère la sauvegarde et le chargement des parties."""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        self._create_save_dir()
    
    def _create_save_dir(self):
        """Crée le dossier de sauvegarde s'il n'existe pas."""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_game(self, game, save_name: str = None) -> str:
        """Sauvegarde la partie."""
        if save_name is None:
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        save_data = {
            "version": "2.0",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resources": game.economy.__dict__,
            "enemy_resources": game.enemy_economy.__dict__ if hasattr(game, 'enemy_economy') else {},
            "faction_id": game.faction_id if hasattr(game, 'faction_id') else "human",
            "state": game.state,
            "units": [u.to_dict() for u in game.units],
            "buildings": [b.to_dict() for b in game.buildings],
            "hero": game.hero.to_dict() if game.hero else None,
            "stats": dict(getattr(game, 'stats', {})),
            "map_width": game.game_map.width,
            "map_height": game.game_map.height,
            "tech_tree": game.tech_tree.to_dict() if hasattr(game, 'tech_tree') else None,
            "resource_nodes": [
                {"x": n.x, "y": n.y, "resource_type": n.resource_type,
                 "amount": n.amount, "max_amount": getattr(n, 'max_amount', n.amount)}
                for n in getattr(game, 'resource_nodes', [])
            ],
            "construction_sites": [],
            "campaign": game.campaign.to_dict() if hasattr(game, 'campaign') and game.campaign else None,
            "mission": game.current_mission.to_dict() if hasattr(game, 'current_mission') and game.current_mission else None,
            "mission_timer": getattr(game, 'mission_timer', 0),
        }
        
        # Constructions en cours (séparé pour lisibilité)
        try:
            sites = game.construction_system.construction_sites
            save_data["construction_sites"] = [
                {"building_type": s.building_type, "x": s.x, "y": s.y,
                 "faction": s.faction, "elapsed_time": s.elapsed_time,
                 "build_time": s.build_time}
                for s in sites
            ]
        except Exception:
            save_data["construction_sites"] = []
        
        save_path = os.path.join(self.save_dir, f"{save_name}.json")
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return save_path
    
    def load_game(self, save_name: str) -> dict:
        """Charge une partie."""
        save_path = os.path.join(self.save_dir, f"{save_name}.json")
        
        if not os.path.exists(save_path):
            raise FileNotFoundError(f"Save file not found: {save_path}")
        
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        return save_data
    
    def list_saves(self) -> list:
        """Liste toutes les sauvegardes."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                save_path = os.path.join(self.save_dir, filename)
                with open(save_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    saves.append({
                        "name": filename[:-5],
                        "timestamp": save_data.get("timestamp", "Unknown"),
                        "version": save_data.get("version", "1.0"),
                    })
        return saves
    
    def delete_save(self, save_name: str):
        """Supprime une sauvegarde."""
        save_path = os.path.join(self.save_dir, f"{save_name}.json")
        if os.path.exists(save_path):
            os.remove(save_path)


class LoadError(Exception):
    """Exception pour les erreurs de chargement."""
    pass
