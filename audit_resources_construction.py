"""
AUDIT COMPLET: Système de Ressources et Construction
Mountain_Roy RTS - Audit des problèmes critiques
"""

print("=" * 70)
print("AUDIT SYSTÈME RESSOURCES & CONSTRUCTION")
print("=" * 70)

# Import necessary modules
import sys
sys.path.insert(0, r'C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy')

from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

print("\n[1] ANALYSE DE LA GÉNÉRATION ACTUELLE")
print("-" * 70)

# Current generation bounds (from game.py)
min_x = 50 * TILE_SIZE
max_x = (MAP_WIDTH - 10) * TILE_SIZE
min_y = 50 * TILE_SIZE
max_y = (MAP_HEIGHT - 10) * TILE_SIZE

print(f"Bornes actuelles:")
print(f"  X: {min_x} - {max_x} pixels ({min_x//TILE_SIZE} - {max_x//TILE_SIZE} tuiles)")
print(f"  Y: {min_y} - {max_y} pixels ({min_y//TILE_SIZE} - {max_y//TILE_SIZE} tuiles)")

# Player base position
player_base_x = 32 * TILE_SIZE  # x = 1024
player_base_y = 64 * TILE_SIZE  # y = 2048

print(f"\nPosition base joueur: ({player_base_x}, {player_base_y})")
print(f"Distance aux bornes:")
print(f"  Gauche: {player_base_x - min_x} pixels")
print(f"  Droite: {max_x - player_base_x} pixels")
print(f"  Haut: {player_base_y - min_y} pixels")
print(f"  Bas: {max_y - player_base_y} pixels")

# Check if resources are near base
resource_near_base = []
for _ in range(20):
    import random
    x = random.randint(min_x, max_x)
    y = random.randint(min_y, max_y)
    dist = ((x - player_base_x)**2 + (y - player_base_y)**2)**0.5
    if dist < 500:  # Within 500 pixels
        resource_near_base.append((x, y, dist))

print(f"\n[R] Ressources dans un rayon de 500px de la base: {len(resource_near_base)}")

print("\n[2] PROBLEMES IDENTIFIES")
print("-" * 70)

problems = [
    ("CRITIQUE", "Resources generées aleatoirement, pas de cluster pres de la base"),
    ("CRITIQUE", "Pas de systeme de construction fonctionnel (build() ne fait rien)"),
    ("CRITIQUE", "UI desalignee - boutons de production mal positionnes"),
    ("MOYEN", "Pas d'assignation de workers pour construire"),
    ("MOYEN", "Pas de barre de progression de construction"),
]

for severity, problem in problems:
    print(f"  [{severity}] {problem}")

print("\n[3] SOLUTIONS PROPOSEES")
print("-" * 70)

solutions = [
    ("1. Generer resources pres de la base", """
        - Cluster de 8-10 mines d'or dans un rayon de 200px de la base
        - Cluster de 15-20 forets dans un rayon de 300px
        - Fermes dispersees mais proches (rayon 400px)
        - Ressources secondaires plus loin pour exploration
    """),
    ("2. Systeme de construction", """
        - UI avec boutons de selection de batiment
        - Click sur la carte pour placer (avec preview)
        - Worker assigne automatiquement pour construire
        - Barre de progression visuelle
        - Coûts: Or + Bois + Nourriture
    """),
    ("3. UI alignee", """
        - Panneau de selection en bas a gauche
        - Boutons de production alignes horizontalement
        - Minimap en bas a droite
        - Barre de ressources en haut
    """),
]

for title, solution in solutions:
    print(f"\n{title}")
    print(solution)

print("\n[4] STRUCTURE DES COUTS DE CONSTRUCTION")
print("-" * 70)

building_costs = {
    "farm": {"gold": 50, "wood": 100, "food": 0, "time": 5.0},
    "barracks": {"gold": 200, "wood": 150, "food": 50, "time": 10.0},
    "lumber_mill": {"gold": 100, "wood": 50, "food": 0, "time": 8.0},
    "tower": {"gold": 150, "wood": 100, "food": 0, "time": 7.0},
}

print("Couts de construction:")
for btype, cost in building_costs.items():
    print(f"  {btype}: {cost['gold']} or, {cost['wood']} bois, {cost['food']} nourriture ({cost['time']}s)")

print("\n[5] PLAN D'ACTION")
print("-" * 70)
print("Etape 1: Modifier _generate_resource_nodes() pour clusteriser pres de la base")
print("Etape 2: Implémenter build() dans ConstructionSystem avec workers")
print("Etape 3: Realign l'UI dans HUD (draw_production_buttons)")
print("Etape 4: Ajouter preview de placement et barre de progression")
print("Etape 5: Tester le flux complet: selectionner -> placer -> construire")

print("\n" + "=" * 70)
print("AUDIT TERMINE - 3 problemes critiques identifies")
print("=" * 70)
