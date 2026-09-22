"""
Mountain_Roy - HUD (Heads-Up Display)
Version alignée: Panneau de sélection, boutons de production et construction
"""

import pygame
from settings import COLORS

class HUD:
    """Interface utilisateur du jeu (HUD) - Version alignée."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.button_font = pygame.font.Font(None, 20)

        # Dimensions
        self.hud_height = 120
        self.hud_y = screen_height - self.hud_height
        self.top_bar_height = 40

        # Minimap
        self.minimap_size = 150
        self.minimap_x = screen_width - self.minimap_size - 20
        self.minimap_y = self.hud_y + 10

        # Construction panel (bottom left)
        self.construction_panel_x = 10
        self.construction_panel_y = self.hud_y + 10

    @staticmethod
    def order_text(unit) -> str:
        """Retourne l'ordre actuel d'une unité (pour indicateur HUD)."""
        if getattr(unit, "construction_target", None) is not None:
            return "Construction"
        if getattr(unit, "target_resource", None) is not None:
            return "Récolte"
        if getattr(unit, "target", None) is not None:
            return "Attaque"
        if getattr(unit, "is_moving", False):
            return "Déplacement"
        return ""

    def draw_resources(self, economy, units=None, buildings=None, faction=None):
        """Dessine la barre de ressources en haut."""
        # Fond
        pygame.draw.rect(self.screen, COLORS["ui_bg"], (0, 0, self.screen.get_width(), self.top_bar_height))
        pygame.draw.rect(self.screen, COLORS["ui_border"], (0, 0, self.screen.get_width(), self.top_bar_height), 2)

        # Calculer la population
        unit_count = len([u for u in units if u.faction == "player"]) if units else 0
        max_pop = economy.get_max_population(buildings or [])

        # Ressources - alignées à gauche
        texts = [
            (f"Or: {economy.gold}", COLORS["gold"]),
            (f"Bois: {economy.wood}", COLORS["wood"]),
            (f"Nourriture: {economy.food}", COLORS["food"]),
            (f"Pop: {unit_count}/{max_pop}", (255, 255, 255)),
        ]

        x_pos = 15
        for text, color in texts:
            rendered = self.font.render(text, True, color)
            self.screen.blit(rendered, (x_pos, 10))
            x_pos += rendered.get_width() + 30

        # Afficher la faction à droite de la barre de ressources
        if faction is not None:
            name = getattr(faction, 'name', str(faction))
            color = getattr(faction, 'color', (255, 255, 255))
            # Icône (cercle coloré) + nom
            pygame.draw.circle(self.screen, color,
                               (self.screen.get_width() - 140, 15), 7)
            f_render = self.font.render(name, True, color)
            self.screen.blit(f_render, (self.screen.get_width() - 125, 8))

    def draw_selection_panel(self, selected_units=None, hero=None):
        """Dessine le panneau de sélection en bas."""
        # Fond
        pygame.draw.rect(self.screen, COLORS["ui_bg"], (0, self.hud_y, self.screen.get_width(), self.hud_height))
        pygame.draw.rect(self.screen, COLORS["ui_border"], (0, self.hud_y, self.screen.get_width(), self.hud_height), 2)

        if selected_units and len(selected_units) > 0:
            if len(selected_units) == 1:
                unit = selected_units[0]

                # Portrait (cercle)
                portrait_color = unit.get_color() if hasattr(unit, 'get_color') else COLORS["player_unit"]
                pygame.draw.circle(self.screen, portrait_color, (50, self.hud_y + 50), 30)

                # Nom
                name = getattr(unit, 'unit_type', 'Unit')
                rendered = self.font.render(name, True, COLORS["ui_text"])
                self.screen.blit(rendered, (90, self.hud_y + 10))

                # Ordre actuel (déplacement/attaque/récolte/construction)
                order = self.order_text(unit)
                if order:
                    order_rendered = self.small_font.render(f"◆ {order}", True, (255, 215, 0))
                    self.screen.blit(order_rendered, (90 + rendered.get_width() + 10, self.hud_y + 14))

                # PV
                hp_ratio = unit.hp / unit.max_hp if hasattr(unit, 'max_hp') and unit.max_hp > 0 else 0
                hp_color = (255, 0, 0) if hp_ratio < 0.3 else (0, 255, 0)
                pygame.draw.rect(self.screen, (100, 100, 100), (90, self.hud_y + 55, 150, 10))
                pygame.draw.rect(self.screen, hp_color, (90, self.hud_y + 55, int(150 * hp_ratio), 10))
                hp_text = f"PV: {unit.hp}/{unit.max_hp}" if hasattr(unit, 'max_hp') else f"PV: {unit.hp}"
                rendered = self.small_font.render(hp_text, True, COLORS["ui_text"])
                self.screen.blit(rendered, (250, self.hud_y + 55))

                # Stats
                stats_text = f"Dégâts: {unit.damage} | Armure: {unit.armor} | Portée: {unit.range}" if hasattr(unit, 'damage') else ""
                rendered = self.small_font.render(stats_text, True, COLORS["ui_text"])
                self.screen.blit(rendered, (90, self.hud_y + 85))

                # Niveau et XP (ennemis tués + progression)
                if hasattr(unit, 'level'):
                    level_xp = ""
                    if hasattr(unit, 'xp') and hasattr(unit, 'xp_to_next') and unit.xp_to_next > 0:
                        pct = min(100, int(unit.xp / unit.xp_to_next * 100))
                        level_xp = f"| XP: {pct}%"
                    level_text = f"Niveau {unit.level} {level_xp} | Kills: {getattr(unit, 'kills', 0)}"
                    rendered = self.small_font.render(level_text, True, (255, 215, 0))
                    self.screen.blit(rendered, (90, self.hud_y + 105))
            else:
                # Multi-sélection
                rendered = self.font.render(f"{len(selected_units)} unités sélectionnées", True, COLORS["ui_text"])
                self.screen.blit(rendered, (90, self.hud_y + 10))

                # Barre de progression moyenne (simplifiée)
                avg_hp_ratio = sum(u.hp / u.max_hp for u in selected_units if hasattr(u, 'max_hp') and u.max_hp > 0) / len(selected_units) if any(hasattr(u, 'max_hp') and u.max_hp > 0 for u in selected_units) else 0
                hp_color = (255, 0, 0) if avg_hp_ratio < 0.3 else (0, 255, 0)
                pygame.draw.rect(self.screen, (100, 100, 100), (90, self.hud_y + 55, 150, 10))
                pygame.draw.rect(self.screen, hp_color, (90, self.hud_y + 55, int(150 * avg_hp_ratio), 10))
                rendered = self.small_font.render(f"PV moyen: {int(avg_hp_ratio * 100)}%", True, COLORS["ui_text"])
                self.screen.blit(rendered, (250, self.hud_y + 55))

        else:
            # Pas de sélection
            rendered = self.font.render("Sélectionnez une unité", True, COLORS["ui_text"])
            self.screen.blit(rendered, (self.screen.get_width() // 2 - 100, self.hud_y + 40))

    def draw_minimap(self, game_map, camera, units, buildings):
        """Dessine la minimap."""
        # Fond
        pygame.draw.rect(self.screen, (30, 30, 30), (self.minimap_x, self.minimap_y, self.minimap_size, self.minimap_size))
        pygame.draw.rect(self.screen, COLORS["ui_border"], (self.minimap_x, self.minimap_y, self.minimap_size, self.minimap_size), 2)

        # Échelle
        map_scale = self.minimap_size / (game_map.width * 32)

        # Dessiner les tuiles visibles (simplifié)
        for y in range(0, game_map.height, 4):
            for x in range(0, game_map.width, 4):
                tile = game_map.get_tile(x, y)
                if tile:
                    color = tile.get_color()
                    screen_x = self.minimap_x + int(x * 32 * map_scale)
                    screen_y = self.minimap_y + int(y * 32 * map_scale)
                    pygame.draw.rect(self.screen, color, (screen_x, screen_y, max(1, 32 * map_scale), max(1, 32 * map_scale)))

        # Dessiner les unités
        for unit in units:
            unit_color = COLORS["player_unit"] if unit.faction == "player" else COLORS["enemy_unit"]
            screen_x = self.minimap_x + int(unit.x * map_scale)
            screen_y = self.minimap_y + int(unit.y * map_scale)
            pygame.draw.circle(self.screen, unit_color, (screen_x, screen_y), 2)

        # Dessiner les bâtiments
        for building in buildings:
            building_color = COLORS["player_unit"] if building.faction == "player" else COLORS["enemy_unit"]
            screen_x = self.minimap_x + int(building.x * map_scale)
            screen_y = self.minimap_y + int(building.y * map_scale)
            pygame.draw.rect(self.screen, building_color, (screen_x - 2, screen_y - 2, 4, 4))

        # Zone visible de la caméra
        cam_x = self.minimap_x + int(camera.x * map_scale)
        cam_y = self.minimap_y + int(camera.y * map_scale)
        cam_w = int(self.screen.get_width() * map_scale)
        cam_h = int(self.screen.get_height() * map_scale)
        pygame.draw.rect(self.screen, (255, 255, 255), (cam_x, cam_y, cam_w, cam_h), 2)

    def minimap_rect(self) -> pygame.Rect:
        """Rectangle de la minimap (pour détecter un clic et déplacer la caméra)."""
        return pygame.Rect(self.minimap_x, self.minimap_y, self.minimap_size, self.minimap_size)

    _HERO_ROLE_NAMES = {"warrior": "Guerrier", "mage": "Mage", "archer": "Archer"}

    def _draw_hero_summon_buttons(self, game=None):
        """Panneau d'invocation des 3 héros de faction (bâtiment à héros sélectionné)."""
        from entities.hero_types import HERO_ORDER, HERO_SUMMON_COSTS, faction_hero_types
        if game is None or not getattr(game, "faction_id", None):
            return
        fid = game.faction_id
        roles = list(HERO_ORDER)
        types = faction_hero_types(fid)

        # Héros joueur vivants sur le terrain (pas de doublon possible).
        alive = set()
        for u in getattr(game, "units", []):
            if (getattr(u, "faction", "") == "player"
                    and getattr(u, "unit_type", "").startswith("hero_")
                    and getattr(u, "hp", 0) > 0):
                alive.add(getattr(u, "unit_type", ""))

        title = self.small_font.render("Héros (touches 1-3) :", True, (255, 215, 0))
        self.screen.blit(title, (10, self.hud_y + 12))

        start_x = 10
        y = self.hud_y + 42
        bw, bh = 112, 40
        for i, role in enumerate(roles):
            ut = types[i]
            name = self._HERO_ROLE_NAMES.get(role, role)
            cost = HERO_SUMMON_COSTS[role]
            x = start_x + i * (bw + 6)

            is_alive = ut in alive
            affordable = (game.economy.gold >= cost["gold"]
                          and game.economy.wood >= cost["wood"]
                          and game.economy.food >= cost["food"])
            if is_alive:
                color = (60, 130, 70)
            elif affordable:
                color = (50, 150, 50)
            else:
                color = (100, 100, 100)

            pygame.draw.rect(self.screen, color, (x, y, bw, bh))
            pygame.draw.rect(self.screen, COLORS["ui_border"], (x, y, bw, bh), 1)

            # Touche
            self.screen.blit(self.button_font.render(str(i + 1), True, (255, 255, 255)),
                             (x + 5, y + 4))
            # Nom
            self.screen.blit(self.small_font.render(name, True, (230, 230, 230)),
                             (x + 5, y + 20))
            # Coût (or / bois)
            cost_line = f"{cost['gold']}o {cost['wood']}b"
            self.screen.blit(self.small_font.render(cost_line, True, (200, 200, 200)),
                             (x + 60, y + 4))
            # Statut
            status = "Présent" if is_alive else ("Invoquer" if affordable else "Manque or")
            status_color = (180, 255, 180) if is_alive else ((180, 255, 180) if affordable else (255, 120, 120))
            self.screen.blit(self.small_font.render(status, True, status_color),
                             (x + 60, y + 20))

    def draw_production_buttons(self, economy, selected_units=None, selected_building=None,
                                production_system=None, faction=None, game=None):
        """Dessine les boutons de production - alignés en bas, filtres par faction."""
        # Si un bâtiment est sélectionné, montrer ses options
        if selected_building:
            # Bâtiment à héros : panneau d'invocation des 3 héros de faction.
            if selected_building.building_type == "hero_hall":
                self._draw_hero_summon_buttons(game)
                return
            unit_names = None
            unlocked_units = None
            # Si le jeu + faction sont fournis, afficher les unités de ce bâtiment
            if faction is not None and game is not None:
                all_units = faction.get_units_for_building(selected_building.building_type)
                # Bâtiments de recherche : montrer "Rechercher" au lieu des unités
                if not all_units:
                    unit_names = None
                else:
                    researched = game.tech_tree.unlocked_techs
                    unlocked_units = [u for u in all_units
                                      if faction.can_produce(u, game.buildings, researched)[0]]
                    # Trier : unités débloquées d'abord (touches 1...N), puis verrouillées
                    unit_names = unlocked_units + [u for u in all_units
                                                   if u not in unlocked_units]
            self._draw_building_actions(economy, selected_building, unit_names, unlocked_units)
            return

        # Noms français des unités
        unit_names = {
            "warrior": "Guerrier", "archer": "Archer", "knight": "Chevalier",
            "mage": "Mage", "healer": "Soigneur", "scout": "Eclaireur",
            "siege_engine": "Siege", "berserker": "Berserker",
            "ranger": "Ranger", "cannon": "Canon",
            }

        # Déterminer les unités produisibles (roster de faction si disponible)
        available = []
        if production_system is not None:
            available = production_system.get_available_units()
        else:
            available = ["worker", "builder", "warrior", "archer", "knight",
                         "mage", "healer", "scout"]

        # Associer une touche à chaque unité
        combat_units = [u for u in available if u not in ("worker", "builder")]
        worker_units = [u for u in available if u in ("worker", "builder")]

        buttons = []
        for i, utype in enumerate(combat_units[:6]):
            key = str(i + 1)
            c = production_system.UNIT_COSTS.get(utype, {}) if production_system else {}
            buttons.append((key, unit_names.get(utype, utype),
                            c.get("gold", 0), c.get("wood", 0), c.get("food", 0)))

        # Workers (W = Worker, J = Builder)
        for i, wtype in enumerate(worker_units):
            key = "W" if wtype == "worker" else "J"
            c = production_system.UNIT_COSTS.get(wtype, {}) if production_system else {}
            buttons.append((key, unit_names.get(wtype, wtype.capitalize()),
                            c.get("gold", 0), c.get("wood", 0), c.get("food", 0)))

        # Position alignée à gauche
        start_x = 10
        y = self.hud_y + 10
        button_width = 100
        button_height = 30

        for i, (key, name, gold, wood, food) in enumerate(buttons):
            x = start_x + i * (button_width + 5)

            # Vérifier si on peut produire
            can_afford = (economy.gold >= gold and economy.wood >= wood and economy.food >= food)

            color = (50, 150, 50) if can_afford else (100, 100, 100)
            pygame.draw.rect(self.screen, color, (x, y, button_width, button_height))
            pygame.draw.rect(self.screen, COLORS["ui_border"], (x, y, button_width, button_height), 1)

            # Touche
            rendered = self.button_font.render(key, True, COLORS["ui_text"])
            self.screen.blit(rendered, (x + 5, y + 5))

            # Nom
            name_rendered = self.small_font.render(name, True, COLORS["ui_text"])
            self.screen.blit(name_rendered, (x + 20, y + 8))

    def _draw_building_actions(self, economy, building, unit_names=None, unlocked_units=None):
        """Dessine les actions/productions disponibles pour un bâtiment."""
        # Panneau d'actions à gauche
        panel_x = 10
        panel_y = self.hud_y + 10
        panel_width = 250

        # Hauteur adaptée au nombre de boutons
        n_buttons = len(unit_names) if unit_names else 1
        panel_height = 90 + n_buttons * 22

        # Fond du panneau
        pygame.draw.rect(self.screen, (40, 40, 60), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, COLORS["ui_border"], (panel_x, panel_y, panel_width, panel_height), 2)

        # Titre
        title = building.building_type.replace("_", " ").title()
        font = pygame.font.Font(None, 16)
        text = font.render(f"{title} - Actions", True, (255, 215, 0))
        self.screen.blit(text, (panel_x + 10, panel_y + 5))

        unit_display = {
            "warrior": "Guerrier", "archer": "Archer", "knight": "Chevalier",
            "mage": "Mage", "healer": "Soigneur", "scout": "Eclaireur",
            "siege_engine": "Siege", "berserker": "Berserker",
            "ranger": "Ranger", "cannon": "Canon",
            "druid": "Druide",
            "worker": "Worker", "builder": "Builder",
        }

        # Boutons selon le type de bâtiment
        y = panel_y + 25
        button_width = 220
        button_height = 18

        # Bâtiment de production: afficher les unités produisibles
        if unit_names:
            for i, utype in enumerate(unit_names):
                name = unit_display.get(utype, utype)
                locked = unlocked_units is not None and utype not in unlocked_units
                color = (80, 80, 80) if locked else (50, 150, 50)
                pygame.draw.rect(self.screen, color, (panel_x + 10, y, button_width, button_height))
                suffix = " [VERR]" if locked else ""
                u_text = font.render(f"[{i+1}] {name}{suffix}", True, COLORS["ui_text"])
                self.screen.blit(u_text, (panel_x + 15, y + 1))
                y += button_height + 4

        # Bouton recherche (académie ou équivalent) - réservé aux bâtiments de recherche
        elif building.building_type == "academy":
            can_research = economy.gold >= 150 and economy.wood >= 100
            color = (50, 150, 50) if can_research else (100, 100, 100)
            pygame.draw.rect(self.screen, color, (panel_x + 10, y, button_width, button_height))
            pygame.draw.rect(self.screen, COLORS["ui_border"], (panel_x + 10, y, button_width, button_height), 1)
            text = font.render("Rechercher [T]", True, COLORS["ui_text"])
            self.screen.blit(text, (panel_x + 15, y + 3))

        # Battiments de récolte
        elif building.building_type == "collection":
            text = font.render("Dépôt: Workers", True, (200, 200, 200))
            self.screen.blit(text, (panel_x + 10, y))

        # Info sur le bâtiment
        info_y = y + 6
        hp_text = f"PV: {building.hp}/{building.max_hp}"
        text = font.render(hp_text, True, (150, 150, 150))
        self.screen.blit(text, (panel_x + 10, info_y))

    def draw_construction_buttons(self, economy, construction_system):
        """Dessine les boutons de construction - alignés en bas à droite."""
        buildings = [
            ("B", "Cabane", 100, 80, 0),
            ("F", "Ferme", 50, 100, 0),
            ("T", "Caserne", 200, 150, 50),
            ("L", "Scierie", 100, 50, 0),
            ("W", "Mur", 30, 50, 0),
        ]

        # Position alignée à droite (avant la minimap)
        start_x = self.minimap_x - 300
        y = self.hud_y + 10
        button_width = 60
        button_height = 30

        for i, (key, name, gold, wood, food) in enumerate(buildings):
            x = start_x + i * (button_width + 5)

            # Vérifier si on peut construire
            can_afford = (economy.gold >= gold and economy.wood >= wood and economy.food >= food)

            color = (50, 150, 50) if can_afford else (100, 100, 100)
            pygame.draw.rect(self.screen, color, (x, y, button_width, button_height))
            pygame.draw.rect(self.screen, COLORS["ui_border"], (x, y, button_width, button_height), 1)

            # Touche
            rendered = self.button_font.render(key, True, COLORS["ui_text"])
            self.screen.blit(rendered, (x + 20, y + 5))

            # Nom
            name_rendered = self.small_font.render(name, True, COLORS["ui_text"])
            self.screen.blit(name_rendered, (x + 5, y + 18))

    def draw_production_queue(self, production_system):
        """Dessine la file de production (unités en cours de fabrication)."""
        if not production_system or not getattr(production_system, 'queue', None):
            return

        y = self.hud_y + 50
        bar_width = 200
        bar_height = 6
        x = self.screen.get_width() // 2 - bar_width // 2
        font = pygame.font.Font(None, 15)

        for entry in production_system.queue[:3]:
            pct = min(1.0, entry["progress"] / entry["total"]) if entry["total"] else 0.0
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 200, 255), (x, y, int(bar_width * pct), bar_height))
            text = f"Production: {entry['unit_type']} ({int(pct * 100)}%)"
            rendered = font.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (x, y + bar_height + 2))
            y += bar_height + 16

    def draw_construction_progress(self, construction_system):
        """Dessine la progression des constructions en cours."""
        if not construction_system.construction_sites:
            return

        y = self.hud_y + 50
        for site in construction_system.construction_sites:
            # Barre de progression
            bar_width = 200
            bar_height = 15
            x = self.screen.get_width() // 2 - bar_width // 2

            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (x, y, int(bar_width * site.progress), bar_height))

            # Texte
            text = f"Construction: {site.building_type} ({int(site.progress * 100)}%)"
            rendered = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (x, y + bar_height + 5))

            y += 30

    def draw_skill_buttons(self, hero):
        """Dessine les boutons de compétences du héros."""
        if not hero or not hasattr(hero, 'skills'):
            return

        x = self.screen.get_width() // 2 - 160
        y = self.hud_y + 10
        font = pygame.font.Font(None, 16)
        small_font = pygame.font.Font(None, 14)

        for i, skill in enumerate(hero.skills):
            sx = x + i * 85
            # Couleur selon disponibilité
            can_use = (hero.mana >= skill['cost'] and skill['cooldown'] <= 0)
            color = (50, 150, 50) if can_use else (80, 80, 80)
            pygame.draw.rect(self.screen, color, (sx, y, 75, 28))
            pygame.draw.rect(self.screen, COLORS["ui_border"], (sx, y, 75, 28), 1)

            # Touche (Espace, Q, E, R)
            keys = ["[Esp]", "[Q]", "[E]", "[R]"]
            key_rendered = small_font.render(keys[i], True, (255, 255, 255))
            self.screen.blit(key_rendered, (sx + 3, y + 3))

            # Nom de la compétence
            name_rendered = small_font.render(skill['name'][:8], True, (200, 200, 200))
            self.screen.blit(name_rendered, (sx + 3, y + 15))

            # Coût en mana
            mana_color = (100, 100, 255) if can_use else (150, 50, 50)
            mana_text = small_font.render(f"MP:{skill['cost']}", True, mana_color)
            self.screen.blit(mana_text, (sx + 55, y + 8))
