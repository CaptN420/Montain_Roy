"""Audit probe : exerce des chemins gameplay headless et signale les exceptions."""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
pygame.init(); pygame.display.set_mode((800, 600))

errors = []

def step(name, fn):
    try:
        fn()
        print(f"OK   {name}")
    except Exception as e:
        errors.append((name, e))
        print(f"FAIL {name}: {type(e).__name__}: {e}")

from core.game import Game
from entities.building import HeroHall

def base():
    g = Game(); g._apply_faction("human"); g.state = "playing"
    g.economy.gold=g.economy.wood=g.economy.food=5000
    return g

# 1. Multi-frame update (all systems) with time acceleration
def upd():
    g = base()
    g.time_scale = 4
    for _ in range(200):
        g.update(0.016)
step("update 200 frames @x4", upd)

# 2. Summon 3 heroes + use skills + death removal + selected cleanup
def herocyc():
    g = base()
    g._selected_building = HeroHall(300,300,"player")
    for i in range(3): g._summon_hero(i)
    heroes = [u for u in g.units if u.unit_type.startswith("hero_")]
    g.selected_units = list(heroes)
    # skill 0 on selected hero
    for h in heroes:
        h.use_skill(0, units=g.units)
    # kill heroes (simulate death removal path)
    for h in heroes:
        h.hp = 0
    # run update: game.Update removes dead units (line ~1296)
    g.update(0.016)
    g.selected_units = [u for u in g.selected_units if getattr(u,'hp',0)>0]
    alive = [u for u in g.units if u.unit_type.startswith("hero_")]
    assert alive == [], f"les 3 héros morts doivent être retirés, restants={len(alive)}"
step("hero cycle (summon+skill+death removal)", herocyc)

# 3. Production queue + unit spawn + faction modifiers
def prod():
    g = base()
    # find a production building
    prod = [b for b in g.buildings if b.building_type=="human_barracks"][0]
    g._selected_building = prod
    g._produce_selected_index(0)  # enqueue first unlocked combat unit
    for _ in range(600):  # enough for production
        g.update(0.016)
    # produced units get faction modifiers & appear
    new_units = [u for u in g.units if u.faction=="player" and u.unit_type not in ("worker","builder","hero") ]
    assert any(u for u in new_units), "aucune unité produite?"
    print("   unités joueur:", [u.unit_type for u in new_units])
step("production queue + spawn", prod)

# 4. Worker auto-gather end-to-end over many frames
def gather():
    g = base()
    for _ in range(3000):
        g.update(0.016)
    # economy should have moved from workers gathering
    print("   gold:", g.economy.gold)
step("worker auto-gather 3000 frames", gather)

# 5. Enemy AI update loop (builds, produces, summons, gathers)
def ailoop():
    g = base()
    g.state = "playing"
    # force enemy to have resources
    g.enemy_economy.gold=g.enemy_economy.wood=g.enemy_economy.food=5000
    for _ in range(2000):
        g.update(0.016)
    print("   enemy units:", len([u for u in g.units if u.faction=='enemy']))
    print("   enemy buildings:", len([b for b in g.buildings if b.faction=='enemy']))
step("enemy AI 2000 frames", ailoop)

# 6. Right-click attack order (combat) over frames
def combat():
    g = base()
    # put a player warrior near enemy
    from entities.unit_types import Warrior
    w = Warrior(100,100,"player"); g.units.append(w)
    for _ in range(300): g.update(0.016)
step("combat frames", combat)

print("\n=== RESULT:", len(errors), "erreurs ===")
for n,e in errors:
    print(f"[{n}] {e}")