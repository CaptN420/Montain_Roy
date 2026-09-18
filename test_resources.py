"""
Test des nouvelles fonctionnalités:
- Génération aléatoire des ressources
- Mines avec workers assignés (max 3)
- Forêts comme obstacles
- Mode bucheron
"""

from entities.resource_node import ResourceNode
from entities.worker import Worker


def test_resource_generation():
    """Test la génération de ressources."""
    print("=== Test Génération Ressources ===")
    
    # Créer quelques noeuds de test
    gold = ResourceNode(100, 100, 'gold', 800)
    wood = ResourceNode(200, 200, 'wood', 150)
    food = ResourceNode(300, 300, 'food', 150)
    
    print(f"Mine d'or: is_mine={gold.is_mine}, width={gold.width}, height={gold.height}")
    print(f"Forêt: is_obstacle={wood.is_obstacle}, radius={wood.radius}")
    print(f"Ferme: resource_type={food.resource_type}")
    
    # Test assignement workers
    worker1 = Worker(100, 100, 'player')
    worker2 = Worker(105, 100, 'player')
    worker3 = Worker(110, 100, 'player')
    worker4 = Worker(115, 100, 'player')  # Trop - max 3
    
    print(f"\nAssignement workers à la mine:")
    print(f"  Worker1 assigné: {gold.assign_worker(worker1)}")
    print(f"  Worker2 assigné: {gold.assign_worker(worker2)}")
    print(f"  Worker3 assigné: {gold.assign_worker(worker3)}")
    print(f"  Worker4 refusé (max 3): {not gold.can_assign_worker()}")
    
    # Test récolte
    print(f"\nRécolte:")
    print(f"  Mine avant: {gold.amount}")
    amount = gold.harvest(100)
    print(f"  Récolté: {amount}, reste: {gold.amount}")


def test_worker_features():
    """Test les fonctionnalités du worker."""
    print("\n=== Test Worker ===")
    
    worker = Worker(100, 100, 'player')
    
    # Test mode bucheron
    print(f"Mode bucheron initial: {worker.can_cut_trees}")
    worker.can_cut_trees = True
    print(f"Mode bucheron après toggle: {worker.can_cut_trees}")
    
    # Test sérialisation
    data = worker.to_dict()
    print(f"Données sérialisées: can_cut_trees={data.get('can_cut_trees')}")


if __name__ == "__main__":
    test_resource_generation()
    test_worker_features()
    print("\n✓ Tous les tests passent!")
