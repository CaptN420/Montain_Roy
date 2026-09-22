"""
Mountain_Roy - Sound Effects Generator (Générateur de Sons Proceduraux)
Étape 15: Audio et effets sonores
"""

import pygame
import math
import random
import struct


class SoundGenerator:
    """Génère des effets sonores procéduralement."""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
    
    def _generate_wave(self, frequency: float, duration: float, 
                       wave_type: str = "sine", volume: float = 0.3) -> pygame.mixer.Sound:
        """Génère une onde sonore."""
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            if wave_type == "sine":
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == "square":
                value = 1 if (i % (self.sample_rate // frequency)) < (self.sample_rate // (frequency * 2)) else -1
            elif wave_type == "sawtooth":
                value = 2 * ((t * frequency) % 1) - 1
            elif wave_type == "triangle":
                value = 2 * abs(((t * frequency) % 1) - 0.5) - 1
            elif wave_type == "noise":
                value = random.uniform(-1, 1)
            
            # Enveloppe ADSR simple
            envelope = 1.0
            if i < num_samples * 0.1:  # Attack
                envelope = i / (num_samples * 0.1)
            elif i > num_samples * 0.8:  # Release
                envelope = (num_samples - i) / (num_samples * 0.2)
            
            samples.append(int(value * volume * envelope * 32767))
        
        # Créer le son - utiliser pygame.mixer.Sound directement
        import struct
        # Convertir les échantillons en format binaire (int16 LE)
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        sound_array = pygame.mixer.Sound(buffer=sample_bytes)
        return sound_array
    
    def generate_hit_sound(self, damage: int = 10) -> pygame.mixer.Sound:
        """Génère un son de coup."""
        frequency = 200 + damage * 5
        return self._generate_wave(frequency, 0.1, "square", 0.2)
    
    def generate_kill_sound(self) -> pygame.mixer.Sound:
        """Génère un son de mort."""
        return self._generate_wave(150, 0.3, "sawtooth", 0.25)
    
    def generate_build_sound(self) -> pygame.mixer.Sound:
        """Génère un son de construction."""
        return self._generate_wave(440, 0.15, "sine", 0.2)
    
    def generate_collect_sound(self) -> pygame.mixer.Sound:
        """Génère un son de collecte."""
        return self._generate_wave(600, 0.1, "sine", 0.15)
    
    def generate_error_sound(self) -> pygame.mixer.Sound:
        """Génère un son d'erreur."""
        return self._generate_wave(100, 0.2, "square", 0.2)
    
    def generate_victory_sound(self) -> pygame.mixer.Sound:
        """Génère un son de victoire."""
        # Mélodie ascendante
        base_freq = 440
        notes = [base_freq, base_freq * 1.125, base_freq * 1.25, base_freq * 1.333, base_freq * 1.5]
        samples = []
        note_duration = 0.15
        
        for freq in notes:
            num_samples = int(self.sample_rate * note_duration)
            for i in range(num_samples):
                t = i / self.sample_rate
                value = math.sin(2 * math.pi * freq * t)
                envelope = min(i / (num_samples * 0.1), (num_samples - i) / (num_samples * 0.2))
                samples.append(int(value * 0.3 * envelope * 32767))
        
        # Créer le son - utiliser pygame.mixer.Sound directement
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        return pygame.mixer.Sound(buffer=sample_bytes)
    
    def generate_defeat_sound(self) -> pygame.mixer.Sound:
        """Génère un son de défaite."""
        base_freq = 440
        notes = [base_freq, base_freq * 0.89, base_freq * 0.75, base_freq * 0.67, base_freq * 0.5]
        samples = []
        note_duration = 0.2
        
        for freq in notes:
            num_samples = int(self.sample_rate * note_duration)
            for i in range(num_samples):
                t = i / self.sample_rate
                value = math.sin(2 * math.pi * freq * t) * 0.8
                envelope = min(i / (num_samples * 0.1), (num_samples - i) / (num_samples * 0.2))
                samples.append(int(value * 0.3 * envelope * 32767))
        
        # Créer le son - utiliser pygame.mixer.Sound directement
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        return pygame.mixer.Sound(buffer=sample_bytes)
    
    def generate_skill_sound(self, skill_index: int = 0) -> pygame.mixer.Sound:
        """Génère un son de compétence."""
        frequencies = [800, 600, 1000, 1200]
        duration = 0.2
        return self._generate_wave(frequencies[skill_index % len(frequencies)], duration, "sine", 0.2)
    
    def generate_ui_click_sound(self) -> pygame.mixer.Sound:
        """Génère un son de clic UI."""
        return self._generate_wave(800, 0.05, "square", 0.1)
    
    def generate_select_sound(self) -> pygame.mixer.Sound:
        """Génère un son de sélection d'unité."""
        return self._generate_wave(600, 0.08, "sine", 0.15)
    
    def generate_move_sound(self) -> pygame.mixer.Sound:
        """Génère un son de déplacement (ordre donné)."""
        return self._generate_wave(400, 0.06, "triangle", 0.1)
    
    def generate_attack_sound(self) -> pygame.mixer.Sound:
        """Génère un son d'attaque."""
        return self._generate_wave(150, 0.12, "sawtooth", 0.2)
    
    def generate_retreat_sound(self) -> pygame.mixer.Sound:
        """Génère un son de retraite."""
        return self._generate_wave(300, 0.15, "sine", 0.15)
    
    def generate_music_loop(self, duration: float = 8.0) -> pygame.mixer.Sound:
        """Génère une boucle musicale d'ambiance procédurale.

        Construit un arpège doux (mineur) répété sur `duration` secondes pour
        servir de musique de fond légère. Volume bas pour ne pas masquer les SFX.
        """
        base_freq = 220.0
        # Arpège en mineur naturel : la, do, mi, la (octave), sol
        notes = [base_freq, base_freq * 1.2, base_freq * 1.5, base_freq * 2.0, base_freq * 1.8]
        note_duration = 0.4
        num_samples = int(self.sample_rate * duration)
        samples = []
        i = 0
        note_idx = 0
        while i < num_samples:
            freq = notes[note_idx % len(notes)]
            n = int(self.sample_rate * note_duration)
            for j in range(n):
                if i >= num_samples:
                    break
                t = i / self.sample_rate
                # Onde douce (sine) + légère harmonique pour la chaleur
                value = math.sin(2 * math.pi * freq * t) * 0.6 + math.sin(2 * math.pi * freq * 2 * t) * 0.2
                # Enveloppe douce (attack/release) pour éviter les clics
                env = min(j / (n * 0.15), (n - j) / (n * 0.3), 1.0)
                samples.append(int(value * 0.12 * env * 32767))
                i += 1
            note_idx += 1
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        return pygame.mixer.Sound(buffer=sample_bytes)

    def generate_combat_music(self, duration: float = 10.0) -> pygame.mixer.Sound:
        """Génère une musique de combat plus intense."""
        # Scale mineure harmonique pour tension
        base_freq = 246.94  # Sol#
        notes = [base_freq, base_freq * 1.19, base_freq * 1.42, base_freq * 1.6, base_freq * 1.89]
        note_duration = 0.25
        num_samples = int(self.sample_rate * duration)
        samples = []
        i = 0
        note_idx = 0
        while i < num_samples:
            freq = notes[note_idx % len(notes)]
            n = int(self.sample_rate * note_duration)
            for j in range(n):
                if i >= num_samples:
                    break
                t = i / self.sample_rate
                # Onde plus agressive (sawtooth doux) + harmonique
                value = (math.sin(2 * math.pi * freq * t) * 0.5 +
                        math.sin(2 * math.pi * freq * 1.5 * t) * 0.15)
                env = min(j / (n * 0.1), (n - j) / (n * 0.2), 1.0)
                samples.append(int(value * 0.18 * env * 32767))
                i += 1
            note_idx += 1
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        return pygame.mixer.Sound(buffer=sample_bytes)

    def generate_victory_music(self) -> pygame.mixer.Sound:
        """Génère une mélodie de victoire triomphale."""
        notes = [440, 554.37, 659.26, 880, 659.26, 880, 1108.73, 880]
        samples = []
        for freq in notes:
            n = int(self.sample_rate * 0.2)
            for i in range(n):
                t = i / self.sample_rate
                value = math.sin(2 * math.pi * freq * t) * 0.4
                env = min(i / (n * 0.1), (n - i) / (n * 0.3), 1.0)
                samples.append(int(value * env * 32767))
        sample_bytes = struct.pack('<' + 'h' * len(samples), *samples)
        return pygame.mixer.Sound(buffer=sample_bytes)


class AudioManager:
    """Gère la lecture des sons."""
    
    def __init__(self):
        self.audio_enabled = True
        self.generator = SoundGenerator()
        self.sounds = {}
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        self.muted = False
        self.music_channel = None

        self._load_sounds()
    
    def _load_sounds(self):
        """Charge tous les sons."""
        # Initialiser le mixer si nécessaire
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            # Mixer non disponible, désactiver l'audio
            self.audio_enabled = False
            self.sounds = {}
            return

        self.sounds = {
            "hit": self.generator.generate_hit_sound(),
            "kill": self.generator.generate_kill_sound(),
            "build": self.generator.generate_build_sound(),
            "collect": self.generator.generate_collect_sound(),
            "error": self.generator.generate_error_sound(),
            "victory": self.generator.generate_victory_sound(),
            "defeat": self.generator.generate_defeat_sound(),
            "ui_click": self.generator.generate_ui_click_sound(),
            "select": self.generator.generate_select_sound(),
            "move": self.generator.generate_move_sound(),
            "attack": self.generator.generate_attack_sound(),
            "retreat": self.generator.generate_retreat_sound(),
            "skill": self.generator._generate_wave(800, 0.2, "sine", 0.2),
        }

        # Musiques
        self.music_loop = None
        self.combat_music = None
    
    def play(self, sound_name: str, volume: float = None):
        """Joue un son."""
        if not self.audio_enabled or self.muted:
            return

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is None:
                volume = self.sfx_volume
            sound.set_volume(volume)
            sound.play()
    
    def play_random(self, prefix: str, min_vol: float = 0.3, max_vol: float = 0.7):
        """Joue un son aléatoire."""
        matching = [k for k in self.sounds.keys() if k.startswith(prefix)]
        if matching:
            sound_name = random.choice(matching)
            vol = random.uniform(min_vol, max_vol)
            self.play(sound_name, vol)
    
    def set_music_volume(self, volume: float):
        """Définit le volume de la musique."""
        self.music_volume = max(0, min(1, volume))
    
    def set_sfx_volume(self, volume: float):
        """Définit le volume des effets sonores."""
        self.sfx_volume = max(0, min(1, volume))
    
    def toggle_mute(self):
        """Active/désactive le son (SFX + musique)."""
        self.muted = not self.muted
        if self.music_channel:
            self.music_channel.set_volume(0 if self.muted else self.music_volume)

    def start_music(self, combat_mode: bool = False):
        """Démarre la musique (ambiance ou combat)."""
        if not self.audio_enabled:
            return
        try:
            if combat_mode:
                music = self.generator.generate_combat_music()
            else:
                music = self.generator.generate_music_loop()
            self.music_channel = pygame.mixer.Channel(0)
            self._music = music
            self.music_channel.set_volume(0 if self.muted else self.music_volume)
            self.music_channel.play(music, loops=-1)
        except Exception:
            self.music_channel = None

    def stop_music(self):
        """Arrête la boucle musicale."""
        if self.music_channel:
            self.music_channel.stop()
            self.music_channel = None


class AudioEvents:
    """Gère les événements audio du jeu."""
    
    def __init__(self, audio_manager: AudioManager):
        self.audio = audio_manager
    
    def on_unit_hit(self, damage: int):
        """Appelé quand une unité subit des dégâts."""
        self.audio.play("hit")
    
    def on_kill(self):
        """Appelé quand un ennemi est tué."""
        self.audio.play("kill")
    
    def on_unit_killed(self):
        """Appelé quand une unité meurt."""
        self.audio.play("kill")
    
    def on_building_built(self):
        """Appelé quand un bâtiment est construit."""
        self.audio.play("build")
    
    def on_resource_collected(self):
        """Appelé quand une ressource est collectée."""
        self.audio.play("collect")
    
    def on_error(self):
        """Appelé quand il y a une erreur."""
        self.audio.play("error")
    
    def on_victory(self):
        """Appelé en cas de victoire."""
        self.audio.play("victory")
        if hasattr(self.audio, 'generator'):
            music = self.audio.generator.generate_victory_music()
            channel = pygame.mixer.Channel(1)
            channel.set_volume(self.audio.music_volume)
            channel.play(music, loops=0)

    def on_defeat(self):
        """Appelé en cas de défaite."""
        self.audio.play("defeat")
    
    def on_skill_used(self, skill_index: int = 0):
        """Appelé quand une compétence est utilisée."""
        self.audio.play("skill")
    
    def on_ui_click(self):
        """Appelé quand un bouton UI est cliqué."""
        self.audio.play("ui_click")
    
    def on_unit_selected(self):
        """Appelé quand une unité est sélectionnée."""
        self.audio.play("select")
    
    def on_order_given(self, order_type: str = "move"):
        """Appelé quand un ordre est donné à une unité."""
        if order_type == "attack":
            self.audio.play("attack")
        elif order_type == "retreat":
            self.audio.play("retreat")
        else:
            self.audio.play("move")
