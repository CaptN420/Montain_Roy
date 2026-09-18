# Mountain_Roy - Audit & Bug Report

## CRITICAL BUGS (Must Fix)

### 1. AI Resource Gathering Bug (game.py line 83-84)
**Problem:** Incorrect operator precedence in condition
```python
# CURRENT (WRONG):
if u.faction == "enemy" and not hasattr(u, 'target') or u.target is None
# Evaluates as: ((u.faction == "enemy") and (not hasattr)) or (u.target is None)
# ANY unit with target=None gets selected, not just enemy workers!

# FIX:
if u.faction == "enemy" and ((not hasattr(u, 'target')) or u.target is None):
```

### 2. AI Defend Base Distance Bug (game.py line 207)
**Problem:** `distance_to()` takes a Vector2 or tuple, not separate x,y
```python
# CURRENT (WRONG):
pygame.math.Vector2(u.x, u.y).distance_to(enemy_units[0].x, enemy_units[0].y)

# FIX:
pygame.math.Vector2(u.x, u.y).distance_to((enemy_units[0].x, enemy_units[0].y))
```

### 3. Tech Tree Cost Check Bypass (tech_tree.py line 159)
**Problem:** Checks against fake resources instead of actual player resources
```python
# CURRENT (WRONG):
if tech and tech.can_research({"gold": 9999, "wood": 9999, "food": 9999}):

# FIX:
if tech and tech.can_research({
    "gold": self.game.economy.gold,
    "wood": self.game.economy.wood,
    "food": self.game.economy.food
}):
```

### 4. Hero Skills Not Implemented (hero.py line 126)
**Problem:** All skills have `pass` statement and do nothing
```python
# CURRENT:
if "damage" in skill:
    pass  # Will be implemented later

# FIX: Implement actual skill effects (damage enemies, heal allies, etc.)
```

---

## IMPORTANT BUGS (Should Fix)

### 5. No Unit Stacking/Collision
Units can overlap completely. Need separation logic.

### 6. Building Placement Validation Missing
Buildings can be placed on top of each other or on water.

### 7. Map Generation Issues
Random placement doesn't ensure passable paths or balanced resource distribution.

---

## GAMEPLAY IMPROVEMENTS

### 8. Add Unit Selection Feedback
- Show selection ring animation
- Add attack/defend order indicators

### 9. Improve AI Behavior
- Add resource management (gather -> build -> produce -> attack cycle)
- Add tactical retreat when low HP
- Add reinforcement production

### 10. Add Sound Effects
- Attack sounds
- Build completion sound
- Unit selection sound
- Resource collection sound

### 11. Improve HUD
- Show unit count per type
- Add production queue display
- Show tech research progress bar

### 12. Add Tutorial/Instructions
- First-time player guide
- Keyboard shortcuts reference
- Mission objectives highlight

---

## IMPLEMENTATION PRIORITY

**P0 (Critical - Fix Now):**
1. AI gather bug
2. AI defend distance bug
3. Tech tree cost check

**P1 (Important - Next Session):**
4. Hero skills implementation
5. Unit collision/stacking
6. Building placement validation

**P2 (Enhancement - Future):**
7-12. Gameplay improvements

---

## FILES TO MODIFY

| File | Changes Needed |
|------|---------------|
| `systems/ai.py` | Fix gather/defend bugs |
| `systems/tech_tree.py` | Fix cost check |
| `entities/hero.py` | Implement skills |
| `systems/movement.py` | Add collision avoidance |
| `systems/construction.py` | Add placement validation |
| `map/game_map.py` | Improve generation |

---

## QUICK FIX COMMANDS

Run these to apply critical fixes:

```bash
cd Mountain_Roy
.venv/Scripts/python.exe -c "
# Fix AI gather bug
import re
with open('systems/ai.py', 'r') as f:
    content = f.read()
content = content.replace(
    'if u.faction == \"enemy\" and not hasattr(u, \\'target\\') or u.target is None:',
    'if u.faction == \"enemy\" and ((not hasattr(u, \\'target\\')) or u.target is None):'
)
with open('systems/ai.py', 'w') as f:
    f.write(content)
print('AI gather bug fixed')
"
```
