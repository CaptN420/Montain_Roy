"""
Mountain_Roy - Sprite Generator (Générateur de Sprites Pixel Art)
Étape 14: Sprites 16-bit (32x32 et 96x128)
"""

import pygame
import math


class SpriteGenerator:
    """Génère des sprites pixel art 16-bit."""
    
    def __init__(self):
        self.sprites = {}
    
    def generate_warrior(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite du guerrier."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Palette de couleurs
        skin = (210, 180, 140)      # Beige
        armor = (100, 100, 120)      # Gris armure
        armor_dark = (70, 70, 90)    # Gris foncé
        sword = (180, 180, 200)      # Argent
        sword_handle = (139, 69, 19) # Marron
        eye = (50, 50, 50)           # Noir
        
        # Corps (centre)
        cx, cy = size // 2, size // 2
        
        # Tête
        pygame.draw.rect(surface, skin, (cx - 6, cy - 12, 12, 10))
        # Casque
        pygame.draw.rect(surface, armor, (cx - 7, cy - 14, 14, 6))
        pygame.draw.rect(surface, armor_dark, (cx - 5, cy - 14, 10, 2))
        
        # Yeux
        pygame.draw.rect(surface, eye, (cx - 4, cy - 8, 2, 2))
        pygame.draw.rect(surface, eye, (cx + 2, cy - 8, 2, 2))
        
        # Corps
        pygame.draw.rect(surface, armor, (cx - 8, cy - 2, 16, 14))
        pygame.draw.rect(surface, armor_dark, (cx - 8, cy - 2, 16, 3))
        
        # Ceinture
        pygame.draw.rect(surface, sword_handle, (cx - 8, cy + 8, 16, 2))
        
        # Jambes
        pygame.draw.rect(surface, skin, (cx - 6, cy + 10, 5, 8))
        pygame.draw.rect(surface, skin, (cx + 1, cy + 10, 5, 8))
        
        # Bras
        pygame.draw.rect(surface, armor, (cx - 12, cy, 4, 10))
        pygame.draw.rect(surface, armor, (cx + 8, cy, 4, 10))
        
        # Épée
        pygame.draw.rect(surface, sword, (cx + 10, cy - 4, 3, 16))
        pygame.draw.rect(surface, sword_handle, (cx + 9, cy + 10, 5, 3))
        
        return surface
    
    def generate_archer(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite de l'archer."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        skin = (210, 180, 140)
        cloth = (60, 120, 60)       # Vert forêt
        cloth_dark = (40, 80, 40)
        bow = (139, 69, 19)         # Marron
        arrow = (160, 160, 160)     # Gris
        
        cx, cy = size // 2, size // 2
        
        # Tête
        pygame.draw.rect(surface, skin, (cx - 6, cy - 12, 12, 10))
        # Capuche
        pygame.draw.rect(surface, cloth, (cx - 7, cy - 14, 14, 6))
        pygame.draw.rect(surface, cloth_dark, (cx - 5, cy - 14, 10, 2))
        
        # Yeux
        pygame.draw.rect(surface, (50, 50, 50), (cx - 4, cy - 8, 2, 2))
        pygame.draw.rect(surface, (50, 50, 50), (cx + 2, cy - 8, 2, 2))
        
        # Corps
        pygame.draw.rect(surface, cloth, (cx - 8, cy - 2, 16, 14))
        pygame.draw.rect(surface, cloth_dark, (cx - 8, cy - 2, 16, 3))
        
        # Ceinture
        pygame.draw.rect(surface, bow, (cx - 8, cy + 8, 16, 2))
        
        # Flèches dans le sac
        for i in range(3):
            pygame.draw.rect(surface, arrow, (cx + 6 + i * 3, cy + 4, 2, 8))
        
        # Jambes
        pygame.draw.rect(surface, skin, (cx - 6, cy + 10, 5, 8))
        pygame.draw.rect(surface, skin, (cx + 1, cy + 10, 5, 8))
        
        # Bras
        pygame.draw.rect(surface, cloth, (cx - 12, cy, 4, 10))
        pygame.draw.rect(surface, cloth, (cx + 8, cy, 4, 10))
        
        # Arc
        pygame.draw.arc(surface, bow, (cx + 8, cy - 8, 8, 20), -math.pi/4, math.pi/4, 2)
        
        return surface
    
    def generate_knight(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite du chevalier."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        armor_light = (150, 150, 170)
        armor_dark = (100, 100, 120)
        armor_shadow = (70, 70, 90)
        visor = (80, 80, 100)
        horse = (80, 60, 40)        # Marron cheval
        
        cx, cy = size // 2, size // 2 + 4  # Décalé pour le cheval
        
        # Cheval (corps)
        pygame.draw.ellipse(surface, horse, (cx - 14, cy - 4, 28, 16))
        # Jambes du cheval
        pygame.draw.rect(surface, horse, (cx - 12, cy + 8, 5, 8))
        pygame.draw.rect(surface, horse, (cx - 3, cy + 8, 5, 8))
        pygame.draw.rect(surface, horse, (cx + 6, cy + 8, 5, 8))
        # Sabots
        pygame.draw.rect(surface, (40, 30, 20), (cx - 12, cy + 14, 5, 2))
        pygame.draw.rect(surface, (40, 30, 20), (cx - 3, cy + 14, 5, 2))
        pygame.draw.rect(surface, (40, 30, 20), (cx + 6, cy + 14, 5, 2))
        
        # Cavalier (corps)
        pygame.draw.rect(surface, armor_light, (cx - 8, cy - 16, 16, 14))
        pygame.draw.rect(surface, armor_dark, (cx - 8, cy - 16, 16, 3))
        
        # Casque
        pygame.draw.rect(surface, armor_light, (cx - 7, cy - 24, 14, 10))
        pygame.draw.rect(surface, visor, (cx - 5, cy - 20, 10, 4))
        
        # Bouclier
        pygame.draw.ellipse(surface, armor_dark, (cx - 14, cy - 8, 8, 12))
        pygame.draw.rect(surface, (200, 200, 50), (cx - 13, cy - 6, 6, 2))  # Croix
        
        return surface
    
    def generate_mage(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite du mage."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        robe = (60, 40, 120)         # Violet
        robe_dark = (40, 25, 80)
        skin = (210, 180, 140)
        staff = (139, 69, 19)
        gem = (100, 100, 255)       # Bleu magique
        
        cx, cy = size // 2, size // 2
        
        # Tête
        pygame.draw.rect(surface, skin, (cx - 6, cy - 12, 12, 10))
        # Chapeau pointu
        pygame.draw.polygon(surface, robe, [(cx, cy - 24), (cx - 10, cy - 12), (cx + 10, cy - 12)])
        pygame.draw.polygon(surface, robe_dark, [(cx, cy - 20), (cx - 6, cy - 12), (cx + 6, cy - 12)])
        
        # Yeux
        pygame.draw.rect(surface, (50, 50, 50), (cx - 4, cy - 8, 2, 2))
        pygame.draw.rect(surface, (50, 50, 50), (cx + 2, cy - 8, 2, 2))
        
        # Barbe
        pygame.draw.polygon(surface, (180, 100, 50), [(cx - 4, cy - 2), (cx + 4, cy - 2), (cx, cy + 6)])
        
        # Corps (robe)
        pygame.draw.polygon(surface, robe, [(cx - 10, cy - 2), (cx + 10, cy - 2), (cx + 14, cy + 14), (cx - 14, cy + 14)])
        pygame.draw.polygon(surface, robe_dark, [(cx - 10, cy - 2), (cx + 10, cy - 2), (cx + 8, cy + 2), (cx - 8, cy + 2)])
        
        # Ceinture
        pygame.draw.rect(surface, (200, 170, 100), (cx - 10, cy + 4, 20, 3))
        
        # Bâton magique
        pygame.draw.rect(surface, staff, (cx + 10, cy - 8, 4, 24))
        pygame.draw.circle(surface, gem, (cx + 12, cy - 8), 4)
        # Effet lumineux
        pygame.draw.circle(surface, (150, 150, 255), (cx + 12, cy - 8), 6)
        
        return surface
    
    def generate_healer(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite du soigneur."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        robe = (200, 200, 220)       # Blanc/bleu
        robe_dark = (150, 150, 170)
        skin = (210, 180, 140)
        cross = (200, 50, 50)        # Rouge croix
        
        cx, cy = size // 2, size // 2
        
        # Tête
        pygame.draw.rect(surface, skin, (cx - 6, cy - 12, 12, 10))
        # Coiffe
        pygame.draw.rect(surface, robe, (cx - 8, cy - 14, 16, 6))
        pygame.draw.rect(surface, robe_dark, (cx - 6, cy - 14, 12, 2))
        
        # Yeux
        pygame.draw.rect(surface, (50, 50, 50), (cx - 4, cy - 8, 2, 2))
        pygame.draw.rect(surface, (50, 50, 50), (cx + 2, cy - 8, 2, 2))
        
        # Corps
        pygame.draw.rect(surface, robe, (cx - 9, cy - 2, 18, 16))
        pygame.draw.rect(surface, robe_dark, (cx - 9, cy - 2, 18, 3))
        
        # Croix sur la poitrine
        pygame.draw.rect(surface, cross, (cx - 2, cy + 2, 4, 8))
        pygame.draw.rect(surface, cross, (cx - 4, cy + 4, 8, 4))
        
        # Jambes
        pygame.draw.rect(surface, robe, (cx - 6, cy + 12, 5, 8))
        pygame.draw.rect(surface, robe, (cx + 1, cy + 12, 5, 8))
        
        # Bras
        pygame.draw.rect(surface, robe, (cx - 13, cy, 4, 10))
        pygame.draw.rect(surface, robe, (cx + 9, cy, 4, 10))
        
        # Potions
        pygame.draw.circle(surface, (100, 200, 100), (cx + 13, cy + 8), 4)
        
        return surface
    
    def generate_scout(self, size: int = 32) -> pygame.Surface:
        """Génère le sprite de l'éclaireur."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cloth = (100, 80, 50)        # Marron clair
        cloth_dark = (70, 55, 35)
        skin = (210, 180, 140)
        dagger = (150, 150, 170)
        
        cx, cy = size // 2, size // 2
        
        # Tête
        pygame.draw.rect(surface, skin, (cx - 6, cy - 12, 12, 10))
        # Bandana
        pygame.draw.rect(surface, cloth, (cx - 7, cy - 14, 14, 4))
        pygame.draw.rect(surface, cloth_dark, (cx - 3, cy - 10, 6, 6))  # Nœud
        
        # Yeux
        pygame.draw.rect(surface, (50, 50, 50), (cx - 4, cy - 8, 2, 2))
        pygame.draw.rect(surface, (50, 50, 50), (cx + 2, cy - 8, 2, 2))
        
        # Corps
        pygame.draw.rect(surface, cloth, (cx - 8, cy - 2, 16, 12))
        pygame.draw.rect(surface, cloth_dark, (cx - 8, cy - 2, 16, 3))
        
        # Ceinture
        pygame.draw.rect(surface, (80, 60, 40), (cx - 8, cy + 6, 16, 2))
        
        # Jambes
        pygame.draw.rect(surface, skin, (cx - 6, cy + 10, 5, 8))
        pygame.draw.rect(surface, skin, (cx + 1, cy + 10, 5, 8))
        
        # Bras
        pygame.draw.rect(surface, cloth, (cx - 12, cy, 4, 8))
        pygame.draw.rect(surface, cloth, (cx + 8, cy, 4, 8))
        
        # Dagues
        pygame.draw.rect(surface, dagger, (cx - 14, cy + 4, 3, 10))
        pygame.draw.rect(surface, dagger, (cx + 11, cy + 4, 3, 10))
        
        return surface
    
    def generate_townhall(self, size: int = 64) -> pygame.Surface:
        """Génère le sprite de l'Hôtel de Ville."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        wall = (180, 160, 120)       # Beige mur
        wall_dark = (140, 120, 90)
        roof = (150, 50, 30)         # Toit rouge
        roof_dark = (120, 40, 25)
        door = (80, 60, 40)          # Porte marron
        window = (100, 150, 200)     # Fenêtre bleue
        
        cx, cy = size // 2, size // 2
        
        # Mur principal
        pygame.draw.rect(surface, wall, (cx - 28, cy - 16, 56, 48))
        pygame.draw.rect(surface, wall_dark, (cx - 28, cy - 16, 56, 4))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 34, cy - 16), (cx + 34, cy - 16), (cx, cy - 36)])
        pygame.draw.polygon(surface, roof_dark, [(cx - 28, cy - 16), (cx + 28, cy - 16), (cx, cy - 30)])
        
        # Porte
        pygame.draw.rect(surface, door, (cx - 8, cy + 8, 16, 20))
        pygame.draw.rect(surface, (60, 40, 25), (cx - 8, cy + 8, 16, 3))
        
        # Fenêtres
        pygame.draw.rect(surface, window, (cx - 24, cy - 8, 10, 10))
        pygame.draw.rect(surface, window, (cx + 14, cy - 8, 10, 10))
        # Cadres
        pygame.draw.rect(surface, wall_dark, (cx - 24, cy - 8, 10, 2))
        pygame.draw.rect(surface, wall_dark, (cx - 24, cy + 2, 10, 2))
        pygame.draw.rect(surface, wall_dark, (cx + 14, cy - 8, 10, 2))
        pygame.draw.rect(surface, wall_dark, (cx + 14, cy + 2, 10, 2))
        
        return surface
    
    def generate_barracks(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de la Caserne."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        wall = (160, 140, 100)
        wall_dark = (120, 100, 70)
        roof = (120, 80, 50)
        door = (70, 50, 30)
        
        cx, cy = size // 2, size // 2
        
        # Mur
        pygame.draw.rect(surface, wall, (cx - 20, cy - 12, 40, 36))
        pygame.draw.rect(surface, wall_dark, (cx - 20, cy - 12, 40, 4))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 24, cy - 12), (cx + 24, cy - 12), (cx, cy - 28)])
        
        # Porte
        pygame.draw.rect(surface, door, (cx - 6, cy + 8, 12, 16))
        
        return surface
    
    def generate_farm(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de la Ferme."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        wall = (180, 150, 100)
        roof = (180, 100, 50)
        
        cx, cy = size // 2, size // 2
        
        # Mur
        pygame.draw.rect(surface, wall, (cx - 18, cy - 10, 36, 32))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 22, cy - 10), (cx + 22, cy - 10), (cx, cy - 26)])
        
        return surface
    
    def generate_tower(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de la Tour défensive."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        stone = (120, 120, 130)
        stone_dark = (90, 90, 100)
        roof = (100, 60, 40)
        
        cx, cy = size // 2, size // 2
        
        # Tour
        pygame.draw.rect(surface, stone, (cx - 12, cy - 28, 24, 52))
        pygame.draw.rect(surface, stone_dark, (cx - 12, cy - 28, 24, 4))
        
        # Créneaux
        for i in range(3):
            pygame.draw.rect(surface, stone, (cx - 14 + i * 10, cy - 32, 6, 6))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 16, cy - 32), (cx + 16, cy - 32), (cx, cy - 44)])
        
        # Fenêtre
        pygame.draw.rect(surface, (50, 50, 80), (cx - 4, cy - 8, 8, 10))
        
        return surface
    
    def generate_mine(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de la Mine."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        stone = (100, 100, 110)
        entrance = (40, 30, 20)
        
        cx, cy = size // 2, size // 2
        
        # Montagne
        pygame.draw.polygon(surface, stone, [(cx - 24, cy + 16), (cx + 24, cy + 16), (cx, cy - 20)])
        
        # Entrée
        pygame.draw.rect(surface, entrance, (cx - 10, cy + 4, 20, 16))
        
        return surface
    
    def generate_lumber_mill(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de la Scierie."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        wood = (139, 90, 43)
        wood_dark = (100, 65, 30)
        roof = (80, 60, 40)
        
        cx, cy = size // 2, size // 2
        
        # Mur
        pygame.draw.rect(surface, wood, (cx - 20, cy - 12, 40, 36))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 24, cy - 12), (cx + 24, cy - 12), (cx, cy - 28)])
        
        return surface
    
    def generate_temple(self, size: int = 64) -> pygame.Surface:
        """Génère le sprite du Temple."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        marble = (200, 200, 220)
        marble_dark = (160, 160, 180)
        roof = (100, 50, 100)
        gold = (255, 215, 0)
        
        cx, cy = size // 2, size // 2
        
        # Mur
        pygame.draw.rect(surface, marble, (cx - 28, cy - 16, 56, 48))
        pygame.draw.rect(surface, marble_dark, (cx - 28, cy - 16, 56, 4))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 32, cy - 16), (cx + 32, cy - 16), (cx, cy - 40)])
        
        # Porte
        pygame.draw.rect(surface, (80, 60, 100), (cx - 8, cy + 8, 16, 20))
        
        # Croix dorée
        pygame.draw.rect(surface, gold, (cx - 2, cy - 36, 4, 12))
        pygame.draw.rect(surface, gold, (cx - 6, cy - 30, 12, 4))
        
        return surface
    
    def generate_workshop(self, size: int = 48) -> pygame.Surface:
        """Génère le sprite de l'Atelier."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        stone = (130, 130, 140)
        roof = (90, 70, 50)
        
        cx, cy = size // 2, size // 2
        
        # Mur
        pygame.draw.rect(surface, stone, (cx - 20, cy - 12, 40, 36))
        
        # Toit
        pygame.draw.polygon(surface, roof, [(cx - 24, cy - 12), (cx + 24, cy - 12), (cx, cy - 28)])
        
        return surface
    
    def generate_all_sprites(self):
        """Génère tous les sprites."""
        # Unités (32x32)
        self.sprites['warrior'] = self.generate_warrior(32)
        self.sprites['archer'] = self.generate_archer(32)
        self.sprites['knight'] = self.generate_knight(32)
        self.sprites['mage'] = self.generate_mage(32)
        self.sprites['healer'] = self.generate_healer(32)
        self.sprites['scout'] = self.generate_scout(32)
        
        # Bâtiments
        self.sprites['town_hall'] = self.generate_townhall(64)
        self.sprites['barracks'] = self.generate_barracks(48)
        self.sprites['farm'] = self.generate_farm(48)
        self.sprites['tower'] = self.generate_tower(48)
        self.sprites['mine'] = self.generate_mine(48)
        self.sprites['lumber_mill'] = self.generate_lumber_mill(48)
        self.sprites['temple'] = self.generate_temple(64)
        self.sprites['workshop'] = self.generate_workshop(48)
        
        return self.sprites


class SpriteSheet:
    """Génère des feuilles de sprites (96x128 pour les animations)."""
    
    def __init__(self):
        self.sheets = {}
    
    def create_unit_sheet(self, unit_type: str, frames: int = 4) -> pygame.Surface:
        """Crée une feuille de sprites pour une unité."""
        width = 96
        height = 128
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Générer le sprite de base
        generator = SpriteGenerator()
        base_sprite = getattr(generator, f'generate_{unit_type}')(32)
        
        # Placer les frames (ici statique pour l'instant)
        frame_width = 32
        frame_height = 32
        
        for row in range(frames // 2):
            for col in range(2):
                x = col * frame_width + 32
                y = row * frame_height + 48
                
                surface.blit(base_sprite, (x, y))
        
        return surface
    
    def create_all_sheets(self):
        """Crée toutes les feuilles de sprites."""
        unit_types = ['warrior', 'archer', 'knight', 'mage', 'healer', 'scout']
        
        for unit_type in unit_types:
            self.sheets[unit_type] = self.create_unit_sheet(unit_type)
        
        return self.sheets


if __name__ == "__main__":
    # Test du générateur
    generator = SpriteGenerator()
    sprites = generator.generate_all_sprites()
    
    # Sauvegarder les sprites
    output_dir = "assets/sprites"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for name, surface in sprites.items():
        pygame.image.save(surface, f"{output_dir}/{name}.png")
        print(f"Saved: {name}.png ({surface.get_width()}x{surface.get_height()})")
