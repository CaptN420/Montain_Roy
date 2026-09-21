"""
Mountain_Roy - Enemy AI System (Intelligence Artificielle Ennemie)
Étape 8: IA pour la faction "La Légion des Cendres"
"""

import random
import pygame
from entities.unit_types import create_unit
from entities.building import TownHall, Barracks


class EnemyAI:
    """Intelligence artificielle pour l'ennemi."""
    
    def __init__(self, game):
        self.game = game
        self.difficulty = "normal"  # easy, normal, hard
        
        # États de l'IA
        self.state = "gather"  # gather, build, produce, attack, defend
        self.state_timer = 0
        
        # Cibles
        self.target_base = None
        self.attack_group = []
        
        # L'IA utilise maintenant les vraies ressources du jeu
        # Plus de ressources virtuelles isolées
        
        # Coûts de production IA
        self.unit_costs = {
            "warrior": {"gold": 50, "wood": 0, "food": 10},
            "archer": {"gold": 40, "wood": 20, "food": 5},
            "knight": {"gold": 100, "wood": 50, "food": 20},
            "mage": {"gold": 80, "wood": 40, "food": 10},
        }
        
        self.building_costs = {
            "barracks": {"gold": 150, "wood": 100, "food": 20},
            "tower": {"gold": 100, "wood": 100, "food": 10},
        }
    
    def update(self, dt: float):
        """Met à jour l'IA."""
        self.state_timer += dt
        
        # Changer d'état périodiquement
        if self.state_timer > 5.0:
            self.state_timer = 0
            self._choose_state()
        
        # Exécuter l'état actuel
        if self.state == "gather":
            self._gather_resources(dt)
        elif self.state == "build":
            self._build_structures()
        elif self.state == "produce":
            self._produce_units()
        elif self.state == "attack":
            self._attack_player()
        elif self.state == "defend":
            self._defend_base()
    
    # ------------------------------------------------------------------
    # Filtres de population ennemie — évite de confondre récolte et combat.
    # ------------------------------------------------------------------
    def _enemy_workers(self):
        """Unités ennemies capables de récolter (worker/builder)."""
        return [u for u in self.game.units
                if u.faction == "enemy"
                and getattr(u, "unit_type", "") in ("worker", "builder")]

    def _enemy_combat(self):
        """Unités ennemies de combat (exclut workers/builders, et les morts)."""
        return [u for u in self.game.units
                if u.faction == "enemy"
                and getattr(u, "unit_type", "") not in ("worker", "builder")
                and getattr(u, "hp", 1) > 0]

    def _order_attack(self, attacker, target):
        """Ordonne à une unité de combat d'attaquer une cible."""
        if hasattr(self.game, "movement_system") and self.game.movement_system is not None:
            self.game.movement_system.attack_target(attacker, target)
        else:
            attacker.target = target

    def _choose_state(self):
        """Choisit l'état suivant."""
        # Compter les unités ennemies
        enemy_count = len([u for u in self.game.units if u.faction == "enemy"])
        player_count = len([u for u in self.game.units if u.faction == "player"])
        
        # Déterminer l'état basé sur la situation
        if enemy_count < 3:
            self.state = "produce"
        elif player_count > enemy_count * 1.5:
            self.state = "attack"
        else:
            self.state = random.choice(["gather", "build", "produce"])
    
    def _gather_resources(self, dt: float):
        """Fait récolter les unités de récolte ennemies (workers/builders)."""
        # SEULEMENT les récolteurs sans cible de récolte déjà assignée.
        workers = [u for u in self._enemy_workers()
                   if getattr(u, "target_resource", None) is None
                   and not getattr(u, "carrying", False)]

        if workers:
            # Trouver une ressource proche
            for node in self.game.resource_nodes:
                if getattr(node, "is_depleted", lambda: False)():
                    continue
                
                # Trouver l'ouvrier le plus proche
                closest_worker = None
                min_distance = float('inf')
                
                for worker in workers:
                    dx = worker.x - node.x
                    dy = worker.y - node.y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_worker = worker
                
                if closest_worker:
                    # Déplacer vers la ressource
                    if hasattr(self.game, "movement_system") and self.game.movement_system is not None:
                        self.game.movement_system.move_to(closest_worker, node.x, node.y)
                    closest_worker.target_resource = node
                    break
    
    def _build_structures(self):
        """Construit des structures."""
        # Vérifier si on peut construire une caserne avec les ressources ennemies
        cost = self.building_costs.get("barracks", {"gold": 150, "wood": 100, "food": 20})
        ec = self.game.enemy_economy

        if not (ec.gold >= cost["gold"] and
                ec.wood >= cost["wood"] and
                ec.food >= cost["food"]):
            return

        # Trouver un emplacement proche d'une unité ennemie
        enemy_units = [u for u in self.game.units if u.faction == "enemy"]
        if not enemy_units:
            return

        base = enemy_units[0]
        # Essayer plusieurs positions pour éviter les chevauchements
        for offset_x, offset_y in [(64, 0), (0, 64), (-64, 0), (0, -64), (64, 64)]:
            new_x = base.x + offset_x
            new_y = base.y + offset_y

            # Valider la position via le système de construction
            ok, _ = self.game.construction_system.validate_build_position("barracks", new_x, new_y)
            if ok:
                # Créer le bâtiment
                new_building = Barracks(new_x, new_y, "enemy")
                self.game.buildings.append(new_building)

                # Déduire les ressources ennemies
                ec.gold -= cost["gold"]
                ec.wood -= cost["wood"]
                ec.food -= cost["food"]
                return
    
    def _produce_units(self):
        """Produit des unités (paye les vraies ressources ennemies)."""
        # Trouver une caserne ennemie
        barracks = [b for b in self.game.buildings if b.building_type == "barracks" and b.faction == "enemy"]
        
        if not barracks:
            return

        ec = self.game.enemy_economy

        # Cap de population : parité avec la règle du joueur (fermes).
        enemy_buildings = [b for b in self.game.buildings if b.faction == "enemy"]
        max_pop = self.game.economy.get_max_population(enemy_buildings)
        pop = len([u for u in self.game.units if u.faction == "enemy"])
        if pop >= max_pop:
            return

        # Préférer l'unité de combat la plus chère abordable ; sinon descendre.
        # (l'ancien code `random.choice` abandonnait toute production si le
        #  coût tiré était inabordable, même quand un guerrier passait)
        unit_types = ["knight", "mage", "archer", "warrior"]
        for unit_type in unit_types:
            cost = self.unit_costs.get(unit_type)
            if cost is None:
                continue
            if (ec.gold >= cost["gold"] and
                    ec.wood >= cost["wood"] and
                    ec.food >= cost["food"]):
                barracks_unit = barracks[0]
                new_unit = create_unit(unit_type, barracks_unit.x, barracks_unit.y, "enemy",
                                       game=self.game)
                self.game.units.append(new_unit)
                # Déduire les ressources ennemies
                ec.gold -= cost["gold"]
                ec.wood -= cost["wood"]
                ec.food -= cost["food"]
                return
        # Aucune unité abordable : on ne produit rien (économie intacte).
    
    def _attack_player(self):
        """Attaque le joueur avec les unités de combat ennemies (jamais les workers)."""
        # Trouver les unités de combat ennemies
        enemy_units = self._enemy_combat()
        
        if not enemy_units:
            return
        
        # Trouver une cible (unité ou bâtiment joueur)
        targets = [u for u in self.game.units if u.faction == "player"]
        targets += [b for b in self.game.buildings if b.faction == "player"]
        
        if not targets:
            return
        
        # Attaquer la cible la plus proche
        for unit in enemy_units:
            closest_target = None
            min_distance = float('inf')
            
            for target in targets:
                dx = target.x - unit.x
                dy = target.y - unit.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_target = target
            
            if closest_target:
                self._order_attack(unit, closest_target)
    
    def _defend_base(self):
        """Défend la base ET les nodes de ressources ennemis des menaces joueur.

        Signale une menace toute unité joueur à portée d'un point d'intérêt
        ennemi (nodes de ressources non épuisés + Town Hall). Seules les
        unités de combat ennemis répondent — les workers restent à récolter.
        """
        combat_units = self._enemy_combat()
        if not combat_units:
            return

        # Points d'intérêt ennemis à protéger : nodes de ressources + base.
        interest = []
        for node in getattr(self.game, "resource_nodes", []):
            if not getattr(node, "is_depleted", lambda: False)():
                interest.append((node.x, node.y))
        for b in self.game.buildings:
            if b.faction == "enemy" and b.building_type == "town_hall":
                interest.append((b.x, b.y))
        if not interest:
            return

        THREAT_RADIUS = 250.0

        # Menaces = unités joueur proches d'un point d'intérêt ennemi.
        threats = []
        for u in self.game.units:
            if u.faction != "player":
                continue
            for (ix, iy) in interest:
                d = ((ix - u.x) ** 2 + (iy - u.y) ** 2) ** 0.5
                if d < THREAT_RADIUS:
                    threats.append(u)
                    break

        if not threats:
            return

        # Chaque unité de combat attaque la menace la plus proche.
        for unit in combat_units:
            if getattr(unit, "target_resource", None) is not None or getattr(unit, "carrying", False):
                continue  # ne pas rappeler un récolteur utilisé en urgence
            closest_threat = None
            min_distance = float('inf')
            for threat in threats:
                d = ((threat.x - unit.x) ** 2 + (threat.y - unit.y) ** 2) ** 0.5
                if d < min_distance:
                    min_distance = d
                    closest_threat = threat
            if closest_threat:
                self._order_attack(unit, closest_threat)
    
    def initialize_enemy_base(self):
        """Initialise la base ennemie."""
        # Créer un bâtiment principal ennemi
        enemy_townhall = TownHall(70 * 32, 70 * 32, "enemy")
        self.game.buildings.append(enemy_townhall)
        
        # Créer quelques unités ennemies
        for i in range(3):
            enemy_unit = create_unit("warrior", 
                                    70 * 32 + i * 32, 
                                    70 * 32 + 32, 
                                    "enemy")
            self.game.units.append(enemy_unit)
