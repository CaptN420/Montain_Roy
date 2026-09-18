"""
Mountain_Roy - Factions (Système de factions)
4 factions jouables: Humains, Elfes, Nains, Orcs

SYSTÈME 100% DATA-DRIVEN : pour ajouter une 5e faction, il suffit
d'ajouter une entrée dans FACTION_DATA et éventuellement de nouvelles
unités/bâtiments dans entities/.

Chaque faction définit:
    - unit_roster  : les types d'unités produisibles (base + uniques)
    - unit_costs   : coût par unité
    - buildings    : les bâtiments constructibles
    - building_costs : coût par bâtiment
    - techs        : technologies accessibles
    - modifiers    : modificateurs de stats unités/bâtiments
    - worker_bonus : bonus de récolte
    - special_ability : capacité spéciale unique
    - forces/faiblesses
"""

# ============================================================
# COÛTS DE BASE (réutilisés par toutes les factions)
# ============================================================

BASE_UNIT_COSTS = {
    "worker":      {"gold": 30,  "wood": 15, "food": 5,  "time": 2.0},
    "builder":     {"gold": 40,  "wood": 20, "food": 5,  "time": 2.5},
    "warrior":     {"gold": 50,  "wood": 0,  "food": 10, "time": 5.0},
    "archer":      {"gold": 40,  "wood": 20, "food": 5,  "time": 6.0},
    "knight":      {"gold": 100, "wood": 50, "food": 20, "time": 10.0},
    "mage":        {"gold": 80,  "wood": 40, "food": 10, "time": 8.0},
    "healer":      {"gold": 60,  "wood": 30, "food": 10, "time": 7.0},
    "scout":       {"gold": 30,  "wood": 10, "food": 0,  "time": 4.0},
    "siege_engine": {"gold": 150, "wood": 100, "food": 30, "time": 15.0},
    # Unités uniques par faction
    "berserker":   {"gold": 90,  "wood": 40, "food": 25, "time": 6.0},
    "ranger":      {"gold": 60,  "wood": 40, "food": 10, "time": 6.0},
    "cannon":      {"gold": 180, "wood": 120, "food": 20, "time": 12.0},
}

BASE_BUILDING_COSTS = {
    "farm":         {"gold": 50,  "wood": 100, "food": 0,  "time": 5.0},
    "barracks":     {"gold": 200, "wood": 150, "food": 50, "time": 10.0},
    "lumber_mill":  {"gold": 100, "wood": 50,  "food": 0,  "time": 8.0},
    "tower":        {"gold": 150, "wood": 100, "food": 0,  "time": 7.0},
    "mine":         {"gold": 300, "wood": 200, "food": 0,  "time": 12.0},
    "temple":       {"gold": 250, "wood": 150, "food": 100, "time": 15.0},
    "workshop":     {"gold": 180, "wood": 120, "food": 30, "time": 9.0},
    "academy":      {"gold": 350, "wood": 250, "food": 100, "time": 18.0},
    "dock":         {"gold": 400, "wood": 300, "food": 0,  "time": 20.0},
    "wall":         {"gold": 30,  "wood": 50,  "food": 0,  "time": 3.0},
    "collection":   {"gold": 100, "wood": 80,  "food": 0,  "time": 6.0},
    # Bâtiments uniques par faction
    "human_barracks":  {"gold": 220, "wood": 160, "food": 40, "time": 9.0},
    "orc_war_hut":     {"gold": 160, "wood": 130, "food": 40, "time": 8.0},
    "elf_ranger_lodge": {"gold": 130, "wood": 100, "food": 20, "time": 8.0},
    "dwarf_forge":     {"gold": 240, "wood": 160, "food": 30, "time": 11.0},
}

# Rôle / nom / icône de chaque bâtiment pour le menu de construction
BUILDING_INFO = {
    "town_hall":       ("Hôtel de Ville", "caserne", "Bâtiment principal"),
    "collection":      ("Bâtiment de récolte", "economie", "Dépôt des ressources"),
    "farm":            ("Ferme", "economie", "Nourriture et population"),
    "lumber_mill":     ("Scierie", "economie", "Production de bois"),
    "mine":            ("Mine", "economie", "Production d'or"),
    "barracks":        ("Caserne", "troupes", "Unités de combat"),
    "human_barracks":  ("Caserne Humaine", "troupes", "Unités humaines"),
    "orc_war_hut":     ("Tanière de Guerre", "troupes", "Unités orques"),
    "elf_ranger_lodge":("Abri de Rangers", "troupes", "Unités elfes"),
    "dwarf_forge":     ("Forge Naine", "troupes", "Unités naines"),
    "workshop":        ("Atelier", "troupes", "Unités spécialisées + artillerie"),
    "dock":            ("Quai", "navale", "Unités navales"),
    "temple":          ("Temple", "recherche", "Recherche / magie"),
    "academy":         ("Académie", "recherche", "Recherche de technologies"),
    "tower":           ("Tour", "defense", "Défense"),
    "wall":            ("Mur", "defense", "Protection"),
}

BUILDING_CATEGORIES = {
    "economie":  "Économie",
    "troupes":   "Caserne & Troupes",
    "navale":    "Navale",
    "recherche": "Recherche",
    "defense":   "Défense",
}

# Technologies communes à toutes les factions
BASE_TECHS = [
    "iron_working", "archery", "heavy_armor", "magic_study",
    "mining", "logging", "agriculture", "fortification",
    "siege_weapons", "hero_training", "ultimate_skill",
]


class Faction:
    """Classe de configuration d'une faction."""

    def __init__(self, data: dict):
        self.faction_id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.color = data["color"]
        self.starting_resources = data["starting_resources"]
        self.worker_bonus = data["worker_bonus"]
        self.unit_roster = data["unit_roster"]      # list[str]
        self.unit_costs = data["unit_costs"]        # dict[type] -> cost
        self.buildings = data["buildings"]           # list[str]
        self.building_costs = data["building_costs"] # dict[type] -> cost
        # Bâtiment de production principal (remplace la caserne de départ)
        self.primary_war_building = data.get("primary_war_building", "barracks")
        self.techs = data["techs"]                   # list[str]
        self.modifiers = data.get("modifiers", {})   # dict[type] -> dict mods
        self.building_bonuses = data.get("building_bonuses", {})
        # Mapping unit -> bâtiment produisant cette unité
        self.unit_building = data.get("unit_building", {})
        # Prérequis: unit -> {"building": X, "tech": Y}
        self.unit_prereq = data.get("unit_prereq", {})
        # Bâtiments de recherche (académie ou équivalent)
        self.research_buildings = data.get("research_buildings", ["academy"])
        self.special_ability = data["special_ability"]
        self.strength = data["strength"]
        self.weakness = data["weakness"]

    # ---- Helpers pour la production/construction ----

    def get_unit_cost(self, unit_type: str) -> dict:
        """Retourne le coût d'une unité pour cette faction."""
        return self.unit_costs.get(unit_type, BASE_UNIT_COSTS.get(unit_type, {}))

    def get_building_cost(self, building_type: str) -> dict:
        """Retourne le coût d'un bâtiment pour cette faction."""
        return self.building_costs.get(building_type, BASE_BUILDING_COSTS.get(building_type, {}))

    def get_units_for_building(self, building_type: str) -> list:
        """Retourne les unités produisibles par ce bâtiment (faction + roster)."""
        result = []
        for utype in self.unit_roster:
            if self.unit_building.get(utype) == building_type:
                result.append(utype)
        return result

    def is_building_production(self, building_type: str) -> bool:
        """Retourne True si ce bâtiment produit des unités (par cette faction)."""
        return any(self.unit_building.get(u) == building_type for u in self.unit_roster)

    def can_produce(self, unit_type: str, buildings: list, researched: list) -> tuple:
        """Vérifie si la faction peut produire cette unité.
        
        Retourne (ok, raison). Raison vide si ok.
        """
        if unit_type not in self.unit_roster:
            return False, "hors répertoire de faction"

        # Prérequis de bâtiment
        req_building = self.unit_prereq.get(unit_type, {}).get("building")
        if req_building:
            own = [b for b in buildings if b.faction == "player"]
            if not any(b.building_type == req_building for b in own):
                return False, f"requiert {req_building}"

        # Prérequis de technologie
        req_tech = self.unit_prereq.get(unit_type, {}).get("tech")
        if req_tech and req_tech not in researched:
            return False, f"requiert recherche '{req_tech}'"

        return True, ""

    def apply_unit_modifiers(self, unit):
        """Applique les modificateurs de faction à une unité."""
        utype = getattr(unit, 'unit_type', '')
        mods = self.modifiers.get(utype, self.modifiers.get('*', {}))
        if 'all' in self.modifiers:
            mods = {**self.modifiers['all'], **mods}
        for attr, value in mods.items():
            if attr in ('max_hp_percent', 'hp_percent'):
                unit.max_hp = int(unit.max_hp * value)
                unit.hp = unit.max_hp
            elif attr == 'damage_percent':
                unit.damage = int(unit.damage * value)
            elif attr == 'speed_percent':
                unit.speed = int(unit.speed * value)
            elif attr == 'attack_speed_percent':
                unit.attack_speed = max(0.3, unit.attack_speed * value)
            elif attr == 'armor':
                unit.armor = getattr(unit, 'armor', 0) + value
            elif attr == 'range_percent':
                unit.range = int(unit.range * value)
            else:
                setattr(unit, attr, value)

    def apply_worker_bonus(self, worker):
        """Applique les bonus de worker."""
        for attr, value in self.worker_bonus.items():
            if hasattr(worker, attr):
                current = getattr(worker, attr)
                if isinstance(current, (int, float)) and isinstance(value, (int, float)):
                    setattr(worker, attr, current + value)
                else:
                    setattr(worker, attr, value)


# ============================================================
# DATA DES 4 FACTIONS
# ============================================================

FACTION_DATA = {
    "human": {
        "id": "human",
        "name": "Humains",
        "description": "Peuple polyvalent et résilient. Excellente production, "
                       "bonnes unités terrestres et économie solide. "
                       "Aucun domaine dominant, mais aucun gros défaut.",
        "color": (100, 149, 237),
        "starting_resources": {"gold": 220, "wood": 170, "food": 120},
        "worker_bonus": {"speed": 5},
        "unit_roster": ["worker", "builder", "warrior", "archer", "knight",
                        "mage", "healer", "scout", "siege_engine", "naval", "boat"],
        "unit_costs": {
            "warrior": {"gold": 50, "wood": 0,  "food": 10, "time": 5.0},
            "archer":  {"gold": 40, "wood": 20, "food": 5,  "time": 6.0},
            "knight":  {"gold": 100, "wood": 50, "food": 20, "time": 10.0},
            "mage":    {"gold": 80, "wood": 40, "food": 10, "time": 8.0},
            "healer":  {"gold": 60, "wood": 30, "food": 10, "time": 7.0},
            "scout":   {"gold": 30, "wood": 10, "food": 0,  "time": 4.0},
        },
        "buildings": ["farm", "barracks", "lumber_mill", "mine", "tower",
                      "temple", "workshop", "academy", "dock", "wall",
                      "collection", "human_barracks"],
        "building_costs": {
            "human_barracks": {"gold": 220, "wood": 160, "food": 40, "time": 9.0},
        },
        "techs": BASE_TECHS + ["gunpowder"],
        "modifiers": {
            "*": {"attack_speed_percent": 0.9},
        },
        "building_bonuses": {
            "*": {"build_time_percent": 0.85},
        },
        "special_ability": {
            "name": "Production Rapide",
            "description": "Les bâtiments et unités se produisent 15% plus vite."
        },
        "primary_war_building": "human_barracks",
        "strength": "Polyvalence et vitesse de production",
        "weakness": "Stats moyennes, rien de dominant",
        "unit_building": {
            "worker": "town_hall", "builder": "town_hall",
            "warrior": "human_barracks", "knight": "human_barracks", "scout": "human_barracks",
            "archer": "human_barracks",
            "mage": "workshop", "healer": "workshop",
            "siege_engine": "workshop",
            "naval": "dock", "boat": "dock",
        },
        "unit_prereq": {
            "knight": {"building": "human_barracks", "tech": "heavy_armor"},
            "mage": {"building": "workshop", "tech": "magic_study"},
            "archer": {"building": "human_barracks", "tech": "archery"},
            "siege_engine": {"building": "workshop", "tech": "gunpowder"},
            "naval": {"building": "dock"},
            "boat": {"building": "dock", "tech": "logging"},
        },
        "research_buildings": ["academy"],
    },

    "orc": {
        "id": "orc",
        "name": "Orcs",
        "description": "Brutes sanguinaires orientées combat rapproché. "
                       "Dégâts massifs et PV élevés, production d'armée rapide. "
                       "Économie simple mais terrifiante en pression agressive.",
        "color": (178, 34, 34),
        "starting_resources": {"gold": 180, "wood": 140, "food": 190},
        "worker_bonus": {"max_carry": -5},
        "unit_roster": ["worker", "builder", "warrior", "berserker",
                        "knight", "scout", "siege_engine"],
        "unit_costs": {
            "warrior":   {"gold": 45, "wood": 0,  "food": 12, "time": 4.0},
            "berserker": {"gold": 85, "wood": 40, "food": 25, "time": 6.0},
            "knight":    {"gold": 90, "wood": 50, "food": 20, "time": 9.0},
            "scout":     {"gold": 25, "wood": 10, "food": 5,  "time": 3.0},
        },
        "buildings": ["farm", "orc_war_hut", "lumber_mill", "mine", "tower",
                      "workshop", "academy", "wall", "collection"],
        "building_costs": {
            "orc_war_hut": {"gold": 150, "wood": 120, "food": 40, "time": 7.0},
        },
        "techs": ["iron_working", "mining", "logging",
                                            "agriculture", "fortification",
                                            "heavy_armor", "siege_weapons",
                                            "orc_warpath"],
        "modifiers": {
            "all": {"damage_percent": 1.25, "max_hp_percent": 1.15},
            "warrior": {"damage_percent": 1.3},
            "archer": {"damage_percent": 0.7},  # orcs n'ont pas d'archers bons
            "mage": {"max_hp_percent": 0.7},
        },
        "building_bonuses": {
            "orc_war_hut": {"build_time_percent": 0.7},
            "barracks": {"cost_percent": 0.8},
        },
        "special_ability": {
            "name": "Furie de Guerre",
            "description": "+25% de dégâts et +15% de PV sur toutes les unités."
        },
        "primary_war_building": "orc_war_hut",
        "strength": "Dégâts/HP énormes, production rapide",
        "weakness": "Pas d'archers/mages efficaces, récolte plus lente",
        "unit_building": {
            "worker": "town_hall", "builder": "town_hall",
            "warrior": "orc_war_hut", "berserker": "orc_war_hut", "scout": "orc_war_hut",
            "knight": "orc_war_hut",
            "siege_engine": "workshop",
        },
        "unit_prereq": {
            "berserker": {"building": "orc_war_hut", "tech": "orc_warpath"},
            "knight": {"building": "orc_war_hut", "tech": "heavy_armor"},
            "siege_engine": {"building": "workshop", "tech": "siege_weapons"},
        },
        "research_buildings": ["academy"],
    },

    "elf": {
        "id": "elf",
        "name": "Elfes",
        "description": "Peuple agile et mystique. Archers et mages puissants, "
                       "unités très mobiles. Fragiles en mêlée mais excellent "
                       "kiting et positionnement tactique.",
        "color": (144, 238, 144),
        "starting_resources": {"gold": 200, "wood": 200, "food": 110},
        "worker_bonus": {"max_carry": 10, "speed": 10},
        "unit_roster": ["worker", "builder", "warrior", "archer", "ranger",
                        "mage", "healer", "scout"],
        "unit_costs": {
            "archer": {"gold": 35, "wood": 20, "food": 5,  "time": 5.0},
            "ranger": {"gold": 60, "wood": 40, "food": 10, "time": 6.0},
            "mage":   {"gold": 75, "wood": 40, "food": 10, "time": 7.0},
            "warrior": {"gold": 50, "wood": 0, "food": 10, "time": 5.0},
            "scout":  {"gold": 25, "wood": 10, "food": 0,  "time": 3.0},
        },
        "buildings": ["farm", "barracks", "elf_ranger_lodge", "lumber_mill",
                      "mine", "tower", "temple", "academy", "dock", "wall",
                      "collection"],
        "building_costs": {
            "elf_ranger_lodge": {"gold": 120, "wood": 100, "food": 20, "time": 7.0},
        },
        "techs": ["iron_working", "archery", "magic_study", "mining", "logging",
                  "agriculture", "fortification", "hero_training",
                  "ultimate_skill", "woodland_craft"],
        "modifiers": {
            "all": {"speed_percent": 1.15},
            "archer": {"damage_percent": 1.35, "range_percent": 1.15},
            "ranger": {"damage_percent": 1.3, "range_percent": 1.2},
            "mage": {"damage_percent": 1.25},
            "warrior": {"max_hp_percent": 0.8},
            "knight": {"max_hp_percent": 0.75},
        },
        "building_bonuses": {
            "elf_ranger_lodge": {"build_time_percent": 0.8},
            "lumber_mill": {"cost_percent": 0.7},
        },
        "special_ability": {
            "name": "Magie des Bois",
            "description": "Archers +35% dégâts et portée, unités rapides."
        },
        "primary_war_building": "elf_ranger_lodge",
        "strength": "Archers/mages très puissants, mobilité",
        "weakness": "Mêlée fragile, PV plus bas",
        "unit_building": {
            "worker": "town_hall", "builder": "town_hall",
            "warrior": "barracks", "scout": "elf_ranger_lodge",
            "archer": "elf_ranger_lodge", "ranger": "elf_ranger_lodge",
            "mage": "workshop", "healer": "workshop",
            "druid": "elf_ranger_lodge",
        },
        "unit_prereq": {
            "ranger": {"building": "elf_ranger_lodge", "tech": "woodland_craft"},
            "druid": {"building": "elf_ranger_lodge", "tech": "magic_study"},
            "archer": {"building": "elf_ranger_lodge", "tech": "archery"},
            "magic": {"building": "workshop", "tech": "magic_study"},
        },
        "research_buildings": ["temple"],
    },

    "dwarf": {
        "id": "dwarf",
        "name": "Nains",
        "description": "Guerriers coriaces des montagnes. Unités lourdement "
                       "blindées, excellentes défenses, artillerie lourde. "
                       "Gameplay lent mais très difficile à déloger.",
        "color": (210, 105, 30),
        "starting_resources": {"gold": 260, "wood": 130, "food": 110},
        "worker_bonus": {"armor": 3},
        "unit_roster": ["worker", "builder", "warrior", "archer", "knight",
                        "healer", "scout", "cannon"],
        "unit_costs": {
            "warrior": {"gold": 50, "wood": 0,  "food": 10, "time": 5.0},
            "knight":  {"gold": 110, "wood": 60, "food": 20, "time": 11.0},
            "cannon":  {"gold": 170, "wood": 120, "food": 20, "time": 12.0},
            "archer":  {"gold": 40, "wood": 20, "food": 5,  "time": 6.0},
            "scout":   {"gold": 30, "wood": 10, "food": 0,  "time": 4.0},
        },
        "buildings": ["farm", "barracks", "dwarf_forge", "lumber_mill", "mine",
                      "tower", "workshop", "academy", "wall", "collection"],
        "building_costs": {
            "dwarf_forge": {"gold": 240, "wood": 160, "food": 30, "time": 11.0},
            "tower": {"gold": 120, "wood": 90, "food": 0, "time": 6.0},
        },
        "techs": ["iron_working", "heavy_armor", "mining", "logging",
                  "agriculture", "fortification", "siege_weapons",
                  "hero_training", "master_armor"],
        "modifiers": {
            "all": {"max_hp_percent": 1.2, "armor": 3, "speed_percent": 0.85},
            "warrior": {"damage_percent": 1.15},
            "knight": {"damage_percent": 1.2, "max_hp_percent": 1.3},
            "cannon": {"damage_percent": 1.2},
            "mage": {"max_hp_percent": 0.8},
        },
        "building_bonuses": {
            "tower": {"cost_percent": 0.8},
            "mine": {"cost_percent": 0.7},
            "wall": {"cost_percent": 0.6},
        },
        "special_ability": {
            "name": "Forge des Montagnes",
            "description": "+20% PV et +3 armure, artillerie et défenses puissantes."
        },
        "primary_war_building": "dwarf_forge",
        "strength": "Blindage/PV énormes, artillerie, défense",
        "weakness": "Lents, magie faible",
        "unit_building": {
            "worker": "town_hall", "builder": "town_hall",
            "warrior": "dwarf_forge", "scout": "dwarf_forge", "healer": "dwarf_forge",
            "knight": "dwarf_forge", "cannon": "dwarf_forge",
            "archer": "barracks",
        },
        "unit_prereq": {
            "knight": {"building": "dwarf_forge", "tech": "heavy_armor"},
            "cannon": {"building": "dwarf_forge", "tech": "master_armor"},
            "archer": {"building": "barracks", "tech": "archery"},
            "scout": {"building": "dwarf_forge"},
            "healer": {"building": "dwarf_forge", "tech": "magic_study"},
        },
        "research_buildings": ["workshop"],
    },
}


# Technologies uniques par faction (définies dans tech_tree.py)
TECH_META = {
    "gunpowder":    {"name": "Poudre à Canon", "cost": {"gold": 300, "wood": 200, "food": 100}},
    "orc_warpath":  {"name": "Sentier de Guerre", "cost": {"gold": 250, "wood": 150, "food": 50}},
    "woodland_craft": {"name": "Art des Bois", "cost": {"gold": 250, "wood": 200, "food": 0}},
    "master_armor": {"name": "Armure de Maître", "cost": {"gold": 400, "wood": 250, "food": 100}},
}


def get_factions():
    """Retourne un dict des factions id -> Faction."""
    return {fid: Faction(data) for fid, data in FACTION_DATA.items()}


def get_faction(faction_id):
    """Retourne une faction par son id."""
    return get_factions().get(faction_id)