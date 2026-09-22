"""
Mountain_Roy - Menus (Menus du jeu)
Étape 6: Écrans de menu
"""

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuButton:
    """Bouton pour les menus."""
    
    def __init__(self, text: str, x: int, y: int, width: int = 200, height: int = 50):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen):
        """Dessine le bouton."""
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2)
        
        rendered = self.font.render(self.text, True, (255, 255, 255))
        text_rect = rendered.get_rect(center=self.rect.center)
        screen.blit(rendered, text_rect)
    
    def is_clicked(self, pos: tuple) -> bool:
        """Vérifie si le bouton a été cliqué."""
        return self.rect.collidepoint(pos)


class MainMenu:
    """Menu principal du jeu."""

    def __init__(self):
        # Center vertically: 5*50 + 4*10 = 290, start at center - 145
        self.buttons = [
            MenuButton("Nouvelle Partie", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 105),
            MenuButton("Charger une Partie", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 35),
            MenuButton("Options", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 35),
            MenuButton("Quitter", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 105),
        ]
    
    def handle_event(self, event) -> str:
        """Gère les événements du menu principal."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for button in self.buttons:
                if button.is_clicked(pos):
                    if button.text == "Nouvelle Partie":
                        return "game_mode"
                    if button.text == "Charger une Partie":
                        return "load_game"
                    if button.text == "Options":
                        return "options"
                    if button.text == "Quitter":
                        return "quit"
        return ""

    def draw(self, screen):
        """Dessine le menu principal."""
        screen.fill((30, 30, 45))
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Mountain Roy", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        for button in self.buttons:
            button.draw(screen)

class GameModeMenu:
    """Écran de sélection du mode de jeu (SANDBOX, ARCADE, STORY)."""
    
    MODES = [
        ("SANDBOX", "Mode Libre", "Pas d'IA, pas de victoire/défaite. Testez vos factions librement."),
        ("ARCADE", "Mode Arcade", "Ressources généreuses et travailleurs automatiques."),
        ("STORY", "Mode Histoire", "Suivez les missions et débloquez des objectifs."),
    ]
    
    def __init__(self):
        self._selected = "SANDBOX"
        self.cards = {}
        for i, (mode_id, label, _) in enumerate(self.MODES):
            y = SCREEN_HEIGHT // 2 - 70 + i * 60
            self.cards[mode_id] = pygame.Rect(SCREEN_WIDTH // 2 - 150, y, 300, 50)
        self.back_button = MenuButton("Retour", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70)
    
    def _mode_at(self, pos):
        for mode_id, rect in self.cards.items():
            if rect.collidepoint(pos):
                return mode_id
        return None
    
    def draw(self, screen):
        screen.fill((30, 30, 45))
        title_font = pygame.font.Font(None, 52)
        title = title_font.render("Choisissez le Mode", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(title, title_rect)
        
        for mode_id, label, desc in self.MODES:
            rect = self.cards[mode_id]
            hovered = (mode_id == self._selected)
            color = {"SANDBOX": (100, 100, 100), "ARCADE": (255, 215, 0), "STORY": (100, 200, 255)}[mode_id]
            pygame.draw.rect(screen, (45, 45, 70), rect, border_radius=8)
            pygame.draw.rect(screen, color, rect, 3 if hovered else 1, border_radius=8)
            
            name_font = pygame.font.Font(None, 28)
            name = name_font.render(label, True, color)
            screen.blit(name, (rect.x + 16, rect.y + 12))
            
            desc_font = pygame.font.Font(None, 15)
            desc_surf = desc_font.render(desc, True, (200, 200, 200))
            screen.blit(desc_surf, (rect.x + 100, rect.y + 16))
        
        self.back_button.draw(screen)
    
    def handle_event(self, event) -> str:
        if event.type == pygame.MOUSEMOTION:
            mode_id = self._mode_at(event.pos)
            if mode_id:
                self._selected = mode_id
            return ""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.back_button.is_clicked(pos):
                return "back"
            mode_id = self._mode_at(pos)
            if mode_id:
                return mode_id
        return ""


class FactionMenu:
    """Écran de sélection de la faction."""

    # Disposition des 4 cartes en grille 2x2
    CARD_W = 280
    CARD_H = 190
    CARD_GAP = 20

    def __init__(self):
        from systems.factions import get_factions
        self.factions = get_factions()
        self.faction_ids = list(self.factions.keys())
        self.back_button = MenuButton("Retour", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70)
        self._selected = "human"  # Faction par défaut (hover)
        self._compute_layout()

    def _compute_layout(self):
        """Calcule les positions des cartes en grille 2x2 centrée."""
        total_w = 2 * self.CARD_W + self.CARD_GAP
        total_h = 2 * self.CARD_H + self.CARD_GAP
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 140  # Sous le titre
        self._cards = {}
        for i, fid in enumerate(self.faction_ids):
            col = i % 2
            row = i // 2
            x = start_x + col * (self.CARD_W + self.CARD_GAP)
            y = start_y + row * (self.CARD_H + self.CARD_GAP)
            self._cards[fid] = pygame.Rect(x, y, self.CARD_W, self.CARD_H)

    def _faction_at(self, pos):
        """Retourne l'id de faction à la position (ou None)."""
        for fid, rect in self._cards.items():
            if rect.collidepoint(pos):
                return fid
        return None

    def draw(self, screen):
        """Dessine l'écran de sélection."""
        screen.fill((30, 30, 45))

        # Titre
        title_font = pygame.font.Font(None, 52)
        title = title_font.render("Choisissez votre Faction", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)

        info_font = pygame.font.Font(None, 20)
        hint = info_font.render("Cliquez sur une faction pour la sélectionner", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 95))
        screen.blit(hint, hint_rect)

        # Cartes des factions
        for fid in self.faction_ids:
            faction = self.factions[fid]
            rect = self._cards[fid]
            hovered = (fid == self._selected)

            # Carte de fond
            pygame.draw.rect(screen, (45, 45, 70), rect, border_radius=10)
            pygame.draw.rect(screen, faction.color, rect, 4, border_radius=10) if hovered else \
                pygame.draw.rect(screen, (100, 100, 120), rect, 2, border_radius=10)

            # Nom
            name_font = pygame.font.Font(None, 34)
            name = name_font.render(faction.name, True, faction.color)
            screen.blit(name, (rect.x + 10, rect.y + 8))

            # Description (multiligne)
            desc_font = pygame.font.Font(None, 16)
            words = faction.description.split(" ")
            lines = []
            current = ""
            for word in words:
                test = current + (" " if current else "") + word
                if desc_font.size(test)[0] < self.CARD_W - 20:
                    current = test
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
            for i, line in enumerate(lines[:3]):
                text_surf = desc_font.render(line, True, (220, 220, 220))
                screen.blit(text_surf, (rect.x + 10, rect.y + 48 + i * 16))

            # Spécialité
            spec_font = pygame.font.Font(None, 16)
            spec = spec_font.render(f"✦ {faction.special_ability['name']}",
                                    True, (255, 215, 0))
            screen.blit(spec, (rect.x + 10, rect.y + rect.h - 42))

            # Force / Faiblesse
            sf_font = pygame.font.Font(None, 14)
            strength = sf_font.render(f"▼ {faction.strength}", True, (140, 255, 140))
            weakness = sf_font.render(f"✖ {faction.weakness}", True, (255, 130, 130))
            screen.blit(strength, (rect.x + 10, rect.y + rect.h - 24))
            screen.blit(weakness, (rect.x + 10, rect.y + rect.h - 10))

        # Bouton retour
        self.back_button.draw(screen)
        self.back_button.text = "Retour"  # garder le texte

    def handle_event(self, event) -> str:
        """Gère les événements. Retourne l'id faction ou 'back'."""
        if event.type == pygame.MOUSEMOTION:
            fid = self._faction_at(event.pos)
            if fid:
                self._selected = fid
            return ""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.back_button.is_clicked(pos):
                return "back"
            fid = self._faction_at(pos)
            if fid:
                return fid  # Sélection → retourne l'id
        return ""


class DifficultyMenu:
    """Écran de sélection de la difficulté (facile / normal / difficile)."""

    DIFFICULTIES = [
        ("easy", "Facile", "Ennemi affaibli, ressources de départ joueur boostées."),
        ("normal", "Normal", "Équilibre classique."),
        ("hard", "Difficile", "Ennemi renforcé, base ennemie plus riche."),
    ]

    def __init__(self):
        self._selected = "normal"
        # Boutons centrés verticalement
        start_y = SCREEN_HEIGHT // 2 - 70
        self.cards = {}
        for i, (diff_id, label, _) in enumerate(self.DIFFICULTIES):
            y = start_y + i * 60
            self.cards[diff_id] = pygame.Rect(SCREEN_WIDTH // 2 - 150, y, 300, 50)
        self.back_button = MenuButton("Retour", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70)

    def _diff_at(self, pos):
        for diff_id, rect in self.cards.items():
            if rect.collidepoint(pos):
                return diff_id
        return None

    def draw(self, screen):
        """Dessine l'écran de difficulté."""
        screen.fill((30, 30, 45))

        title_font = pygame.font.Font(None, 52)
        title = title_font.render("Choisissez la Difficulté", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(title, title_rect)

        hint_font = pygame.font.Font(None, 20)
        hint = hint_font.render("Cliquez sur un niveau pour commencer la campagne",
                                True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 110))
        screen.blit(hint, hint_rect)

        for diff_id, label, desc in self.DIFFICULTIES:
            rect = self.cards[diff_id]
            hovered = (diff_id == self._selected)
            color = {"easy": (60, 150, 60), "normal": (200, 170, 60),
                     "hard": (200, 70, 50)}[diff_id]
            pygame.draw.rect(screen, (45, 45, 70), rect, border_radius=8)
            pygame.draw.rect(screen, color, rect, 3 if hovered else 1, border_radius=8)

            name_font = pygame.font.Font(None, 28)
            name = name_font.render(label, True, color)
            screen.blit(name, (rect.x + 16, rect.y + 12))

            desc_font = pygame.font.Font(None, 15)
            desc_surf = desc_font.render(desc, True, (200, 200, 200))
            screen.blit(desc_surf, (rect.x + 100, rect.y + 16))

        self.back_button.draw(screen)

    def handle_event(self, event) -> str:
        """Gère les événements. Retourne l'id difficulté ou 'back'."""
        if event.type == pygame.MOUSEMOTION:
            diff_id = self._diff_at(event.pos)
            if diff_id:
                self._selected = diff_id
            return ""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.back_button.is_clicked(pos):
                return "back"
            diff_id = self._diff_at(pos)
            if diff_id:
                return diff_id
        return ""


class PauseMenu:
    """Menu de pause."""

    def __init__(self):
        # Center vertically: total height = 3*50 + 2*10 = 170, start at center - 85
        self.buttons = [
            MenuButton("Reprendre", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 85),
            MenuButton("Sauvegarder", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25),
            MenuButton("Menu Principal", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 35),
        ]

    def draw(self, screen, game=None):
        """Dessine le menu de pause."""
        # Dessiner le jeu en arrière-plan (flou)
        if game:
            game._draw_game()
        else:
            screen.fill((0, 0, 0, 150))

        # Panneau central semi-transparent
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(screen, (30, 30, 50), panel_rect)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, 2)

        # Titre
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pause", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title, title_rect)

        # Info faction
        if game and hasattr(game, 'faction') and game.faction:
            faction_font = pygame.font.Font(None, 20)
            fid = game.faction_id if hasattr(game, 'faction_id') else 'inconnue'
            ftext = faction_font.render(f"Faction: {game.faction.name if hasattr(game.faction, 'name') else fid}",
                                        True, game.faction.color if hasattr(game.faction, 'color') else (255,255,255))
            screen.blit(ftext, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 130))

        # Info mission si en cours
        if game and game.current_mission:
            mission_font = pygame.font.Font(None, 20)
            y_offset = SCREEN_HEIGHT // 2 - 60
            mission_name = mission_font.render(f"Mission: {game.current_mission.name}", True, (255, 215, 0))
            screen.blit(mission_name, (SCREEN_WIDTH // 2 - 100, y_offset))

            y_offset += 25
            for objective in game.current_mission.objectives:
                status = "✓" if objective.completed else f"{objective.current}/{objective.target}"
                color = (0, 255, 0) if objective.completed else (255, 255, 255)
                obj_text = mission_font.render(f"{objective.description}: {status}", True, color)
                screen.blit(obj_text, (SCREEN_WIDTH // 2 - 100, y_offset))
                y_offset += 20

            timer_text = mission_font.render(f"Temps: {int(game.mission_timer)}s", True, (200, 200, 200))
            screen.blit(timer_text, (SCREEN_WIDTH // 2 - 100, y_offset + 10))

        # Boutons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_event(self, event) -> str:
        """Gère les événements du menu de pause."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for button in self.buttons:
                if button.is_clicked(pos):
                    if button.text == "Reprendre":
                        return "resume"
                    elif button.text == "Sauvegarder":
                        return "save"
                    elif button.text == "Menu Principal":
                        return "main_menu"
        return ""


class VictoryScreen:
    """Écran de victoire."""

    def __init__(self):
        self.font = pygame.font.Font(None, 72)
        # Center button vertically below title
        self.button = MenuButton("Menu Principal", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20)
    
    def draw(self, screen):
        """Dessine l'écran de victoire."""
        screen.fill((0, 100, 0))
        
        title = self.font.render("Victoire!", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title, title_rect)
    
    def handle_event(self, event) -> str:
        """Gère les événements."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.button.is_clicked(pos):
                return "main_menu"
        return ""


class DefeatScreen:
    """Écran de défaite."""

    def __init__(self):
        self.font = pygame.font.Font(None, 72)
        # Center button vertically below title
        self.button = MenuButton("Menu Principal", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20)
    
    def draw(self, screen):
        """Dessine l'écran de défaite."""
        screen.fill((100, 0, 0))
        
        title = self.font.render("Défaite...", True, (200, 200, 200))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title, title_rect)
    
    def handle_event(self, event) -> str:
        """Gère les événements."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.button.is_clicked(pos):
                return "main_menu"
        return ""


class OptionsMenu:
    """Écran d'options : musique, SFX, plein écran."""

    SLIDER_W = 240
    SLIDER_H = 14
    KNOB_R = 10

    def __init__(self):
        self._music_vol = 0.7
        self._sfx_vol = 0.8
        self._fullscreen = False

        y_base = SCREEN_HEIGHT // 2 - 80
        self._music_slider_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + 20, y_base, self.SLIDER_W, self.SLIDER_H)
        self._sfx_slider_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + 20, y_base + 50, self.SLIDER_W, self.SLIDER_H)

        self._fs_button = MenuButton(
            "Plein Écran: OFF", SCREEN_WIDTH // 2 - 100, y_base + 120, 280, 44)
        self.back_button = MenuButton(
            "Retour", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70)

    # ── helpers ──────────────────────────────────────────────

    def _knob_x(self, slider_rect, value):
        return int(slider_rect.x + value * self.SLIDER_W)

    def _slider_clicked(self, event, slider_rect):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        mx, my = event.pos
        if slider_rect.x <= mx <= slider_rect.x + self.SLIDER_W and \
           slider_rect.y - 8 <= my <= slider_rect.y + self.SLIDER_H + 8:
            return max(0.0, min(1.0, (mx - slider_rect.x) / self.SLIDER_W))
        return None

    # ── draw ─────────────────────────────────────────────────

    def draw(self, screen):
        screen.fill((30, 30, 45))

        title_font = pygame.font.Font(None, 48)
        t = title_font.render("Options", True, (255, 215, 0))
        screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        label_font = pygame.font.Font(None, 28)
        val_font = pygame.font.Font(None, 22)

        # ── musique ──
        mx = self._knob_x(self._music_slider_rect, self._music_vol)
        screen.blit(label_font.render("Musique", True, (220, 220, 220)),
                    (SCREEN_WIDTH // 2 - 140, self._music_slider_rect.y - 4))
        pygame.draw.rect(screen, (80, 80, 100), self._music_slider_rect,
                         border_radius=self.SLIDER_H // 2)
        pygame.draw.rect(screen, (100, 180, 255),
                         pygame.Rect(self._music_slider_rect.x, self._music_slider_rect.y,
                                     int(self._music_vol * self.SLIDER_W), self.SLIDER_H),
                         border_radius=self.SLIDER_H // 2)
        pygame.draw.circle(screen, (220, 220, 255),
                           (mx, self._music_slider_rect.centery), self.KNOB_R)
        screen.blit(val_font.render(f"{int(self._music_vol * 100)}%", True, (180, 180, 180)),
                    (mx + 18, self._music_slider_rect.y - 2))

        # ── SFX ──
        sx = self._knob_x(self._sfx_slider_rect, self._sfx_vol)
        screen.blit(label_font.render("Effets", True, (220, 220, 220)),
                    (SCREEN_WIDTH // 2 - 140, self._sfx_slider_rect.y - 4))
        pygame.draw.rect(screen, (80, 80, 100), self._sfx_slider_rect,
                         border_radius=self.SLIDER_H // 2)
        pygame.draw.rect(screen, (255, 180, 100),
                         pygame.Rect(self._sfx_slider_rect.x, self._sfx_slider_rect.y,
                                     int(self._sfx_vol * self.SLIDER_W), self.SLIDER_H),
                         border_radius=self.SLIDER_H // 2)
        pygame.draw.circle(screen, (255, 220, 180),
                           (sx, self._sfx_slider_rect.centery), self.KNOB_R)
        screen.blit(val_font.render(f"{int(self._sfx_vol * 100)}%", True, (180, 180, 180)),
                    (sx + 18, self._sfx_slider_rect.y - 2))

        # ── plein écran ──
        self._fs_button.text = f"Plein Écran: {'ON' if self._fullscreen else 'OFF'}"
        self._fs_button.draw(screen)

        self.back_button.draw(screen)

    # ── events ──────────────────────────────────────────────

    def handle_event(self, event):
        """Retourne 'back' ou ''."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.back_button.is_clicked(pos):
                return "back"

            if self._fs_button.is_clicked(pos):
                self._fullscreen = not self._fullscreen
                pygame.display.toggle_fullscreen()
                return ""

            mv = self._slider_clicked(event, self._music_slider_rect)
            if mv is not None:
                self._music_vol = mv
                return ""

            sv = self._slider_clicked(event, self._sfx_slider_rect)
            if sv is not None:
                self._sfx_vol = sv
                return ""

        return ""