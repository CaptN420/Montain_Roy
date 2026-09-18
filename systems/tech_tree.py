"""
Mountain_Roy - Tech Tree (Arbre Technologique)
Étape 15: Système de recherche et améliorations

Corrections (audit 2026-09-18):
- Les technologies sont en état d'instance (plus de partage entre parties).
- start_research débite le coût exactement une fois (au lancement).
- Une tech finie vide current_research et n'est déverrouillée qu'une fois.
- start_research sans ressources est refusé (plus de 9999 implicites).
- to_dict/from_dict conservent progression, recherches et recherche en cours.
"""

from enum import Enum


class TechType(Enum):
    """Types de technologies."""
    MILITARY = "military"
    ECONOMIC = "economic"
    DEFENSIVE = "defensive"
    HERO = "hero"


class TechRequirement:
    """Dépendance pour une technologie."""

    def __init__(self, tech_id: str, required: bool = True):
        self.tech_id = tech_id
        self.required = required


class Technology:
    """Technologie researchable."""

    def __init__(self, tech_id: str, name: str, description: str,
                 cost: dict = None, requirements: list = None):
        self.tech_id = tech_id
        self.name = name
        self.description = description
        self.cost = cost or {"gold": 100, "wood": 50, "food": 0}
        self.requirements = requirements or []
        self.researched = False
        self.research_time = 30.0  # secondes
        self.research_progress = 0

    def can_research(self, researched_ids) -> bool:
        """Vérifie si les prérequis sont satisfaits (ids de technologies recherchées)."""
        if self.researched:
            return False
        for req in self.requirements:
            if req.required and req.tech_id not in researched_ids:
                return False
        return True

    def start_research(self):
        """Démarre la recherche."""
        if not self.researched:
            self.research_progress = 0

    def update(self, dt: float):
        """Met à jour la progression de recherche."""
        if not self.researched:
            self.research_progress += dt
            if self.research_progress >= self.research_time:
                self.researched = True

    def to_dict(self) -> dict:
        """Sérialise la technologie."""
        return {
            "tech_id": self.tech_id,
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "requirements": [{"tech_id": r.tech_id, "required": r.required} for r in self.requirements],
            "researched": self.researched,
            "research_progress": self.research_progress,
        }


class TechTree:
    """Arbre technologique."""

    # Données sources (immuables) - chaque instance en fait sa copie
    _TECH_DEFS = [
        # Militaires
        ("iron_working", "Travail du Fer", "Augmente les dégâts des unités terrestres de 10%",
         {"gold": 150, "wood": 0, "food": 0}, []),
        ("archery", "Archerie", "Débloque les archers et augmente leur portée",
         {"gold": 100, "wood": 50, "food": 0}, [("iron_working", True)]),
        ("heavy_armor", "Armure Lourde", "Augmente l'armure des chevaliers de 20%",
         {"gold": 200, "wood": 100, "food": 0}, [("iron_working", True)]),
        ("magic_study", "Études Magiques", "Débloque les mages et augmente leur puissance",
         {"gold": 250, "wood": 150, "food": 50}, [("archery", True)]),
        # Économiques
        ("mining", "Minage", "Les mineurs collectent 2x plus d'or",
         {"gold": 100, "wood": 50, "food": 0}, []),
        ("logging", "Sylviculture", "Les bûcherons collectent 2x plus de bois",
         {"gold": 80, "wood": 0, "food": 0}, []),
        ("agriculture", "Agriculture", "Augmente la production de nourriture de 50%",
         {"gold": 120, "wood": 80, "food": 0}, [("logging", True)]),
        # Défensives
        ("fortification", "Fortification", "Les bâtiments ont +20% de PV",
         {"gold": 150, "wood": 100, "food": 0}, [("mining", True)]),
        ("siege_weapons", "Armes de Siège", "Débloque les engins de siège",
         {"gold": 300, "wood": 200, "food": 100}, [("heavy_armor", True)]),
        # Héros
        ("hero_training", "Entraînement Héros", "Le héros gagne 50% plus d'XP",
         {"gold": 200, "wood": 100, "food": 50}, []),
        ("ultimate_skill", "Compétence Ultime", "Débloque la compétence Météore du héros",
         {"gold": 400, "wood": 200, "food": 100}, [("magic_study", True)]),
        # Uniques par faction
        ("gunpowder", "Poudre à Canon", "Débloque l'engin de siège avancé et +10% de dégâts",
         {"gold": 300, "wood": 200, "food": 100}, [("heavy_armor", True)]),
        ("orc_warpath", "Sentier de Guerre", "Unités orques +15% vitesse d'attaque",
         {"gold": 250, "wood": 150, "food": 50}, [("iron_working", True)]),
        ("woodland_craft", "Art des Bois", "Archers et rangers +15% de dégâts supplémentaires",
         {"gold": 250, "wood": 200, "food": 0}, [("archery", True)]),
        ("master_armor", "Armure de Maître", "Toutes les unités naines +5 armure",
         {"gold": 400, "wood": 250, "food": 100}, [("heavy_armor", True)]),
    ]

    def __init__(self):
        self.technologies = {}
        self.unlocked_techs = []
        self.current_research = None
        self._initialize_technologies()

    def _initialize_technologies(self):
        """Initialise les technologies (copie par instance)."""
        self.technologies = {}
        for tech_id, name, desc, cost, reqs in self._TECH_DEFS:
            requirements = [TechRequirement(r_id, required) for r_id, required in reqs]
            self.technologies[tech_id] = Technology(tech_id, name, desc, dict(cost), requirements)

    @property
    def researched_ids(self):
        """Ensemble des technologies complétées."""
        return set(self.unlocked_techs)

    def get_technology(self, tech_id: str):
        """Récupère une technologie par son ID."""
        return self.technologies.get(tech_id)

    def start_research(self, tech_id: str, resources=None) -> bool:
        """Démarre une recherche. Débite le coût exactement une fois.

        `resources` doit fournir can_afford(cost) -> bool et pay_cost(cost).
        Retourne False si la recherche est impossible ou si resources est None.
        """
        if resources is None:
            return False

        tech = self.get_technology(tech_id)
        if tech is None or tech.researched:
            return False
        if not tech.can_research(self.researched_ids):
            return False
        # Recherche en cours : refus (ne pas écraser)
        if self.current_research is not None:
            return False
        # Vérifier et débiter le coût (une seule fois, au lancement)
        if not self._can_afford(resources, tech.cost):
            return False

        self._pay_cost(resources, tech.cost)
        tech.start_research()
        self.current_research = tech
        return True

    @staticmethod
    def _can_afford(resources, cost) -> bool:
        if hasattr(resources, "can_afford"):
            return resources.can_afford(cost)
        # backward-compat avec dict
        return (resources.get("gold", 0) >= cost.get("gold", 0) and
                resources.get("wood", 0) >= cost.get("wood", 0) and
                resources.get("food", 0) >= cost.get("food", 0))

    @staticmethod
    def _pay_cost(resources, cost):
        if hasattr(resources, "pay_cost"):
            resources.pay_cost(cost)
        elif hasattr(resources, "get"):
            for key in ("gold", "wood", "food"):
                if key in cost:
                    value = cost[key]
                    setattr(resources, key, getattr(resources, key, 0) - value)

    def update(self, dt: float):
        """Met à jour la recherche en cours. Déverrouille UNE fois."""
        if not self.current_research:
            return
        tech = self.current_research
        tech.update(dt)
        if tech.researched:
            # Déverrouiller une seule fois, vider la recherche active
            if tech.tech_id not in self.unlocked_techs:
                self.unlocked_techs.append(tech.tech_id)
            self.current_research = None

    def get_available_research(self, resources, tech_ids: list = None) -> list:
        """Retourne les technologies disponibles (prérequis remplis) et abordables."""
        available = []
        for tech_id, tech in self.technologies.items():
            if tech.researched:
                continue
            if tech_ids is not None and tech_id not in tech_ids:
                continue
            if tech.can_research(self.researched_ids):
                if self._can_afford(resources, tech.cost):
                    available.append(tech)
        return available

    def to_dict(self) -> dict:
        """Sérialise l'arbre technologique."""
        return {
            "unlocked_techs": list(self.unlocked_techs),
            "current_research": self.current_research.tech_id if self.current_research else None,
            "technologies": [t.to_dict() for t in self.technologies.values()],
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crée un arbre technologique depuis un dictionnaire."""
        tech_tree = cls()
        # Restaurer l'état par id (pas de duplication)
        for tech_data in data.get("technologies", []):
            tech_id = tech_data["tech_id"]
            tech = tech_tree.get_technology(tech_id)
            if tech is None:
                continue
            tech.research_progress = tech_data.get("research_progress", 0)
            tech.researched = tech_data.get("researched", False)

        tech_tree.unlocked_techs = [t for t in data.get("unlocked_techs", [])
                                    if t in tech_tree.technologies]
        cur = data.get("current_research")
        if cur and cur in tech_tree.technologies and not tech_tree.technologies[cur].researched:
            tech_tree.current_research = tech_tree.technologies[cur]
        return tech_tree