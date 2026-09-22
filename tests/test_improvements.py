"""Tests des améliorations : animations de sprites, audio, difficulté.

- Animations : les unités ont un état d'animation (idle/walk/attack/death)
  et le SpriteAnimator génère des frames pour chaque état.
- Audio : le générateur produit des sons utilisables, la musique démarre/arrête.
- Difficulté : _apply_difficulty scale la config ennemie selon easy/normal/hard.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import pytest

from entities.unit import Unit
from systems.sprite_anim import (
    get_animator, ANIM_IDLE, ANIM_WALK, ANIM_ATTACK, ANIM_DEATH,
    FRAME_COUNTS, FRAME_FPS,
)


# ---------------------------------------------------------------------------
# Animations de sprites
# ---------------------------------------------------------------------------

def make_unit(unit_type="warrior", x=100, y=100, game=None):
    u = Unit(x, y, "player", game=game)
    u.unit_type = unit_type
    return u


def test_unit_has_animation_state():
    u = make_unit()
    assert u.anim_state == ANIM_IDLE
    assert u.anim_frame == 0
    assert u.facing in (1, -1)


def test_animator_generates_frames_for_all_states():
    animator = get_animator()
    for state in (ANIM_IDLE, ANIM_WALK, ANIM_ATTACK, ANIM_DEATH):
        frames = animator.get_frames("warrior", state)
        assert len(frames) == FRAME_COUNTS[state], f"{state}: {len(frames)} frames"
        for f in frames:
            assert f.get_width() == 32 and f.get_height() == 32


def test_animator_has_worker_and_hero_sprites():
    animator = get_animator()
    for unit_type in ("worker", "hero"):
        frames = animator.get_frames(unit_type, ANIM_WALK)
        assert len(frames) == FRAME_COUNTS[ANIM_WALK]


def test_idle_unit_stays_idle():
    u = make_unit()
    for _ in range(60):
        u.update(0.1)
    assert u.anim_state == ANIM_IDLE


def test_moving_unit_uses_walk():
    u = make_unit()
    u.is_moving = True
    u.move_target = (500, 100)  # loin : reste en marche pendant le test
    for _ in range(30):
        u.update(0.1)
    assert u.anim_state == ANIM_WALK


def test_dead_unit_uses_death():
    u = make_unit()
    u.hp = 0
    u.update(0.1)
    assert u.anim_state == ANIM_DEATH


def test_animation_frame_advances():
    u = make_unit()
    u.is_moving = True
    u.move_target = (200, 100)
    u.update(0.1)
    initial = u.anim_frame
    advanced = False
    for _ in range(50):
        u.update(1.0 / FRAME_FPS[ANIM_WALK])
        if u.anim_frame != initial:
            advanced = True
            break
    assert advanced


def test_draw_does_not_crash_with_sprite():
    screen = pygame.display.get_surface()
    u = make_unit("warrior")
    u.draw(screen, 0, 0)
    u.anim_state = ANIM_DEATH
    u.draw(screen, 0, 0)


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

def test_audio_generator_produces_sounds():
    from systems.audio import SoundGenerator, AudioManager
    gen = SoundGenerator()
    for name in ("hit", "kill", "build", "collect", "error", "victory", "defeat"):
        sound = getattr(gen, f"generate_{name}_sound")()
        assert sound is not None


def test_music_loop_generated():
    from systems.audio import SoundGenerator
    gen = SoundGenerator()
    music = gen.generate_music_loop()
    assert music is not None


def test_audio_manager_start_stop_music():
    from systems.audio import AudioManager
    am = AudioManager()
    am.start_music()
    am.stop_music()
    assert am.music_channel is None


def test_audio_events_play_hit():
    from systems.audio import AudioManager, AudioEvents
    am = AudioManager()
    events = AudioEvents(am)
    events.on_unit_hit(10)
    events.on_victory()
    events.on_defeat()


# ---------------------------------------------------------------------------
# Difficulté
# ---------------------------------------------------------------------------

def test_difficulty_scales_enemy_config():
    from core.game import Game
    from systems.campaign import create_default_campaign
    g = Game()
    g._apply_faction("human")
    g.campaign = create_default_campaign()
    g.current_mission = g.campaign.start_next_mission()
    base = dict(g.current_mission.enemy_config)

    def reset():
        g.current_mission.enemy_config = dict(base)

    # Normal : inchangé
    reset()
    g.difficulty = "normal"
    g._apply_difficulty()
    assert g.current_mission.enemy_config == base

    # Facile : moins de guerriers, or réduit, ressources joueur boostées
    reset()
    g.difficulty = "easy"
    gold_before = g.economy.gold
    g._apply_difficulty()
    cfg = g.current_mission.enemy_config
    assert cfg["warriors"] < base["warriors"]
    assert cfg["gold"] < base["gold"]
    assert g.economy.gold > gold_before

    # Difficile : plus de guerriers, or augmenté
    reset()
    g.difficulty = "hard"
    g._apply_difficulty()
    cfg = g.current_mission.enemy_config
    assert cfg["warriors"] > base["warriors"]
    assert cfg["gold"] > base["gold"]


def test_difficulty_menu_flow():
    from ui.menus import DifficultyMenu
    menu = DifficultyMenu()
    assert "easy" in menu.cards and "normal" in menu.cards and "hard" in menu.cards
    # Le clic sur la carte "easy" retourne "easy"
    pos = menu.cards["easy"].center
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
    assert menu.handle_event(event) == "easy"