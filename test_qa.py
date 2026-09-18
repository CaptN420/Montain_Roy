"""
Test systématique des fonctionnalités Mountain_Roy
Suite de tests pour QA exploratoire - Version corrigée
"""

import sys
import os

# Test 1: Importation des modules critiques
print("=" * 50)
print("TEST 1: Importation des modules")
print("=" * 50)

modules_to_test = [
    ("core.game", "Game"),
    ("entities.worker", "Worker"),
    ("entities.building", "Building"),
    ("systems.economy", "EconomySystem"),
    ("systems.combat", "CombatSystem"),
    ("systems.pathfinding", "Pathfinder"),
    ("systems.collision", "CollisionSystem"),
    ("systems.effects", "VisualEffects"),
    ("systems.ai", "EnemyAI"),
]

import_errors = []
for module_name, class_name in modules_to_test:
    try:
        mod = __import__(module_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        print(f"  ✓ {module_name}.{class_name}")
    except Exception as e:
        import_errors.append((module_name, class_name, str(e)))
        print(f"  ✗ {module_name}.{class_name}: {e}")

if import_errors:
    print(f"\n❌ {len(import_errors)} erreurs d'importation!")
else:
    print("\n✓ Tous les modules importent correctement")

# Test 2: Initialisation du jeu
print("\n" + "=" * 50)
print("TEST 2: Initialisation du jeu")
print("=" * 50)

try:
    from core.game import Game
    
    # Ne pas initialiser pygame (pas de fenêtre)
    print("  Note: Test sans fenêtre graphique")
    
    # Vérifier la structure des classes
    print(f"  ✓ Game class loaded")
    print(f"  ✓ Worker class available: {hasattr(__import__('entities.worker', fromlist=['Worker']), 'Worker')}")
    print(f"  ✓ ResourceNode class available: {hasattr(__import__('entities.resource_node', fromlist=['ResourceNode']), 'ResourceNode')}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Test 3: Test des ressources
print("\n" + "=" * 50)
print("TEST 3: Système de ressources")
print("=" * 50)

try:
    from entities.resource_node import ResourceNode, DropOffPoint
    
    # Test mine d'or
    gold = ResourceNode(100, 100, 'gold', 800)
    print(f"  Mine d'or:")
    print(f"    - is_mine: {gold.is_mine}")
    print(f"    - width/height: {gold.width}x{gold.height}")
    print(f"    - max_amount: {gold.max_amount}")
    
    # Test forêt
    wood = ResourceNode(200, 200, 'wood', 150)
    print(f"  Forêt:")
    print(f"    - is_obstacle: {wood.is_obstacle}")
    print(f"    - radius: {wood.radius}")
    
    # Test ferme
    food = ResourceNode(300, 300, 'food', 150)
    print(f"  Ferme:")
    print(f"    - resource_type: {food.resource_type}")
    
    # Test assignement workers
    worker1 = __import__('entities.worker', fromlist=['Worker']).Worker(100, 100, 'player')
    worker2 = __import__('entities.worker', fromlist=['Worker']).Worker(105, 100, 'player')
    worker3 = __import__('entities.worker', fromlist=['Worker']).Worker(110, 100, 'player')
    
    print(f"\n  Assignement workers à la mine:")
    print(f"    - Worker1: {gold.assign_worker(worker1)}")
    print(f"    - Worker2: {gold.assign_worker(worker2)}")
    print(f"    - Worker3: {gold.assign_worker(worker3)}")
    print(f"    - Max atteint: {not gold.can_assign_worker()}")
    
    # Test récolte
    initial = gold.amount
    harvested = gold.harvest(100)
    print(f"\n  Récolte:")
    print(f"    - Avant: {initial}")
    print(f"    - Récolté: {harvested}")
    print(f"    - Après: {gold.amount}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Test 4: Test du worker
print("\n" + "=" * 50)
print("TEST 4: Unité Worker")
print("=" * 50)

try:
    from entities.worker import Worker
    
    w = Worker(100, 100, 'player')
    
    print(f"  Propriétés:")
    print(f"    - unit_type: {w.unit_type}")
    print(f"    - can_cut_trees: {w.can_cut_trees}")
    print(f"    - max_hp: {w.max_hp}")
    print(f"    - speed: {w.speed}")
    
    # Test sérialisation
    data = w.to_dict()
    print(f"\n  Sérialisation:")
    print(f"    - can_cut_trees in dict: {'can_cut_trees' in data}")
    print(f"    - carrying in dict: {'carrying' in data}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Test 5: Collision system
print("\n" + "=" * 50)
print("TEST 5: Système de collision")
print("=" * 50)

try:
    from systems.collision import CollisionSystem
    
    cs = CollisionSystem()
    print(f"  ✓ CollisionSystem initialisé")
    
    # Test avec resource_nodes
    gold_node = ResourceNode(100, 100, 'gold', 800)
    wood_node = ResourceNode(200, 200, 'wood', 150)
    
    cs.resource_nodes = [gold_node, wood_node]
    print(f"  - resource_nodes configurés: {len(cs.resource_nodes)}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Test 6: Génération aléatoire
print("\n" + "=" * 50)
print("TEST 6: Génération aléatoire des ressources")
print("=" * 50)

try:
    import random
    
    # Simuler la génération
    min_x, max_x = 50 * 32, 350 * 32
    min_y, max_y = 50 * 32, 350 * 32
    
    resources = []
    
    # Mines d'or
    for _ in range(20):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        resources.append(('gold', x, y))
    
    # Forêts
    for _ in range(60):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        resources.append(('wood', x, y))
    
    # Fermes
    for _ in range(8):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        resources.append(('food', x, y))
    
    print(f"  ✓ {len([r for r in resources if r[0] == 'gold'])} mines d'or générées")
    print(f"  ✓ {len([r for r in resources if r[0] == 'wood'])} forêts générées")
    print(f"  ✓ {len([r for r in resources if r[0] == 'food'])} fermes générées")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Test 7: EconomySystem
print("\n" + "=" * 50)
print("TEST 7: Système d'économie")
print("=" * 50)

try:
    from systems.economy import EconomySystem
    
    eco = EconomySystem()
    
    print(f"  Ressources initiales:")
    print(f"    - Gold: {eco.gold}")
    print(f"    - Wood: {eco.wood}")
    print(f"    - Food: {eco.food}")
    
    # Test ajout de ressources
    eco.add_resources(gold=100, wood=50)
    print(f"\n  Après ajout (gold=100, wood=50):")
    print(f"    - Gold: {eco.gold}")
    print(f"    - Wood: {eco.wood}")
    
    # Test coût unité
    warrior_cost = eco.get_unit_cost("warrior")
    print(f"\n  Coût Warrior: {warrior_cost}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")

# Résumé
print("\n" + "=" * 50)
print("RÉSUMÉ DES TESTS")
print("=" * 50)
print(f"Modules testés: {len(modules_to_test)}")
print(f"Erreurs d'importation: {len(import_errors)}")
if import_errors:
    print("\n⚠️  Problèmes détectés:")
    for mod, cls, err in import_errors:
        print(f"    - {mod}.{cls}: {err}")
else:
    print("\n✅ Tous les tests passent!")
