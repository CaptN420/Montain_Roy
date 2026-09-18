# Mountain_Roy - Worker System Audit & Bug Fixes

## Issues Found and Fixed

### 1. Type Mismatch in Auto-Gather
**Bug**: `_auto_gather_resources()` checked for `unit.unit_type == "scout"` instead of `"worker"`
- Workers were never auto-assigned to resources
- Only units typed as "scout" would trigger resource finding

**Fix**: Changed check from `"scout"` to `"worker"`

### 2. Resource Type Filtering Missing
**Bug**: No filtering for wood/food vs gold mines
- Workers would try to harvest any resource type indiscriminately
- Gold mines need special handling (max 3 workers per mine)

**Fix**: Added resource_type checks:
- Prefer wood/food within 300px radius
- Fall back to gold mines with available slots

### 3. Duplicate Harvest Logic
**Bug**: Two separate harvest systems running in parallel:
1. `_auto_gather_resources()` method (called once per frame)
2. Inline harvesting in `update()` loop (also called every frame)

This caused:
- Conflicting movement commands
- Double resource collection
- Inconsistent state

**Fix**: Consolidated all worker logic into one place:
- Removed inline harvest code from game.py update loop
- Worker update now handled entirely in worker.py's `update()` method
- Game loop only calls `unit.update(dt)` for workers

### 4. Movement System Conflict
**Bug**: `_auto_gather_resources()` called `self.movement_system.move_to()` but then the inline code also tried to move the unit
- Workers received conflicting movement commands
- Sometimes moved toward resource, sometimes stopped

**Fix**: 
- Removed `movement_system.move_to()` call from auto-gather
- Worker handles its own movement in worker.py update()
- Game loop just calls `unit.update(dt)` without interference

## How It Works Now

### Complete Worker Lifecycle:
```
1. Spawn near base (4 workers)
2. _auto_gather_resources() finds nearest wood/food/gold
3. Worker.set target_resource and starts moving
4. At <30px: harvest 10 units, set carrying=True
5. Find drop_off_point (Town Hall)
6. Move back to Town Hall
7. Deposit resources via _deposit_resources()
8. Clear carrying, find new resource
9. Repeat forever
```

### Gold Mine Special Handling:
- Max 3 workers per mine (assigned_workers list)
- Workers auto-assign to mines with available slots
- Visual indicator shows worker count on mine
- Workers stay at mine until depleted

## Controls
| Key | Action |
|-----|--------|
| `1-6` | Produce units (workers included) |
| `B` | Toggle build mode |
| Click | Select units / place buildings |
| Right-click | Order selected units to resource/enemy |

## Files Modified
- `core/game.py`:
  - Fixed `_auto_gather_resources()` type check
  - Added resource type filtering (wood/food vs gold)
  - Removed duplicate harvest logic from update loop
  - Workers now use their own update() method
  
- `entities/worker.py`:
  - Added `_find_and_assign_to_resource()` method
  - Fixed movement logic for continuous gathering
  - Added safety checks for game reference

## Testing Results
✓ Worker creation works
✓ Resource assignment works
✓ Movement toward resources works
✓ Resource harvesting works
✓ Drop-off point assignment works
✓ Game runs without errors
