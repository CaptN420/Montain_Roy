"""
Mountain_Roy - Mission System (Système de Missions)
Étape 10: Campagne et missions
"""

from enum import Enum
import json


class MissionStatus(Enum):
    """Statut d'une mission."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Objective:
    """Objectif d'une mission."""
    
    def __init__(self, objective_id: str, description: str, type: str, target: int = 0):
        self.objective_id = objective_id
        self.description = description
        self.type = type  # "kill", "build", "produce", "survive", "collect"
        self.target = target
        self.current = 0
        self.completed = False
    
    def update(self, amount: int = 1):
        """Met à jour la progression."""
        if not self.completed:
            self.current += amount
            if self.current >= self.target:
                self.completed = True
    
    def is_completed(self) -> bool:
        """Vérifie si l'objectif est complété."""
        return self.completed


class Mission:
    """Mission de la campagne."""
    
    def __init__(self, mission_id: str, name: str, description: str):
        self.mission_id = mission_id
        self.name = name
        self.description = description
        self.status = MissionStatus.PENDING
        self.objectives = []
        self.rewards = {
            "gold": 0,
            "wood": 0,
            "food": 0,
            "experience": 0,
        }
        # Composition du camp ennemi pour cette mission (difficulté).
        # Vide = utiliser DEFAULT_ENEMY_CONFIG.
        self.enemy_config = {}
    
    def add_objective(self, objective: Objective):
        """Ajoute un objectif."""
        self.objectives.append(objective)
    
    def check_completion(self) -> bool:
        """Vérifie si toutes les objectives sont complétées."""
        return all(obj.completed for obj in self.objectives)
    
    def start(self):
        """Démarre la mission."""
        self.status = MissionStatus.IN_PROGRESS
    
    def complete(self):
        """Marque la mission comme complétée."""
        self.status = MissionStatus.COMPLETED
    
    def fail(self):
        """Marque la mission comme échouée."""
        self.status = MissionStatus.FAILED
    
    def to_dict(self) -> dict:
        """Sérialise la mission."""
        return {
            "mission_id": self.mission_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "objectives": [
                {
                    "objective_id": obj.objective_id,
                    "description": obj.description,
                    "type": obj.type,
                    "target": obj.target,
                    "current": obj.current,
                    "completed": obj.completed,
                }
                for obj in self.objectives
            ],
            "rewards": self.rewards,
            "enemy_config": self.enemy_config,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Mission":
        """Crée une mission depuis un dictionnaire."""
        mission = cls(data["mission_id"], data["name"], data["description"])
        mission.status = MissionStatus(data.get("status", "pending"))
        
        for obj_data in data.get("objectives", []):
            objective = Objective(
                obj_data["objective_id"],
                obj_data["description"],
                obj_data["type"],
                obj_data.get("target", 0),
            )
            objective.current = obj_data.get("current", 0)
            objective.completed = obj_data.get("completed", False)
            mission.objectives.append(objective)
        
        mission.rewards = data.get("rewards", {})
        mission.enemy_config = data.get("enemy_config", {})
        return mission


class Campaign:
    """Campagne de jeu."""
    
    def __init__(self):
        self.missions = []
        self.current_mission_index = 0
        self.completed_missions = []
    
    def add_mission(self, mission: Mission):
        """Ajoute une mission."""
        self.missions.append(mission)
    
    def start_next_mission(self):
        """Démarre la prochaine mission."""
        if self.current_mission_index < len(self.missions):
            self.missions[self.current_mission_index].start()
            return self.missions[self.current_mission_index]
        return None
    
    def complete_current_mission(self):
        """Marque la mission actuelle comme complétée."""
        if self.current_mission_index < len(self.missions):
            self.missions[self.current_mission_index].complete()
            self.completed_missions.append(self.current_mission_index)
            self.current_mission_index += 1
    
    def get_current_mission(self) -> Mission:
        """Retourne la mission actuelle."""
        if self.current_mission_index < len(self.missions):
            return self.missions[self.current_mission_index]
        return None
    
    def is_campaign_complete(self) -> bool:
        """Vérifie si la campagne est terminée."""
        return self.current_mission_index >= len(self.missions)
    
    def to_dict(self) -> dict:
        """Sérialise la campagne."""
        return {
            "current_mission_index": self.current_mission_index,
            "completed_missions": self.completed_missions,
            "missions": [m.to_dict() for m in self.missions],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        """Crée une campagne depuis un dictionnaire."""
        campaign = cls()
        campaign.current_mission_index = data.get("current_mission_index", 0)
        campaign.completed_missions = data.get("completed_missions", [])
        
        for mission_data in data.get("missions", []):
            mission = Mission.from_dict(mission_data)
            campaign.missions.append(mission)
        
        return campaign


def create_default_campaign() -> Campaign:
    """Crée une campagne par défaut."""
    campaign = Campaign()
    
    # Mission 1: Première attaque
    mission1 = Mission("mission_1", "Premier Contact", 
                       "Détruisez la base ennemie pour prouver votre valeur.")
    mission1.add_objective(Objective("kill_enemies", "Ennemis tués", "kill", 5))
    mission1.add_objective(Objective("build_barracks", "Construire une caserne", "build", 1))
    mission1.rewards = {"gold": 200, "wood": 100, "experience": 100}
    mission1.enemy_config = {"workers": 4, "warriors": 3, "farms": 3, "barracks": True,
                             "towers": 0, "gold": 200, "wood": 150, "food": 100}
    campaign.add_mission(mission1)
    
    # Mission 2: Expansion
    mission2 = Mission("mission_2", "Expansion", 
                       "Produisez 10 unités et construisez une tour défensive.")
    mission2.add_objective(Objective("produce_units", "Unités produites", "produce", 10))
    mission2.add_objective(Objective("build_tower", "Construire une tour", "build", 1))
    mission2.rewards = {"gold": 300, "wood": 150, "food": 100, "experience": 150}
    mission2.enemy_config = {"workers": 4, "warriors": 5, "farms": 3, "barracks": True,
                             "towers": 1, "gold": 260, "wood": 180, "food": 120}
    campaign.add_mission(mission2)
    
    # Mission 3: Contre-attaque
    mission3 = Mission("mission_3", "Contre-Attaque", 
                       "Défendez votre base contre l'assaut ennemi.")
    mission3.add_objective(Objective("survive", "Survivre", "survive", 120))  # 120 secondes
    mission3.add_objective(Objective("kill_enemies", "Ennemis tués", "kill", 15))
    mission3.rewards = {"gold": 400, "wood": 200, "experience": 200}
    mission3.enemy_config = {"workers": 5, "warriors": 7, "farms": 4, "barracks": True,
                             "towers": 2, "gold": 320, "wood": 220, "food": 150}
    campaign.add_mission(mission3)
    
    # Mission 4: Conquête
    mission4 = Mission("mission_4", "Conquête", 
                       "Détruisez toutes les bases ennemies.")
    mission4.add_objective(Objective("destroy_bases", "Bases ennemies détruites", "destroy_building", 3))
    mission4.rewards = {"gold": 500, "wood": 300, "food": 200, "experience": 300}
    mission4.enemy_config = {"workers": 6, "warriors": 9, "farms": 4, "barracks": True,
                             "towers": 2, "gold": 400, "wood": 280, "food": 180}
    campaign.add_mission(mission4)
    
    return campaign
