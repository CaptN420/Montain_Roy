"""
Mountain_Roy - Sprite Animation System (Système d'Animations de Sprites)
Étape 16: Animations marche / attaque / mort pour les unités.

Génère des frames procédurales à partir des sprites 32x32 de base, sans
dépendre de fichiers externes (robuste dans les tests : pygame.init() suffit,
aucun display requis pour dessiner sur des surfaces SRCALPHA).
"""

import pygame
import math

from systems.sprite_generator import SpriteGenerator


# États d'animation d'une unité
ANIM_IDLE = "idle"
ANIM_WALK = "walk"
ANIM_ATTACK = "attack"
ANIM_DEATH = "death"

# Nombre de frames par état
FRAME_COUNTS = {
    ANIM_IDLE: 2,
    ANIM_WALK: 4,
    ANIM_ATTACK: 3,
    ANIM_DEATH: 4,
}

# Vitesse d'animation (fps) par état
FRAME_FPS = {
    ANIM_IDLE: 3,
    ANIM_WALK: 8,
    ANIM_ATTACK: 12,
    ANIM_DEATH: 6,
}


class SpriteAnimator:
    """Génère et met en cache les frames animées de chaque type d'unité."""

    def __init__(self):
        self._generator = SpriteGenerator()
        self._base_sprites = {}
        self._frames = {}  # unit_type -> {state: [Surface, ...]}
        self._cache = {}

    def _get_base(self, unit_type: str) -> pygame.Surface:
        """Récupère (et met en cache) le sprite de base 32x32 de l'unité."""
        if unit_type not in self._base_sprites:
            gen = getattr(self._generator, f"generate_{unit_type}", None)
            if gen is not None:
                try:
                    self._base_sprites[unit_type] = gen(32)
                except Exception:
                    self._base_sprites[unit_type] = self._placeholder(unit_type)
            else:
                self._base_sprites[unit_type] = self._placeholder(unit_type)
        return self._base_sprites[unit_type]

    @staticmethod
    def _placeholder(unit_type: str) -> pygame.Surface:
        """Sprite de substitution si aucun générateur n'existe pour ce type."""
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surface, (120, 120, 200), (8, 8, 16, 16))
        return surface

    def _blit_shifted(self, base: pygame.Surface, dx: int, dy: int) -> pygame.Surface:
        """Crée une frame en décalant le sprite de base."""
        frame = pygame.Surface((32, 32), pygame.SRCALPHA)
        frame.blit(base, (dx, dy))
        return frame

    def _rotate(self, base: pygame.Surface, angle: float) -> pygame.Surface:
        """Crée une frame en pivotant le sprite (centré)."""
        frame = pygame.transform.rotozoom(base, angle, 1.0)
        # Re-centrer dans une 32x32
        out = pygame.Surface((32, 32), pygame.SRCALPHA)
        out.blit(frame, ((32 - frame.get_width()) // 2, (32 - frame.get_height()) // 2))
        return out

    def _generate_state_frames(self, unit_type: str, state: str):
        """Génère les frames d'un état pour un type d'unité."""
        base = self._get_base(unit_type)
        count = FRAME_COUNTS[state]
        frames = []
        if state == ANIM_IDLE:
            # Léger "respiration" : 2 frames avec un petit décalage vertical
            for i in range(count):
                dy = 0 if i % 2 == 0 else -1
                frames.append(self._blit_shifted(base, 0, dy))
        elif state == ANIM_WALK:
            # Bounce vertical + oscillation horizontale → illusion de marche
            for i in range(count):
                dy = -2 if i % 2 == 0 else 0
                dx = 1 if i == 1 else (-1 if i == 3 else 0)
                frames.append(self._blit_shifted(base, dx, dy))
        elif state == ANIM_ATTACK:
            # Pivotement progressif : arme levée → frappe
            for i in range(count):
                angle = -12 + i * 12  # -12°, 0°, +12°
                frames.append(self._rotate(base, angle))
        elif state == ANIM_DEATH:
            # Chute : passe de debout à couché (rotation 90°) avec fondu
            for i in range(count):
                angle = 0 + i * 30  # 0°, 30°, 60°, 90°
                frame = self._rotate(base, angle)
                # Fondu progressif (alpha)
                alpha = int(255 * (1 - i / count))
                frame.set_alpha(alpha)
                frames.append(frame)
        return frames

    def get_frames(self, unit_type: str, state: str) -> list:
        """Retourne les frames d'un état (générées et mises en cache)."""
        key = (unit_type, state)
        if key not in self._frames:
            self._frames[key] = self._generate_state_frames(unit_type, state)
        return self._frames[key]

    def draw(self, screen, unit_type: str, state: str, frame: int,
             screen_x: int, screen_y: int, flip_x: bool = False,
             radius: int = 16):
        """Dessine la frame demandée centrée sur (screen_x, screen_y)."""
        frames = self.get_frames(unit_type, state)
        frame = frame % len(frames)
        sprite = frames[frame]
        if flip_x:
            sprite = pygame.transform.flip(sprite, True, False)
        # Échelle pour tenir compte du rayon (les unités ont des rayons variés)
        scale = max(1.0, radius / 16.0)
        if scale != 1.0:
            w, h = int(32 * scale), int(32 * scale)
            sprite = pygame.transform.scale(sprite, (w, h))
        screen.blit(sprite, (int(screen_x - sprite.get_width() // 2),
                             int(screen_y - sprite.get_height() // 2)))


# Singleton partagé (évite de régénérer les frames à chaque unité)
_ANIMATOR = None


def get_animator() -> SpriteAnimator:
    """Retourne l'animateur singleton partagé."""
    global _ANIMATOR
    if _ANIMATOR is None:
        _ANIMATOR = SpriteAnimator()
    return _ANIMATOR