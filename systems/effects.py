"""
Mountain_Roy - Optimizations & Polish
Étape 11: Optimisation et finition
"""

import pygame
import math
import random


class ParticleSystem:
    """Système de particules pour les effets visuels."""
    
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x: int, y: int, color: tuple, life: float = 1.0, 
                     vx: float = 0, vy: float = 0, size: int = 3):
        """Ajoute une particule."""
        self.particles.append({
            'x': x,
            'y': y,
            'color': color,
            'life': life,
            'max_life': life,
            'vx': vx,
            'vy': vy,
            'size': size,
        })
    
    def update(self, dt: float):
        """Met à jour les particules."""
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, screen):
        """Dessine les particules."""
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            size = max(1, int(p['size'] * (p['life'] / p['max_life'])))
            
            # Dessiner avec une transparence simulée
            color = p['color']
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), size)


class EffectManager:
    """Gère les effets visuels."""
    
    def __init__(self):
        self.particles = ParticleSystem()
        self.floating_texts = []
    
    def add_damage_number(self, x: int, y: int, damage: int, color: tuple = (255, 0, 0)):
        """Ajoute un nombre de dégâts flottant."""
        self.floating_texts.append({
            'x': x,
            'y': y,
            'text': str(damage),
            'color': color,
            'life': 1.0,
            'vy': -30,
        })
    
    def add_heal_number(self, x: int, y: int, heal: int):
        """Ajoute un nombre de soin flottant."""
        self.floating_texts.append({
            'x': x,
            'y': y,
            'text': f"+{heal}",
            'color': (0, 255, 0),
            'life': 1.0,
            'vy': -30,
        })
    
    def add_explosion(self, x: int, y: int, color: tuple = (255, 100, 0)):
        """Crée une explosion de particules améliorée."""
        # Explosion principale
        for _ in range(20):
            angle = random.random() * 2 * math.pi
            speed = 60 + random.random() * 120
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.add_particle(x, y, color, 0.6 + random.random() * 0.4, vx, vy, 5)
        # Étincelles
        for _ in range(10):
            angle = random.random() * 2 * math.pi
            speed = 100 + random.random() * 80
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            self.particles.add_particle(x, y, (255, 255, 200), 0.3 + random.random() * 0.2, vx, vy, 2)
    
    def add_spell_effect(self, x: int, y: int, spell_type: str):
        """Ajoute un effet de sort amélioré."""
        if spell_type == "meteor":
            # Météore - particules descendantes + impact
            for _ in range(25):
                vx = (random.random() - 0.5) * 150
                vy = -80 - random.random() * 120
                self.particles.add_particle(x + (random.random() - 0.5) * 60,
                                           y - 120, (255, 150, 0), 1.2, vx, vy, 7)
            # Impact au sol
            for _ in range(15):
                angle = random.random() * 2 * math.pi
                speed = 80 + random.random() * 60
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                self.particles.add_particle(x, y, (255, 100, 0), 0.8, vx, vy, 6)
        elif spell_type == "shield":
            # Bouclier - cercle autour de l'unité
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                px = x + math.cos(rad) * 40
                py = y + math.sin(rad) * 40
                self.particles.add_particle(px, py, (100, 150, 255), 1.0, 0, 0, 4)
        elif spell_type == "war_cry":
            # Cri de guerre - ondes multiples
            for ring in range(4):
                radius = 30 + ring * 25
                for angle in range(0, 360, 15):
                    rad = math.radians(angle)
                    px = x + math.cos(rad) * radius
                    py = y + math.sin(rad) * radius
                    self.particles.add_particle(px, py, (255, 215, 0), 0.6 + ring * 0.15,
                                               math.cos(rad) * 60, math.sin(rad) * 60, 5)
    
    def update(self, dt: float):
        """Met à jour les effets."""
        self.particles.update(dt)
        
        # Mettre à jour les textes flottants
        for ft in self.floating_texts[:]:
            ft['y'] += ft['vy'] * dt
            ft['life'] -= dt
            
            if ft['life'] <= 0:
                self.floating_texts.remove(ft)
    
    def draw(self, screen):
        """Dessine les effets."""
        self.particles.draw(screen)
        
        # Dessiner les textes flottants
        font = pygame.font.Font(None, 20)
        for ft in self.floating_texts:
            alpha = int(255 * ft['life'])
            rendered = font.render(ft['text'], True, ft['color'])
            screen.blit(rendered, (int(ft['x']), int(ft['y'])))


class PerformanceMonitor:
    """Surveille les performances."""
    
    def __init__(self):
        self.fps = 0
        self.frame_time = 0
        self.unit_count = 0
        self.building_count = 0
    
    def update(self, dt: float, unit_count: int, building_count: int):
        """Met à jour les stats."""
        self.fps = 1 / dt if dt > 0 else 0
        self.frame_time = dt * 1000  # en ms
        self.unit_count = unit_count
        self.building_count = building_count
    
    def draw(self, screen):
        """Dessine les stats de performance."""
        font = pygame.font.Font(None, 18)
        
        stats = [
            f"FPS: {self.fps:.1f}",
            f"Frame: {self.frame_time:.2f}ms",
            f"Unités: {self.unit_count}",
            f"Bâtiments: {self.building_count}",
        ]
        
        for i, stat in enumerate(stats):
            rendered = font.render(stat, True, (0, 255, 0))
            screen.blit(rendered, (10, 50 + i * 20))


# Utilitaires d'optimisation
class QuadTree:
    """Arbre quadtree pour la détection de collisions."""
    
    def __init__(self, bounds, capacity):
        self.bounds = bounds
        self.capacity = capacity
        self.objects = []
        self.divided = False
        self.children = None
    
    def subdivide(self):
        """Crée les enfants."""
        x, y, w, h = self.bounds
        half_w, half_h = w // 2, h // 2
        
        self.children = [
            QuadTree((x, y, half_w, half_h), self.capacity),
            QuadTree((x + half_w, y, half_w, half_h), self.capacity),
            QuadTree((x, y + half_h, half_w, half_h), self.capacity),
            QuadTree((x + half_w, y + half_h, half_w, half_h), self.capacity),
        ]
        self.divided = True
    
    def insert(self, obj):
        """Insère un objet."""
        if not self._intersects(obj):
            return False
        
        if len(self.objects) >= self.capacity and not self.divided:
            self.subdivide()
        
        if self.divided:
            for child in self.children:
                if child.insert(obj):
                    return True
        else:
            self.objects.append(obj)
        
        return True
    
    def _intersects(self, obj) -> bool:
        """Vérifie l'intersection."""
        x, y, w, h = self.bounds
        return (obj.x > x and obj.x < x + w and 
                obj.y > y and obj.y < y + h)


class CacheManager:
    """Gère le cache de surfaces."""
    
    def __init__(self):
        self._cache = {}
    
    def get_surface(self, key: str, width: int, height: int, color: tuple, 
                    radius: int = 0) -> pygame.Surface:
        """Récupère ou crée une surface."""
        cache_key = f"{key}_{width}_{height}_{color}_{radius}"
        
        if cache_key not in self._cache:
            if radius > 0:
                surface = pygame.Surface((width * 2 + 1, height * 2 + 1), pygame.SRCALPHA)
                center = (width, height)
                pygame.draw.circle(surface, color + (255,), radius, center)
            else:
                surface = pygame.Surface((width, height))
                surface.fill(color)
            
            self._cache[cache_key] = surface
        
        return self._cache[cache_key]
    
    def clear(self):
        """Vide le cache."""
        self._cache.clear()


# Alias pour compatibilité
VisualEffects = EffectManager
AudioEvents = None  # Placeholder - will be defined in audio module if needed
