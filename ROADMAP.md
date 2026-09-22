# Mountain_Roy Roadmap

## 1. Immediate Priority: Stability & Infrastructure (The "Foundation")
The presence of many "AUDIT" files and "FIX" notes suggests the project is currently in a heavy debugging/refactoring phase.
*   **Verify the Core Loop:** Run the project using `run_game.bat` or `play.bat` to see if the current state is actually playable.
*   **Fix Worker/Economy Issues:** The `AUDIT_WORKERS.md`, `AUDIT_WORKER_FIX.md`, and `WORKER_CONTROL_FIX.md` files indicate significant issues with how workers gather resources.
    *   *Action:* Review `systems/economy.py` and `entities/worker.py` to ensure the worker state machine is robust.

## 2. Content & Mechanics (The "Meat")
Once the workers are gathering resources correctly, move to the features that define the RTS experience:
*   **Pathfinding & Movement:** Check `systems/pathfinding.py`. Ensure units navigate around obstacles (tiles in `map/tile.py`) and don't get stuck on corners.
*   **Construction System:** Review `systems/construction.py` and `entities/building.py`. Ensure the transition from "construction site" to "functional building" is seamless.
*   **Tech Tree:** Verify `systems/tech_tree.py`. This is the backbone of progression.

## 3. Polish & UX (The "Feel")
*   **Fog of War:** The `systems/fog_of_war.py` file is present but often one of the hardest systems to optimize. Ensure it doesn't tank the FPS.
*   **UI/HUD:** Work on `ui/hud.py` and `ui/menus.py` to ensure the user can actually see the stats (resources, unit counts) and interact with the construction menu.
*   **AI Behavior:** Once the mechanics are solid, start fleshing out `systems/ai.py`.

## 4. Quality Assurance (The "Safety Net")
*   **Run the Test Suite:** You have a massive `tests/` directory. You should be running these regularly to ensure new fixes don't break old systems.
    *   *Action:* Run `pytest` (or whatever runner is configured) on the `tests/` folder.
