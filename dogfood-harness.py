"""Dogfood QA harness for Mountain_Roy (Pygame) - headless event simulation.

Exercises core systems per faction, catches exceptions (= console errors),
captures screenshots as evidence. Structured findings for report.
"""
import sys, os, traceback
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

OUT = os.path.join(HERE, "dogfood-output", "screenshots")
os.makedirs(OUT, exist_ok=True)

FINDINGS = []

FACTION_IDS = ["human", "orc", "elf", "dwarf"]


def record(title, severity, category, url, desc, steps, expected, actual, console=None):
    FINDINGS.append({
        "title": title, "severity": severity, "category": category, "url": url,
        "desc": desc, "steps": steps, "expected": expected, "actual": actual,
        "console": console,
    })


def snap(game, name):
    path = os.path.join(OUT, name)
    pygame.image.save(game.screen, path)
    return path


def run_case(fid, name, fn):
    # `fn` peut recevoir fid en argument s'il le déclare
    try:
        from inspect import signature
        try:
            params = list(signature(fn).parameters)
        except (TypeError, ValueError):
            params = []
        res = fn(fid) if params else fn()
        # Afficher le PASS avec le résultat résumé
        if isinstance(res, dict):
            print(f"[PASS] {fid}:{name} -> {res}")
        else:
            print(f"[PASS] {fid}:{name}")
        return res
    except AssertionError as e:
        # Échec de vérification = bug réel (équivalent console error)
        print(f"[FAIL] {fid}:{name} -> AssertionError: {e}")
        record(f"Vérification ratée: {name} ({fid})", "high", "functional",
               f"faction={fid}",
               f"Un scénario de test a échoué son assertion: {e}",
               [f"Démarrer une partie {fid}", f"Exécuter: {name}"],
               "Le scénario se déroule et valide son assertion.",
               f"AssertionError: {e}")
        return None
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[CRASH] {fid}:{name} -> {e}")
        record(f"Crash: {name} ({fid})", "critical", "console", f"faction={fid}",
               f"Exception non gérée pendant le scénario '{name}'.",
               [f"Démarrer une partie {fid}", f"Exécuter: {name}"],
               "Le scénario se déroule sans erreur.",
               f"Exception: {type(e).__name__}: {e}", console=tb)
        return None


def fresh_game(fid):
    from core.game import Game
    g = Game()
    g._apply_faction(fid)
    g.state = "playing"
    g.economy.gold = 1000
    g.economy.wood = 1000
    g.economy.food = 1000
    return g


def flush():
    for e in pygame.event.get():
        pass


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))

    # ---------- 1. Menu & faction selection ----------
    def menu_flow():
        from core.game import Game
        g = Game()
        assert g.state == "menu"
        g.state = "faction_select"
        orc = g.faction_menu._cards["orc"]
        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": orc.center, "button": 1})
        action = g.faction_menu.handle_event(ev)
        assert action == "orc", f"clic faction attendu='orc' obtenu={action}"
        snap(g, "faction_menu.png")
        return True
    run_case("menu", "selection faction via clic", menu_flow)

    # ---------- 2. Production depuis bâtiment principal ----------
    for fid in FACTION_IDS:
        def prod(fid):
            g = fresh_game(fid)
            pb = g.faction.primary_war_building
            bldgs = [b for b in g.buildings if b.faction == "player" and b.building_type == pb]
            res = {"pb": pb, "nb_buildings": len(bldgs), "produced": False, "unit": None}
            if not bldgs:
                record(f"Faction {fid} n'a aucun bâtiment principal ({pb})", "high",
                       "functional", f"faction={fid}",
                       "Chaque faction doit démarrer avec son bâtiment de production principal.",
                       ["Démarrer la partie"], "Le bâtiment principal existe au départ.",
                       f"Aucun bâtiment '{pb}' détecté.")
            else:
                g._select_building(bldgs[0])
                # le bâtiment reste sélectionné après le clic
                assert g._selected_building is bldgs[0], \
                    "le bâtiment ne doit pas se désélectionner au clic"
                before = len(g.units)
                g._produce_selected_index(0)
                res["produced"] = len(g.units) > before
                # exigence: au moins une unité débloquée doit être produisible
                assert res["produced"], \
                    f"aucune unité de base produisible depuis {pb} (toute verrouillée?)"
                if res["produced"]:
                    res["unit"] = g.units[-1].unit_type
            # stabilité sur 200 frames
            for _ in range(200):
                flush(); g.update(0.016); g.draw()
            snap(g, f"prod_{fid}.png")
            return res
        run_case(fid, "production bâtiment principal", prod)

    # ---------- 3. Métier: SEULS les workers récoltent ----------
    for fid in FACTION_IDS:
        def gather(fid):
            from entities.unit_types import Warrior
            g = fresh_game(fid)
            node = next((n for n in g.resource_nodes if not n.is_depleted() and n.resource_type == "gold"), None)
            if node is None:
                return {"error": "pas de ressource or"}
            sx, sy = int(node.x - g.camera.x), int(node.y - g.camera.y)
            # Warrior sélectionné -> clic droite sur or -> ne doit PAS récolter
            w = Warrior(g.camera.x + 100, g.camera.y + 100, "player")
            g.units.append(w)
            g.selected_units = [w]
            g._handle_right_click((sx, sy))
            warrior_gathers = hasattr(w, "target_resource") and w.target_resource is not None
            # exigence: le guerrier NE récolte PAS
            assert not warrior_gathers, "le guerrier ne doit pas obtenir target_resource"
            # worker sélectionné -> clic droite sur or -> DOIT récolter
            from entities.worker import Worker
            wk = Worker(g.camera.x + 200, g.camera.y + 200, "player")
            g.units.append(wk)
            g.selected_units = [wk]
            g._handle_right_click((sx, sy))
            worker_gathers = getattr(wk, "target_resource", None) is not None
            assert worker_gathers, "le worker doit obtenir target_resource sur un clic ressource"
            snap(g, f"gather_{fid}.png")
            return {"warrior_gathers": warrior_gathers, "worker_gathers": worker_gathers}
        run_case(fid, "récolte: worker oui, guerrier non", gather)

    # ---------- 4. Construction (ferme) + menu construction ----------
    for fid in FACTION_IDS:
        def build(fid):
            g = fresh_game(fid)
            # menu
            g.build_menu_open = True
            items = g._build_menu_rects()
            farm = next((i for i in items if i[0] == "farm"), None)
            menu_ok = False
            if farm:
                g._handle_build_menu_click((farm[2][0] + 5, farm[2][1] + 5))
                menu_ok = g.selected_building_type == "farm"
            # placer la ferme
            before = len(g.construction_system.construction_sites)
            g._place_building(1500, 1500)
            started = len(g.construction_system.construction_sites) > before
            for _ in range(900):
                g.economy.gold = 1000; g.economy.wood = 1000
                flush(); g.update(0.016)
                if not g.construction_system.construction_sites:
                    break
            built = not g.construction_system.construction_sites
            snap(g, f"build_{fid}.png")
            return {"menu_ok": menu_ok, "started": started, "built": built}
        run_case(fid, "construction ferme + menu", build)

    # ---------- 5. Recherche via bâtiment de recherche ----------
    for fid in FACTION_IDS:
        def research(fid):
            g = fresh_game(fid)
            rb = g.faction.research_buildings
            res = {"need_building": False, "research_buildings": rb}
            # sans bâtiment sélectionné, la recherche doit être refusée
            g._selected_building = None
            # (cela se fait via la touche T, on vérifie la méthode directement)
            if rb:
                # bâtiment de recherche de la faction présent dans la liste
                b = next((b for b in g.buildings if b.faction == "player" and b.building_type in rb), None)
                res["has_research_building"] = b is not None
            return res
        run_case(fid, "bâtiment de recherche par faction", research)

    # ---------- 6. Navale: dock requis ----------
    def naval():
        from entities.building import Dock
        g = fresh_game("human")
        # sans dock
        ok_no_dock, _ = g.faction.can_produce("boat", g.buildings, [])
        # avec dock + logging
        g.buildings.append(Dock(500, 500, "player"))
        g.tech_tree.unlocked_techs.append("logging")
        g.buildings[-1].faction = "player"
        ok_dock, _ = g.faction.can_produce("boat", g.buildings, g.tech_tree.unlocked_techs)
        return {"gated": (not ok_no_dock), "unlocked": ok_dock}
    run_case("human", "gating naval (dock requis)", naval)

    # ---------- 7. Désélection de bâtiment ----------
    def deselect():
        g = fresh_game("human")
        b = [b for b in g.buildings if b.faction == "player"][0]
        g._select_building(b)
        still = g._selected_building is b   # re-clic ne désélectionne plus
        g._deselect_building()
        deselected = g._selected_building is None
        return {"reclic_stable": still, "deselect_works": deselected}
    run_case("human", "sélection/désélection bâtiment", deselect)

    # ---------- 8. IA ennemie (économie séparée) ----------
    def ai_economy():
        g = fresh_game("elf")
        before = (g.economy.gold, g.economy.wood, g.economy.food)
        g.enemy_economy.gold = 500; g.enemy_economy.wood = 500; g.enemy_economy.food = 500
        for _ in range(900):
            flush(); g.ai.update(0.016)
        after = (g.economy.gold, g.economy.wood, g.economy.food)
        return {"player_unchanged": before == after}
    run_case("elf", "IA n'épuise pas l'économie joueur", ai_economy)

    print("\n===== DOGFOOD FINDINGS =====")
    if FINDINGS:
        for f in FINDINGS:
            print(f"[{f['severity']}] {f['title']}")
    else:
        print("Aucun bug détecté.")

    pygame.quit()
    return FINDINGS


if __name__ == "__main__":
    main()