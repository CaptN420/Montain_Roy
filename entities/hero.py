"""
Mountain_Roy - Hero (Héros)
Étape 3: Système de héros
"""

import pygame
from entities.unit import Unit
from settings import COLORS


class Hero(Unit):
    """Classe pour le héros du joueur."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        
        # Stats améliorées du héros
        self.max_hp = 500
        self.hp = self.max_hp
        self.damage = 25
        self.armor = 5
        self.speed = 60
        self.range = 40
        self.attack_speed = 0.8
        
        self.radius = 20
        
        # Système de niveaux
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Mana
        self.max_mana = 100
        self.mana = self.max_mana
        
        # Compétences
        self.skills = [
            {
                "name": "Frappe dévastatrice",
                "cost": 20,
                "cooldown": 0,
                "max_cooldown": 5.0,
                "damage": 50,
                "range": 64,
                "aoe": 64,
                "skill_type": "aoe",
            },
            {
                "name": "Bouclier magique",
                "cost": 30,
                "cooldown": 0,
                "max_cooldown": 10.0,
                "shield": 50,
                "duration": 6.0,
                "skill_type": "shield",
            },
            {
                "name": "Cri de guerre",
                "cost": 25,
                "cooldown": 0,
                "max_cooldown": 8.0,
                "aura_damage": 10,
                "aura_range": 96,
                "skill_type": "aura",
            },
            {
                "name": "Météore",
                "cost": 50,
                "cooldown": 0,
                "max_cooldown": 15.0,
                "damage": 100,
                "range": 128,
                "aoe": 80,
                "skill_type": "aoe",
            },
        ]
        
        # Inventaire simple
        self.inventory = []
    
    def get_color(self) -> tuple:
        """Retourne la couleur dorée du héros."""
        return COLORS["hero"]
    
    def update(self, dt: float):
        """Met à jour le héros."""
        super().update(dt)
        
        # Mise à jour des cooldowns des compétences
        for skill in self.skills:
            if skill["cooldown"] > 0:
                skill["cooldown"] -= dt

        # Expiration du bouclier temporaire
        if self.shield > 0 and self.shield_duration > 0:
            self.shield_duration -= dt
            if self.shield_duration <= 0:
                self.shield = 0
                self.shield_duration = 0
    
    def gain_experience(self, amount: int):
        """Gagne de l'expérience."""
        self.experience += amount
        if self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Monte de niveau."""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Amélioration des stats
        self.max_hp += 50
        self.hp = min(self.hp + 50, self.max_hp)
        self.damage += 5
        self.armor += 1
    
    def use_skill(self, skill_index: int, target_x: int = None, target_y: int = None,
              units: list = None):
        """Utilise une compétence.

        Args:
            skill_index: Index de la compétence dans self.skills.
            target_x, target_y: Position cible (pour les attaques de zone).
            units: Liste des unités présentes ; seules les unités ennemies
                sont affectées par les compétences offensives.

        Returns:
            True si la compétence a été lancée, False sinon.
        """
        if skill_index < 0 or skill_index >= len(self.skills):
            return False

        skill = self.skills[skill_index]

        if self.mana < skill["cost"]:
            return False

        if skill["cooldown"] > 0:
            return False

        # Consommer le mana et activer la compétence
        self.mana -= skill["cost"]
        skill["cooldown"] = skill["max_cooldown"]

        if units is None:
            units = []

        skill_type = skill.get("skill_type", "aoe")

        if skill_type == "aoe":
            self._cast_aoe(skill, target_x, target_y, units)
        elif skill_type == "shield":
            self.shield += skill.get("shield", 0)
            self.shield_duration = skill.get("duration", 6.0)
        elif skill_type == "aura":
            self._cast_aura(skill, units)

        return True

    def _enemies(self, units: list) -> list:
        """Retourne les unités ennemies vivantes."""
        return [u for u in units
                if getattr(u, 'faction', None) != self.faction
                and getattr(u, 'hp', 0) > 0]

    def _cast_aoe(self, skill: dict, target_x: int = None, target_y: int = None, units: list = None):
        """Attaque de zone : dégâts aux ennemis dans le rayon autour de la cible."""
        if target_x is None or target_y is None:
            cx, cy = self.x, self.y
        else:
            cx, cy = target_x, target_y
        aoe_radius = skill.get("aoe", skill.get("range", 64))
        damage = skill.get("damage", 0)
        for enemy in self._enemies(units):
            dist = ((enemy.x - cx) ** 2 + (enemy.y - cy) ** 2) ** 0.5
            if dist <= aoe_radius:
                enemy.take_damage(damage, attacker=self)

    def _cast_aura(self, skill: dict, units: list):
        """Aura autour du héros : dégâts aux ennemis proches."""
        aura_range = skill.get("aura_range", 96)
        damage = skill.get("aura_damage", 0)
        for enemy in self._enemies(units):
            dist = ((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2) ** 0.5
            if dist <= aura_range:
                enemy.take_damage(damage, attacker=self)
    
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Dessine le héros."""
        # Cercle doré pour le héros
        color = self.get_color()
        if self.selected:
            color = COLORS["selected"]
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Barre de vie
        bar_width = 40
        bar_height = 6
        hp_ratio = self.hp / self.max_hp
        
        hp_color = (255, 0, 0) if hp_ratio < 0.3 else (0, 255, 0)
        
        pygame.draw.rect(
            screen, 
            (100, 100, 100), 
            (int(self.x) - bar_width // 2, int(self.y) - self.radius - 12, bar_width, bar_height)
        )
        pygame.draw.rect(
            screen, 
            hp_color, 
            (int(self.x) - bar_width // 2, int(self.y) - self.radius - 12, int(bar_width * hp_ratio), bar_height)
        )
        
        # Barre de mana
        mana_bar_y = int(self.y) - self.radius - 6
        pygame.draw.rect(
            screen, 
            (50, 50, 50), 
            (int(self.x) - bar_width // 2, mana_bar_y, bar_width, 4)
        )
        pygame.draw.rect(
            screen, 
            (0, 0, 255), 
            (int(self.x) - bar_width // 2, mana_bar_y, int(bar_width * (self.mana / self.max_mana)), 4)
        )
    
    def to_dict(self) -> dict:
        """Sérialise le héros."""
        return {
            "x": self.x,
            "y": self.y,
            "faction": self.faction,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "damage": self.damage,
            "armor": self.armor,
            "speed": self.speed,
            "range": self.range,
            "level": self.level,
            "experience": self.experience,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "skills": self.skills,
        }
