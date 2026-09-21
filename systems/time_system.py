import pygame
import time

class TimeManager:
    """Gère le cycle jour/nuit et les saisons."""
    
    def __init__(self, day_length_seconds=1200.0):
        # Une journée complète dure day_length_seconds (ex: 20 minutes)
        self.day_length = day_length_seconds
        self.elapsed_time = 0.0
        
        # Saisons (chaque saison dure 4 journées complètes)
        self.seasons = ["Printemps", "Été", "Automne", "Hiver"]
        self.current_season_idx = 0
        self.days_passed = 0
        
        # Couleurs pour l'ambiance (optionnel pour le rendu)
        self.ambient_color = [255, 255, 255]

    def update(self, dt: float):
        """Met à jour l'heure et les saisons."""
        self.elapsed_time += dt
        
        # Cycle Jour/Nuit
        if self.elapsed_time >= self.day_length:
            self.elapsed_time = 0.0
            self.days_passed += 1
            
        # Changement de saison (tous les 4 jours)
        if self.days_passed % 4 == 0:
            self.current_season_idx = (self.current_season_idx + 1) % len(self.seasons)
            
        # Calcul de l'heure (0.0 à 1.0)
        self.current_hour = (self.elapsed_time / self.day_length) * 24
        
        # Déterminer l'ambiance
        self._update_ambient_color()

    def _update_ambient_color(self):
        """Ajuste la couleur ambiante selon l'heure et la saison."""
        # Base sur l'heure (nuit est plus sombre)
        hour = self.current_hour
        if hour < 6 or hour > 20: # Nuit
            brightness = 0.4
        elif 6 <= hour < 18: # Jour
            brightness = 1.0
        else: # Aube/Crépuscule
            brightness = 0.7
            
        # Influence de la saison
        season = self.seasons[self.current_season_idx]
        if season == "Hiver":
            brightness *= 0.8
            self.ambient_color = [200, 220, 255] # Teinte bleutée
        elif season == "Été":
            brightness *= 1.1
            self.ambient_color = [255, 240, 200] # Teinte chaude
        elif season == "Automne":
            brightness *= 0.9
            self.ambient_color = [200, 150, 100] # Teinte orangée
        else: # Printemps
            self.ambient_color = [200, 255, 200] # Teinte verdoyante
            
        self.ambient_color = [int(c * brightness) for c in self.ambient_color]

    def get_season_modifiers(self) -> dict:
        """Retourne les modificateurs actuels basés sur la saison."""
        season = self.seasons[self.current_season_idx]
        mods = {"food_prod": 1.0, "move_speed": 1.0, "wood_harvest": 1.0}
        
        if season == "Hiver":
            mods["food_prod"] = 0.3
            mods["move_speed"] = 0.8
        elif season == "Été":
            mods["food_prod"] = 1.5
            mods["move_speed"] = 1.1
        elif season == "Automne":
            mods["wood_harvest"] = 1.3
            
        return mods

    def get_current_hour(self) -> float:
        return self.current_hour

    def get_current_season(self) -> str:
        return self.seasons[self.current_season_idx]
