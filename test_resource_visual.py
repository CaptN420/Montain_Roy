"""
Test visuel des ressources - Style Warcraft/Civilization
"""
import pygame
import sys
import math

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Resource Visual Test - Warcraft/Civ Style")
clock = pygame.time.Clock()

# Import la classe ResourceNode
from entities.resource_node import ResourceNode

# Créer des ressources de test
gold_mine = ResourceNode(400, 300, 'gold', 800)
forest = ResourceNode(200, 200, 'wood', 150)
farm = ResourceNode(600, 200, 'food', 150)

# Assign some workers to the mine
worker1 = type('Worker', (), {'x': 400, 'y': 300})()
worker2 = type('Worker', (), {'x': 410, 'y': 310})()
gold_mine.assign_worker(worker1)
gold_mine.assign_worker(worker2)

# Réduire un peu la forêt pour montrer la barre
forest.harvest(50)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Réinitialiser les quantités
                gold_mine.amount = 800
                forest.amount = 150
                farm.amount = 150
            elif event.key == pygame.K_h:
                # Récolter un peu
                gold_mine.harvest(100)
                forest.harvest(30)

    # Fond herbeux
    screen.fill((34, 139, 34))

    # Dessiner les ressources
    forest.draw(screen, 0, 0)
    farm.draw(screen, 0, 0)
    gold_mine.draw(screen, 0, 0)

    # Titre
    font = pygame.font.Font(None, 36)
    title = font.render("Resource Visual Test (Warcraft/Civ Style)", True, (255, 255, 255))
    screen.blit(title, (10, 10))

    # Instructions
    info_font = pygame.font.Font(None, 24)
    info1 = info_font.render("R = Reset quantities", True, (200, 200, 200))
    info2 = info_font.render("H = Harvest some resources", True, (200, 200, 200))
    screen.blit(info1, (10, 50))
    screen.blit(info2, (10, 80))

    # Stats
    stats = f"Gold: {gold_mine.amount}/{gold_mine.max_amount} | Wood: {forest.amount}/{forest.max_amount} | Food: {farm.amount}/{farm.max_amount}"
    stats_text = info_font.render(stats, True, (255, 255, 150))
    screen.blit(stats_text, (10, 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
