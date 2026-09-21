"""
Mountain_Roy - Construction System (Système de construction)
Version améliorée: Workers assignés, progression visuelle
"""

import pygame
import math
from entities.building import TownHall, Barracks, Farm, LumberMill, Mine, Tower, Temple, Workshop, Academy, Dock, Wall, CollectionBuilding, HumanBarracks, OrcWarHut, ElfRangerLodge, DwarfForge, HeroHall


class BuildingProgress:
    """Gère la progression de construction d'un bâtiment."""

    def __init__(self, building_type: str, x: int, y: int, faction: str, build_time: float = 10.0):
        self.building_type = building_type
        self.x = x
        self.y = y
        self.faction = faction
        self.build_time = build_time
        self.elapsed_time = 0.0
        self.progress = 0.0  # 0.0 to 1.0
        self.assigned_workers = []

    def update(self, dt: float):
        """Met à jour la progression."""
        if len(self.assigned_workers) > 0:
            self.elapsed_time += dt
            self.progress = min(1.0, self.elapsed_time / self.build_time)

    def is_complete(self) -> bool:
        return self.progress >= 1.0

    def draw(self, screen, camera_x: float, camera_y: float):
        """Dessine la progression de construction."""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Dessiner le bâtiment en construction (translucide)
        alpha = 128
        color = (100, 100, 100) if self.faction == "player" else (150, 50, 50)
        pygame.draw.rect(screen, color, (screen_x - 32, screen_y - 32, 64, 64), border_radius=8)

        # Barre de progression
        bar_width = 64
        bar_height = 8
        pygame.draw.rect(screen, (50, 50, 50), (screen_x - bar_width // 2, screen_y + 40, bar_width, bar_height), border_radius=4)
        pygame.draw.rect(screen, (0, 255, 0), (screen_x - bar_width // 2, screen_y + 40, int(bar_width * self.progress), bar_height), border_radius=4)

        # Indicateur de workers
        if self.assigned_workers:
            font = pygame.font.Font(None, 16)
            text = font.render(f"Workers: {len(self.assigned_workers)}", True, (255, 255, 255))
            screen.blit(text, (screen_x - 40, screen_y + 52))

    @classmethod
    def from_data(cls, data: dict) -> "BuildingProgress":
        """Crée un site de construction depuis un dict de sauvegarde."""
        progress = cls(data["building_type"], data["x"], data["y"],
                       data.get("faction", "player"), data.get("build_time", 10.0))
        progress.elapsed_time = data.get("elapsed_time", 0.0)
        progress.progress = min(1.0, progress.elapsed_time / progress.build_time) if progress.build_time else 0.0
        return progress


class ConstructionSystem:
    """Gère la construction de bâtiments."""

    # Coûts et temps de construction
    # Coûts et temps de construction (workers peuvent être produits)
    WORKER_COSTS = {
        "worker": {"gold": 30, "wood": 15, "food": 5, "time": 2.0},
        "builder": {"gold": 40, "wood": 20, "food": 5, "time": 2.5},
    }

    BUILDING_COSTS = {
        "farm": {"gold": 50, "wood": 100, "food": 0, "time": 5.0},
        "barracks": {"gold": 200, "wood": 150, "food": 50, "time": 10.0},
        "lumber_mill": {"gold": 100, "wood": 50, "food": 0, "time": 8.0},
        "tower": {"gold": 150, "wood": 100, "food": 0, "time": 7.0},
        "mine": {"gold": 300, "wood": 200, "food": 0, "time": 12.0},
        "temple": {"gold": 250, "wood": 150, "food": 100, "time": 15.0},
        "workshop": {"gold": 180, "wood": 120, "food": 30, "time": 9.0},
        "academy": {"gold": 350, "wood": 250, "food": 100, "time": 18.0},
        "dock": {"gold": 400, "wood": 300, "food": 0, "time": 20.0},
        "wall": {"gold": 30, "wood": 50, "food": 0, "time": 3.0},
        "collection": {"gold": 100, "wood": 80, "food": 0, "time": 6.0},  # Cabane de récolte
    }

    def __init__(self, economy, units: list, buildings: list):
        self.economy = economy
        self.units = units
        self.buildings = buildings
        self.construction_sites = []  # Liste des BuildingProgress
        self.selected_building_type = None
        self.preview_position = None
        # Bonus de faction: dict type -> {"cost_percent": x, "time_percent": y}
        self.faction_bonuses = {}
        # Rosters de faction (None = tout disponible)
        self._faction = None
        self._available_buildings = None  # list[str] ou None

    def set_faction(self, faction):
        """Configure le système pour une faction donnée (rosters + coûts)."""
        from systems.factions import BASE_BUILDING_COSTS
        self._faction = faction
        if faction:
            self._available_buildings = faction.buildings
            # Fusionner les coûts de bâtiments de la faction avec la base
            merged = dict(BASE_BUILDING_COSTS)
            for btype, cost in faction.building_costs.items():
                merged[btype] = cost
            self.BUILDING_COSTS = merged

    # Largeur (px) des bâtiments pour la détection de chevauchement
    _BUILDING_FOOTPRINT = {
        "farm": 48, "barracks": 48, "lumber_mill": 48, "tower": 48, "mine": 48,
        "temple": 48, "workshop": 48, "academy": 48, "dock": 48,
        "human_barracks": 48, "orc_war_hut": 48, "elf_ranger_lodge": 48,
        "dwarf_forge": 48, "wall": 32, "collection": 48, "town_hall": 64,
        "hero_hall": 48,
    }

    def validate_build_position(self, building_type: str, x: int, y: int) -> tuple:
        """Valide la position d'un bâtiment.

        Retourne (ok: bool, raison: str). Raison vide si ok.
        Refuse: hors carte, terrain non constructible, bâtiment existant,
        chantier existant, ressource, unité, superposition.
        """
        # 1) Dans la carte
        map_ = getattr(self, '_game_map', None)
        if map_ is None:
            return True, ""  # pas de carte: on ne peut pas valider le terrain
        tile_x = int(x / 32)
        tile_y = int(y / 32)
        tile = map_.get_tile(tile_x, tile_y)
        if tile is None:
            return False, "Hors de la carte"

        # 2) Terrain constructible (herbe ou chemin)
        from map.tile import TileType
        if tile.tile_type not in (TileType.GRASS, TileType.PATH):
            label = tile.tile_type.value
            return False, f"Terrain non constructible ({label})"

        # 3) Chevauchement avec bâtiment existant
        footprint = self._BUILDING_FOOTPRINT.get(building_type, 48)
        for b in self.buildings:
            d = ((b.x - x) ** 2 + (b.y - y) ** 2) ** 0.5
            if d < footprint:
                return False, "Un bâtiment est déjà là"

        # 4) Chevauchement avec chantier existant
        for s in self.construction_sites:
            d = ((s.x - x) ** 2 + (s.y - y) ** 2) ** 0.5
            if d < footprint:
                return False, "Un chantier est déjà là"

        # 5) Chevauchement avec une ressource
        for node in getattr(self, '_all_nodes', []):
            if getattr(node, 'is_depleted', lambda: False)():
                continue
            d = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
            if d < footprint:
                return False, "Une ressource est déjà là"

        # 6) Chevauchement avec une unité
        for u in self.units:
            d = ((u.x - x) ** 2 + (u.y - y) ** 2) ** 0.5
            if d < footprint // 2:
                return False, "Une unité est déjà là"

        return True, ""

    def can_build(self, building_type: str, x: int, y: int) -> bool:
        """Vérifie si on peut construire un bâtiment (validité position + coûts)."""
        if building_type not in self.BUILDING_COSTS:
            return False

        ok, _ = self.validate_build_position(building_type, x, y)
        if not ok:
            return False

        # Vérifier le coût
        cost, _ = self._adjusted_cost("building", building_type)
        return self.economy.can_afford(cost)

    def start_construction(self, building_type: str, x: int, y: int) -> bool:
        """Commence la construction d'un bâtiment."""
        if building_type not in self.BUILDING_COSTS:
            return False
        # Vérifier que la faction peut construire ce bâtiment
        if self._available_buildings is not None and building_type not in self._available_buildings:
            return False
        # Valider la position (hors carte, terrain, superposition)
        ok, reason = self.validate_build_position(building_type, x, y)
        if not ok:
            print(f"Cannot build {building_type}: {reason}")
            return False

        cost, time_bonus = self._adjusted_cost("building", building_type)

        # Vérifier les ressources
        if not self.economy.can_afford(cost):
            return False

        # Payer le coût
        self.economy.pay_cost(cost)

        # Créer le site de construction
        base_time = self.BUILDING_COSTS[building_type]["time"]
        build_time = base_time * time_bonus
        progress = BuildingProgress(building_type, x, y, "player", build_time)
        self.construction_sites.append(progress)

        # Assigner automatiquement un worker si disponible
        self._assign_worker_to_construction(progress)

        return True

    def _adjusted_cost(self, kind: str, name: str):
        """Retourne le coût, time_bonus ajustés par les bonus de faction.
        
        kind: "building" ou "unit" ou "worker".
        Renvoie (cout_ajuste, bonus_temps_mult).
        """
        source = self.BUILDING_COSTS if kind == "building" else self.WORKER_COSTS if kind == "worker" else self.UNIT_COSTS
        base_cost = source[name]
        cost = dict(base_cost)

        # Bonus faction (spécifique d'abord, puis "*")
        bonus = self.faction_bonuses.get(name, self.faction_bonuses.get('*', {}))
        cost_percent = bonus.get('cost_percent', 1.0)
        time_percent = bonus.get('time_percent', 1.0)

        for key in ("gold", "wood", "food"):
            if key in cost:
                cost[key] = int(cost[key] * cost_percent)
        return cost, time_percent

    def _assign_worker_to_construction(self, progress: BuildingProgress):
        """Assigne un builder (ou worker) disponible au chantier de construction."""
        candidates = [u for u in self.units
                      if (hasattr(u, 'unit_type') and u.unit_type in ["builder", "worker"])
                      and getattr(u, 'construction_target', None) is None]
        # Prioriser les builders (qui ne récoltent pas automatiquement), puis les workers
        builders = [u for u in candidates if u.unit_type == "builder"]
        workers = [u for u in candidates if u.unit_type == "worker"]
        # Pour les builders : les prendre même s'ils récoltent
        ordered = builders + workers
        for unit in ordered:
            unit.construction_target = progress
            unit.target_resource = None  # Neutraliser la récolte pour la construction
            unit.carrying = False
            unit.carry_amount = 0
            progress.assigned_workers.append(unit)
            return True
        return False

    def update(self, dt: float):
        """Met à jour tous les sites de construction."""
        for site in self.construction_sites[:]:
            site.update(dt)

            # Si construction terminée, créer le bâtiment
            if site.is_complete():
                building = self._create_building(site.building_type, site.x, site.y, site.faction)
                if building:
                    self.buildings.append(building)

                # Libérer les workers assignés
                for worker in site.assigned_workers[:]:
                    if hasattr(worker, 'construction_target'):
                        delattr(worker, 'construction_target')
                    # Le worker retourne à sa récolte automatique

                # Retirer le site
                self.construction_sites.remove(site)

    def _create_building(self, building_type: str, x: int, y: int, faction: str):
        """Crée le bâtiment après construction."""
        buildings = {
            "town_hall": TownHall,
            "barracks": Barracks,
            "farm": Farm,
            "lumber_mill": LumberMill,
            "mine": Mine,
            "tower": Tower,
            "temple": Temple,
            "workshop": Workshop,
            "academy": Academy,
            "dock": Dock,
            "wall": Wall,
            "collection": CollectionBuilding,
            # Bâtiments uniques par faction
            "human_barracks": HumanBarracks,
            "orc_war_hut": OrcWarHut,
            "elf_ranger_lodge": ElfRangerLodge,
            "dwarf_forge": DwarfForge,
            "hero_hall": HeroHall,
        }

        if building_type in buildings:
            b = buildings[building_type](x, y, faction)
            # Appliquer la couleur de faction si elle est définie
            if self._faction is not None:
                b.faction_color = self._faction.color
            return b
        return None

    def get_available_buildings(self) -> list:
        """Retourne la liste des bâtiments constructibles (filtrés par faction)."""
        keys = list(self.BUILDING_COSTS.keys())
        if self._available_buildings is not None:
            keys = [k for k in keys if k in self._available_buildings]
        return keys

    def get_worker_costs(self) -> dict:
        """Retourne les coûts de production des workers."""
        return self.WORKER_COSTS

    def _create_site_from_data(self, data: dict):
        """Recrée un site de construction depuis un dict de sauvegarde."""
        from systems.construction import BuildingProgress as BP
        progress = BP.from_data(data)
        return progress

    def produce_worker(self, worker_type: str, x: int, y: int, game=None) -> bool:
        """Produit un worker (ouvrier ou builder).

        `game` : référence à l'objet Game (nécessaire pour la récolte/le dépôt).
        """
        if worker_type not in self.WORKER_COSTS:
            return False

        cost, _ = self._adjusted_cost("worker", worker_type)

        # Vérifier les ressources
        if not self.economy.can_afford(cost):
            return False

        # Payer le coût
        self.economy.pay_cost(cost)

        # Créer le worker
        from entities.worker import Worker
        from entities.unit_types import Builder

        if worker_type == "worker":
            unit = Worker(x, y, "player")
        else:  # builder
            unit = Builder(x, y, "player")

        # Assigner la référence au jeu (objet Game, pas l'économie!)
        # Le worker a besoin de resource_nodes, buildings, economy, enemy_economy
        if game is not None:
            unit.game = game
        else:
            # Fallback: trouver le Game via la liste units (owner) - dernier recours
            unit.game = getattr(self, '_game_ref', None)

        # Ajouter à la liste des unités
        self.units.append(unit)

        return True

    def set_game(self, game):
        """Stocke la référence au Game pour les workers produits et la validation terrain."""
        self._game_ref = game
        if game is not None:
            self._game_map = getattr(game, 'game_map', None)
            self._all_buildings = list(getattr(game, 'buildings', []))
            self._all_units = list(getattr(game, 'units', []))
            self._all_nodes = list(getattr(game, 'resource_nodes', []))

    def get_building_cost(self, building_type: str) -> dict:
        """Retourne le coût d'un bâtiment."""
        return self.BUILDING_COSTS.get(building_type, {})


class ProductionSystem:
    """Gère la production d'unités."""

    UNIT_COSTS = {
        "warrior": {"gold": 50, "wood": 0, "food": 10, "time": 5.0},
        "archer": {"gold": 40, "wood": 20, "food": 5, "time": 6.0},
        "knight": {"gold": 100, "wood": 50, "food": 20, "time": 10.0},
        "mage": {"gold": 80, "wood": 40, "food": 10, "time": 8.0},
        "healer": {"gold": 60, "wood": 30, "food": 10, "time": 7.0},
        "scout": {"gold": 30, "wood": 10, "food": 0, "time": 4.0},
    }

    def __init__(self, economy, units: list):
        self.economy = economy
        self.units = units
        self.production_queue = []
        # File de production (progression par unité, FIFO)
        self.queue = []
        # Bonus de faction: dict type -> {"cost_percent": x}
        self.faction_bonuses = {}
        # Roster de faction (None = tout disponible)
        self._faction = None
        self._available_units = None  # list[str] ou None

    def set_faction(self, faction):
        """Configure le système pour une faction donnée (rosters + coûts)."""
        from systems.factions import BASE_UNIT_COSTS
        self._faction = faction
        if faction:
            self._available_units = faction.unit_roster
            merged = dict(BASE_UNIT_COSTS)
            for utype, cost in faction.unit_costs.items():
                merged[utype] = cost
            self.UNIT_COSTS = merged

    def can_produce(self, unit_type: str) -> bool:
        """Vérifie si on peut produire une unité."""
        if unit_type not in self.UNIT_COSTS:
            return False
        cost = self.UNIT_COSTS[unit_type]
        return self.economy.can_afford(cost)

    def produce(self, unit_type: str, x: int, y: int) -> bool:
        """Produit une unité."""
        if unit_type not in self.UNIT_COSTS:
            return False
        # Vérifier que la faction peut produire cette unité
        if self._available_units is not None and unit_type not in self._available_units:
            return False

        # Appliquer les bonus de faction (coût réduit)
        cost = dict(self.UNIT_COSTS[unit_type])
        bonus = self.faction_bonuses.get(unit_type, self.faction_bonuses.get('*', {}))
        cost_percent = bonus.get('cost_percent', 1.0)
        for key in ("gold", "wood", "food"):
            if key in cost:
                cost[key] = int(cost[key] * cost_percent)

        # Payer le coût
        if not self.economy.can_afford(cost):
            return False

        self.economy.pay_cost(cost)

        # Créer l'unité (à implémenter selon unit_types)
        from entities.unit_types import create_unit
        unit = create_unit(unit_type, x, y, "player")
        if unit:
            self.units.append(unit)
            return True

        return False

    def get_available_units(self) -> list:
        """Retourne la liste des unités produisibles (filtrés par faction)."""
        keys = list(self.UNIT_COSTS.keys())
        if self._available_units is not None:
            keys = [k for k in keys if k in self._available_units]
        return keys

    def enqueue(self, unit_type: str, x: int, y: int) -> bool:
        """Met une unité en file de production (débite le coût à la saisie).

        L'unité n'apparaît qu'une fois la progression terminée (voir update()).
        Retourne False si impossible (type inconnu / roster / ressources).
        """
        if unit_type not in self.UNIT_COSTS:
            return False
        if self._available_units is not None and unit_type not in self._available_units:
            return False

        # Bonus de faction (coût ajusté), cohérent avec produce()
        cost = dict(self.UNIT_COSTS[unit_type])
        bonus = self.faction_bonuses.get(unit_type, self.faction_bonuses.get('*', {}))
        cost_percent = bonus.get('cost_percent', 1.0)
        for key in ("gold", "wood", "food"):
            if key in cost:
                cost[key] = int(cost[key] * cost_percent)

        if not self.economy.can_afford(cost):
            return False

        self.economy.pay_cost(cost)
        self.queue.append({
            "unit_type": unit_type,
            "x": x,
            "y": y,
            "total": self.UNIT_COSTS[unit_type].get("time", 5.0),
            "progress": 0.0,
        })
        return True

    def update(self, dt: float) -> list:
        """Fait progresser la file de production (FIFO).

        Retourne la liste des unités nouvellement créées pendant ce tick.
        """
        spawned = []
        if not self.queue:
            return spawned
        head = self.queue[0]
        head["progress"] += dt
        if head["progress"] >= head["total"]:
            self.queue.pop(0)
            from entities.unit_types import create_unit
            unit = create_unit(head["unit_type"], head["x"], head["y"], "player")
            if unit:
                self.units.append(unit)
                spawned.append(unit)
        return spawned
