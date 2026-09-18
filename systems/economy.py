"""
Mountain_Roy - Economy System (Système de ressources)
Étape 5: Gestion des ressources et récolte
"""


class EconomySystem:
    """Gère les ressources et l'économie du jeu."""
    
    def __init__(self):
        self.gold = 200
        self.wood = 150
        self.food = 100
        self.max_food = 100
        
        # Coûts de production
        self.unit_costs = {
            "warrior": {"gold": 50, "wood": 0, "food": 10},
            "archer": {"gold": 40, "wood": 20, "food": 5},
            "knight": {"gold": 100, "wood": 50, "food": 20},
            "mage": {"gold": 80, "wood": 40, "food": 10},
            "healer": {"gold": 60, "wood": 30, "food": 10},
            "siege_engine": {"gold": 150, "wood": 100, "food": 30},
            "scout": {"gold": 30, "wood": 10, "food": 5},
        }
        
        self.building_costs = {
            "town_hall": {"gold": 0, "wood": 0, "food": 0},
            "barracks": {"gold": 150, "wood": 100, "food": 20},
            "farm": {"gold": 50, "wood": 50, "food": 0},
            "lumber_mill": {"gold": 100, "wood": 0, "food": 10},
            "mine": {"gold": 200, "wood": 50, "food": 20},
            "tower": {"gold": 100, "wood": 100, "food": 10},
            "temple": {"gold": 300, "wood": 200, "food": 50},
            "workshop": {"gold": 200, "wood": 150, "food": 30},
            "academy": {"gold": 250, "wood": 150, "food": 40},
            "dock": {"gold": 300, "wood": 200, "food": 50},
            "wall": {"gold": 50, "wood": 50, "food": 0},
        }

        # Prérequis de construction
        self.building_prerequisites = {
            "academy": ["town_hall"],
            "dock": ["town_hall"],
            "workshop": ["barracks"],
        }
    
    def can_afford(self, cost: dict) -> bool:
        """Vérifie si on peut payer un coût."""
        return (
            self.gold >= cost.get("gold", 0) and
            self.wood >= cost.get("wood", 0) and
            self.food >= cost.get("food", 0)
        )

    def can_build(self, building_type: str, buildings: list = None) -> bool:
        """Vérifie si on peut construire un bâtiment (coût + prérequis)."""
        if building_type not in self.building_costs:
            return False

        # Vérifier le coût
        cost = self.building_costs[building_type]
        if not self.can_afford(cost):
            return False

        # Vérifier les prérequis
        if building_type in self.building_prerequisites and buildings:
            prereqs = self.building_prerequisites[building_type]
            for prereq in prereqs:
                if not any(b.building_type == prereq for b in buildings):
                    return False

        return True
    
    def pay_cost(self, cost: dict):
        """Payer un coût."""
        self.gold -= cost.get("gold", 0)
        self.wood -= cost.get("wood", 0)
        self.food -= cost.get("food", 0)
    
    def add_resources(self, gold: int = 0, wood: int = 0, food: int = 0):
        """Ajoute des ressources."""
        self.gold += gold
        self.wood += wood
        self.food += food
    
    def get_population(self, units: list) -> int:
        """Calcule la population actuelle."""
        return len(units)
    
    def get_max_population(self, buildings: list) -> int:
        """Calcule la population max basée sur les fermes."""
        farm_count = sum(1 for b in buildings if b.building_type == "farm")
        return 10 + (farm_count * 5)
    
    def get_unit_cost(self, unit_type: str) -> dict:
        """Retourne le coût d'une unité."""
        return self.unit_costs.get(unit_type, {"gold": 50, "wood": 0, "food": 10})
    
    def get_building_cost(self, building_type: str) -> dict:
        """Retourne le coût d'un bâtiment."""
        return self.building_costs.get(building_type, {"gold": 100, "wood": 50, "food": 10})


class ResourceNode:
    """Noeud de ressource (mine d'or ou arbre)."""
    
    def __init__(self, x: int, y: int, resource_type: str, amount: int):
        self.x = x
        self.y = y
        self.resource_type = resource_type  # "gold" ou "wood"
        self.amount = amount
        self.max_amount = amount  # Pour la régénération
    
    def is_depleted(self) -> bool:
        """Vérifie si la ressource est épuisée."""
        return self.amount <= 0
    
    def harvest(self, amount: int) -> int:
        """Récupère une quantité de ressource."""
        harvested = min(amount, self.amount)
        self.amount -= harvested
        return harvested
    
    def draw(self, screen, camera_x: float, camera_y: float):
        """Dessine le nœud de ressource."""
        import pygame
        
        if self.is_depleted():
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Couleurs par type
        colors = {
            "gold": (255, 215, 0),      # Or
            "wood": (34, 139, 34),       # Vert forêt
            "food": (220, 20, 60),       # Rouge tomate
        }
        
        color = colors.get(self.resource_type, (255, 255, 255))
        radius = max(8, int(15 * (self.amount / self.max_amount)))
        
        if self.resource_type == "gold":
            # Mine dorée - cercle avec éclat
            pygame.draw.circle(screen, color, (screen_x, screen_y), radius)
            pygame.draw.circle(screen, (255, 255, 200), (screen_x - 5, screen_y - 5), max(3, radius // 3))
        elif self.resource_type == "wood":
            # Forêt - triangle vert avec plusieurs arbres
            for i in range(-1, 2):
                offset = i * radius // 2
                points = [
                    (screen_x + offset, screen_y - radius),
                    (screen_x + offset - radius // 2, screen_y + radius // 2),
                    (screen_x + offset + radius // 2, screen_y + radius // 2),
                ]
                pygame.draw.polygon(screen, color, points)
        elif self.resource_type == "food":
            # Ferme - carré rouge avec motif
            pygame.draw.rect(screen, color, 
                           (screen_x - radius, screen_y - radius, 
                            radius * 2, radius * 2))
            # Motif de culture
            for i in range(-1, 2):
                pygame.draw.line(screen, (180, 160, 50),
                               (screen_x + i * radius // 2, screen_y - 5),
                               (screen_x + i * radius // 2, screen_y + 5), 2)
