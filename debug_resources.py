"""
Debug: Vérifier la génération et le rendu des ressources
"""
import pygame
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, r'C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy')

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, COLORS

def debug_resources():
    """Test la génération et l'affichage des ressources."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Debug Resources - Mountain_Roy")
    clock = pygame.time.Clock()

    # Importer les classes nécessaires
    from entities.resource_node import ResourceNode
    from core.camera import Camera

    # Générer des ressources de test
    print("\n=== TEST DE GÉNÉRATION DES RESSOURCES ===\n")

    resource_nodes = []

    # Mine d'or - position visible (centre de la carte)
    mine_x = 64 * TILE_SIZE  # x = 2048 (centre)
    mine_y = 64 * TILE_SIZE  # y = 2048 (centre)
    gold_node = ResourceNode(mine_x, mine_y, 'gold', 800)
    resource_nodes.append(gold_node)
    print(f"✓ Mine d'or créée à ({mine_x}, {mine_y})")

    # Forêt - position visible
    forest_x = 70 * TILE_SIZE  # x = 2240
    forest_y = 70 * TILE_SIZE  # y = 2240
    wood_node = ResourceNode(forest_x, forest_y, 'wood', 150)
    resource_nodes.append(wood_node)
    print(f"✓ Forêt créée à ({forest_x}, {forest_y})")

    # Ferme - position visible
    farm_x = 58 * TILE_SIZE  # x = 1856
    farm_y = 58 * TILE_SIZE  # y = 1856
    food_node = ResourceNode(farm_x, farm_y, 'food', 150)
    resource_nodes.append(food_node)
    print(f"✓ Ferme créée à ({farm_x}, {farm_y})")

    # Caméra centrée sur les ressources
    camera = Camera(MAP_WIDTH, MAP_HEIGHT)
    camera.x = 64 * TILE_SIZE - SCREEN_WIDTH // 2
    camera.y = 64 * TILE_SIZE - SCREEN_HEIGHT // 2

    print(f"\nCaméra positionnée à ({camera.x}, {camera.y})")
    print(f"Position écran des ressources:")

    for node in resource_nodes:
        screen_x = int(node.x - camera.x)
        screen_y = int(node.y - camera.y)
        print(f"  {node.resource_type}: map=({node.x}, {node.y}), screen=({screen_x}, {screen_y})")

    # Boucle de test
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Récolter la mine pour tester
                    if gold_node.amount > 0:
                        amount = gold_node.harvest(100)
                        print(f"\nRécolté {amount} or, il reste {gold_node.amount}")

        # Dessiner
        screen.fill(COLORS["grass"])

        # Dessiner les ressources
        for node in resource_nodes:
            if not node.is_depleted():
                node.draw(screen, camera.x, camera.y)

        # Dessiner une grille pour référence
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (SCREEN_WIDTH, y))
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(screen, (0, 0, 0, 30), (x, 0), (x, SCREEN_HEIGHT))

        # Titre
        font = pygame.font.Font(None, 36)
        title = font.render("Debug Resources - SPACE to harvest", True, (255, 255, 255))
        screen.blit(title, (10, 10))

        # Info
        info_font = pygame.font.Font(None, 24)
        info = f"Gold: {gold_node.amount}, Wood: {wood_node.amount}, Food: {food_node.amount}"
        info_text = info_font.render(info, True, (255, 255, 255))
        screen.blit(info_text, (10, 50))

        pygame.display.flip()
        clock.tick(60)

    print("\n=== FIN DU TEST ===")


if __name__ == "__main__":
    debug_resources()
