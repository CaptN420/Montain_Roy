"""
Mountain_Roy - Sound System (Système de Sons)
Étape 12: Sons et effets visuels
"""

import pygame
import random


class SoundManager:
    """Gère la lecture des sons."""
    
    def __init__(self):
        self.sounds = {}
        self.music = None
        self.volume = 0.5
    
    def load_sound(self, name: str, path: str):
        """Charge un son."""
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except:
            # Son de substitution si le fichier n'existe pas
            self.sounds[name] = None
    
    def play_sound(self, name: str, volume: float = None):
        """Joue un son."""
        if name in self.sounds and self.sounds[name]:
            if volume is None:
                volume = self.volume
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()
    
    def play_random(self, name_prefix: str, min_vol: float = 0.3, max_vol: float = 0.7):
        """Joue un son aléatoire avec un préfixe."""
        matching = [k for k in self.sounds.keys() if k.startswith(name_prefix)]
        if matching:
            sound_name = random.choice(matching)
            vol = random.uniform(min_vol, max_vol)
            self.play_sound(sound_name, vol)
    
    def play_music(self, path: str, loops: int = -1):
        """Joue de la musique."""
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops)
        except:
            pass
    
    def stop_music(self):
        """Arrête la musique."""
        pygame.mixer.music.stop()
    
    def set_volume(self, volume: float):
        """Définit le volume."""
        self.volume = max(0, min(1, volume))


class VisualEffects:
    """Gère les effets visuels avancés."""
    
    def __init__(self):
        self.particles = []
        self.screen_shake = 0
        self.flash_alpha = 0
    
    def add_particle(self, x: int, y: int, color: tuple, life: float = 1.0,
                     vx: float = 0, vy: float = 0, size: int = 3):
        """Ajoute une particule."""
        self.particles.append({
            'x': x, 'y': y, 'color': color, 'life': life,
            'max_life': life, 'vx': vx, 'vy': vy, 'size': size,
        })
    
    def add_explosion(self, x: int, y: int, num_particles: int = 15, 
                      color: tuple = (255, 100, 0)):
        """Crée une explosion."""
        for _ in range(num_particles):
            angle = random.random() * 2 * math.pi
            speed = 50 + random.random() * 100
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.add_particle(x, y, color, 0.5 + random.random() * 0.5, vx, vy, 4)
    
    def add_damage_number(self, x: int, y: int, damage: int):
        """Ajoute un nombre de dégâts."""
        self.particles.append({
            'x': x, 'y': y, 'color': (255, 0, 0), 'life': 1.0,
            'max_life': 1.0, 'vx': 0, 'vy': -50, 'size': 0,
            'text': str(damage), 'is_text': True,
        })
    
    def screen_shake(self, intensity: float = 5.0):
        """Ajoute un effet de secousse."""
        self.screen_shake = intensity
    
    def flash_screen(self, color: tuple = (255, 255, 255), alpha: int = 50):
        """Ajoute un flash écran."""
        self.flash_alpha = alpha
        self.flash_color = color
    
    def update(self, dt: float):
        """Met à jour les effets."""
        # Mettre à jour les particules
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # Décrémenter la secousse
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
            if self.screen_shake < 0.1:
                self.screen_shake = 0
        
        # Décrémenter le flash
        if self.flash_alpha > 0:
            self.flash_alpha *= 0.9
            if self.flash_alpha < 1:
                self.flash_alpha = 0
    
    def draw(self, screen):
        """Dessine les effets."""
        # Dessiner les particules
        for p in self.particles:
            if 'is_text' in p and p['is_text']:
                # Texte flottant
                font = pygame.font.Font(None, 20)
                alpha = int(255 * (p['life'] / p['max_life']))
                rendered = font.render(p['text'], True, p['color'])
                screen.blit(rendered, (int(p['x']), int(p['y'])))
            else:
                # Particule normale
                size = max(1, int(p['size'] * (p['life'] / p['max_life'])))
                pygame.draw.circle(screen, p['color'], 
                                 (int(p['x']), int(p['y'])), size)
        
        # Dessiner le flash
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            flash_surface.fill(self.flash_color + (int(self.flash_alpha),))
            screen.blit(flash_surface, (0, 0))


# Import math pour les calculs
import math
