"""Héros par faction (registre).

Chaque faction dispose de 3 archétypes de héros (guerrier / mage / archer),
chaque héros ayant un unit_type, un nom et des stats propres. Ils peuvent
coexister sur le terrain (invoqués depuis un bâtiment à héros).
"""
from entities.hero import Hero


# ----------------------------------------------------------------- archétypes
WARRIOR_SKILLS = [
    {"name": "Frappe dévastatrice", "cost": 20, "cooldown": 0, "max_cooldown": 5.0,
     "damage": 50, "range": 64, "aoe": 64, "skill_type": "aoe"},
    {"name": "Bouclier magique", "cost": 30, "cooldown": 0, "max_cooldown": 10.0,
     "shield": 50, "duration": 6.0, "skill_type": "shield"},
    {"name": "Cri de guerre", "cost": 25, "cooldown": 0, "max_cooldown": 8.0,
     "aura_damage": 10, "aura_range": 96, "skill_type": "aura"},
    {"name": "Météore", "cost": 50, "cooldown": 0, "max_cooldown": 15.0,
     "damage": 100, "range": 128, "aoe": 80, "skill_type": "aoe"},
]

MAGE_SKILLS = [
    {"name": "Boule de feu", "cost": 30, "cooldown": 0, "max_cooldown": 5.0,
     "damage": 60, "range": 96, "aoe": 48, "skill_type": "aoe"},
    {"name": "Barrière arcane", "cost": 25, "cooldown": 0, "max_cooldown": 8.0,
     "shield": 40, "duration": 5.0, "skill_type": "shield"},
    {"name": "Chaîne d'éclair", "cost": 40, "cooldown": 0, "max_cooldown": 9.0,
     "damage": 45, "range": 110, "aoe": 40, "skill_type": "aoe"},
    {"name": "Météore", "cost": 55, "cooldown": 0, "max_cooldown": 14.0,
     "damage": 110, "range": 128, "aoe": 80, "skill_type": "aoe"},
]

ARCHER_SKILLS = [
    {"name": "Tir perçant", "cost": 20, "cooldown": 0, "max_cooldown": 3.5,
     "damage": 45, "range": 140, "aoe": 20, "skill_type": "aoe"},
    {"name": "Rafale de flèches", "cost": 30, "cooldown": 0, "max_cooldown": 7.0,
     "damage": 30, "range": 130, "aoe": 45, "skill_type": "aoe"},
    {"name": "Flèche empoisonnée", "cost": 35, "cooldown": 0, "max_cooldown": 10.0,
     "damage": 70, "range": 140, "aoe": 18, "skill_type": "aoe"},
    {"name": "Éclat d'argent", "cost": 45, "cooldown": 0, "max_cooldown": 12.0,
     "damage": 80, "range": 135, "aoe": 50, "skill_type": "aoe"},
]

ARCHETYPE_SKILLS = {
    "warrior": WARRIOR_SKILLS,
    "mage": MAGE_SKILLS,
    "archer": ARCHER_SKILLS,
}

# Stats de base par archétype
ARCHETYPE_STATS = {
    "warrior": {"max_hp": 550, "damage": 30, "armor": 8, "speed": 50, "range": 40,
                "attack_speed": 0.8, "radius": 20, "max_mana": 100},
    "mage": {"max_hp": 350, "damage": 40, "armor": 2, "speed": 45, "range": 96,
             "attack_speed": 1.2, "radius": 16, "max_mana": 160},
    "archer": {"max_hp": 320, "damage": 28, "armor": 3, "speed": 62, "range": 130,
               "attack_speed": 1.0, "radius": 16, "max_mana": 90},
}

# Modificateurs de faction appliqués aux stats de base de l'archétype
FACTION_MODS = {
    "human": {},            # équilibré
    "orc": {"damage": 5},
    "elf": {"speed": 8, "range": 12},
    "dwarf": {"armor": 3, "max_hp": 50},
}

# Noms + unit_type propres à chaque faction × archétype
HERO_IDENTITY = {
    "human": {"warrior": ("hero_swordmaster", "Lionel"), "mage": ("hero_arcanist", "Alaric"),
              "archer": ("hero_warden", "Rhea")},
    "orc": {"warrior": ("hero_berserker", "Grulka"), "mage": ("hero_shaman", "Drak'thar"),
            "archer": ("hero_harrier", "Skarra")},
    "elf": {"warrior": ("hero_blade", "Faelan"), "mage": ("hero_druid", "Elowen"),
            "archer": ("hero_ranger", "Aelwin")},
    "dwarf": {"warrior": ("hero_ironguard", "Borin"), "mage": ("hero_runesmith", "Frida"),
              "archer": ("hero_marksman", "Kjell")},
}

HERO_ORDER = ("warrior", "mage", "archer")

# Coût d'invocation par archétype (identique pour toutes les factions)
HERO_SUMMON_COSTS = {
    "warrior": {"gold": 220, "wood": 100, "food": 20},
    "mage": {"gold": 300, "wood": 120, "food": 10},
    "archer": {"gold": 200, "wood": 80, "food": 20},
}


def faction_hero_types(faction: str) -> list:
    """Retourne les unit_type des héros de la faction, dans l'ordre d'invocation."""
    ident = HERO_IDENTITY.get(faction, HERO_IDENTITY["human"])
    return [ident[role][0] for role in HERO_ORDER]


def hero_config(faction: str, role: str) -> dict:
    """Construit la config d'un héros (stats fusionnées + skills)."""
    role = role if role in ("warrior", "mage", "archer") else "warrior"
    ident = HERO_IDENTITY.get(faction, HERO_IDENTITY["human"]).get(role)
    unit_type, name = ident
    stats = dict(ARCHETYPE_STATS[role])
    for k, v in FACTION_MODS.get(faction, {}).items():
        stats[k] = stats.get(k, 0) + v
    return {
        "unit_type": unit_type,
        "name": name,
        "role": role,
        "faction_id": faction,
        "stats": stats,
        "skills": [dict(s) for s in ARCHETYPE_SKILLS[role]],
    }


def create_faction_hero(faction: str, role: str, x: int, y: int,
                        side: str = "player") -> Hero:
    """Crée un héros de faction (role: warrior/mage/archer) pour le camp `side`."""
    config = hero_config(faction, role)
    hero = Hero(x, y, side, config=config)
    return hero


def resolve_unit_type(unit_type: str):
    """Retrouve (faction, role) à partir d'un unit_type de héros, sinon None."""
    if not isinstance(unit_type, str):
        return None
    for faction, roles in HERO_IDENTITY.items():
        for role, (ut, _name) in roles.items():
            if ut == unit_type:
                return faction, role
    return None