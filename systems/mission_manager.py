"""Mission System - Mountain_Roy RTS
Gère les objectifs, les niveaux et la progression de l'histoire.
"""

import json
import os

class MissionManager:
    """Gère l'état actuel de la mission et les objectifs."""
    
    def __init__(self, mission_id: str = "prologue"):
        self.current_mission_id = mission_id
        self.objectives = []
        self.is_completed = False
        self.is_failed = False
        self.current_objective_idx = 0
        self.mission_data = self._load_mission_data()
        
        # Initialiser la mission actuelle
        self._setup_mission(mission_id)

    def _load_mission_data(self) -> dict:
        """Charge les données des missions depuis un fichier JSON."""
        # Pour le moment, on utilise des données par défaut si le fichier manque
        default_missions = {
            "prologue": {
                "name": "L'éveil de la forêt",
                "description": "Établissez votre premier campement et récoltez des ressources de base.",
                "objectives": [
                    {"id": "collect_wood", "desc": "Récolter 100 de bois", "type": "resource", "target": 100, "key": "wood"},
                    {"id": "build_barracks", "desc": "Construire une caserne", "type": "building", "target": "barracks"}
                ],
                "victory_conditions": ["collect_wood", "build_barracks"]
            },
            "first_contact": {
                "name": "Premier Contact",
                "description": "Un groupe d'éclaireurs ennemis rôde. Défendez votre territoire.",
                "objectives": [
                    {"id": "defeat_scouts", "desc": "Détruire les éclaireurs ennemis", "type": "kill", "target": 5}
                ],
                "victory_conditions": ["defeat_scouts"]
            }
        }
        
        # On pourrait charger depuis un fichier réel ici
        # with open("data/missions.json", "r") as f:
        #     return json.load(f)
        
        return default_missions

    def _setup_mission(self, mission_id: str):
        """Prépare les données de la mission sélectionnée."""
        if mission_id in self.mission_data:
            data = self.mission_data[mission_id]
            self.objectives = data["objectives"]
            self.victory_conditions = data["victory_conditions"]
            self.current_objective_idx = 0
            self.is_completed = False
            self.is_failed = False
        else:
            print(f"Erreur: Mission {mission_id} non trouvée.")

    def update(self, game_state: dict) -> str:
        """
        Met à jour la progression des objectifs.
        game_state: dictionnaire contenant les ressources, unités tuées, bâtiments, etc.
        Retourne le texte de l'objectif actuel.
        """
        if self.is_completed or self.is_failed:
            return "Mission terminée"

        current_obj = self.objectives[self.current_objective_idx]
        
        # Vérification selon le type d'objectif
        met = False
        if current_obj["type"] == "resource":
            met = game_state.get("resources", {}).get(current_obj["key"], 0) >= current_obj["target"]
        elif current_obj["type"] == "building":
            # Vérifie si le bâtiment est dans la liste des bâtiments du joueur
            buildings = game_state.get("buildings", [])
            met = any(b.get("type") == current_obj["target"] for b in buildings)
        elif current_obj["type"] == "kill":
            met = game_state.get("kills", 0) >= current_obj["target"]

        if met:
            self.current_objective_idx += 1
            if self.current_objective_idx >= len(self.objectives):
                self.is_completed = True
                return "Mission réussie !"
            return f"Objectif complété ! Prochain : {self.objectives[self.current_objective_idx]['desc']}"

        return f"Objectif : {current_obj['desc']}"

    def get_current_objective_text(self) -> str:
        if self.is_completed:
            return "Mission réussie !"
        if self.is_failed:
            return "Mission échouée"
        
        if self.current_objective_idx < len(self.objectives):
            return self.objectives[self.current_objective_idx]["desc"]
        return "Objectif inconnu"

# Exemple d'utilisation pour le debug
if __name__ == "__main__":
    manager = MissionManager("prologue")
    print(f"Mission : {manager.mission_data['prologue']['name']}")
    print(f"Objectif initial : {manager.get_current_objective_text()}")
    
    # Simuler la progression
    print("\n--- Simulant la récolte de bois ---")
    state = {"resources": {"wood": 100, "gold": 50}, "buildings": []}
    print(manager.update(state))
    
    print("\n--- Simulant la construction de la caserne ---")
    state = {"resources": {"wood": 200, "gold": 200}, "buildings": [{"type": "barracks"}]}
    print(manager.update(state))
