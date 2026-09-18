"""
Mountain_Roy - Worker Unit (Ouvrier avec récolte)
Version améliorée: Assignment aux mines, mode bucheron
"""

import pygame
import random
from entities.unit import Unit


class Worker(Unit):
    """Ouvrier - peut récolter des ressources et les rapporter."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "worker"
        self.max_hp = 60
        self.hp = self.max_hp
        self.damage = 5
        self.armor = 1
        self.speed = 45
        self.range = 32
        self.attack_speed = 1.0
        self.radius = 12

        # Référence au jeu (pour accéder à l'économie)
        self.game = None

        # Capacité de récolte
        self.can_gather = True
        self.carrying = False
        self.carry_amount = 0
        self.max_carry = 15  # Augmenté pour porter plus

        # Système de fatigue et multi-ressources
        self.fatigue_timer = 0.0  # Temps depuis le dernier dépôt
        self.fatigue_duration = 3.0  # Temps de fatigue après un dépôt
        self.carrying_types = []  # Types de ressources actuellement portés
        self.max_carry_types = 2  # Max 2 types différents avant fatigue

        # Hyper mode (rare) - peut porter les 3 types si disponibles
        self.hyper_mode = False
        self.hyper_timer = 0.0
        self.hyper_duration = 10.0  # Durée du hyper mode

        # Cible de récolte
        self.target_resource = None
        self.drop_off_point = None  # Point de dépôt (Town Hall ou bâtiment)

        # Pour la compatibilité avec le système de jeu
        self.carry_resources = True  # Marqueur pour le système de jeu

        # Mode bucheron - peut passer à travers les forêts
        self.can_cut_trees = True  # Workers peuvent traverser les arbres

        # Coût de production
        self.cost = {
            "gold": 40,
            "wood": 20,
            "food": 5,
        }
        self.production_time = 2.5

        # Système de personnalité et humeur
        self.personality = self._generate_personality()
        self.mood = "neutral"  # neutral, happy, tired, motivated, demotivated
        self.mood_timer = 0.0
        self.motivation_level = 1.0  # 0.0 à 1.0
        self.chat_bubble = None  # Bubble de dialogue
        self.chat_timer = 0.0

        # Système de motivation de groupe
        self.can_motivate_others = False
        self.motivation_radius = 100  # Rayon de motivation

    def _generate_personality(self) -> dict:
        """Génère une personnalité aléatoire pour le worker."""
        traits = {
            "work_ethic": random.uniform(0.5, 1.5),  # Taux de travail
            "social": random.uniform(0.3, 1.2),  # Propension à interagir
            "optimism": random.uniform(0.4, 1.0),  # Optimisme
            "resilience": random.uniform(0.5, 1.0),  # Résistance à la fatigue
        }
        # Traits de personnalité textuels
        personality_types = [
            ("hardworking", "Je peux travailler toute la journée!"),
            ("lazy", "Pourquoi travailler si on peut dormir?"),
            ("optimist", "Tout ira bien, demain sera meilleur!"),
            ("pessimist", "Rien ne marche jamais..."),
            ("social", "On devrait tous se connaître!"),
            ("loner", "J'aime mon espace personnel."),
        ]
        primary_trait = random.choice(personality_types)
        return {
            "traits": traits,
            "primary": primary_trait[0],
            "phrase": primary_trait[1],
        }

    def update(self, dt: float):
        """Met à jour l'ouvrier."""
        # Mettre à jour la fatigue et le hyper mode
        self.fatigue_timer += dt
        if self.hyper_mode:
            self.hyper_timer += dt
            if self.hyper_timer >= self.hyper_duration:
                self.hyper_mode = False
                self.hyper_timer = 0.0

        # Mettre à jour l'humeur et la personnalité
        self._update_mood(dt)

        # Gestion des bulles de dialogue
        self.chat_timer += dt
        if self.chat_bubble and self.chat_timer > 4.0:
            self.chat_bubble = None
            self.chat_timer = 0.0

        # Même sélectionné, le worker doit finir son cycle: récolter →
        # porter au dépôt → déposer → retourner récolter automatiquement.

        # Si on porte des ressources mais pas de point de dépôt, en trouver un
        if self.carrying and not self.drop_off_point:
            self._find_drop_off_point()

        # Gestion du mouvement vers target (ressource ou drop-off)
        if self.is_moving and self.move_target:
            dx = self.move_target[0] - self.x
            dy = self.move_target[1] - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 5:
                self.x += (dx / distance) * self.speed * dt
                self.y += (dy / distance) * self.speed * dt
            else:
                self.is_moving = False
                self.move_target = None

        # === CONSTRUCTION D'UN BÂTIMENT ===
        # Si ce worker/builder est assigné à un chantier, s'y rendre
        construction = getattr(self, 'construction_target', None)
        if construction is not None:
            # Se déplacer vers le chantier
            cdx = construction.x - self.x
            cdy = construction.y - self.y
            cdistance = (cdx ** 2 + cdy ** 2) ** 0.5
            if cdistance > 25:
                self.x += (cdx / cdistance) * self.speed * dt
                self.y += (cdy / cdistance) * self.speed * dt
            # Arrivé sur place : la construction avance via BuildingProgress.update
            return

        # Gestion de la récolte - chercher une ressource si pas de cible
        if not self.target_resource and not self.carrying:
            self._find_and_assign_to_resource()

        # Récolter la ressource actuelle
        if self.target_resource and not self.carrying:
            node = self.target_resource
            if node and not node.is_depleted():
                dx = node.x - self.x
                dy = node.y - self.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < 30:
                    # Récolter la ressource - quantité basée sur max_carry (affectée par le bonus de recherche)
                    amount = node.harvest(self.max_carry)
                    if amount > 0:
                        self.carrying = True
                        self.carry_amount = amount
                        # Ajouter le type si pas déjà dans la liste
                        resource_type = node.resource_type
                        if resource_type not in self.carrying_types:
                            if len(self.carrying_types) < self.max_carry_types or self.hyper_mode:
                                self.carrying_types.append(resource_type)
                        # Déterminer le point de dépôt si pas déjà défini
                        if not self.drop_off_point and hasattr(self, 'game'):
                            self._find_drop_off_point()
                else:
                    # Se déplacer vers la ressource
                    self.is_moving = True
                    self.move_target = (node.x, node.y)

            # Si la ressource est épuisée, chercher une nouvelle cible
            if node and node.is_depleted():
                self.target_resource = None

        # Gestion du rapport (retour au point de dépôt)
        if self.carrying and not self.is_moving:
            if self.drop_off_point:
                dx = self.drop_off_point.x - self.x
                dy = self.drop_off_point.y - self.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < 40:
                    # Déposer les ressources
                    self._deposit_resources()
                else:
                    # Se déplacer vers le point de dépôt
                    self.is_moving = True
                    self.move_target = (self.drop_off_point.x, self.drop_off_point.y)
        elif self.carrying and self.is_moving:
            # Continuer à aller vers le drop-off
            pass

        # Gestion du combat (si target ennemi)
        if self.target and hasattr(self.target, 'hp') and self.target.hp > 0:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= self.range:
                # Attaquer
                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.attack_timer = 0
                    self.target.take_damage(self.damage)
            else:
                # Déplacer vers la cible
                self.is_moving = True
                self.move_target = (self.target.x, self.target.y)
        else:
            self.target = None

    def _update_mood(self, dt: float):
        """Met à jour l'humeur en fonction du temps et des actions."""
        # Obtenir l'heure du jour (simulée)
        hour = pygame.time.get_ticks() / 1000 % 24

        # Les workers sont plus motivés le matin (6-12h)
        if 6 <= hour <= 12:
            motivation_boost = 0.2
        elif 12 <= hour <= 18:
            motivation_boost = 0.1
        else:
            motivation_boost = -0.1

        # Ajuster la motivation selon l'humeur
        self.motivation_level = max(0.0, min(1.0,
            self.motivation_level + motivation_boost * dt * 0.1
        ))

        # Changer l'humeur selon la fatigue et la motivation
        if self.fatigue_timer > self.fatigue_duration * 2:
            self.mood = "tired"
        elif self.motivation_level < 0.3:
            self.mood = "demotivated"
        elif self.motivation_level > 0.8 and self.hyper_mode:
            self.mood = "motivated"
        elif self.carrying and self.fatigue_timer < self.fatigue_duration:
            self.mood = "happy"
        else:
            self.mood = "neutral"

        # Générer aléatoirement des bulles de dialogue
        if random.random() < 0.001 * dt:  # Très rare
            self._generate_chat()

    def _generate_chat(self):
        """Génère une phrase de dialogue selon l'humeur."""
        chats = {
            "happy": [
                "Ça va bien!",
                "J'adore travailler!",
                "Encore un peu!",
                "On y est presque!",
            ],
            "tired": [
                "J'en peux plus...",
                "Il faut que je me repose.",
                "Trop fatigant...",
                "Zzz...",
            ],
            "motivated": [
                "Je suis prêt à tout!",
                "On va gagner!",
                "En avant!",
                "Je suis invincible!",
                "Allez les gars, on y est presque!",
                "Ne lâchez rien!",
            ],
            "demotivated": [
                "Pourquoi je fais ça?",
                "C'est pas juste...",
                "J'ai envie de partir.",
                "Personne ne m'aime.",
            ],
            "neutral": [
                "Bon, continuons.",
                "Il fait beau aujourd'hui.",
                "J'ai faim.",
                "C'est calme.",
            ],
        }

        # Ajouter la phrase de personnalité aléatoirement
        if random.random() < self.personality["traits"]["social"]:
            personality_phrases = [
                "Salut les gars!",
                "Vous allez bien?",
                "On devrait tous se connaître.",
                "C'est sympa d'être ensemble.",
                "Ensemble, on est plus forts!",
            ]
            chats["neutral"].extend(personality_phrases)

        self.chat_bubble = random.choice(chats.get(self.mood, chats["neutral"]))

    def try_motivate_nearby(self, nearby_workers):
        """Tente de motiver les workers proches."""
        if self.mood not in ["motivated", "happy"]:
            return False

        motivated_count = 0
        for other in nearby_workers:
            if other is self or other.mood == "motivated":
                continue

            # Calculer la distance
            dx = other.x - self.x
            dy = other.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < self.motivation_radius:
                # Motiver l'autre worker
                other.motivation_level = min(1.0, other.motivation_level + 0.2)
                other.mood = "motivated"
                motivated_count += 1

        return motivated_count > 0

    def _find_and_assign_to_resource(self):
        """Trouve et assigne un worker à une ressource proche."""
        # Ne pas chercher de ressources si le worker est sélectionné
        if getattr(self, 'selected', False):
            return

        if not hasattr(self, 'game') or not self.game:
            return

        # Si on porte déjà des ressources, ne PAS chercher une nouvelle cible
        # Le worker doit d'abord déposer ce qu'il porte
        if self.carrying:
            return

        # Chercher une ressource proche (wood, food ou gold)
        closest_resource = None
        closest_distance = 600  # Rayon de recherche

        for node in self.game.resource_nodes:
            if node.is_depleted():
                continue

            dx = node.x - self.x
            dy = node.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < closest_distance:
                closest_distance = distance
                closest_resource = node

        # Assigner le worker à la ressource trouvée
        if closest_resource:
            self.target_resource = closest_resource
            # Si c'est une mine d'or, assigner aussi à la mine
            if hasattr(closest_resource, 'is_mine') and closest_resource.is_mine and hasattr(closest_resource, 'assign_worker'):
                closest_resource.assign_worker(self)

    def _find_drop_off_point(self):
        """Trouve le point de dépôt le plus proche (bâtiment de la faction)."""
        # Chercher le bâtiment le plus proche de la même faction
        if not hasattr(self, 'game') or not self.game:
            return

        closest_building = None
        closest_distance = float('inf')  # Pas de limite de distance

        for building in self.game.buildings:
            if building.faction != self.faction:
                continue

            dx = building.x - self.x
            dy = building.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < closest_distance:
                closest_distance = distance
                closest_building = building

        # Utiliser le bâtiment trouvé comme point de dépôt
        if closest_building:
            self.drop_off_point = closest_building

    def _deposit_resources(self):
        """Dépose les ressources collectées."""
        if self.carry_amount > 0:
            # Ajouter les ressources au système d'économie (selon la faction)
            if hasattr(self, 'game') and self.game:
                ec = self.game.enemy_economy if getattr(self, 'faction', 'player') == 'enemy' else self.game.economy
                if self.target_resource and hasattr(self.target_resource, 'resource_type'):
                    resource_type = self.target_resource.resource_type
                    if resource_type == "gold":
                        ec.add_resources(gold=self.carry_amount)
                    elif resource_type == "wood":
                        ec.add_resources(wood=self.carry_amount)
                    elif resource_type == "food":
                        ec.add_resources(food=self.carry_amount)

            # Son de dépôt
            if hasattr(self, 'game') and hasattr(self.game, 'audio_events'):
                self.game.audio_events.on_resource_collected()

            # Reset - mais garder les types pour continuer à collecter
            self.carrying = False
            self.carry_amount = 0
            self.fatigue_timer = 0.0  # Reset fatigue timer

            # Activer le hyper mode aléatoirement (10% de chance)
            if not self.hyper_mode and len(self.carrying_types) >= 2:
                if random.random() < 0.1:
                    self.hyper_mode = True
                    self.hyper_timer = 0.0

        # Si on a atteint le max de types, reset la liste après un dépôt
        if len(self.carrying_types) >= self.max_carry_types and not self.hyper_mode:
            self.carrying_types = []

    def set_drop_off_point(self, point):
        """Définit le point de dépôt."""
        self.drop_off_point = point

    def get_color(self) -> tuple:
        """Retourne la couleur de l'unité."""
        if self.faction == "player":
            return (100, 149, 237)  # Bleu
        return (178, 34, 34)  # Rouge

    def to_dict(self) -> dict:
        """Sérialise l'unité."""
        data = super().to_dict()
        data["unit_type"] = self.unit_type
        data["carrying"] = self.carrying
        data["carry_amount"] = self.carry_amount
        data["can_cut_trees"] = self.can_cut_trees
        data["mood"] = self.mood
        data["motivation"] = self.motivation_level
        return data

    def draw_chat_bubble(self, screen, camera_x, camera_y):
        """Dessine la bulle de dialogue au-dessus du worker."""
        if not self.chat_bubble:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Dessiner la bulle
        font = pygame.font.Font(None, 14)
        text = font.render(self.chat_bubble, True, (255, 255, 255))

        # Position de la bulle (au-dessus du worker)
        bubble_x = screen_x - text.get_width() // 2
        bubble_y = screen_y - 40

        # Fond de la bulle
        pygame.draw.rect(screen, (0, 0, 0, 180),
                        (bubble_x - 5, bubble_y - 5,
                         text.get_width() + 10, text.get_height() + 10),
                        border_radius=8)

        # Texte
        screen.blit(text, (bubble_x, bubble_y))
