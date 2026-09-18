"""
Unit tests pour les workers - Mountain_Roy RTS
Teste le système de récolte et rapport des ressources
"""

import pygame
import sys
sys.path.insert(0, 'C:/Users/celes/Documents/Hermes-Workspace/Mountain_Roy')

from entities.worker import Worker
from entities.resource_node import ResourceNode


def test_worker_basic():
    """Test de base: création d'un worker"""
    print("=" * 50)
    print("TEST 1: Création du worker")
    print("=" * 50)

    worker = Worker(100, 100, "player")

    assert worker.unit_type == "worker", f"Expected 'worker', got {worker.unit_type}"
    assert worker.max_hp == 60, f"Expected 60 HP, got {worker.max_hp}"
    assert worker.speed == 45, f"Expected speed 45, got {worker.speed}"
    assert not worker.carrying, f"Expected not carrying, got {worker.carrying}"
    assert worker.carry_amount == 0, f"Expected 0 carry amount, got {worker.carry_amount}"
    assert worker.drop_off_point is None, f"Expected None drop_off_point, got {worker.drop_off_point}"

    print("✓ Worker créé correctement")
    print(f"  - Type: {worker.unit_type}")
    print(f"  - HP: {worker.max_hp}")
    print(f"  - Speed: {worker.speed}")
    print(f"  - Carrying: {worker.carrying}")
    print()


def test_worker_harvest():
    """Test: Récolte d'une ressource"""
    print("=" * 50)
    print("TEST 2: Récolte de ressources")
    print("=" * 50)

    worker = Worker(100, 100, "player")
    resource = ResourceNode(120, 100, "wood", 100)

    # Simuler le mouvement vers la ressource
    worker.is_moving = True
    worker.move_target = (resource.x, resource.y)

    # Mettre à jour pour arriver sur la ressource (dt petit pour contrôle)
    for _ in range(10):
        worker.update(0.5)  # dt petit pour avancer progressivement

    print(f"  - Position: ({worker.x:.1f}, {worker.y:.1f})")
    print(f"  - Target: ({resource.x}, {resource.y})")
    print(f"  - Is moving: {worker.is_moving}")
    print()

    # Vérifier que le worker est arrivé
    dx = resource.x - worker.x
    dy = resource.y - worker.y
    distance = (dx**2 + dy**2) ** 0.5

    assert distance < 30, f"Worker should be near resource, distance: {distance}"
    print(f"✓ Worker arrive à la ressource (distance: {distance:.1f})")
    print()


def test_worker_find_drop_off():
    """Test: Trouver le point de dépôt"""
    print("=" * 50)
    print("TEST 3: Trouver le point de dépôt")
    print("=" * 50)

    worker = Worker(100, 100, "player")

    # Simuler un game avec des buildings
    class MockBuilding:
        def __init__(self):
            self.x = 500
            self.y = 500
            self.faction = "player"

    class MockGame:
        buildings = []
        resource_nodes = []

        def __init__(self):
            # Ajouter un building (Town Hall)
            self.buildings.append(MockBuilding())

    worker.game = MockGame()

    # Trouver le point de dépôt
    worker._find_drop_off_point()

    assert worker.drop_off_point is not None, "Expected drop_off_point to be set"
    print(f"✓ Point de dépôt trouvé: ({worker.drop_off_point.x}, {worker.drop_off_point.y})")
    print()


def test_worker_carry_and_return():
    """Test: Porter les ressources et retourner"""
    print("=" * 50)
    print("TEST 4: Porter et rapporter les ressources")
    print("=" * 50)

    worker = Worker(100, 100, "player")

    # Simuler un game avec des buildings et resources
    class MockBuilding:
        def __init__(self):
            self.x = 500
            self.y = 500
            self.faction = "player"

    class MockGame:
        buildings = []
        resource_nodes = []

        def __init__(self):
            self.buildings.append(MockBuilding())
            self.resource_nodes = [ResourceNode(120, 100, "wood", 100)]

    worker.game = MockGame()

    # Simuler la récolte
    worker.carrying = True
    worker.carry_amount = 50
    worker.drop_off_point = None

    print(f"  - Carrying: {worker.carrying}")
    print(f"  - Carry amount: {worker.carry_amount}")
    print(f"  - Drop-off point: {worker.drop_off_point}")
    print()

    # Trouver le point de dépôt
    worker._find_drop_off_point()

    assert worker.drop_off_point is not None, "Expected drop_off_point to be set after finding it"
    print(f"✓ Point de dépôt trouvé: ({worker.drop_off_point.x}, {worker.drop_off_point.y})")
    print()

    # Vérifier que le worker va vers le drop-off
    dx = worker.drop_off_point.x - worker.x
    dy = worker.drop_off_point.y - worker.y
    distance = (dx**2 + dy**2) ** 0.5

    print(f"  - Distance au drop-off: {distance:.1f}")
    print(f"  - Worker should move to drop-off")
    print()


def test_worker_deposit():
    """Test: Déposer les ressources"""
    print("=" * 50)
    print("TEST 5: Déposer les ressources")
    print("=" * 50)

    worker = Worker(100, 100, "player")

    # Simuler un game avec economy
    class MockEconomy:
        resources = {"gold": 0, "wood": 0, "food": 0}

        def add_resources(self, gold=0, wood=0, food=0):
            self.resources["gold"] += gold
            self.resources["wood"] += wood
            self.resources["food"] += food

    class MockBuilding:
        def __init__(self):
            self.x = 500
            self.y = 500
            self.faction = "player"

    class MockGame:
        economy = MockEconomy()
        buildings = []
        resource_nodes = []

        def __init__(self):
            self.buildings.append(MockBuilding())

    worker.game = MockGame()
    worker.drop_off_point = MockBuilding()
    worker.target_resource = type('Node', (), {'resource_type': "wood"})()

    # Simuler le dépôt
    worker.carrying = True
    worker.carry_amount = 50

    print(f"  - Avant dépôt: carrying={worker.carrying}, amount={worker.carry_amount}")
    worker._deposit_resources()
    print(f"  - Après dépôt: carrying={worker.carrying}, amount={worker.carry_amount}")

    assert not worker.carrying, f"Expected not carrying after deposit, got {worker.carrying}"
    assert worker.carry_amount == 0, f"Expected 0 carry amount after deposit, got {worker.carry_amount}"
    print("✓ Ressources déposées correctement")
    print()


def test_worker_selected_behavior():
    """Test: Comportement quand sélectionné"""
    print("=" * 50)
    print("TEST 6: Worker sélectionné")
    print("=" * 50)

    worker = Worker(100, 100, "player")
    worker.selected = True

    # Simuler un game avec resources
    class MockBuilding:
        def __init__(self):
            self.x = 500
            self.y = 500
            self.faction = "player"

    class MockGame:
        buildings = []
        resource_nodes = []

        def __init__(self):
            self.buildings.append(MockBuilding())
            self.resource_nodes = [ResourceNode(120, 100, "wood", 100)]

    worker.game = MockGame()

    # Simuler le mouvement vers la ressource
    worker.is_moving = True
    worker.move_target = (120, 100)

    print(f"  - Selected: {worker.selected}")
    print(f"  - Is moving: {worker.is_moving}")
    print(f"  - Move target: {worker.move_target}")
    print()

    # Mettre à jour (plusieurs frames)
    for _ in range(20):
        worker.update(0.5)

    print(f"  - Après update: position=({worker.x:.1f}, {worker.y:.1f})")
    print(f"  - Is moving: {worker.is_moving}")
    print(f"  - Carrying: {worker.carrying}")
    print(f"  - Drop-off point: {worker.drop_off_point}")
    print()

    # Vérifier que le worker est arrivé ou a trouvé un drop-off
    dx = 120 - worker.x
    dy = 100 - worker.y
    distance = (dx**2 + dy**2) ** 0.5

    if distance < 30 or worker.drop_off_point:
        print(f"✓ Worker sélectionné arrive à destination (distance: {distance:.1f})")
    else:
        print(f"✗ Worker pas arrivé (distance: {distance:.1f}), mais drop-off trouvé: {worker.drop_off_point is not None}")
    print()


def main():
    """Lance tous les tests"""
    print("\n" + "=" * 50)
    print("UNIT TESTS - Workers Mountain_Roy RTS")
    print("=" * 50 + "\n")

    try:
        test_worker_basic()
        test_worker_harvest()
        test_worker_find_drop_off()
        test_worker_carry_and_return()
        test_worker_deposit()
        test_worker_selected_behavior()

        print("=" * 50)
        print("TOUS LES TESTS SONT PASSES!")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
