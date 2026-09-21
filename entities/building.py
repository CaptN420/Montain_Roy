"""
Mountain_Roy - Building (Bâtiment)
Étape 3: Système de bâtiments
"""

import pygame
from settings import COLORS


class Building:
    """Classe de base pour les bâtiments."""
    
    def __init__(self, x: int, y: int, faction: str = "player", building_type: str = "generic"):
        self.x = x
        self.y = y
        self.faction = faction
        self.building_type = building_type
        
        # Stats de base (à override)
        self.max_hp = 500
        self.hp = self.max_hp
        self.width = 48
        self.height = 48
        
        # Production
        self.can_produce = False
        self.production_queue = []
        
        # Selection
        self.selected = False
    
    def get_color(self) -> tuple:
        """Retourne la couleur du bâtiment (couleur de faction si définie)."""
        faction_color = getattr(self, 'faction_color', None)
        if faction_color:
            return faction_color
        if self.faction == "player":
            return (100, 149, 237)  # Bleu
        return (178, 34, 34)  # Rouge
    
    def receive_resources(self, amount: int, resource_type: str = None, economy=None):
        """Reçoit des ressources d'un worker et les ajoute à l'économie de la faction."""
        if amount <= 0:
            return

        if economy is None:
            return

        if resource_type == "gold":
            economy.add_resources(gold=amount)
        elif resource_type == "wood":
            economy.add_resources(wood=amount)
        elif resource_type == "food":
            economy.add_resources(food=amount)
    
    def take_damage(self, damage: int, attacker=None):
        """Subit des dégâts.
        
        Args:
            damage: Dégâts subis.
            attacker: Unité qui a infligé les dégâts (attribution de l'XP).
        """
        self.hp -= damage
        if attacker is not None:
            self.killed_by = attacker
    
    def is_alive(self) -> bool:
        """Vérifie si le bâtiment est debout."""
        return self.hp > 0
    
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Dessine le bâtiment."""
        # Convertir les coordonnées map en coordonnées écran
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        color = self.get_color()
        if self.selected:
            color = COLORS["selected"]

        # Rectangle pour le bâtiment
        pygame.draw.rect(
            screen,
            color,
            (screen_x - self.width // 2, screen_y - self.height // 2, self.width, self.height)
        )

        # Bordure
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (screen_x - self.width // 2, screen_y - self.height // 2, self.width, self.height),
            2
        )

        # Barre de vie
        bar_width = 40
        bar_height = 6
        hp_ratio = self.hp / self.max_hp

        hp_color = (255, 0, 0) if hp_ratio < 0.3 else (0, 255, 0)

        pygame.draw.rect(
            screen,
            (100, 100, 100),
            (screen_x - bar_width // 2, screen_y - self.height // 2 - 10, bar_width, bar_height)
        )
        pygame.draw.rect(
            screen,
            hp_color,
            (screen_x - bar_width // 2, screen_y - self.height // 2 - 10, int(bar_width * hp_ratio), bar_height)
        )

        # Texte du nom du bâtiment au milieu
        try:
            import pygame as pg
            font = pg.font.Font(None, 16)
            type_name = self.building_type.replace("_", " ").title()
            text_surface = font.render(type_name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(text_surface, text_rect)
        except Exception:
            pass
    
    def to_dict(self) -> dict:
        """Sérialise le bâtiment."""
        return {
            "x": self.x,
            "y": self.y,
            "faction": self.faction,
            "type": self.building_type,
            "hp": self.hp,
            "max_hp": self.max_hp,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Building":
        """Crée un bâtiment depuis un dictionnaire."""
        return cls(data["x"], data["y"], data.get("faction", "player"), data.get("type", "generic"))


class TownHall(Building):
    """Hôtel de ville - bâtiment principal."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "town_hall")
        self.max_hp = 1000
        self.hp = self.max_hp
        self.width = 64
        self.height = 64


class CollectionBuilding(Building):
    """Cabane de récolte - où les workers déposent les ressources."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "collection")
        self.max_hp = 300
        self.hp = self.max_hp
        self.width = 48
        self.height = 48


class Barracks(Building):
    """Caserne - production d'unités terrestres."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "barracks")
        self.can_produce = True
        self.production_time = 5.0  # secondes


class Farm(Building):
    """Ferme - augmente la population max."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "farm")
        self.population_bonus = 5


class LumberMill(Building):
    """Scierie - améliore la récolte de bois."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "lumber_mill")


class Mine(Building):
    """Mine - collecte d'or."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "mine")


class Tower(Building):
    """Tour défensive."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "tower")
        self.damage = 20
        self.range = 128


class Temple(Building):
    """Temple - pour les héros et les compétences."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "temple")


class Workshop(Building):
    """Atelier - production d'unités spécialisées."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "workshop")
        self.can_produce = True


class Academy(Building):
    """Académie - recherche de technologies et formation d'unités."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "academy")
        self.can_produce = True
        self.research_unlocked = False


class Dock(Building):
    """Quai - production d'unités navales."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "dock")
        self.can_produce = True


class Wall(Building):
    """Mur défensif."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "wall")
        self.max_hp = 300
        self.hp = self.max_hp
        self.width = 32
        self.height = 32


class HeroHall(Building):
    """Bâtiment à héros : permet de recruter/ressusciter le héros (coût)."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "hero_hall")
        self.max_hp = 400
        self.hp = self.max_hp
        self.width = 48
        self.height = 48


class DropOffPoint:
    """Point de dépôt - où les workers rapportent les ressources."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        self.x = x
        self.y = y
        self.faction = faction
        self.radius = 30

        # Couleurs par faction
        self.colors = {
            "player": (100, 149, 237),  # Bleu
            "enemy": (178, 34, 34),     # Rouge
        }

    def draw(self, screen, camera_x: float, camera_y: float):
        """Dessine le point de dépôt."""
        import pygame
        from settings import COLORS

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        color = self.colors.get(self.faction, (255, 255, 255))

        # Dessiner un cercle avec bordure
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius, 3)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), self.radius - 5, 1)

        # Icône de dépôt (triangle)
        points = [
            (screen_x, screen_y - 10),
            (screen_x - 8, screen_y + 5),
            (screen_x + 8, screen_y + 5),
        ]
        pygame.draw.polygon(screen, (255, 255, 255), points)


# ============================================================
# BÂTIMENTS UNIQUES PAR FACTION
# ============================================================

class HumanBarracks(Barracks):
    """Caserne humaine : production plus rapide (spécialité humaine)."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.building_type = "human_barracks"


class OrcWarHut(Barracks):
    """Tanière de guerre orque : unités produites 25% plus vite (agressif)."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.building_type = "orc_war_hut"


class ElfRangerLodge(Building):
    """Abri de rangers elfes : produit les unités à distance avancées."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "elf_ranger_lodge")
        self.max_hp = 500
        self.hp = self.max_hp
        self.can_produce = True


class DwarfForge(Building):
    """Forge naine : produit l'artillerie et améliore les armes."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction, "dwarf_forge")
        self.max_hp = 700
        self.hp = self.max_hp
        self.can_produce = True
