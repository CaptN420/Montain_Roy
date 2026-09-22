"""
Mountain_Roy - Unit (Unité de base)
Étape 3: Système d'entités
"""

import pygame
from settings import COLORS


class Unit:
    """Classe de base pour toutes les unités."""
    
    def __init__(self, x: int, y: int, faction: str = "player", game=None):
        self.x = x
        self.y = y
        self.faction = faction  # "player" ou "enemy"
        self.game = game
        
        # Stats de base (à override)
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 10
        self.armor = 0
        self.speed = 50  # pixels par seconde
        self.range = 32
        self.attack_speed = 1.0  # secondes entre les attaques
        
        # Niveau et XP
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.kills = 0
        self.killed_by = None  # Dernière unité qui nous a tués (pour l'XP)
        
        # Selection
        self.selected = False
        self.radius = 16  # rayon pour la collision
        
        # Combat
        self.target = None
        self.attack_timer = 0
        
        # Bouclier temporaire (peut être défini par les compétences)
        self.shield = 0
        self.shield_duration = 0
        
        # Movement
        self.is_moving = False
        self.move_target = None
        self.path = []  # points de passage en pixels, calculés par MovementSystem

        # Animation de sprites (marche / attaque / mort)
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.facing = 1  # 1 = droite, -1 = gauche (pour le flip)
    
    def get_color(self) -> tuple:
        """Retourne la couleur de l'unité (couleur de faction si définie)."""
        faction_color = getattr(self, 'faction_color', None)
        if faction_color:
            return faction_color
        if self.faction == "player":
            return COLORS["player_unit"]
        return COLORS["enemy_unit"]
    
    def update(self, dt: float):
        """Met à jour l'unité."""
        # Gestion du mouvement
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
        
        # Gestion du combat
        if self.target and self.target.hp > 0:
            # Calcul des bonus de synergie
            synergies = self.get_synergy_bonus(self.game) if hasattr(self, 'game') and self.game else {"damage_mult": 1.0, "range_mult": 1.0}
            
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            effective_range = self.range * synergies["range_mult"]
            
            if distance <= effective_range:
                # Attaquer
                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.attack_timer = 0
                    actual_damage = self.damage * synergies["damage_mult"]
                    self.target.take_damage(actual_damage, attacker=self)
            else:
                # Déplacer vers la cible
                self.is_moving = True
                self.move_target = (self.target.x, self.target.y)
        else:
            self.target = None
        
        # Mise à jour de l'état d'animation
        self._update_animation(dt)

    def _update_animation(self, dt: float):
        """Détermine l'état d'animation (idle/walk/attack/death) et avance les frames."""
        from systems.sprite_anim import ANIM_IDLE, ANIM_WALK, ANIM_ATTACK, ANIM_DEATH, FRAME_COUNTS

        # Direction du personnage (vers la cible ou le déplacement)
        if self.target is not None and self.target.hp > 0:
            if self.target.x > self.x:
                self.facing = 1
            else:
                self.facing = -1
        elif self.is_moving and self.move_target:
            if self.move_target[0] > self.x:
                self.facing = 1
            else:
                self.facing = -1

        if not self.is_alive():
            new_state = ANIM_DEATH
        elif self.target is not None and self.target.hp > 0 and self.attack_timer < self.attack_speed * 0.4:
            # Pendant la fenêtre d'attaque
            new_state = ANIM_ATTACK
        elif self.is_moving:
            new_state = ANIM_WALK
        else:
            new_state = ANIM_IDLE

        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_frame = 0
            self.anim_timer = 0.0

        # Avancer la frame selon la vitesse de l'état
        from systems.sprite_anim import FRAME_FPS
        fps = FRAME_FPS.get(new_state, 8)
        self.anim_timer += dt
        if self.anim_timer >= 1.0 / fps:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % FRAME_COUNTS.get(new_state, 2)
    
    def take_damage(self, damage: int, attacker=None):
        """Subit des dégâts.
        
        Le bouclier (s'il est actif) absorbe les dégâts en priorité.

        Args:
            damage: Dégâts subis.
            attacker: Unité qui a infligé les dégâts (pour l'attribution de l'XP).
        """
        # Le bouclier absorbe les dégâts en premier.
        if getattr(self, 'shield', 0) > 0:
            absorbed = min(self.shield, damage)
            self.shield -= absorbed
            damage -= absorbed
            if damage <= 0:
                # Dégâts entièrement absorbés.
                if attacker is not None:
                    self.killed_by = attacker
                return
        actual_damage = max(1, damage - self.armor)
        self.hp -= actual_damage
        if attacker is not None:
            self.killed_by = attacker
        
        # Son de coup sur la cible (si le jeu est branché à l'audio)
        if getattr(self, 'game', None) is not None and hasattr(self.game, 'audio_events'):
            try:
                self.game.audio_events.on_unit_hit(actual_damage)
            except Exception:
                pass
            
    def is_alive(self) -> bool:
        """Vérifie si l'unité est vivante."""
        return self.hp > 0
    
    def gain_xp(self, amount: int):
        """Donne de l'XP à l'unité et gère les montées de niveau."""
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level_up()
    
    def level_up(self):
        """Passe au niveau supérieur - l'unité devient plus forte."""
        self.level += 1
        self.xp_to_next = int(self.xp_to_next * 1.3)  # Augmente la difficulté de montée
        # Améliorations par niveau
        self.max_hp += 10
        self.damage += 3
        self.armor += 1
        self.hp = self.max_hp  # Soigne complètement au niveau supérieur
    
    def xp_on_kill(self, target) -> int:
        """Retourne l'XP gagnée quand on tue une cible."""
        base_xp = 25
        # Tuer une cible de niveau supérieur donne plus d'XP
        target_level = getattr(target, 'level', 1)
        level_bonus = max(0, (target_level - self.level) * 10)
        return base_xp + level_bonus
    
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Dessine l'unité (sprite animé + barre de vie)."""
        # Convertir les coordonnées map en coordonnées écran
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Dessiner le sprite animé s'il est disponible, sinon un cercle
        try:
            from systems.sprite_anim import get_animator
            animator = get_animator()
            unit_type = getattr(self, "unit_type", "")
            if unit_type:
                animator.draw(screen, unit_type, self.anim_state, self.anim_frame,
                              screen_x, screen_y, flip_x=(self.facing < 0),
                              radius=self.radius)
            else:
                self._draw_circle(screen, screen_x, screen_y)
        except Exception:
            self._draw_circle(screen, screen_x, screen_y)

        # Cercle de sélection (léger, sous l'unité)
        if self.selected:
            pygame.draw.circle(screen, (0, 255, 0), (screen_x, screen_y),
                               self.radius + 3, 1)

        # Barre de vie
        bar_width = 30
        bar_height = 4
        hp_ratio = self.hp / self.max_hp

        hp_color = (255, 0, 0) if hp_ratio < 0.3 else (0, 255, 0)

        pygame.draw.rect(
            screen, 
            (100, 100, 100), 
            (screen_x - bar_width // 2, screen_y - self.radius - 10, bar_width, bar_height)
        )
        pygame.draw.rect(
            screen, 
            hp_color, 
            (screen_x - bar_width // 2, screen_y - self.radius - 10, int(bar_width * hp_ratio), bar_height)
        )

    def _draw_circle(self, screen, screen_x, screen_y):
        """Fallback : dessine l'unité en cercle coloré (si pas de sprite)."""
        color = self.get_color()
        if self.selected:
            color = COLORS["selected"]
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
    
    def get_synergy_bonus(self, game) -> dict:
        """Calcule les bonus de synergie basés sur l'environnement et les alliés proches."""
        bonuses = {"damage_mult": 1.0, "range_mult": 1.0}
        
        # Synergie Archer : +20% de portée si derrière un mur ou une tour
        if self.unit_type == "archer":
            for b in game.buildings:
                if b.faction == self.faction and b.building_type in ["wall", "tower"]:
                    dist = ((b.x - self.x)**2 + (b.y - self.y)**2)**0.5
                    if dist < 128:
                        bonuses["range_mult"] = 1.2
                        break

        # Synergie Chevalier : +15% de dégâts si au moins 2 autres chevaliers sont proches
        if self.unit_type == "knight":
            knights = [u for u in game.units if u.unit_type == "knight" and u.faction == self.faction and u != self]
            close_knights = 0
            for k in knights:
                dist = ((k.x - self.x)**2 + (k.y - self.y)**2)**0.5
                if dist < 64:
                    close_knights += 1
            if close_knights >= 2:
                bonuses["damage_mult"] = 1.15

        return bonuses

    def to_dict(self) -> dict:
        """Sérialise l'unité."""
        return {
            "unit_type": getattr(self, "unit_type", ""),
            "x": self.x,
            "y": self.y,
            "faction": self.faction,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "damage": self.damage,
            "armor": self.armor,
            "speed": self.speed,
            "range": self.range,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Unit":
        """Crée une unité depuis un dictionnaire."""
        unit_type = data.get("type", "warrior")
        # Pour l'instant, créer un warrior par défaut
        return Warrior(data["x"], data["y"], data.get("faction", "player"))
