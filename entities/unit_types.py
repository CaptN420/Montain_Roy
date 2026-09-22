"""
Mountain_Roy - Unit Types (Types d'unités)
Étape 3: Définition des types d'unités
"""

from entities.unit import Unit
from entities.hero import Hero
from entities.worker import Worker


class Warrior(Unit):
    """Guerrier - unité terrestre de base."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "warrior"
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 15
        self.armor = 2
        self.speed = 40
        self.range = 64  # Doit dépasser la séparation de collision (~49px)
        self.attack_speed = 1.0
        self.radius = 12
        
        # Coût de production
        self.cost = {
            "gold": 50,
            "wood": 0,
            "food": 10,
        }
        self.production_time = 3.0


class Archer(Unit):
    """Archer - unité à distance."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "archer"
        self.max_hp = 60
        self.hp = self.max_hp
        self.damage = 16
        self.armor = 0
        self.speed = 45
        self.range = 128
        self.attack_speed = 1.0
        self.radius = 12
        
        self.cost = {
            "gold": 40,
            "wood": 20,
            "food": 5,
        }
        self.production_time = 2.5


class Knight(Unit):
    """Chevalier - unité blindée."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "knight"
        self.max_hp = 200
        self.hp = self.max_hp
        self.damage = 25
        self.armor = 8
        self.speed = 55
        self.range = 64
        self.attack_speed = 1.5
        self.radius = 16
        
        self.cost = {
            "gold": 100,
            "wood": 50,
            "food": 20,
        }
        self.production_time = 5.0


class Mage(Unit):
    """Mage - unité magique."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "mage"
        self.max_hp = 80
        self.hp = self.max_hp
        self.damage = 40
        self.armor = 0
        self.speed = 35
        self.range = 96
        self.attack_speed = 1.6
        self.radius = 14
        
        self.cost = {
            "gold": 80,
            "wood": 40,
            "food": 10,
        }
        self.production_time = 4.0


class Healer(Unit):
    """Soigneur - unité spécialisée."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "healer"
        self.max_hp = 70
        self.hp = self.max_hp
        self.damage = 5
        self.armor = 0
        self.speed = 40
        self.range = 64
        self.attack_speed = 1.5
        self.radius = 12
        
        # Capacité de soin
        self.heal_amount = 20
        
        self.cost = {
            "gold": 60,
            "wood": 30,
            "food": 10,
        }
        self.production_time = 3.5


class SiegeEngine(Unit):
    """Engin de siège."""
    
    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "siege_engine"
        self.max_hp = 300
        self.hp = self.max_hp
        self.damage = 50
        self.armor = 5
        self.speed = 20
        self.range = 160
        self.attack_speed = 3.0
        self.radius = 20
        
        self.cost = {
            "gold": 150,
            "wood": 100,
            "food": 30,
        }
        self.production_time = 8.0


class Scout(Unit):
    """Éclaireur."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "scout"
        self.max_hp = 50
        self.hp = self.max_hp
        self.damage = 8
        self.armor = 0
        self.speed = 70
        self.range = 64
        self.attack_speed = 0.8
        self.radius = 10

        self.cost = {
            "gold": 30,
            "wood": 10,
            "food": 5,
        }
        self.production_time = 2.0


class Builder(Worker):
    """Ouvrier - peut construire des bâtiments."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        # Initialize as Worker first to get all worker functionality
        Worker.__init__(self, x, y, faction)
        self.unit_type = "builder"
        self.can_build = True
        self.building_target = None

        self.cost = {
            "gold": 40,
            "wood": 20,
            "food": 5,
        }
        self.production_time = 2.5


class Berserker(Unit):
    """Berserker - unité élite de mêlée orque (agressive, dégâts massifs)."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "berserker"
        self.max_hp = 140
        self.hp = self.max_hp
        self.damage = 30
        self.armor = 3
        self.speed = 55
        self.range = 64
        self.attack_speed = 1.2
        self.radius = 14

        self.cost = {
            "gold": 90,
            "wood": 40,
            "food": 25,
        }
        self.production_time = 5.0


class Ranger(Unit):
    """Ranger - archer d'élite elfe (portée et vitesse)."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "ranger"
        self.max_hp = 70
        self.hp = self.max_hp
        self.damage = 18
        self.armor = 1
        self.speed = 60
        self.range = 160
        self.attack_speed = 1.0
        self.radius = 12

        self.cost = {
            "gold": 60,
            "wood": 40,
            "food": 10,
        }
        self.production_time = 5.0


class Cannon(Unit):
    """Canon nain - artillerie lourde défensive."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "cannon"
        self.max_hp = 220
        self.hp = self.max_hp
        self.damage = 60
        self.armor = 6
        self.speed = 22
        self.range = 200
        self.attack_speed = 3.0
        self.radius = 18

        self.cost = {
            "gold": 180,
            "wood": 120,
            "food": 20,
        }
        self.production_time = 10.0


class NavalUnit(Unit):
    """Unité navale - peut se déplacer sur l'eau."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "naval"
        self.max_hp = 150
        self.hp = self.max_hp
        self.damage = 20
        self.armor = 3
        self.speed = 60
        self.range = 96
        self.attack_speed = 1.5
        self.radius = 14
        self.is_aquatic = True

        self.cost = {
            "gold": 80,
            "wood": 60,
            "food": 15,
        }
        self.production_time = 4.0


class Boat(NavalUnit):
    """Bateau de transport."""

    def __init__(self, x: int, y: int, faction: str = "player"):
        super().__init__(x, y, faction)
        self.unit_type = "boat"
        self.max_hp = 200
        self.hp = self.max_hp
        self.damage = 10
        self.armor = 2
        self.speed = 50
        self.range = 64
        self.attack_speed = 2.0
        self.radius = 18

        self.transport_capacity = 5

        self.cost = {
            "gold": 100,
            "wood": 80,
            "food": 20,
        }
        self.production_time = 5.0


def create_unit(unit_type: str, x: int, y: int, faction: str = "player", game=None) -> Unit:
    """Crée une unité selon son type."""
    units = {
        "warrior": Warrior,
        "archer": Archer,
        "knight": Knight,
        "mage": Mage,
        "healer": Healer,
        "siege_engine": SiegeEngine,
        "scout": Scout,
        "builder": Builder,
        "worker": Worker,  # Add worker type for resource gathering
        "naval": NavalUnit,
        "boat": Boat,
        # Unités uniques par faction
        "berserker": Berserker,  # Orc
        "ranger": Ranger,        # Elf
        "cannon": Cannon,        # Dwarf
    }

    unit_class = units.get(unit_type, Warrior)
    # Héros de faction : reconstruit via le registre (hero_types).
    if isinstance(unit_type, str) and unit_type.startswith("hero_"):
        from entities.hero_types import create_faction_hero, resolve_unit_type
        res = resolve_unit_type(unit_type)
        if res is not None:
            gfaction, role = res
            unit = create_faction_hero(gfaction, role, x, y, side=faction)
            if game is not None:
                unit.game = game
            return unit
        from entities.hero import Hero
        unit = Hero(x, y, faction)
    else:
        unit = unit_class(x, y, faction)
    # Les __init__ des sous-classes ne prennent pas encore le paramètre `game` :
    # on l'assigne après construction (base Unit.__init__ accepte game=None).
    if game is not None:
        unit.game = game
    return unit
