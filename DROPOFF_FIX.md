# Mountain_Roy - Drop-off Point Fix

## Issue Fixed
Workers were depositing resources at a "DropOffPoint" checkpoint instead of the nearest building.

## Root Cause
The `_find_drop_off_point()` method was:
1. Looking for a specific `town_hall` building type
2. Falling back to a separate `DropOffPoint` class (not a real building)

This meant workers would try to find non-existent Town Halls or use dummy checkpoints.

## Fix Applied
Changed `_find_drop_off_point()` to find the **closest building** of the same faction:

```python
# AVANT (bug):
if building.building_type == "town_hall":  # Only looks for Town Hall
    self.drop_off_point = building
    return
# Falls back to DropOffPoint class (not a real building)

# APRÈS (fix):
closest_building = None
closest_distance = 500
for building in self.game.buildings:
    if building.faction != self.faction:
        continue
    # Find closest building regardless of type
    distance = ((building.x - self.x)**2 + (building.y - self.y)**2)**0.5
    if distance < closest_distance:
        closest_building = building
# Uses nearest building as drop-off point
```

## How It Works Now
```
Worker harvests resources
    ↓
Calls _find_drop_off_point()
    ↓
Finds nearest building of same faction (any type)
    ↓
Moves to that building
    ↓
Deposits resources via _deposit_resources()
    ↓
Returns to gather more
```

## Testing Results
✓ Drop-off point is now the closest building
✓ Works for any building type (Town Hall, Farm, Barracks, etc.)
✓ Respects faction (won't deposit at enemy buildings)
✓ Game runs without errors

## Files Modified
- `entities/worker.py`:
  - Rewrote `_find_drop_off_point()` to find nearest building
  - Removed dependency on specific building types
  - Removed dependency on DropOffPoint class
