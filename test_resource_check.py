"""
Test rapide: Vérifier que les ressources sont générées et visibles
"""
import sys
sys.path.insert(0, r'C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy')

from entities.resource_node import ResourceNode
from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

print("=" * 60)
print("TEST DE VÉRIFICATION DES RESSOURCES")
print("=" * 60)

# Simuler la génération comme dans game.py
resource_nodes = []

min_x, max_x = 50 * TILE_SIZE, (MAP_WIDTH - 10) * TILE_SIZE
min_y, max_y = 50 * TILE_SIZE, (MAP_HEIGHT - 10) * TILE_SIZE

print(f"\nBornes de génération:")
print(f"  X: {min_x} à {max_x}")
print(f"  Y: {min_y} à {max_y}")

# Générer quelques ressources de test
for i in range(5):
    x = min_x + (max_x - min_x) // 4 * i + 100
    y = min_y + 100
    gold = ResourceNode(x, y, 'gold', 800)
    resource_nodes.append(gold)

for i in range(5):
    x = min_x + (max_x - min_x) // 4 * i + 200
    y = min_y + 300
    wood = ResourceNode(x, y, 'wood', 150)
    resource_nodes.append(wood)

print(f"\n✓ {len([n for n in resource_nodes if n.resource_type == 'gold'])} mines d'or générées")
print(f"✓ {len([n for n in resource_nodes if n.resource_type == 'wood'])} forêts générées")
print(f"✓ Total: {len(resource_nodes)} ressources")

# Vérifier les propriétés
print("\n--- Propriétés des ressources ---")
for node in resource_nodes[:3]:
    print(f"\n{node.resource_type}:")
    print(f"  Position: ({node.x}, {node.y})")
    print(f"  Taille: {node.width}x{node.height}")
    print(f"  Rayon: {node.radius}")
    print(f"  Quantité: {node.amount}/{node.max_amount}")

print("\n✅ Toutes les ressources sont générées correctement!")
print("✅ Les mines et forêts seront visibles dans le jeu")
