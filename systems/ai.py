"""
Mountain_Roy - Enemy AI System (Intelligence Artificielle Ennemie)
Étape 8: IA pour la faction "La Légion des Cendres"
"""

import random
import pygame
from entities.unit_types import create_unit
from entities.building import TownHall, Barracks, Farm, Tower, CollectionBuilding, HeroHall


DEFAULT_ENEMY_CONFIG = {
    "town_hall": True,
    "barracks": True,
    "farms": 3,
    "collection": True,
    "towers": 0,
    "workers": 4,
    "warriors": 3,
    "gold": 200,
    "wood": 150,
    "food": 100,
}


class EnemyAI:
    """Intelligence artificielle pour l'ennemi."""
    
    def __init__(self, game):
        self.game = game
        self.difficulty = "normal"  # easy, normal, hard
        
        # États de l'IA
        self.state = "gather"  # gather, develop, build, produce, attack, defend
        self.state_timer = 0
        
        # Cibles
        self.target_base = None
        self.attack_group = []
        
        # Développement : cibles d'économie / armée / défense selon difficulté.
        self._set_development_targets()
        
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
            "hero_hall": {"gold": 180, "wood": 120, "food": 40},
            "farm": {"gold": 50, "wood": 100, "food": 0},
        }
    
    def _set_development_targets(self):
        """Définit les cibles de base d'économie / armée / défense selon difficulté.

        Ces cibles sont les BASES ; `_army_target()` et `_worker_target()`
        les augmentent avec le temps de mission (escalade) pour que l'IA ne
        plafonne jamais et continue de se développer face à un joueur qui
        accumule des ressources/units.
        """
        d = self.difficulty
        targets = {
            "easy":   {"workers": 7,  "army": 6,  "garrison": 2, "barracks": 2, "towers": 3},
            "normal": {"workers": 10, "army": 8,  "garrison": 3, "barracks": 3, "towers": 4},
            "hard":   {"workers": 14, "army": 12, "garrison": 4, "barracks": 4, "towers": 6},
        }
        self.dev = targets.get(d, targets["normal"])
        # Temps entre chaque micro-décision de développement (plus rapide en hard).
        self.dev_interval = {"easy": 1.2, "normal": 0.8, "hard": 0.5}.get(d, 1.0)
        self._dev_timer = 0.0

    def _mission_time(self):
        """Temps écoulé de la mission (secondes). Retourne 0 hors jeu."""
        return float(getattr(self.game, "mission_timer", 0) or 0)

    def _army_target(self):
        """Cible d'armée = base + escalade temporelle (armée +1 toutes les ~30s).

        L'IA grossit au fil du jeu : contre un joueur qui amasse 50 workers,
        elle finit par aligner une armée d'une taille comparable.
        """
        base = self.dev["army"]
        growth = int(self._mission_time() / 30.0)
        cap = None
        if self.difficulty == "easy":
            cap = 20
        elif self.difficulty == "normal":
            cap = 34
        else:
            cap = 50
        return min(cap, base + growth)

    def _worker_target(self):
        """Cible de workers = base + escalade temporelle (worker +1 toutes les ~45s)."""
        base = self.dev["workers"]
        growth = int(self._mission_time() / 45.0)
        return min(24, base + growth)
    
    def update(self, dt: float):
        """Met à jour l'IA (développement continu + état tactique périodique)."""
        self.state_timer += dt

        # Développement CONTINU : produire des workers et construire selon une
        # cadence rapide, indépendamment de l'état tactique choisi.
        self._dev_timer += dt
        if self._dev_timer >= self.dev_interval:
            self._dev_timer = 0.0
            # En fast-forward, l'IA fait plusieurs actions par tick pour suivre
            # le rythme du joueur (qui peut spammer commandes manuellement).
            time_scale = getattr(self.game, 'time_scale', 1)
            actions = max(1, int(time_scale // 2))
            for _ in range(actions):
                self._develop()

        # Changer d'état tactique périodiquement
        if self.state_timer > 3.0:
            self.state_timer = 0
            self._choose_state()
            # Rappeler les unités blessées après changement d'état
            self._retreat_low_hp_units()

        # Invoquer les héros ennemis dès qu'un bâtiment à héros est disponible
        self._manage_heroes()

        # Exécuter l'état actuel
        if self.state == "gather":
            self._gather_resources(dt)
        elif self.state == "develop":
            self._produce_workers()
        elif self.state == "build":
            self._build_structures()
        elif self.state == "produce":
            self._produce_units()
        elif self.state == "attack":
            self._attack_player()
        elif self.state == "defend":
            self._defend_base()

    # ------------------------------------------------------------------
    # Développement continu — l'IA fait grossir son économie et sa base.
    # ------------------------------------------------------------------
    def _enemy_buildings(self, btype=None):
        bs = [b for b in self.game.buildings if getattr(b, "faction", "") == "enemy"]
        if btype:
            return [b for b in bs if b.building_type == btype]
        return bs

    def _enemy_pop(self):
        return len([u for u in self.game.units if u.faction == "enemy"])

    def _develop(self):
        """Une micro-décision de développement par tick.

        Priorité : workers (économie scaling) -> armée (jusqu'à `_army_target()`)
        -> fermes si la production d'unités est bloquée par le cap de population
        -> casernes -> tours défensives.
        """
        ec = self.game.enemy_economy

        # 0) En dessous de la moitié des workers visés : pousser l'économie.
        half_workers = self._worker_target() * 0.5
        if len(self._enemy_workers()) < half_workers:
            self._produce_workers()
            return

        # 1) Armée : produire un combattant si on est sous la cible.
        if len(self._enemy_combat()) < self._army_target():
            produced = self._produce_units()
            if produced:
                return
            # Si rien produit : cap de population atteint OU pas assez d'or.
            # Construire une ferme pour lever le cap (débloque la production).
            if ec.gold >= 150:
                self._build_farms_as_needed()
                return

        # 2) Compléter les workers entre 50% et 100% de la cible.
        if len(self._enemy_workers()) < self._worker_target():
            self._produce_workers()
            return

        # 3) Construire fermes / casernes / tours.
        self._build_farms_as_needed()
        self._build_extra_barracks()
        self._build_towers()

        # 4) Ressources excédentaires : accumuler de l'armée au-delà de la cible
        #    pour exercer une pression continue sur le joueur.
        if len(self._enemy_combat()) < self._army_target() + 6:
            self._produce_units()

    def _produce_workers(self):
        """Produit un worker ennemi depuis le town hall si les ressources le permettent."""
        # Un worker par tick max (production limitée par l'économie).
        ec = self.game.enemy_economy
        townhalls = self._enemy_buildings("town_hall")
        if not townhalls:
            return
        hall = townhalls[0]
        cost = {"gold": 30, "wood": 15, "food": 5}
        if not (ec.gold >= cost["gold"] and ec.wood >= cost["wood"] and ec.food >= cost["food"]):
            return
        # Garder une réserve pour la production d'unités.
        if ec.gold < 120:
            return
        # Ne pas dépasser le cap de population (les fermes l'augmentent).
        if self._enemy_pop() >= self.game.economy.get_max_population(self._enemy_buildings()):
            return
        worker = create_unit("worker", hall.x + 40, hall.y + 60, "enemy")
        worker.game = self.game  # nécessaire pour la récolte/dépôt
        self.game.units.append(worker)
        ec.gold -= cost["gold"]
        ec.wood -= cost["wood"]
        ec.food -= cost["food"]

    def _can_afford(self, cost) -> bool:
        ec = self.game.enemy_economy
        return (ec.gold >= cost.get("gold", 0) and ec.wood >= cost.get("wood", 0)
                and ec.food >= cost.get("food", 0))

    def _try_place(self, btype, building_cls, max_jitter=5):
        """Place un bâtiment ennemi près d'un bâtiment existant si possible.

        Retourne True si placé (bâtiment ajouté + coût débité).
        """
        ec = self.game.enemy_economy
        cost = self.building_costs.get(btype)
        if cost is None or not self._can_afford(cost):
            return False
        # Base pour le placement : le town hall si présent, sinon n'importe quel bâtiment.
        base = None
        th = self._enemy_buildings("town_hall")
        if th:
            base = th[0]
        elif self._enemy_buildings():
            base = self._enemy_buildings()[0]
        if base is None:
            return False
        for _ in range(max_jitter):
            ox = random.choice([-90, -60, 60, 90, 0, 120])
            oy = random.choice([-90, -60, 60, 90, 0, 120])
            new_x, new_y = base.x + ox, base.y + oy
            ok, _ = self.game.construction_system.validate_build_position(btype, new_x, new_y)
            if not ok:
                continue
            nb = building_cls(new_x, new_y, "enemy")
            self.game.buildings.append(nb)
            ec.gold -= cost.get("gold", 0)
            ec.wood -= cost.get("wood", 0)
            ec.food -= cost.get("food", 0)
            return True
        return False

    def _build_farms_as_needed(self):
        """Construit des fermes pour que le cap de population couvre la cible.

        Au lieu d'attendre d'être à 80% du cap (ce qui bloquait l'IA), elle
        construit des fermes en AVANCE pour que max_pop >= workers + armée +
        marge. Nécessaire pour que l'armée puisse grossir avec l'escalade.
        """
        max_pop = self.game.economy.get_max_population(self._enemy_buildings())
        needed = self._worker_target() + self._army_target() + 6
        # Trop de fermes coûtent cher : ajouter mais rester raisonnable.
        needed = min(needed, 70)
        if max_pop < needed:
            self._try_place("farm", Farm)

    def _build_extra_barracks(self):
        """Construit des casernes supplémentaires pour produire plus vite."""
        barracks_count = len(self._enemy_buildings("barracks"))
        if barracks_count < self.dev["barracks"]:
            self._try_place("barracks", Barracks)

    def _build_towers(self):
        """Construit des tours défensives autour de la base."""
        towers = len(self._enemy_buildings("tower"))
        if towers < self.dev["towers"] and len(self._enemy_combat()) >= 2:
            self._try_place("tower", Tower)
    
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
        """Choisit l'état tactique suivant (proactif, dépend de la difficulté).

        L'IA ne reste plus passive : elle développe son économie au début,
        produit une armée, puis ATTAQUE dès qu'elle atteint sa cible d'armée —
        même si elle n'est pas numériquement supérieure au joueur. Elle défend
        quand le joueur la domine fortement.
        """
        enemy_combat = self._enemy_combat()
        player_combat = [u for u in self.game.units
                         if u.faction == "player"
                         and getattr(u, "unit_type", "") not in ("worker", "builder")
                         and getattr(u, "hp", 1) > 0]
        enemy_count = len(enemy_combat)
        player_count = len(player_combat)

        atk_target = self._army_target()
        # Agressivité : seuil d'attaque = ~2/3 de la cible (attaquer plus tôt)
        # en difficulté normale/difficile ; en facile on attend la cible pleine.
        aggr_threshold = atk_target
        if self.difficulty in ("normal", "hard"):
            aggr_threshold = max(3, int(atk_target * 0.66))

        # Le joueur épuise-t-il nos ressources (raiders de workers) ? Si oui,
        # défendre pour les chasser — sinon il draine toutes les mines/forêts.
        if self._player_raiding_resources():
            self.state = "defend"
            return

        # L'armée atteint son seuil -> attaquer (proactif, même à parité). Un
        # état "defend" actif reste prioritaire (le joueur assiège la base).
        if self.state != "defend" and enemy_count >= aggr_threshold:
            self.state = "attack"
        elif len(self._enemy_workers()) < self._worker_target() and enemy_count < atk_target:
            self.state = random.choice(["develop", "gather"])
            return
        elif player_count > enemy_count * 1.5:
            # Le joueur domine largement -> protéger la base + reconstruire.
            self.state = "defend"
        elif enemy_count < atk_target * 0.5:
            self.state = "produce"
        elif self.state == "attack":
            # En pleine attaque mais moins de combat que la cible : refaire le plein.
            self.state = "produce"
        else:
            self.state = random.choice(["produce", "build", "develop", "gather"])

    def _retreat_low_hp_units(self):
        """Rappel les unités blessées (< 30% PV) vers la base ennemie."""
        combat = self._enemy_combat()
        if not combat:
            return
        base = self._enemy_base_pos()
        if base is None:
            return
        retreated = 0
        for unit in combat[:]:
            hp_ratio = getattr(unit, 'hp', unit.max_hp) / getattr(unit, 'max_hp', 100)
            if hp_ratio < 0.3 and unit.target is None:
                # Rappeler vers la base
                self.game.movement_system.move_to(unit, base[0], base[1])
                retreated += 1
        if retreated > 0:
            self.audio_events.on_order_given("retreat")

    def _player_raiding_resources(self):
        """True si des workers/builders joueur récoltent nos nodes de ressources.

        Un node appartient de fait à l'ennemi quand il est proche de sa base.
        Si le joueur envoie ses récolteurs dessus, il les draine : l'IA doit
        réagir (défendre) plutôt que de continuer à attaquer/produire.
        """
        base = self._enemy_base_pos()
        if base is None:
            return False
        bx, by = base
        # Nodes proches de la base ennemie = ressource à protéger.
        nearby = [n for n in getattr(self.game, "resource_nodes", [])
                  if not getattr(n, "is_depleted", lambda: False)()
                  and ((n.x - bx) ** 2 + (n.y - by) ** 2) ** 0.5 < 600]
        if not nearby:
            return False
        nset = set(id(n) for n in nearby)
        for u in self.game.units:
            if u.faction == "player" and getattr(u, "unit_type", "") in ("worker", "builder"):
                if getattr(u, "target_resource", None) is not None and id(u.target_resource) in nset:
                    return True
        return False
    
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
        """Construit la caserne puis un bâtiment à héros (chaque joueur)."""
        ec = self.game.enemy_economy
        # Priorité : barraques d'abord, puis bâtiment à héros pour invoquer les héros.
        for btype in ("barracks", "hero_hall"):
            if any(b.building_type == btype and getattr(b, "faction", "") == "enemy"
                   for b in self.game.buildings):
                continue  # déjà présent
            cost = self.building_costs.get(btype)
            if cost is None:
                continue
            if not (ec.gold >= cost["gold"] and ec.wood >= cost["wood"]
                    and ec.food >= cost["food"]):
                continue  # pas assez de ressources : essayer le bâtiment suivant
            enemy_units = [u for u in self.game.units if u.faction == "enemy"]
            if not enemy_units:
                break
            base = enemy_units[0]
            for offset_x, offset_y in [(64, 0), (0, 64), (-64, 0), (0, -64), (64, 64)]:
                new_x = base.x + offset_x
                new_y = base.y + offset_y

                ok, _ = self.game.construction_system.validate_build_position(btype, new_x, new_y)
                if not ok:
                    continue
                building_cls = Barracks if btype == "barracks" else HeroHall
                new_building = building_cls(new_x, new_y, "enemy")
                self.game.buildings.append(new_building)
                ec.gold -= cost["gold"]
                ec.wood -= cost["wood"]
                ec.food -= cost["food"]
                return  # un bâtiment par défaut : passer la main
    
    def _manage_heroes(self):
        """Invoque les héros ennemis (3/faction) depuis un bâtiment à héros.

        Chaque joueur peut invoquer ses 3 héros : l'IA fait de même quand elle
        possède un hero_hall et les ressources — sans dédoubler un héros vivant.
        """
        from entities.hero_types import (HERO_ORDER, HERO_SUMMON_COSTS,
                                         faction_hero_types, create_faction_hero)
        fid = getattr(self.game, "faction_id", None)
        if not fid:
            return
        halls = [b for b in self.game.buildings
                 if b.building_type == "hero_hall" and getattr(b, "faction", "") == "enemy"]
        if not halls:
            return
        hall = halls[0]
        ec = self.game.enemy_economy
        types = faction_hero_types(fid)
        alive = {u.unit_type for u in self.game.units
                 if getattr(u, "faction", "") == "enemy"
                 and getattr(u, "unit_type", "").startswith("hero_")
                 and getattr(u, "hp", 0) > 0}
        for i, role in enumerate(HERO_ORDER):
            unit_type = types[i]
            if unit_type in alive:
                continue
            cost = HERO_SUMMON_COSTS[role]
            if (ec.gold >= cost["gold"] and ec.wood >= cost["wood"]
                    and ec.food >= cost["food"]):
                hero = create_faction_hero(fid, role, hall.x + 40, hall.y, side="enemy")
                hero.game = self.game
                self.game.units.append(hero)
                ec.gold -= cost["gold"]
                ec.wood -= cost["wood"]
                ec.food -= cost["food"]
                return  # un héros par tick
    
    def _produce_units(self) -> bool:
        """Produit des unités (paye les vraies ressources ennemies).

        Retourne True si une unité a été produite (utile pour savoir si le
        dev doit construire une ferme ensuite), sinon False.
        """
        # Trouver une caserne ennemie
        barracks = [b for b in self.game.buildings if b.building_type == "barracks" and b.faction == "enemy"]
        
        if not barracks:
            return False

        ec = self.game.enemy_economy

        # Cap de population : parité avec la règle du joueur (fermes).
        enemy_buildings = [b for b in self.game.buildings if b.faction == "enemy"]
        max_pop = self.game.economy.get_max_population(enemy_buildings)
        pop = len([u for u in self.game.units if u.faction == "enemy"])
        if pop >= max_pop:
            return False

        # Préférer l'unité de combat la plus chère abordable ; sinon descendre.
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
                return True
        # Aucune unité abordable : on ne produit rien (économie intacte).
        return False
    
    def _attack_player(self):
        """Attaque le joueur de façon TACTIQUE (jamais les workers).

        - Choisit UNE cible stratégique pour toute l'armée (bâtiment de
          production joueur prioritaire, sinon hôtel de ville, sinon unités).
        - Concentre l'armée dessus au lieu d'éparpiller chaque unité sur la
          cible la plus proche.
        - Garde une petite garnison en défense de la base pendant l'attaque.
        """
        enemy_units = self._enemy_combat()
        if not enemy_units:
            return

        # Cible stratégique commune pour la concentration.
        target = self._strategic_player_target()
        if target is None:
            return

        # Le gros de l'armée attaque la cible stratégique.
        assault = enemy_units[:]
        garrison_size = self.dev.get("garrison", 2)
        if len(assault) > garrison_size:
            # Les unités déjà proches de la base défendent plutôt.
            base = self._enemy_base_pos()
            if base is not None:
                proximity = sorted(enemy_units,
                                   key=lambda u: ((u.x - base[0]) ** 2 + (u.y - base[1]) ** 2) ** 0.5)
                garrison = proximity[:garrison_size]
                assault = [u for u in enemy_units if u not in garrison]
                # La garnison ne part pas au combat.
                for g in garrison:
                    if g.target is None:
                        g.target = None  # reste en place (défense passive)
            if not assault:
                assault = enemy_units[garrison_size:]

        for unit in assault:
            self._order_attack(unit, target)

    def _enemy_base_pos(self):
        th = self._enemy_buildings("town_hall")
        if th:
            return (th[0].x, th[0].y)
        if self._enemy_buildings():
            b = self._enemy_buildings()[0]
            return (b.x, b.y)
        return None

    def _strategic_player_target(self):
        """Choisit la cible stratégique la plus précieuse du joueur.

        Priorité : bâtiments de production -> hôtel de ville -> unité ennemie
        la plus proche de l'armée. Toujours affecter l'armée sur une cible
        commune (concentration de force).
        """
        PROD = ("barracks", "workshop", "human_barracks", "orc_war_hut",
                "elf_ranger_lodge", "dwarf_forge", "academy", "dock")
        # 1) Bâtiment de production joueur, le plus proche de l'armée ennemie.
        prod = [b for b in self.game.buildings
                if b.faction == "player" and b.building_type in PROD]
        if prod:
            return min(prod, key=lambda b: self._dist_to_army(b.x, b.y))
        # 2) Hôtel de ville joueur (coup dur).
        th = [b for b in self.game.buildings
              if b.faction == "player" and b.building_type == "town_hall"]
        if th:
            return min(th, key=lambda b: self._dist_to_army(b.x, b.y))
        # 3) Sinon le premier bâtiment joueur atteignable.
        pb = [b for b in self.game.buildings if b.faction == "player"]
        if pb:
            return min(pb, key=lambda b: self._dist_to_army(b.x, b.y))
        # 4) En dernier recours : l'unité joueur la plus proche de l'armée.
        players = [u for u in self.game.units if u.faction == "player"]
        if players:
            return min(players, key=lambda u: self._dist_to_army(u.x, u.y))
        return None

    def _dist_to_army(self, x, y):
        """Distance entre un point et la première unité de combat ennemie."""
        combat = self._enemy_combat()
        if not combat:
            return float('inf')
        anchor = combat[0]
        return ((x - anchor.x) ** 2 + (y - anchor.y) ** 2) ** 0.5
    
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
    
    def _enemy_config(self):
        """Config du camp ennemi : celle de la mission courante, sinon la valeur par défaut."""
        mission = getattr(self.game, "current_mission", None)
        cfg = getattr(mission, "enemy_config", None)
        return cfg if cfg else DEFAULT_ENEMY_CONFIG

    def initialize_enemy_base(self, config: dict | None = None):
        """Initialise la base ennemie selon une config de mission.

        `config` (ou enemy_config de la mission courante, sinon DEFAULT_ENEMY_CONFIG)
        détermine la composition du camp : bâtiments (town hall, caserne, fermes,
        tours, cabane de récolte) et unités (ouvriers, guerriers), ainsi que les
        ressources de départ de l'économie ennemie. Permet une difficulté croissante
        au fil des missions.
        """
        cfg = config if config is not None else self._enemy_config()
        base_x = 70 * 32
        base_y = 70 * 32

        if cfg.get("town_hall", True):
            self.game.buildings.append(TownHall(base_x, base_y, "enemy"))
        if cfg.get("barracks", True):
            self.game.buildings.append(Barracks(base_x - 80, base_y, "enemy"))
        for i in range(cfg.get("farms", 0)):
            self.game.buildings.append(Farm(base_x + 60 + i * 50, base_y + 40, "enemy"))
        if cfg.get("collection", True):
            self.game.buildings.append(CollectionBuilding(base_x + 120, base_y - 40, "enemy"))
        for i in range(cfg.get("towers", 0)):
            self.game.buildings.append(Tower(base_x - 120 - i * 40, base_y, "enemy"))

        for i in range(cfg.get("workers", 0)):
            worker = create_unit("worker", base_x - 20 - i * 24, base_y + 60 + i * 16, "enemy")
            worker.game = self.game  # nécessaire pour la récolte (drop-off)
            self.game.units.append(worker)
        for i in range(cfg.get("warriors", 0)):
            unit = create_unit("warrior", base_x + 40 + i * 40, base_y + 90 + (i % 2) * 24,
                               "enemy", game=self.game)
            self.game.units.append(unit)

        ec = getattr(self.game, "enemy_economy", None)
        if ec is not None:
            ec.gold = cfg.get("gold", ec.gold)
            ec.wood = cfg.get("wood", ec.wood)
            ec.food = cfg.get("food", ec.food)
