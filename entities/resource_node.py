"""
Mountain_Roy - Resource Nodes (Noeuds de ressources)
Style Warcraft/Civilization: Mines et forêts bien visibles
"""

import pygame
import math
from settings import COLORS


class ResourceNode:
    """Nœud de ressource (forêt, mine, ferme)."""

    def __init__(self, x: int, y: int, resource_type: str, amount: int):
        self.x = x
        self.y = y
        self.resource_type = resource_type  # "gold", "wood", "food"
        self.amount = amount
        self.max_amount = amount

        # Pour les mines d'or (comme bâtiments)
        self.is_mine = resource_type == "gold"
        self.assigned_workers = []  # Liste des workers assignés (max 3)
        self.mining_speed = 10 if self.is_mine else 5

        # Taille selon type
        if self.is_mine:
            self.width = 64
            self.height = 64
            self.radius = 32
        else:
            self.width = 48
            self.height = 48
            self.radius = 24

        # Pour les forêts (obstacle)
        self.is_obstacle = resource_type == "wood"

        # Couleurs par type
        self.colors = {
            "gold": COLORS["gold"],
            "wood": (34, 139, 34),  # Vert forêt
            "food": (220, 20, 60),  # Rouge tomate
        }

    def is_depleted(self) -> bool:
        """Vérifie si la ressource est épuisée."""
        return self.amount <= 0

    def harvest(self, amount: int) -> int:
        """Récolte la ressource et retourne la quantité récoltée."""
        if self.is_depleted():
            return 0

        actual = min(amount, self.amount)
        self.amount -= actual
        return actual

    def assign_worker(self, worker) -> bool:
        """Assigne un worker à la mine (max 3)."""
        if not self.is_mine:
            return False
        if len(self.assigned_workers) >= 3:
            return False
        if worker not in self.assigned_workers:
            self.assigned_workers.append(worker)
            return True
        return False

    def remove_worker(self, worker):
        """Retire un worker de la mine."""
        if worker in self.assigned_workers:
            self.assigned_workers.remove(worker)

    def can_assign_worker(self) -> bool:
        """Vérifie si on peut assigner un worker."""
        return self.is_mine and len(self.assigned_workers) < 3

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Dessine le nœud de ressource - Style Warcraft/Civilization."""
        if self.is_depleted():
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Cacher si hors écran
        if (screen_x < -100 or screen_x > screen.get_width() + 100 or
                screen_y < -100 or screen_y > screen.get_height() + 100):
            return

        # Dessiner selon le type
        if self.resource_type == "gold":
            self._draw_gold_mine(screen, screen_x, screen_y)

        elif self.resource_type == "wood":
            self._draw_forest(screen, screen_x, screen_y)

        elif self.resource_type == "food":
            self._draw_farm(screen, screen_x, screen_y)

    def _draw_gold_mine(self, screen, x, y):
        """Dessine une mine d'or style Warcraft - Montagne dorée avec cratère."""
        # Ombre portée
        pygame.draw.ellipse(screen, (50, 40, 20), (x - 35, y + 10, 70, 20))

        # Montagne principale (triangle)
        pygame.draw.polygon(screen, (180, 140, 40), [
            (x - 32, y + 20),
            (x + 32, y + 20),
            (x, y - 32)
        ])

        # Cratère lumineux au sommet
        pygame.draw.circle(screen, (255, 215, 0), (x, y - 15), 12)
        pygame.draw.circle(screen, (255, 255, 150), (x, y - 15), 8)

        # Details rocheux
        pygame.draw.polygon(screen, (200, 160, 50), [
            (x - 20, y + 10),
            (x - 10, y),
            (x, y + 10)
        ])
        pygame.draw.polygon(screen, (200, 160, 50), [
            (x + 10, y + 10),
            (x + 20, y + 5),
            (x + 15, y + 15)
        ])

        # Effet de brillance pulsante (si workers assignés)
        if self.assigned_workers:
            glow_size = int(35 + math.sin(pygame.time.get_ticks() / 200) * 3)
            pygame.draw.circle(screen, (255, 215, 0, 80), (x, y), glow_size)

        # Indicateur de workers assignés - bulle au-dessus
        if self.assigned_workers:
            font = pygame.font.Font(None, 18)
            text = font.render(f"{len(self.assigned_workers)}/3", True, (255, 255, 255))
            # Fond de la bulle
            pygame.draw.rect(screen, (0, 0, 0, 180), (x - 18, y - 45, 36, 20), border_radius=4)
            screen.blit(text, (x - 10, y - 42))

        # Barre de quantité en dessous
        if self.amount < self.max_amount:
            bar_width = 48
            bar_height = 6
            pygame.draw.rect(screen, (50, 50, 50), (x - bar_width // 2, y + 25, bar_width, bar_height), border_radius=3)
            pygame.draw.rect(screen, (255, 215, 0),
                             (x - bar_width // 2, y + 25,
                              int(bar_width * self.amount / self.max_amount), bar_height), border_radius=3)

    def _draw_forest(self, screen, x, y):
        """Dessine une forêt style Civilization - Cluster d'arbres."""
        # Ombre portée globale
        pygame.draw.ellipse(screen, (30, 50, 20), (x - 28, y + 15, 56, 15))

        # Troncs multiples
        trunk_colors = [(101, 67, 33), (80, 50, 20), (120, 80, 40)]
        for i, offset in enumerate([-12, 0, 12]):
            pygame.draw.rect(screen, trunk_colors[i], (x + offset - 3, y - 5, 6, 18))

        # Feuillage en couches (style Civilization)
        # Couche arrière
        pygame.draw.circle(screen, (0, 80, 0), (x - 15, y - 10), 14)
        pygame.draw.circle(screen, (0, 80, 0), (x + 15, y - 10), 14)

        # Couche milieu
        pygame.draw.circle(screen, (34, 100, 34), (x - 8, y - 18), 16)
        pygame.draw.circle(screen, (34, 100, 34), (x + 8, y - 18), 16)
        pygame.draw.circle(screen, (34, 100, 34), (x, y - 25), 14)

        # Couche avant
        pygame.draw.circle(screen, (50, 140, 50), (x, y - 12), 18)

        # Points lumineux dans le feuillage
        for i in range(5):
            angle = i * 1.2 + pygame.time.get_ticks() / 1000
            lx = x + math.cos(angle) * 10
            ly = y - 15 + math.sin(angle) * 8
            pygame.draw.circle(screen, (100, 200, 100), (int(lx), int(ly)), 2)

        # Barre de quantité au-dessus
        if self.amount < self.max_amount:
            bar_width = 40
            bar_height = 5
            pygame.draw.rect(screen, (50, 50, 50), (x - bar_width // 2, y - 38, bar_width, bar_height), border_radius=3)
            pygame.draw.rect(screen, (50, 180, 50),
                             (x - bar_width // 2, y - 38,
                              int(bar_width * self.amount / self.max_amount), bar_height), border_radius=3)

    def _draw_farm(self, screen, x, y):
        """Dessine une ferme style Civilization - Parcelles de culture."""
        # Ombre portée
        pygame.draw.ellipse(screen, (80, 60, 30), (x - 28, y + 18, 56, 12))

        # Sol labouré (carré brun)
        pygame.draw.rect(screen, (139, 90, 43), (x - 24, y - 12, 48, 36), border_radius=4)

        # Rangées de cultures
        for row in range(-1, 2):
            for col in range(-1, 2):
                crop_x = x + col * 14
                crop_y = y + row * 10
                # Tige
                pygame.draw.line(screen, (180, 140, 40), (crop_x, crop_y + 8), (crop_x, crop_y - 2), 2)
                # Feuilles
                pygame.draw.circle(screen, (100, 180, 50), (crop_x, crop_y - 2), 4)

        # Bordure de la ferme
        pygame.draw.rect(screen, (100, 70, 30), (x - 24, y - 12, 48, 36), 3, border_radius=4)

        # Indicateur de quantité en dessous
        if self.amount < self.max_amount:
            bar_width = 40
            bar_height = 5
            pygame.draw.rect(screen, (50, 50, 50), (x - bar_width // 2, y + 22, bar_width, bar_height), border_radius=3)
            pygame.draw.rect(screen, (100, 200, 50),
                             (x - bar_width // 2, y + 22,
                              int(bar_width * self.amount / self.max_amount), bar_height), border_radius=3)


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

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Dessine le point de dépôt."""
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
