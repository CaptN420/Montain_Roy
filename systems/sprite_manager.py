"""
Mountain_Roy - Sprite Manager (Gestionnaire de Sprites)
Étape 14: Gestion et rendu des sprites
"""

import pygame
import os


class SpriteManager:
    """Gère le chargement et le rendu des sprites."""
    
    def __init__(self, sprite_dir: str = "assets/sprites"):
        self.sprite_dir = sprite_dir
        self.sprites = {}
        self._load_sprites()
    
    def _load_sprites(self):
        """Charge tous les sprites depuis le dossier."""
        if not os.path.exists(self.sprite_dir):
            print(f"Sprite directory not found: {self.sprite_dir}")
            return
        
        for filename in os.listdir(self.sprite_dir):
            if filename.endswith('.png'):
                name = filename[:-4]
                path = os.path.join(self.sprite_dir, filename)
                try:
                    self.sprites[name] = pygame.image.load(path).convert_alpha()
                except Exception as e:
                    print(f"Error loading {path}: {e}")
    
    def get_sprite(self, name: str, default_size: int = 32) -> pygame.Surface:
        """Récupère un sprite par son nom."""
        if name in self.sprites:
            return self.sprites[name]
        
        # Retourner un rectangle de substitution si le sprite n'existe pas
        surface = pygame.Surface((default_size, default_size), pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 255), (0, 0, default_size, default_size))
        return surface
    
    def draw_sprite(self, sprite_name: str, screen, x: int, y: int, 
                    scale: float = 1.0, flip_x: bool = False):
        """Dessine un sprite."""
        sprite = self.get_sprite(sprite_name)
        
        if scale != 1.0:
            new_size = (int(sprite.get_width() * scale), 
                       int(sprite.get_height() * scale))
            sprite = pygame.transform.scale(sprite, new_size)
        
        if flip_x:
            sprite = pygame.transform.flip(sprite, True, False)
        
        screen.blit(sprite, (x - sprite.get_width() // 2, y - sprite.get_height() // 2))


class AnimationManager:
    """Gère les animations de sprites."""
    
    def __init__(self):
        self.animations = {}
        self.current_frame = 0
        self.frame_timer = 0
    
    def add_animation(self, name: str, frames: list, fps: int = 10):
        """Ajoute une animation."""
        self.animations[name] = {
            'frames': frames,
            'fps': fps,
            'current_frame': 0,
            'timer': 0,
        }
    
    def update(self, dt: float) -> int:
        """Met à jour l'animation et retourne l'index du frame actuel."""
        for anim in self.animations.values():
            anim['timer'] += dt
            if anim['timer'] >= 1 / anim['fps']:
                anim['timer'] = 0
                anim['current_frame'] = (anim['current_frame'] + 1) % len(anim['frames'])
        
        return self.animations.get('default', {'current_frame': 0})['current_frame']
    
    def get_frame(self, animation_name: str, default_frame: int = 0) -> int:
        """Récupère l'index du frame actuel."""
        if animation_name in self.animations:
            return self.animations[animation_name]['current_frame']
        return default_frame


class SpriteRenderer:
    """Optimise le rendu des sprites."""
    
    def __init__(self, sprite_manager: SpriteManager):
        self.sprite_manager = sprite_manager
        self._cache = {}
    
    def draw_unit(self, screen, x: int, y: int, unit_type: str, 
                  faction: str = "player", selected: bool = False):
        """Dessine une unité avec son sprite."""
        # Déterminer le nom du sprite
        sprite_name = f"{unit_type}_{faction}"
        
        # Dessiner le sprite
        self.sprite_manager.draw_sprite(sprite_name, screen, x, y)
        
        # Indicateur de sélection
        if selected:
            pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 20)
    
    def draw_building(self, screen, x: int, y: int, building_type: str, 
                      faction: str = "player"):
        """Dessine un bâtiment."""
        sprite_name = f"{building_type}_{faction}"
        self.sprite_manager.draw_sprite(sprite_name, screen, x, y, scale=1.5)


# Générateur de sprites par défaut (fallback)
def create_default_sprites():
    """Crée des sprites par défaut si aucun fichier n'existe."""
    from systems.sprite_generator import SpriteGenerator
    
    generator = SpriteGenerator()
    sprites = generator.generate_all_sprites()
    
    output_dir = "assets/sprites"
    os.makedirs(output_dir, exist_ok=True)
    
    for name, surface in sprites.items():
        pygame.image.save(surface, f"{output_dir}/{name}.png")
    
    return sprites
