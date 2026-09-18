# Mountain_Roy - Étape 10: Campagne et Missions

## Fichiers créis/modifiés pour l'Étape 10

### Nouveaux fichiers :
- `systems/campaign.py` - Système de campagne et missions

### Fichiers modifiés :
- `core/game.py` - Intègre la campagne et les missions

## Ce qui fonctionne maintenant

1. ✅ **Campagne** - 4 missions progressives
2. ✅ **Objectifs** - Kill, Build, Produce, Survive
3. ✅ **Récompenses** - Or, Bois, XP à la complétion
4. ✅ **Écran de mission** - Affichage avant chaque mission
5. ✅ **HUD de mission** - Objectifs en temps réel
6. ✅ **Progression** - Mission suivante après victoire

## Missions disponibles

1. **Premier Contact** - Tuer 5 ennemis, construire une caserne
2. **Expansion** - Produire 10 unités, construire une tour
3. **Contre-Attaque** - Survivre 120s, tuer 15 ennemis
4. **Conquête** - Détruire 3 bases ennemies

## Pour lancer le jeu

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Contrôles

- **WASD** ou **Flèches** : Déplacer la caméra
- **Molette** : Zoom avant/arrière
- **Clic gauche** : Sélectionner une unité alliée
- **Clic droit** : Déplacer, attaquer ou récolter
- **1, 2, 3** : Produire Warrior, Archer, Knight
- **Espace, Q, E, R** : Compétences du héros
- **ESC** : Pause
- **F5** : Sauvegarder rapidement
- **F9** : Charger la dernière sauvegarde

## Structure du projet

```
Mountain_Roy/
├── main.py
├── settings.py
├── core/
│   ├── game.py          # Moteur principal
│   ├── camera.py        # Caméra RTS
│   └── save_system.py   # Sauvegarde/Chargement
├── entities/
│   ├── unit.py          # Unité de base
│   ├── hero.py          # Héros
│   ├── building.py      # Bâtiments
│   └── unit_types.py    # Types d'unités
├── systems/
│   ├── pathfinding.py   # A* Pathfinding
│   ├── movement.py      # Mouvement
│   ├── combat.py        # Combat
│   ├── economy.py       # Ressources
│   ├── construction.py  # Construction/Production
│   ├── fog_of_war.py    # Brouillard de guerre
│   ├── ai.py            # IA ennemie
│   └── campaign.py      # Campagne/Missions
├── map/
│   ├── tile.py          # Tuiles
│   └── game_map.py      # Carte
├── ui/
│   ├── hud.py           # Interface utilisateur
│   └── menus.py         # Menus
└── assets/              # Sprites, sons, maps
```

## Résumé des étapes complétées

- ✅ Étape 1: Moteur et fenêtre
- ✅ Étape 2: Carte et caméra
- ✅ Étape 3: Unités et sélection
- ✅ Étape 4: Déplacement et pathfinding
- ✅ Étape 5: Ressources et récolte
- ✅ Étape 6: Interface complète (HUD)
- ✅ Étape 7: Brouillard de guerre
- ✅ Étape 8: IA ennemie
- ✅ Étape 9: Sauvegarde/Chargement
- ✅ Étape 10: Campagne et missions

## Prochaines étapes (optionnelles)

- Étape 11: Optimisation et finition
- Étape 12: Sons et effets visuels
- Étape 13: Multiplayer (optionnel)
- Étape 14: Export des sprites en pixel art
