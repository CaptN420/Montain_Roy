"""
Mountain_Roy - Core Game Engine (Version Optimisée)
Étape 11 & 12: Optimisation, Sons et Effets Visuels
"""

import pygame
import sys
import json
import os
import math
import random
import time
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from core.camera import Camera
from map.game_map import GameMap
from entities.unit_types import create_unit
from entities.hero import Hero
from entities.building import TownHall, DropOffPoint, CollectionBuilding
from entities.worker import Worker
from systems.pathfinding import Pathfinder
from systems.movement import MovementSystem
from systems.combat import CombatSystem
from systems.economy import EconomySystem
from systems.construction import ConstructionSystem, ProductionSystem
from systems.fog_of_war import FogOfWar
from systems.ai import EnemyAI
from core.save_system import SaveSystem, LoadError
from systems.campaign import Campaign, create_default_campaign, MissionStatus
from systems.effects import VisualEffects, ParticleSystem
from systems.audio import AudioManager, AudioEvents
from systems.formation import FormationManager
from systems.tech_tree import TechTree
from ui.hud import HUD
from ui.menus import MainMenu, FactionMenu, PauseMenu, VictoryScreen, DefeatScreen
from systems.factions import get_factions

# Bâtiments capables de produire des unités (y compris les bâtiments uniques de faction)
PRODUCTION_BUILDINGS = ["barracks", "workshop", "human_barracks", "orc_war_hut",
                        "elf_ranger_lodge", "dwarf_forge"]


class Game:
    """Main game class handling the game loop and state."""
    
    def __init__(self):
        pygame.init()
        # Use existing display surface if available, otherwise create new one
        self.screen = pygame.display.get_surface() or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mountain_Roy - RTS")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = "menu"
        self.faction_id = "human"  # Faction choisie par le joueur (défaut humain)
        self.faction = None        # Objet Faction (sera appliqué au démarrage)
        
        # Economy
        self.economy = EconomySystem()
        # Économie séparée pour l'ennemi (ne doit PAS partager le pool du joueur)
        self.enemy_economy = EconomySystem()
        self.enemy_economy.gold = 200
        self.enemy_economy.wood = 150
        self.enemy_economy.food = 100
        self.construction_system = None  # Will be initialized after entities exist
        self.production_system = None  # Will be initialized after entities exist

        # Entities
        self.units = []
        self.buildings = []
        self.hero = None
        
        # Map and Camera
        self.game_map = GameMap()
        self.camera = Camera(MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
        
        # Systems
        self.pathfinder = Pathfinder(self.game_map)
        self.movement_system = MovementSystem(self.game_map, self.pathfinder)
        self.combat_system = CombatSystem()
        self.fog_of_war = FogOfWar(MAP_WIDTH, MAP_HEIGHT)
        self.ai = EnemyAI(self)
        
        # Collision system (prevent stacking)
        from systems.collision import CollisionSystem
        self.collision_system = CollisionSystem()
        
        # Save system
        self.save_system = SaveSystem()
        
        # Campaign
        self.campaign = create_default_campaign()
        self.current_mission = None
        
        # Effects
        self.visual_effects = VisualEffects()
        self.audio_manager = AudioManager()
        self.audio_events = AudioEvents(self.audio_manager)
        
        # Formations
        self.formation_manager = FormationManager()
        
        # Tech tree
        self.tech_tree = TechTree()
        
        # Selection
        self.selected_units = []
        self.selection_box = None
        
        # Box selection state
        self._mouse_down = False
        self._selection_start = None  # (map_x, map_y)

        # Selected building for interaction
        self._selected_building = None
        
        # Resource nodes
        self.resource_nodes = []
        self.drop_off_points = []  # Points de dépôt pour les ressources
        self._generate_resource_nodes()
        
        # Set collision system resource nodes
        self.collision_system.resource_nodes = self.resource_nodes
        self.collision_system.game_map = self.game_map
        
        # UI
        self.hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.main_menu = MainMenu()
        self.faction_menu = FactionMenu()
        self.pause_menu = PauseMenu()
        self.victory_screen = VictoryScreen()
        self.defeat_screen = DefeatScreen()
        
        # Stats
        self.stats = {
            "enemies_killed": 0,
            "units_produced": 0,
            "buildings_built": 0,
            "time_survived": 0,
        }
        self.mission_timer = 0

        # Accélération du temps (fast-forward) : 1/2/4/8/16
        self.TIME_SCALES = (1, 2, 4, 8, 16)
        self.time_scale = 1  # index 0 de TIME_SCALES
        
        # Initialize game entities
        self._initialize_entities()

        # Initialize construction and production systems (after entities exist)
        self.construction_system = ConstructionSystem(self.economy, self.units, self.buildings)
        self.production_system = ProductionSystem(self.economy, self.units)
        # Le système de construction a besoin de la référence Game pour produire des workers
        self.construction_system.set_game(self)

        # Selection and construction state
        self.selected_building_type = None
        self.construction_preview_pos = None
        # Menu de construction (ouvert/fermé)
        self.build_menu_open = False

        # Messages UI (raisons / tutoriel) avec durée de vie
        self.ui_message = None
        self.ui_message_color = (255, 255, 255)
        self.ui_message_timer = 0.0

        # Tutoriel contextuel (n'apparaît qu'une fois par type)
        self.tutorial_shown = {}
        self._last_player_building_count = len(
            [b for b in self.buildings if b.faction == "player"])
        self._last_working_gatherers = 0
    
    def _generate_resource_nodes(self):
        """Génère les noeuds de ressources en clusters près des bases."""
        random.seed(int(time.time()) % 10000)

        from entities.resource_node import ResourceNode as EconomyResourceNode

        # Zone de génération étendue pour l'exploration
        explore_min_x, explore_max_x = 50 * TILE_SIZE, (MAP_WIDTH - 10) * TILE_SIZE
        explore_min_y, explore_max_y = 50 * TILE_SIZE, (MAP_HEIGHT - 10) * TILE_SIZE

        # === CLUSTER PRÈS DE LA BASE JOUEUR ===
        player_base_x = 32 * TILE_SIZE
        player_base_y = 64 * TILE_SIZE

        # Mines d'or proches (rayon 250px) - pour construire des mines
        for i in range(10):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(100, 250)
            x = player_base_x + math.cos(angle) * dist
            y = player_base_y + math.sin(angle) * dist
            # S'assurer que c'est dans les bornes
            x = max(explore_min_x, min(explore_max_x, x))
            y = max(explore_min_y, min(explore_max_y, y))
            gold_node = EconomyResourceNode(x, y, 'gold', 800)
            self.resource_nodes.append(gold_node)

        # Forêts proches (rayon 350px) - pour construire des scieries
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(150, 350)
            x = player_base_x + math.cos(angle) * dist
            y = player_base_y + math.sin(angle) * dist
            x = max(explore_min_x, min(explore_max_x, x))
            y = max(explore_min_y, min(explore_max_y, y))
            wood_node = EconomyResourceNode(x, y, 'wood', 150)
            self.resource_nodes.append(wood_node)

        # Fermes proches (rayon 400px) - pour la nourriture
        for i in range(8):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(200, 400)
            x = player_base_x + math.cos(angle) * dist
            y = player_base_y + math.sin(angle) * dist
            x = max(explore_min_x, min(explore_max_x, x))
            y = max(explore_min_y, min(explore_max_y, y))
            food_node = EconomyResourceNode(x, y, 'food', 150)
            self.resource_nodes.append(food_node)

        # === RESSOURCES LOINTAINES POUR L'EXPLORATION ===
        # Mines d'or lointaines (rayon 600-1000px)
        for i in range(15):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(600, 1000)
            x = player_base_x + math.cos(angle) * dist
            y = player_base_y + math.sin(angle) * dist
            x = max(explore_min_x, min(explore_max_x, x))
            y = max(explore_min_y, min(explore_max_y, y))
            gold_node = EconomyResourceNode(x, y, 'gold', 800)
            self.resource_nodes.append(gold_node)

        # Forêts lointaines
        for i in range(30):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(500, 900)
            x = player_base_x + math.cos(angle) * dist
            y = player_base_y + math.sin(angle) * dist
            x = max(explore_min_x, min(explore_max_x, x))
            y = max(explore_min_y, min(explore_max_y, y))
            wood_node = EconomyResourceNode(x, y, 'wood', 150)
            self.resource_nodes.append(wood_node)

        # Points de dépôt pour chaque base (aléatoires mais proches des bords)
        # NOTE: Ces points sont maintenant remplacés par des CollectionBuildings construits par le joueur
        player_drop_x = random.randint(50 * TILE_SIZE, 150 * TILE_SIZE)
        player_drop_y = random.randint(50 * TILE_SIZE, 150 * TILE_SIZE)
        enemy_drop_x = random.randint((MAP_WIDTH - 150) * TILE_SIZE, (MAP_WIDTH - 50) * TILE_SIZE)
        enemy_drop_y = random.randint(50 * TILE_SIZE, 150 * TILE_SIZE)

        from entities.building import DropOffPoint as DropClass
        player_drop = DropClass(player_drop_x, player_drop_y, "player")
        enemy_drop = DropClass(enemy_drop_x, enemy_drop_y, "enemy")
        self.drop_off_points = [player_drop, enemy_drop]

    @staticmethod
    def _sin(x: float) -> float:
        """Helper for trigonometry."""
        import math
        return math.sin(x)

    @staticmethod
    def _cos(x: float) -> float:
        """Helper for trigonometry."""
        import math
        return math.cos(x)

    def _initialize_entities(self):
        """Initialise les entités de départ."""
        # Base joueur (côté gauche) - Style Warcraft
        player_base_x = 32 * TILE_SIZE  # x = 1024
        player_base_y = 64 * TILE_SIZE  # y = 2048

        # Town Hall (Château)
        town_hall_player = TownHall(player_base_x, player_base_y, "player")
        self.buildings.append(town_hall_player)

        # Barracks (Casernes) - pour produire des unités terrestres
        barracks_player = __import__('entities.building', fromlist=['Barracks']).Barracks(
            player_base_x + 80, player_base_y, "player"
        )
        self.buildings.append(barracks_player)

        # 3 Farms (Ferme) - pour la population
        for i in range(3):
            farm = __import__('entities.building', fromlist=['Farm']).Farm(
                player_base_x - 60 + i * 50, player_base_y + 40, "player"
            )
            self.buildings.append(farm)

        # 4 Workers joueurs (scouts qui vont automatiquement récolter)
        for i in range(4):
            worker = Worker(
                player_base_x + 20 + i * 24,
                player_base_y + 60 + i * 16,
                "player"
            )
            # Assign game reference (drop-off point will be found automatically)
            worker.game = self
            self.units.append(worker)

        # 1 Builder unit for construction - spawns near the village
        builder = __import__('entities.unit_types', fromlist=['Builder']).Builder(
            player_base_x + 160, player_base_y + 20, "player"
        )
        builder.game = self  # Set game reference for worker functionality
        self.units.append(builder)

        # Hero spawns near the village
        from entities.hero import Hero
        hero = Hero(player_base_x - 40, player_base_y + 80, "player")
        self.hero = hero
        self.units.append(hero)

        # Collection Building (Cabane de récolte) - near the village
        collection_player = CollectionBuilding(
            player_base_x + 120, player_base_y - 40, "player"
        )
        self.buildings.append(collection_player)

        # Base ennemie (côté droit) - Même configuration mais plus proche
        enemy_base_x = 96 * TILE_SIZE  # x = 3072 (plus proche!)
        enemy_base_y = 64 * TILE_SIZE  # y = 2048

        town_hall_enemy = TownHall(enemy_base_x, enemy_base_y, "enemy")
        self.buildings.append(town_hall_enemy)

        barracks_enemy = __import__('entities.building', fromlist=['Barracks']).Barracks(
            enemy_base_x - 80, enemy_base_y, "enemy"
        )
        self.buildings.append(barracks_enemy)

        # 3 Farms ennemies
        for i in range(3):
            farm = __import__('entities.building', fromlist=['Farm']).Farm(
                enemy_base_x + 60 + i * 50, enemy_base_y + 40, "enemy"
            )
            self.buildings.append(farm)

        # 4 Workers ennemis
        for i in range(4):
            worker = Worker(
                enemy_base_x - 20 - i * 24,
                enemy_base_y + 60 + i * 16,
                "enemy"
            )
            # Assign game reference (drop-off point will be found automatically)
            worker.game = self
            self.units.append(worker)

        # Collection Building for enemy (near their village)
        collection_enemy = CollectionBuilding(
            enemy_base_x + 120, enemy_base_y - 40, "enemy"
        )
        self.buildings.append(collection_enemy)

        # Positionner la caméra sur la base joueur (visible au démarrage)
        self.camera.x = player_base_x - SCREEN_WIDTH // 2
        self.camera.y = player_base_y - SCREEN_HEIGHT // 2

        # Révéler la zone autour de la base joueur au démarrage
        self.fog_of_war.update(self.units, self.buildings)

    def _auto_gather_resources(self):
        """Fait récolter automatiquement les workers."""
        working = 0
        for unit in self.units[:]:
            # Si l'unité est un worker et n'a pas de target, chercher une ressource
            if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
                # Utiliser la logique du worker pour trouver une ressource
                if not hasattr(unit, 'target_resource') or unit.target_resource is None:
                    unit._find_and_assign_to_resource()
                if getattr(unit, 'target_resource', None) is not None:
                    working += 1
        # Tutoriel récolte (premier worker assigné à une ressource)
        if working > 0 and self._last_working_gatherers == 0:
            self._show_tutorial("gather",
                                "Workers assignés à la récolte ! Ils rapportent or, bois "
                                "et nourriture à la base.")
        self._last_working_gatherers = working
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt * self.time_scale)
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif self.state == "menu":
                action = self.main_menu.handle_event(event)
                if action == "new_game":
                    # Aller au choix de faction d'abord
                    self.state = "faction_select"
                elif action == "load_game":
                    self._show_load_menu()
                elif action == "quit":
                    self.running = False

            elif self.state == "faction_select":
                action = self.faction_menu.handle_event(event)
                if action == "back":
                    self.state = "menu"
                elif action and action in get_factions():
                    self.faction_id = action
                    self._start_campaign()
            
            elif self.state == "load_menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
            
            elif self.state == "mission_screen":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "playing"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
            
            elif self.state == "paused":
                action = self.pause_menu.handle_event(event)
                if action == "resume":
                    self.state = "playing"
                elif action == "save":
                    self._quick_save()
                elif action == "main_menu":
                    self.state = "menu"
            
            elif self.state in ["victory", "defeat"]:
                action = self.victory_screen.handle_event(event) if self.state == "victory" else self.defeat_screen.handle_event(event)
                if action == "main_menu":
                    self.state = "menu"
            
            elif self.state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Échap : sortir du mode construction d'abord
                        if self.build_menu_open:
                            self.build_menu_open = False
                            self.selected_building_type = None
                            self.construction_preview_pos = None
                            print("Mode construction fermé [Échap]")
                        elif self.selected_building_type:
                            # Mode placement d'un bâtiment : annuler le placement
                            self.selected_building_type = None
                            self.construction_preview_pos = None
                            print("Placement annulé [Échap]")
                        elif self._selected_building:
                            # Bâtiment sélectionné : le désélectionner
                            self._deselect_building()
                        else:
                            self.state = "paused"
                    elif event.key == pygame.K_F5:
                        self._quick_save()
                    elif event.key == pygame.K_F9:
                        self._quick_load()
                    
                    # Production depuis le bâtiment sélectionné (touches 1-6)
                    elif event.key == pygame.K_1:
                        self._produce_selected_index(0)
                    elif event.key == pygame.K_2:
                        self._produce_selected_index(1)
                    elif event.key == pygame.K_3:
                        self._produce_selected_index(2)
                    elif event.key == pygame.K_4:
                        self._produce_selected_index(3)
                    elif event.key == pygame.K_5:
                        self._produce_selected_index(4)
                    elif event.key == pygame.K_6:
                        self._produce_selected_index(5)
                    elif event.key == pygame.K_p:
                        self._produce_from_building()

                    # Workers (W = Worker, J = Builder)
                    elif event.key == pygame.K_w:
                        self._produce_worker("worker")
                    elif event.key == pygame.K_j:
                        self._produce_worker("builder")

                    # Construction (B = ouvrir le menu de construction
                    elif event.key == pygame.K_b:
                        # Ouvre le menu de construction (choisir avec la souris)
                        self.build_menu_open = not self.build_menu_open
                        if not self.build_menu_open:
                            self.selected_building_type = None
                        else:
                            self._deselect_building()
                    
                    # Compétences
                    elif event.key == pygame.K_SPACE and self.hero:
                        self.hero.use_skill(0, units=self.units)
                        self.audio_events.on_skill_used(0)
                    
                    # Formations (Touche F pour ouvrir menu)
                    elif event.key == pygame.K_f:
                        self._cycle_formation()
                    
                    # Accélération du temps [G] : 1/2/4/8/16
                    elif event.key == pygame.K_g:
                        self._cycle_time_scale()
                    
                    # Recherche [T]: doit passer par un bâtiment de recherche (académie ou équivalent)
                    elif event.key == pygame.K_t:
                        self._handle_research_key()
                    elif event.key == pygame.K_q and self.hero:
                        self.hero.use_skill(1, units=self.units)
                    elif event.key == pygame.K_e and self.hero:
                        self.hero.use_skill(2, units=self.units)
                
                elif event.type == pygame.MOUSEMOTION:
                    # Update construction preview position
                    if self.selected_building_type:
                        map_x = event.pos[0] + self.camera.x
                        map_y = event.pos[1] + self.camera.y
                        self.construction_preview_pos = (map_x, map_y)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.camera.zoom_in()
                    elif event.button == 5:
                        self.camera.zoom_out()
                    elif event.button == 1:
                        # Start box selection OR place building
                        if self.build_menu_open:
                            # Clic dans le menu de construction : choisir un bâtiment à construire
                            self._handle_build_menu_click(event.pos)
                        elif self.selected_building_type:
                            # Place building instead of selecting
                            map_x = event.pos[0] + self.camera.x
                            map_y = event.pos[1] + self.camera.y
                            self._place_building(map_x, map_y)
                        else:
                            # Cliquer sur un bâtiment joueur (sélection + panneau de production)
                            map_x = event.pos[0] + self.camera.x
                            map_y = event.pos[1] + self.camera.y
                            clicked = self._find_building_at(map_x, map_y, radius=48)
                            if clicked:
                                self._select_building(clicked)
                            else:
                                # Clic sur vide/unité : désélectionner le bâtiment
                                self._deselect_building()
                                # Start box selection
                                self._mouse_down = True
                                self._selection_start = (map_x, map_y)
                                self.selected_units = []
                                for u in self.units:
                                    u.selected = False
                    elif event.button == 3:
                        self._handle_right_click(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self._mouse_down:
                        # Finalize box selection
                        map_x = event.pos[0] + self.camera.x
                        map_y = event.pos[1] + self.camera.y
                        
                        # Calculate box coordinates
                        x1, y1 = self._selection_start
                        x2, y2 = map_x, map_y
                        
                        # If it's a single click (no drag), select the unit at that position
                        if abs(x2 - x1) < 5 and abs(y2 - y1) < 5:
                            # Single click - find unit at this position
                            clicked_unit = None
                            min_distance = 30
                            for unit in self.units:
                                if unit.faction == "player":
                                    dx = unit.x - x1
                                    dy = unit.y - y1
                                    distance = (dx ** 2 + dy ** 2) ** 0.5
                                    if distance < min_distance:
                                        min_distance = distance
                                        clicked_unit = unit
                            
                            if clicked_unit:
                                self.selected_units = [clicked_unit]
                                clicked_unit.selected = True
                        else:
                            # Drag selection - calculate box coordinates
                            box_left = min(x1, x2)
                            box_right = max(x1, x2)
                            box_top = min(y1, y2)
                            box_bottom = max(y1, y2)
                            
                            # Select all player units within the box
                            self.selected_units = []
                            for unit in self.units:
                                if unit.faction == "player":
                                    if box_left <= unit.x <= box_right and box_top <= unit.y <= box_bottom:
                                        unit.selected = True
                                        self.selected_units.append(unit)
                        
                        self._mouse_down = False
                        self._selection_start = None
    
    def _place_building(self, x: int, y: int):
        """Place un bâtiment au clic."""
        if not self.selected_building_type:
            return

        btype = self.selected_building_type
        # Try to build
        if self.construction_system.start_construction(btype, x, y):
            print(f"Construction started: {btype} at ({x}, {y})")
            self._show_ui_message(f"Chantier {btype} lancé !", (0, 255, 0))
            # Clear selection after successful placement
            self.selected_building_type = None
            self.construction_preview_pos = None
        else:
            # Raison précise du blocage (position invalide OU ressources insuffisantes)
            ok, reason = self.construction_system.validate_build_position(btype, x, y)
            if ok:
                cost = self.construction_system.get_building_cost(btype)
                self._show_ui_message(
                    f"Ressources insuffisantes pour {btype} "
                    f"(il faut {cost.get('gold', 0)} or, {cost.get('wood', 0)} bois).",
                    (255, 100, 100))
            else:
                self._show_ui_message(f"Construction impossible: {reason}", (255, 100, 100))
            print(f"Cannot build {btype}: insufficient resources or invalid position")

    def _build_menu_rects(self):
        """Calcule les rectangles des boutons du menu de construction."""
        from systems.factions import BUILDING_CATEGORIES
        available = self.construction_system.get_available_buildings()
        # Grouper par catégorie
        categories = {cat: [] for cat in BUILDING_CATEGORIES}
        for btype in available:
            info = __import__('systems.factions', fromlist=['BUILDING_INFO']).BUILDING_INFO.get(btype)
            cat = info[1] if info else "troupes"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(btype)
        # Layout: panneau à gauche, les catégories empilées
        panel_x, panel_y = 10, 60
        btn_w, btn_h, gap = 180, 24, 4
        y = panel_y
        self._build_menu_items = []  # (rect, btype)
        for cat, blist in categories.items():
            if not blist:
                continue
            # Label de catégorie
            self._build_menu_items.append(("label", cat, (panel_x, y, btn_w, 18)))
            y += 22
            for btype in blist:
                rect = (panel_x, y, btn_w, btn_h)
                self._build_menu_items.append((btype, cat, rect))
                y += btn_h + gap
        self._build_menu_height = y - panel_y
        return self._build_menu_items

    def _handle_build_menu_click(self, pos):
        """Gère le clic dans le menu de construction : sélectionne un bâtiment."""
        self._build_menu_rects()  # recalcule les positions
        for item in self._build_menu_items:
            kind, cat, rect = item
            if kind != "label":
                r = pygame.Rect(rect)
                if r.collidepoint(pos):
                    self.selected_building_type = kind
                    print(f"Choisi: {kind} (catégorie {cat})")
                    # Fermer le menu mais rester en mode placement
                    self.build_menu_open = False
                    return

    def _start_campaign(self):
        """Démarre la campagne avec la faction choisie."""
        # Appliquer la faction choisie
        self._apply_faction(self.faction_id)
        self.campaign = create_default_campaign()
        self.current_mission = self.campaign.start_next_mission()
        # Le camp ennemi de la mission 1 vient de la CONFIG de la mission
        # (et non du setup inline de __init__, qui ne crée aucun guerrier),
        # pour assurer une cohérence stricte avec les missions 2+.
        # Mutation SUR PLACE (pas de rebind) : ConstructionSystem référence ces
        # listes depuis __init__ (l.151). Un rebind casserait produce_worker
        # (le worker serait ajouté à l'ancienne liste, jamais visible en jeu).
        self.units[:] = [u for u in self.units if u.faction != "enemy"]
        self.buildings[:] = [b for b in self.buildings if b.faction != "enemy"]
        self.ai.initialize_enemy_base()
        self.state = "mission_screen"

    def _apply_faction(self, faction_id: str):
        """Applique les bonus de la faction à l'économie et aux entités."""
        factions = get_factions()
        self.faction = factions.get(faction_id, factions["human"])
        self.faction_id = self.faction.faction_id

        # Appliquer la couleur de la faction aux unités joueur
        self._faction_color = self.faction.color

        # Ressources de départ selon la faction
        starting = self.faction.starting_resources
        self.economy.gold = starting.get("gold", 220)
        self.economy.wood = starting.get("wood", 170)
        self.economy.food = starting.get("food", 120)

        # Appliquer les modificateurs aux unités et bâtiments du joueur
        for unit in self.units:
            if unit.faction == "player":
                unit.faction_color = self.faction.color
                self.faction.apply_unit_modifiers(unit)
                if hasattr(unit, 'unit_type') and unit.unit_type in ("worker", "builder"):
                    self.faction.apply_worker_bonus(unit)
        for building in self.buildings:
            if building.faction == "player":
                building.faction_color = self.faction.color
                self._apply_building_bonus(building)

        # Convertir la caserne de départ en bâtiment de production principal de la faction
        self._convert_starter_barracks()

        # Transférer les bonus de coût/temps vers les systèmes de construction
        self._apply_faction_cost_bonuses()

        # Configurer les rostres (unités/bâtiments disponibles) et coûts
        self.construction_system.set_faction(self.faction)
        self.production_system.set_faction(self.faction)

        print(f"Faction {self.faction.name} sélectionnée: {self.faction.special_ability['name']}")

    def _convert_starter_barracks(self):
        """Remplace la caserne générique de départ par le bâtiment principal de la faction."""
        if not self.faction:
            return
        target_type = self.faction.primary_war_building
        if target_type == "barracks":
            return
        for building in self.buildings:
            if building.faction == "player" and building.building_type == "barracks":
                # Utiliser la factory pour créer le bâtiment de faction au même emplacement
                new_b = self.construction_system._create_building(target_type,
                                                                   building.x, building.y, "player")
                if new_b is not None:
                    new_b.faction_color = self.faction.color
                    self.buildings[self.buildings.index(building)] = new_b
                break

    def _apply_building_bonus(self, building):
        """Applique les bonus de construction de la faction."""
        bonuses = getattr(self.faction, 'building_bonuses', {})
        btype = getattr(building, 'building_type', '')
        mods = bonuses.get(btype, bonuses.get('*', {}))
        # Les bonus de coût sont gérés au moment de la construction
        if hasattr(building, 'max_hp'):
            hp_percent = mods.get('hp_percent', 1.0)
            building.max_hp = int(building.max_hp * hp_percent)
            building.hp = building.max_hp
        # Bonus de production (temps de construction réduit)
        if 'build_time_percent' in mods and hasattr(building, 'production_time'):
            building.production_time = max(1.0, building.production_time * mods['build_time_percent'])

    def _apply_faction_cost_bonuses(self):
        """Transfère les bonus de coût/temps de la faction aux systèmes."""
        building_bonuses = getattr(self.faction, 'building_bonuses', {})
        # Construction system (bâtiments)
        self.construction_system.faction_bonuses = {}
        for btype, mods in building_bonuses.items():
            entry = {}
            if 'cost_percent' in mods:
                entry['cost_percent'] = mods['cost_percent']
            if 'build_time_percent' in mods:
                entry['time_percent'] = mods['build_time_percent']
            if entry:
                self.construction_system.faction_bonuses[btype] = entry
    
    def _show_load_menu(self):
        """Affiche le menu de chargement."""
        self.state = "load_menu"
        saves = self.save_system.list_saves()
        if saves:
            self._load_save(saves[0]["name"])
    
    def _quick_save(self):
        """Sauvegarde rapide."""
        try:
            self.save_system.save_game(self)
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def _quick_load(self):
        """Charge la dernière sauvegarde."""
        saves = self.save_system.list_saves()
        if saves:
            self._load_save(saves[-1]["name"])
    
    def _load_save(self, save_name: str):
        """Charge une sauvegarde."""
        try:
            save_data = self.save_system.load_game(save_name)

            # Version de format: migrer / valider
            version = save_data.get("version", "1.0")
            if version not in ("1.0", "2.0"):
                raise LoadError(f"Version de sauvegarde incompatible: {version}")

            # Restaurer la faction (avant les unités, pour les modificateurs)
            from systems.factions import get_factions
            fid = save_data.get("faction_id", "human")
            if fid in get_factions():
                self.faction_id = fid
                self._apply_faction(fid)

            # Restaurer les ressources
            if "resources" in save_data:
                for key, value in save_data["resources"].items():
                    if hasattr(self.economy, key):
                        setattr(self.economy, key, value)

            # Restaurer les ressources ennemies
            if "enemy_resources" in save_data:
                for key, value in save_data["enemy_resources"].items():
                    if hasattr(self.enemy_economy, key):
                        setattr(self.enemy_economy, key, value)

            # Restaurer l'arbre technologique
            from systems.tech_tree import TechTree
            if save_data.get("tech_tree"):
                self.tech_tree = TechTree.from_dict(save_data["tech_tree"])

            # Restaurer les nœuds de ressources
            from entities.resource_node import ResourceNode as SaveResourceNode
            if "resource_nodes" in save_data and save_data["resource_nodes"]:
                self.resource_nodes = []
                for n in save_data["resource_nodes"]:
                    node = SaveResourceNode(n["x"], n["y"], n["resource_type"],
                                            n.get("max_amount", n.get("amount", 0)))
                    node.amount = n.get("amount", node.max_amount)
                    self.resource_nodes.append(node)
                self.collision_system.resource_nodes = self.resource_nodes

            # Restaurer les unités (avec réattachement des workers au Game)
            self.units[:] = []  # mutation sur place : garder la référence ConstructionSystem
            if "units" in save_data:
                for unit_data in save_data["units"]:
                    unit = create_unit(unit_data.get("type", "warrior"),
                                      unit_data["x"], unit_data["y"],
                                      unit_data.get("faction", "player"))
                    if "hp" in unit_data:
                        unit.hp = unit_data["hp"]
                    # Réattacher le worker au Game (pour la récolte/dépôt)
                    if hasattr(unit, 'unit_type') and unit.unit_type in ("worker", "builder"):
                        unit.game = self
                        unit.target_resource = None
                        unit.carrying = False
                        unit.carry_amount = 0
                    self.units.append(unit)

            # Restaurer le héros
            if "hero" in save_data and save_data["hero"]:
                hero_data = save_data["hero"]
                self.hero = Hero(hero_data["x"], hero_data["y"], hero_data.get("faction", "player"))
                self.hero.level = hero_data.get("level", 1)
                self.hero.experience = hero_data.get("experience", 0)
                self.hero.mana = hero_data.get("mana", 100)
                self.units.append(self.hero)

            # Restaurer les bâtiments avec leur VRAI type (via la factory)
            self.buildings[:] = []  # mutation sur place : garder la référence ConstructionSystem
            if "buildings" in save_data:
                for building_data in save_data["buildings"]:
                    building = self.construction_system._create_building(
                        building_data.get("type", "town_hall"),
                        building_data["x"], building_data["y"],
                        building_data.get("faction", "player"))
                    if building is None:
                        building = TownHall(building_data["x"], building_data["y"],
                                            building_data.get("faction", "player"))
                    if "hp" in building_data:
                        building.hp = building_data["hp"]
                    if "max_hp" in building_data:
                        building.max_hp = building_data["max_hp"]
                    self.buildings.append(building)

            # Restaurer les constructions en cours
            self.construction_system.construction_sites = []
            if "construction_sites" in save_data:
                for s in save_data["construction_sites"]:
                    progress = self.construction_system._create_site_from_data(s)
                    if progress:
                        self.construction_system.construction_sites.append(progress)

            # Restaurer les statistiques
            if "stats" in save_data:
                self.stats.update(save_data["stats"])

            # Restaurer l'IA
            enemy_units = [u for u in self.units if u.faction == "enemy"]
            enemy_buildings = [b for b in self.buildings if b.faction == "enemy"]
            if not enemy_units or not enemy_buildings:
                self.ai.initialize_enemy_base()

            # Restaurer la campagne + mission en cours
            if "campaign" in save_data:
                self.campaign = Campaign.from_dict(save_data["campaign"])
                if "mission" in save_data and save_data["mission"]:
                    from systems.campaign import Mission
                    self.current_mission = Mission.from_dict(save_data["mission"])
                else:
                    self.current_mission = self.campaign.get_current_mission()
            if "mission_timer" in save_data:
                self.mission_timer = save_data["mission_timer"]

            # Mettre à jour le brouillard de guerre
            self.fog_of_war = FogOfWar(MAP_WIDTH, MAP_HEIGHT)
            self.fog_of_war.update(self.units, self.buildings)

            self.state = "playing"

        except LoadError as e:
            print(f"Error loading game: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def _produce_worker(self, worker_type: str):
        """Produit un worker (ouvrier ou builder)."""
        cost = self.construction_system.WORKER_COSTS.get(worker_type)
        if not cost or not self.economy.can_afford(cost):
            return

        # Produire le worker près du town hall
        town_hall = None
        for building in self.buildings:
            if building.building_type == "town_hall":
                town_hall = building
                break

        x = town_hall.x + 50 if town_hall else 65 * TILE_SIZE
        y = town_hall.y if town_hall else 65 * TILE_SIZE

        if self.construction_system.produce_worker(worker_type, x, y, game=self):
            self.stats["units_produced"] += 1
            self._update_mission_progress("produce", 1)
            # Appliquer les modificateurs de faction à la nouvelle unité
            if self.faction:
                new_unit = self.units[-1]
                self.faction.apply_unit_modifiers(new_unit)
                self.faction.apply_worker_bonus(new_unit)

    def _produce_unit(self, unit_type: str):
        """Produit une unité."""
        # Vérifier si on peut produire
        cost = self.production_system.UNIT_COSTS.get(unit_type)
        if not cost or not self.economy.can_afford(cost):
            return

        # Trouver un bâtiment de production disponible (barracks ou workshop)
        production_building = None
        for building in self.buildings:
            if building.building_type in PRODUCTION_BUILDINGS:
                production_building = building
                break

        # Si pas de bâtiment, en construire un à côté du town hall
        if production_building is None:
            barracks_cost = {"gold": 150, "wood": 100, "food": 20}
            if self.economy.can_afford(barracks_cost):
                # Chercher le town hall pour construire près de lui
                town_hall = None
                for building in self.buildings:
                    if building.building_type == "town_hall":
                        town_hall = building
                        break

                x = town_hall.x + 100 if town_hall else 65 * TILE_SIZE
                y = town_hall.y if town_hall else 65 * TILE_SIZE

                # Démarrer la construction de la caserne
                self.construction_system.start_construction("barracks", x, y)
        # Produire l'unité près du bâtiment de production
        x = production_building.x if production_building else 65 * TILE_SIZE
        y = production_building.y if production_building else 65 * TILE_SIZE

        if self.production_system.produce(unit_type, x, y):
            self.stats["units_produced"] += 1
            self._update_mission_progress("produce", 1)
            # Appliquer les modificateurs de faction à la nouvelle unité
            if self.faction:
                new_unit = self.units[-1]
                self.faction.apply_unit_modifiers(new_unit)

    def _produce_from_building(self):
        """Produit une unité depuis le bâtiment sélectionné."""
        if not self._selected_building:
            print("Sélectionnez d'abord un bâtiment de production (clic droit).")
            return

        # Déterminer les unités que ce bâtiment peut produire
        units = self._get_building_units(self._selected_building)
        if not units:
            print("Ce bâtiment ne produit pas d'unités.")
            return

        # Produire la première unité disponible (celles déjà satisfaites)
        for utype in units:
            ok, _ = self._can_produce_unit(utype)
            if ok:
                self._spawn_unit(utype)
                return
        print("Toutes les unités de ce bâtiment requièrent des prérequis non satisfaits.")

    def _produce_selected_index(self, index: int):
        """Produit l'unité ~index~ du bâtiment sélectionné, en sautant les vérrouées."""
        if not self._selected_building:
            print("Sélectionnez d'abord un bâtiment de production (clic droit).")
            return
        # Unités de combat de ce bâtiment, triées par ordre choisi par la faction
        units = self._get_building_units(self._selected_building)
        combat = [u for u in units if u not in ("worker", "builder")]
        # Sauter les unités non débloquées (prérequis non satisfaits)
        producible = []
        for u in combat:
            ready, _ = self._is_unlocked(u)
            if ready:
                producible.append(u)
        if 0 <= index < len(producible):
            self._spawn_unit(producible[index])
        else:
            print("Aucune unité débloquée à cette touche.")

    def _is_unlocked(self, unit_type: str) -> tuple:
        """Vérifie uniquement les prérequis (bâtiment + tech), sans le coût."""
        if self.faction is not None:
            researched = self.tech_tree.unlocked_techs
            return self.faction.can_produce(unit_type, self.buildings, researched)
        return True, ""

    def _get_building_units(self, building) -> list:
        """Retourne les unités que ce bâtiment peut produire (faction-aware)."""
        if self.faction is None:
            # Fallback: units du bâtiment par défaut
            mapping = {
                "barracks": ["worker", "builder", "warrior", "archer", "knight"],
                "town_hall": ["worker", "builder"],
            }
            return mapping.get(building.building_type, [])
        return self.faction.get_units_for_building(building.building_type)

    def _can_produce_unit(self, unit_type: str) -> tuple:
        """Vérifie (coût + prérequis faction). Retourne (ok, raison)."""
        if self.faction is not None:
            researched = self.tech_tree.unlocked_techs
            ok, reason = self.faction.can_produce(unit_type, self.buildings, researched)
            if not ok:
                return False, reason
        # Vérifier la capacité de population
        max_pop = self.economy.get_max_population(self.buildings or [])
        player_count = len([u for u in self.units if getattr(u, 'faction', 'player') == "player"])
        if player_count >= max_pop:
            return False, f"population maximale atteinte ({player_count}/{max_pop})"
        cost = self.production_system.UNIT_COSTS.get(unit_type)
        if not cost:
            return False, "type inconnu"
        if not self.economy.can_afford(cost):
            return False, "ressources insuffisantes"
        return True, ""

    def _spawn_unit(self, unit_type: str):
        """Fait apparaître une unité près du bâtiment sélectionné (ou du town hall)."""
        # Vérifier la capacité de population
        max_pop = self.economy.get_max_population(self.buildings or [])
        player_count = len([u for u in self.units if getattr(u, 'faction', 'player') == "player"])
        if player_count >= max_pop:
            self._show_ui_message(
                f"Population maximale atteinte ({player_count}/{max_pop})",
                (255, 100, 100))
            return

        building = self._selected_building
        if building is None:
            # Trouver le town hall
            for b in self.buildings:
                if b.building_type == "town_hall":
                    building = b
                    break
        x = (building.x + 40) if building else 65 * TILE_SIZE
        y = building.y if building else 65 * TILE_SIZE

        # Mise en file de production : l'unité apparaît quand la progression atteint 100%
        # (la stat units_produced et les modificateurs de faction sont gérés dans update()).
        if self.production_system.enqueue(unit_type, x, y):
            print(f"En production: {unit_type}")
    
    def _handle_selection(self, pos: tuple):
        """Gère la sélection d'unités."""
        mouse_x, mouse_y = pos
        
        # Convertir la position souris en coordonnées map
        map_x = mouse_x + self.camera.x
        map_y = mouse_y + self.camera.y

        clicked_unit = None
        min_distance = 30

        for unit in self.units:
            if unit.faction == "player":
                dx = unit.x - map_x
                dy = unit.y - map_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    clicked_unit = unit
        
        if clicked_unit:
            self.selected_units = [clicked_unit]
            for u in self.units:
                u.selected = False
            clicked_unit.selected = True
    
    def _find_building_at(self, map_x, map_y, radius=48):
        """Retourne le bâtiment joueur à la position map (ou None)."""
        best = None
        best_dist = radius
        for building in self.buildings:
            if building.faction != "player":
                continue
            dx = building.x - map_x
            dy = building.y - map_y
            d = (dx ** 2 + dy ** 2) ** 0.5
            if d < best_dist:
                best_dist = d
                best = building
        return best

    def _select_building(self, building):
        """Sélectionne un bâtiment joueur (re-clic = reste sélectionné)."""
        # Désélectionner toutes les unités
        for unit in self.units:
            unit.selected = False
        self.selected_units = []

        # Sélectionner le bâtiment (re-clic ne désélectionne PAS : désélection via clic vide ou Échap)
        building.selected = True
        self._selected_building = building
        print(f"Sélectionné: {building.building_type}")

    def _deselect_building(self):
        """Désélectionne le bâtiment en cours."""
        if self._selected_building:
            self._selected_building.selected = False
            self._selected_building = None
            print("Bâtiment désélectionné")

    def _handle_right_click(self, pos: tuple):
        """Gère le clic droit."""
        mouse_x, mouse_y = pos

        # Convertir la position souris en coordonnées map
        map_x = mouse_x + self.camera.x
        map_y = mouse_y + self.camera.y

        # Si on clique sur un bâtiment joueur, le sélectionner (production/recherche)
        clicked_building = self._find_building_at(map_x, map_y, radius=56)
        if clicked_building:
            self._select_building(clicked_building)
            return

        # Vérifier ressource
        clicked_resource = None
        min_distance = 40
        for node in self.resource_nodes:
            if node.is_depleted():
                continue
            dx = node.x - map_x
            dy = node.y - map_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                clicked_resource = node

        # Vérifier ennemi (unité)
        clicked_enemy = None
        min_distance = 40
        for unit in self.units:
            if unit.faction == "enemy":
                dx = unit.x - map_x
                dy = unit.y - map_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    clicked_enemy = unit

        # Vérifier bâtiment ennemi (à détruire)
        clicked_enemy_building = None
        min_distance = 48
        for building in self.buildings:
            if building.faction == "enemy":
                dx = building.x - map_x
                dy = building.y - map_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    clicked_enemy_building = building

        for unit in self.selected_units:
            # Si clic sur une ressource et que c'est un worker
            if clicked_resource and not clicked_resource.is_depleted():
                # Cas 1: Mine d'or - assigner le worker (max 3)
                if clicked_resource.resource_type == "gold" and clicked_resource.is_mine:
                    if getattr(unit, 'unit_type', '') == "worker":
                        # Assigner le worker à la mine
                        if clicked_resource.assign_worker(unit):
                            unit.target_resource = clicked_resource
                            self.audio_events.on_ui_click()
                            continue

                # Cas 2: Forêt - mode bucheron (couper sans récolter)
                elif clicked_resource.resource_type == "wood":
                    # Toggle le mode bucheron
                    if hasattr(unit, 'can_cut_trees'):
                        unit.can_cut_trees = not unit.can_cut_trees
                        self.audio_events.on_ui_click()
                        continue

                # Cas 3: Récolte normale (food ou bois) - UNIQUEMENT pour les workers
                else:
                    if getattr(unit, 'unit_type', '') in ("worker", "builder"):
                        self.movement_system.move_to(unit, clicked_resource.x, clicked_resource.y)
                        unit.target_resource = clicked_resource
                    # Unités de combat : le clic sur une ressource ne fait que s'en approcher
                    else:
                        self.movement_system.move_to(unit, clicked_resource.x, clicked_resource.y)
            elif clicked_enemy_building:
                # Ordonner d'attaquer (détruire) le bâtiment ennemi
                unit.target = clicked_enemy_building
                unit.is_moving = False
                # Libérer le worker d'une éventuelle récolte en cours
                if hasattr(unit, 'target_resource'):
                    unit.target_resource = None
                    unit.carrying = False
            elif clicked_enemy:
                unit.target = clicked_enemy
                unit.is_moving = False
            else:
                self.movement_system.move_to(unit, map_x, map_y)
    
    def update(self, dt: float):
        """Update game state."""
        if self.state != "playing":
            return

        self.mission_timer += dt

        # Auto-gather resources for workers
        self._auto_gather_resources()

        # Déplacement caméra
        keys = pygame.key.get_pressed()
        camera_speed = 200 * dt
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera.move(0, -camera_speed)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera.move(0, camera_speed)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera.move(-camera_speed, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera.move(camera_speed, 0)
        
        # Mettre à jour le brouillard de guerre
        self.fog_of_war.update(self.units, self.buildings)
        
        # Mettre à jour l'IA
        self.ai.update(dt)
        
        # Mettre à jour les unités
        for unit in self.units[:]:
            # Récolte automatique pour workers (le worker gère lui-même maintenant)
            if hasattr(unit, 'unit_type') and unit.unit_type == "worker":
                unit.update(dt)

                # Try to motivate nearby workers occasionally
                if random.random() < 0.01:
                    nearby = [u for u in self.units
                             if hasattr(u, 'unit_type') and u.unit_type == "worker"
                             and u is not unit]
                    unit.try_motivate_nearby(nearby)
            else:
                # Normal unit movement
                self.movement_system.update(unit, dt)

            # Résoudre les collisions (prevent stacking)
            self.collision_system.resolve_collision(unit, self.units, self.resource_nodes)
            
            # Retirer les unités mortes
            if not unit.is_alive():
                # Attribuer l'XP au tueur
                if unit.killed_by is not None and unit.killed_by in self.units:
                    xp = unit.killed_by.xp_on_kill(unit)
                    unit.killed_by.gain_xp(xp)
                    unit.killed_by.kills += 1
                    self.visual_effects.add_explosion(unit.x, unit.y, (255, 215, 0))

                if unit.faction == "enemy":
                    self.stats["enemies_killed"] += 1
                    self._update_mission_progress("kill", 1)
                    self.visual_effects.add_explosion(unit.x, unit.y, (255, 100, 0))
                    self.audio_events.on_kill()
                    self._show_tutorial("combat",
                                        "Ennemi éliminé ! Cliquez-droit sur un ennemi pour "
                                        "ordonner l'attaque.")
                
                self.units.remove(unit)
        
        # Gérer les bâtiments détruits
        for building in self.buildings[:]:
            if not building.is_alive():
                # Attribuer l'XP pour la destruction du bâtiment
                if getattr(building, 'killed_by', None) is not None and building.killed_by in self.units:
                    xp = building.killed_by.xp_on_kill(building)
                    building.killed_by.gain_xp(xp)
                    building.killed_by.kills += 1

                if building.faction == "enemy":
                    self._handle_building_destroyed(building)
                self.visual_effects.add_explosion(building.x, building.y, (255, 80, 0))
                self.audio_events.on_kill()
                self.buildings.remove(building)
        
        # Mettre à jour les effets visuels
        self.visual_effects.update(dt)

        # Mettre à jour les constructions (les builders construisent les chantiers)
        self.construction_system.update(dt)

        # Tutoriel construction (premier bâtiment joueur terminé)
        player_buildings = [b for b in self.buildings if b.faction == "player"]
        if len(player_buildings) > self._last_player_building_count:
            self._show_tutorial("build",
                                "Bâtiment construit ! Sélectionnez-le pour produire des unités.")
        self._last_player_building_count = len(player_buildings)

        # File de production : faire progresser les unités en cours de fabrication
        for spawned in self.production_system.update(dt):
            self.stats["units_produced"] += 1
            self._update_mission_progress("produce", 1)
            if self.faction:
                self.faction.apply_unit_modifiers(spawned)

        # Décrémenter le compteur du message UI (le message disparaît après la durée)
        if self.ui_message_timer > 0:
            self.ui_message_timer -= dt
            if self.ui_message_timer <= 0:
                self.ui_message = None
                self.ui_message_timer = 0.0

        # Régénération des ressources (bois seulement)
        self._regenerate_resources(dt)
        
        # Mettre à jour l'arbre technologique
        self.tech_tree.update(dt)

        # Appliquer les effets des recherches nouvellement terminées
        self._apply_research_effects()

        # Vérifier les objectifs de mission
        self._check_mission_objectives()
        
        # Vérifier victoire/défaite
        self._check_victory_defeat()
    
    def _check_victory_defeat(self):
        """Vérifie la victoire/défaite et fait progresser la campagne.

        - Défaite : plus aucun bâtiment joueur.
        - Victoire : tous les ennemis (unités + bâtiments) détruits.
          Le camp ennemi est ensuite récréé pour la mission suivante, sinon
          la nouvelle mission détecterait 0 ennemi et enchaînerait (cascade).
        """
        player_buildings = [b for b in self.buildings if b.faction == "player"]
        enemy_units = [u for u in self.units if u.faction == "enemy"]
        enemy_buildings = [b for b in self.buildings if b.faction == "enemy"]

        # Échec par temps : si la mission impose un délai et qu'il est dépassé.
        limit = getattr(self.current_mission, "time_limit", 0) if self.current_mission else 0
        if limit and self.mission_timer >= limit:
            self.state = "defeat"
            if self.current_mission:
                self.current_mission.fail()
            return
        
        if len(player_buildings) == 0:
            self.state = "defeat"
            return
        elif len(enemy_units) == 0 and len(enemy_buildings) == 0:
            # Victoire seulement si tous les ennemis ET bâtiments sont détruits
            if self.current_mission:
                self.current_mission.complete()
                self.campaign.complete_current_mission()
                
                rewards = self.current_mission.rewards
                self.economy.add_resources(
                    gold=rewards.get("gold", 0),
                    wood=rewards.get("wood", 0),
                    food=rewards.get("food", 0)
                )
                if self.hero:
                    self.hero.gain_experience(rewards.get("experience", 0))
            
            if self.campaign.is_campaign_complete():
                self.state = "victory"
            else:
                self.current_mission = self.campaign.start_next_mission()
                if self.current_mission:
                    # Recréer un camp ennemi pour la mission suivante afin
                    # d'éviter une victoire en chaîne (0 ennemi restant).
                    self.ai.initialize_enemy_base()
                    self.state = "mission_screen"
                else:
                    self.state = "victory"
    
    def _update_mission_progress(self, objective_type: str, amount: int = 1):
        """Met à jour la progression de la mission."""
        if not self.current_mission:
            return
        
        for objective in self.current_mission.objectives:
            if objective.type == objective_type:
                objective.update(amount)
                if objective.completed and self.current_mission.check_completion():
                    self.current_mission.complete()
    
    def _cycle_formation(self):
        """Change la formation des unités sélectionnées."""
        formations = ["line", "column", "triangle", "circle", "diamond"]
        current_index = formations.index(self.formation_manager.current_formation)
        next_index = (current_index + 1) % len(formations)
        self.formation_manager.set_formation(formations[next_index])
        
        # Appliquer la formation si des unités sont sélectionnées
        if self.selected_units:
            target_x = self.selected_units[0].x
            target_y = self.selected_units[0].y
            self.formation_manager.apply_formation(self.selected_units, target_x, target_y)
        
        self.audio_events.on_ui_click()
    
    def _cycle_time_scale(self):
        """Cycle l'accélération du temps : 1 -> 2 -> 4 -> 8 -> 16 -> 1."""
        idx = self.TIME_SCALES.index(self.time_scale)
        self.set_time_scale(self.TIME_SCALES[(idx + 1) % len(self.TIME_SCALES)])
        self.audio_events.on_ui_click()
    
    def set_time_scale(self, scale: int):
        """Règle le multiplicateur de temps (ignoré si non valide)."""
        if scale in self.TIME_SCALES:
            self.time_scale = scale
    
    def effective_dt(self, dt: float) -> float:
        """dt effectif à l'échelle temporelle courante (dt * time_scale)."""
        return dt * self.time_scale
    
    def _research_next_tech(self):
        """Recherche la prochaine technologie disponible."""
        available = self.tech_tree.get_available_research(
            self.economy,
            self.faction.techs if self.faction else None,
        )

        if not available:
            # Recherche en cours ou tout recherché → raison précise
            if self.tech_tree.current_research is not None:
                self._show_ui_message(
                    f"Recherche en cours: {self.tech_tree.current_research.name}",
                    (200, 200, 0))
            else:
                self._show_ui_message("Toutes les recherches disponibles sont terminées "
                                      "ou hors de portée.", (200, 200, 200))
            return

        tech = available[0]
        if self.tech_tree.start_research(tech.tech_id, self.economy):
            self.audio_events.on_building_built()
            self._show_ui_message(f"Recherche lancée: {tech.name}", (0, 255, 0))
            self._show_tutorial("research",
                                "Recherche lancée ! Les améliorations s'appliquent "
                                "automatiquement aux unités et bâtiments.")
        else:
            self._show_ui_message("Impossible de lancer la recherche (prérequis ou "
                                  "ressources manquants).", (255, 100, 100))

    def _research_requirement_message(self) -> str:
        """Message UI expliquant le bâtiment de recherche requis et son coût."""
        cost = {}
        if self.construction_system:
            cost = self.construction_system.get_building_cost("academy")
        gold = cost.get("gold", 0)
        wood = cost.get("wood", 0)
        food = cost.get("food", 0)
        parts = []
        for name, val in (("or", gold), ("bois", wood), ("nourriture", food)):
            if val:
                parts.append(f"{val} {name}")
        return (f"Rechercher nécessite un bâtiment de recherche (Académie): "
                f"coût {' et '.join(parts)}")

    def _handle_research_key(self):
        """Gère la touche T : recherche via un bâtiment de recherche sélectionné."""
        if self._selected_building and self.faction and \
           self._selected_building.building_type in self.faction.research_buildings:
            self._research_next_tech()
        else:
            self._show_ui_message(self._research_requirement_message(), (255, 200, 0))

    def _show_ui_message(self, text: str, color=None, duration: float = 4.0):
        """Affiche un message contextuel à l'écran (remplace le print console)."""
        self.ui_message = text
        if color:
            self.ui_message_color = tuple(color[:3]) if len(color) >= 3 else (255, 255, 255)
        self.ui_message_timer = duration

    def _show_tutorial(self, key: str, text: str) -> bool:
        """Montre un tutoriel contextuel la première fois seulement.

        Retourne True si le tutoriel vient d'être affiché, False sinon.
        """
        if self.tutorial_shown.get(key):
            return False
        self.tutorial_shown[key] = True
        self._show_ui_message(f"💡 {text}", (255, 215, 0), duration=6.0)
        return True

    def _handle_building_destroyed(self, building):
        """À appeler quand un bâtiment est détruit et retiré du monde."""
        if building.faction == "enemy":
            self.stats["enemies_killed"] += 1
            self._update_mission_progress("destroy_building", 1)

    # Effets des technologies communes (appliqués aux unités/bâtiments du joueur)
    _RESEARCH_EFFECTS = {
        "iron_working":   {"damage_percent": 1.10},   # +10% dégâts
        "heavy_armor":    {"armor": 2},               # +2 armure (chevaliers surtout)
        "archery":        {"range_percent": 1.10},    # +10% portée (archers)
        "magic_study":    {"damage_percent": 1.10},   # +10% dégâts (mages)
        "mining":         {"worker_boost": {"gold": 2}},   # 2x or par voyage
        "logging":        {"worker_boost": {"wood": 2}},   # 2x bois par voyage
        "agriculture":    {"worker_boost": {"food": 1}},   # +1 nourriture/voyage
        "fortification":  {"building_hp": 1.20},      # +20% PV bâtiments
    }

    def _apply_research_effects(self):
        """Applique les effets des recherches terminées aux unités/bâtiments joueur."""
        if not hasattr(self, '_applied_tech_effects'):
            self._applied_tech_effects = set()

        for tid in self.tech_tree.unlocked_techs:
            if tid in self._applied_tech_effects:
                continue
            self._applied_tech_effects.add(tid)
            self._apply_one_research_effect(tid)

    def _apply_one_research_effect(self, tech_id: str):
        """Applique l'effet d'une recherche aux unités et bâtiments du joueur."""
        effect = self._RESEARCH_EFFECTS.get(tech_id, {})
        if not effect:
            return

        # Bonus de récolte des workers (mining/logging/agriculture)
        worker_boost = effect.get("worker_boost")
        if worker_boost:
            # Le bonus est un multiplicateur (ex: {"gold": 2} = ×2 or par voyage)
            factor = max(worker_boost.values()) if worker_boost else 1.0
            for u in self.units:
                if u.faction == "player" and hasattr(u, 'unit_type') and u.unit_type in ("worker", "builder"):
                    u.max_carry = int(getattr(u, 'max_carry', 15) * max(1.0, factor))

        # Bonus aux bâtiments
        if "building_hp" in effect:
            for b in self.buildings:
                if b.faction == "player":
                    b.max_hp = int(b.max_hp * effect["building_hp"])
                    b.hp = b.max_hp

        # Bonus aux unités existantes
        for u in self.units:
            if u.faction != "player":
                continue
            if "damage_percent" in effect:
                u.damage = int(u.damage * effect["damage_percent"])
            if "armor" in effect:
                u.armor = getattr(u, 'armor', 0) + effect["armor"]
            if "range_percent" in effect:
                u.range = int(u.range * effect["range_percent"])
    
    def _check_mission_objectives(self):
        """Vérifie les objectifs de la mission."""
        if not self.current_mission:
            return
        
        for objective in self.current_mission.objectives:
            if objective.type == "survive":
                # Temps écoulé (activation directe : objectif rempli à la durée cible)
                objective.current = int(self.mission_timer)
                if objective.current >= objective.target and not objective.completed:
                    objective.completed = True
            elif objective.type == "kill":
                # Vérifier si l'objectif est complété
                if objective.current >= objective.target and not objective.completed:
                    objective.update(1)  # Marquer comme complété
            elif objective.type == "build":
                # Compter les bâtiments construits et mettre à jour
                player_buildings = len([b for b in self.buildings if b.faction == "player"])
                if player_buildings >= objective.target and not objective.completed:
                    objective.update(player_buildings)
            elif objective.type == "produce":
                # Vérifier si l'objectif est complété
                if self.stats["units_produced"] >= objective.target and not objective.completed:
                    objective.update(self.stats["units_produced"])
    
    def draw(self):
        """Render the game."""
        if self.state == "menu":
            self.main_menu.draw(self.screen)
        elif self.state == "faction_select":
            self.faction_menu.draw(self.screen)
        elif self.state == "load_menu":
            self._draw_load_menu()
        elif self.state == "mission_screen":
            self._draw_mission_screen()
        elif self.state == "paused":
            self._draw_game()
            self.pause_menu.draw(self.screen, self)
        elif self.state in ["victory", "defeat"]:
            if self.state == "victory":
                self.victory_screen.draw(self.screen)
            else:
                self.defeat_screen.draw(self.screen)
        else:
            self._draw_game()
    
    def _draw_load_menu(self):
        """Dessine le menu de chargement."""
        self.screen.fill((50, 50, 50))
        font = pygame.font.Font(None, 36)
        title = font.render("Charger une partie", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3))
        
        saves = self.save_system.list_saves()
        if saves:
            for i, save in enumerate(saves):
                save_text = font.render(f"{save['name']} - {save['timestamp']}", True, (200, 200, 200))
                self.screen.blit(save_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3 + 50 + i * 40))
        else:
            no_save = font.render("Aucune sauvegarde trouvée", True, (200, 200, 200))
            self.screen.blit(no_save, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3 + 50))
        
        hint = pygame.font.Font(None, 24).render("ESC pour revenir au menu", True, (150, 150, 150))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
    
    def _draw_mission_screen(self):
        """Dessine l'écran de mission."""
        self.screen.fill((30, 30, 50))
        
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
        
        if self.current_mission:
            title = font.render(self.current_mission.name, True, (255, 215, 0))
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(title, title_rect)
            
            desc = small_font.render(self.current_mission.description, True, (200, 200, 200))
            desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
            self.screen.blit(desc, desc_rect)
            
            y_offset = SCREEN_HEIGHT // 2
            for objective in self.current_mission.objectives:
                status = "✓" if objective.completed else f"{objective.current}/{objective.target}"
                color = (0, 255, 0) if objective.completed else (255, 255, 255)
                obj_text = small_font.render(f"{objective.description}: {status}", True, color)
                self.screen.blit(obj_text, (SCREEN_WIDTH // 2 - 150, y_offset))
                y_offset += 30
            
            rewards_text = f"Récompenses: Or +{self.current_mission.rewards.get('gold', 0)}, Bois +{self.current_mission.rewards.get('wood', 0)}, XP +{self.current_mission.rewards.get('experience', 0)}"
            rewards = small_font.render(rewards_text, True, (255, 215, 0))
            self.screen.blit(rewards, (SCREEN_WIDTH // 2 - 150, y_offset + 20))
            
            hint = small_font.render("Appuyez sur ESPACE pour commencer", True, (150, 150, 150))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100))
        else:
            campaign_title = font.render("Campagne Terminée!", True, (255, 215, 0))
            self.screen.blit(campaign_title, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 3))
            
            hint = small_font.render("Appuyez sur ESPACE pour retourner au menu", True, (150, 150, 150))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
    
    def _draw_game(self):
        """Dessine le jeu."""
        # Clear screen
        self.screen.fill(COLORS["grass"])

        # Draw map
        self.game_map.draw(self.screen, self.camera.x, self.camera.y)

        # Draw resource nodes - render as forests and mines
        # Resources are always visible if explored (not just visible)
        for node in self.resource_nodes:
            if not node.is_depleted():
                # Vérifier si explorée OU visible
                if self.fog_of_war.is_explored(node.x, node.y) or self.fog_of_war.is_visible(node.x, node.y):
                    node.draw(self.screen, self.camera.x, self.camera.y)

        # Draw drop-off points
        for drop_point in getattr(self, 'drop_off_points', []):
            if self.fog_of_war.is_visible(drop_point.x, drop_point.y):
                drop_point.draw(self.screen, self.camera.x, self.camera.y)

        # Draw buildings
        for building in self.buildings:
            if self.fog_of_war.is_visible(building.x, building.y):
                building.draw(self.screen, self.camera.x, self.camera.y)
        
        # Draw units
        for unit in self.units:
            if self.fog_of_war.is_visible(unit.x, unit.y):
                unit.draw(self.screen, self.camera.x, self.camera.y)
                # Draw chat bubble for workers
                if hasattr(unit, 'draw_chat_bubble') and unit.chat_bubble:
                    unit.draw_chat_bubble(self.screen, self.camera.x, self.camera.y)

        # Draw effects (before fog so explosions are visible)
        self.visual_effects.draw(self.screen)

        # Draw fog of war LAST so it doesn't cover units/buildings
        self.fog_of_war.draw(self.screen, self.game_map, self.camera)
        
        # Draw selection box if dragging
        if self._mouse_down and self._selection_start:
            start_x = self._selection_start[0] - self.camera.x
            start_y = self._selection_start[1] - self.camera.y
            end_x = pygame.mouse.get_pos()[0]
            end_y = pygame.mouse.get_pos()[1]
            
            # Draw rectangle
            rect_x = min(start_x, end_x)
            rect_y = min(start_y, end_y)
            rect_w = abs(end_x - start_x)
            rect_h = abs(end_y - start_y)
            
            pygame.draw.rect(self.screen, (0, 255, 0), (rect_x, rect_y, rect_w, rect_h), 1)
            pygame.draw.rect(self.screen, (0, 128, 0), (rect_x, rect_y, rect_w, rect_h), 2)
        
        # Draw HUD
        self.hud.draw_resources(self.economy, self.units, self.buildings, self.faction)
        self.hud.draw_selection_panel(self.selected_units, self.hero)
        self.hud.draw_minimap(self.game_map, self.camera, self.units, self.buildings)
        self.hud.draw_production_buttons(self.economy, self.selected_units, self._selected_building,
                                         self.production_system, self.faction, self)
        self.hud.draw_construction_buttons(self.economy, self.construction_system)
        self.hud.draw_construction_progress(self.construction_system)
        self.hud.draw_production_queue(self.production_system)

        # Draw construction preview
        if self.selected_building_type and self.construction_preview_pos:
            self._draw_construction_preview()

        if self.hero:
            self.hud.draw_skill_buttons(self.hero)
        
        # Draw formation info
        self._draw_formation_hud()
        
        # Draw tech tree info
        self._draw_tech_hud()

        # Menu de construction (B)
        if self.build_menu_open:
            self._draw_build_menu()

        # Message UI contextuel (raisons / tutoriel)
        self._draw_ui_message()

    def _draw_ui_message(self):
        """Dessine le message UI contextuel en haut au centre de l'écran."""
        if not self.ui_message:
            return
        font = pygame.font.Font(None, 22)
        text = font.render(self.ui_message, True, self.ui_message_color)
        pad = 10
        box_w = text.get_width() + pad * 2
        box_h = text.get_height() + pad
        x = (SCREEN_WIDTH - box_w) // 2
        y = 60
        # Fond semi-transparent
        overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (x, y))
        pygame.draw.rect(self.screen, self.ui_message_color, (x, y, box_w, box_h), 1)
        self.screen.blit(text, (x + pad, y + pad // 2))
    
    def _regenerate_resources(self, dt: float):
        """Régénère les ressources naturelles (bois uniquement)."""
        for node in self.resource_nodes:
            if node.resource_type == "wood" and not node.is_depleted():
                # Régénération progressive - 1% par seconde max
                regen_amount = int(node.max_amount * 0.01 * dt)
                if regen_amount > 0:
                    node.amount = min(node.max_amount, node.amount + regen_amount)

    def _draw_mission_hud(self):
        """Dessine les infos de la mission."""
        font = pygame.font.Font(None, 20)

        pygame.draw.rect(self.screen, (0, 0, 0, 150), (10, SCREEN_HEIGHT - 120, 300, 110))

        mission_name = font.render(f"Mission: {self.current_mission.name}", True, (255, 215, 0))
        self.screen.blit(mission_name, (20, SCREEN_HEIGHT - 110))

        y = SCREEN_HEIGHT - 85
        for objective in self.current_mission.objectives:
            status = "✓" if objective.completed else f"{objective.current}/{objective.target}"
            color = (0, 255, 0) if objective.completed else (255, 255, 255)
            obj_text = font.render(f"{objective.description}: {status}", True, color)
            self.screen.blit(obj_text, (20, y))
            y += 20

        timer_text = font.render(f"Temps: {int(self.mission_timer)}s", True, (200, 200, 200))
        self.screen.blit(timer_text, (20, y))

        # Indicateur d'accélération du temps (visible quand != 1x)
        if self.time_scale != 1:
            speed_color = (255, 170, 0)
            speed_text = font.render(f"Vitesse x{self.time_scale} [G]", True, speed_color)
            self.screen.blit(speed_text, (20, y + 24))
    
    def _draw_build_menu(self):
        """Dessine le menu de construction (choix du bâtiment par catégorie)."""
        from systems.factions import BUILDING_CATEGORIES, BUILDING_INFO
        items = self._build_menu_rects()
        # Fond du panneau
        panel_w = 190
        panel_h = self._build_menu_height + 10
        pygame.draw.rect(self.screen, (30, 30, 50, 230),
                         (5, 55, panel_w, panel_h))
        pygame.draw.rect(self.screen, (100, 100, 150),
                         (5, 55, panel_w, panel_h), 2)
        font = pygame.font.Font(None, 18)
        small = pygame.font.Font(None, 15)

        for item in items:
            kind, cat, rect = item
            r = pygame.Rect(rect)
            if kind == "label":
                color = (255, 215, 0)
                label = BUILDING_CATEGORIES.get(cat, cat)
                t = font.render("— " + label + " —", True, color)
                self.screen.blit(t, (r.x + 5, r.y))
            else:
                btype = kind
                info = BUILDING_INFO.get(btype, (btype, cat, ""))
                name = info[0]
                cost = self.construction_system.get_building_cost(btype)
                # Couleur selon catégorie
                cat_colors = {
                    "economie": (120, 160, 80), "troupes": (200, 80, 80),
                    "navale": (80, 120, 200), "recherche": (180, 140, 200),
                    "defense": (180, 160, 60), "caserne": (200, 80, 80),
                }
                fill = cat_colors.get(cat, (120, 120, 120))
                can_afford = (self.economy.gold >= cost.get("gold", 0) and
                              self.economy.wood >= cost.get("wood", 0) and
                              self.economy.food >= cost.get("food", 0))
                colored = fill if can_afford else (70, 70, 90)
                pygame.draw.rect(self.screen, colored, r)
                pygame.draw.rect(self.screen, (200, 200, 200), r, 1)
                t = small.render(f"{name} ({cost.get('gold',0)} or)", True, (255, 255, 255))
                self.screen.blit(t, (r.x + 5, r.y + 3))

    def _draw_construction_preview(self):
        """Dessine l'aperçu de construction."""
        if not self.construction_preview_pos:
            return

        x, y = self.construction_preview_pos
        screen_x = int(x - self.camera.x)
        screen_y = int(y - self.camera.y)

        # Dessiner le preview (cercle vert si possible, rouge si impossible)
        cost = self.construction_system.BUILDING_COSTS.get(self.selected_building_type, {})
        can_afford = self.economy.can_afford(cost) if cost else False

        color = (0, 255, 0) if can_afford else (255, 0, 0)
        pygame.draw.circle(self.screen, (*color[:3], 128), (screen_x, screen_y), 32, 2)

        # Dessiner le nom du bâtiment
        font = pygame.font.Font(None, 16)
        text = font.render(f"Construire: {self.selected_building_type}", True, (255, 255, 255))
        self.screen.blit(text, (screen_x - 60, screen_y - 50))

        # Afficher le coût
        if cost:
            cost_text = font.render(f"Coût: {cost.get('gold', 0)} or, {cost.get('wood', 0)} bois", True, (255, 255, 100))
            self.screen.blit(cost_text, (screen_x - 80, screen_y - 30))

    def _draw_formation_hud(self):
        """Dessine les infos de formation."""
        font = pygame.font.Font(None, 18)
        
        # Affichage en haut à droite
        x, y = SCREEN_WIDTH - 150, 10
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (x - 10, y - 20, 160, 40))
        
        formation_text = font.render(f"Formation: {self.formation_manager.current_formation}", True, (255, 255, 255))
        self.screen.blit(formation_text, (x, y))
        
        hint_text = font.render("[F] Changer", True, (150, 150, 150))
        self.screen.blit(hint_text, (x, y + 20))
    
    def _draw_tech_hud(self):
        """Dessine les infos technologiques."""
        font = pygame.font.Font(None, 18)
        
        # Affichage en haut à droite sous la formation
        x, y = SCREEN_WIDTH - 150, 60
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (x - 10, y - 20, 160, 40))
        
        current_research = self.tech_tree.current_research
        if current_research:
            progress = int((current_research.research_progress / current_research.research_time) * 100)
            tech_text = font.render(f"Recherche: {current_research.name}", True, (255, 215, 0))
            self.screen.blit(tech_text, (x, y))
            
            bar_width = 140
            bar_height = 8
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y + 20, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (x, y + 20, int(bar_width * progress / 100), bar_height))
        else:
            tech_text = font.render("Pas de recherche", True, (150, 150, 150))
            self.screen.blit(tech_text, (x, y))
        
        hint_text = font.render("[T] Rechercher", True, (150, 150, 150))
        self.screen.blit(hint_text, (x, y + 30))


if __name__ == "__main__":
    game = Game()
    game.run()
