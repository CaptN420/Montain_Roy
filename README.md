# Mountain_Roy - Projet RTS Complet

## Résumé du projet

**Mountain_Roy** est un jeu de stratégie en temps réel (RTS) développé en Python avec Pygame, inspiré des classiques comme Warcraft III.

## Structure finale du projet

```
Mountain_Roy/
├── main.py                      # Point d'entrée
├── settings.py                  # Configuration globale
├── core/
│   ├── game.py                  # Moteur principal (672 lignes)
│   ├── camera.py                # Caméra RTS
│   └── save_system.py           # Sauvegarde/Chargement
├── entities/
│   ├── unit.py                  # Unité de base
│   ├── hero.py                  # Héros (niveaux, mana, compétences)
│   ├── building.py              # Bâtiments (8 types)
│   └── unit_types.py            # Types d'unités (7 types)
├── systems/
│   ├── pathfinding.py           # A* Pathfinding
│   ├── movement.py              # Mouvement
│   ├── combat.py                # Combat
│   ├── economy.py               # Ressources (or, bois, nourriture)
│   ├── construction.py          # Construction/Production
│   ├── fog_of_war.py            # Brouillard de guerre
│   ├── ai.py                    # IA ennemie
│   ├── campaign.py              # Campagne (4 missions)
│   ├── effects.py               # Particules et effets visuels
│   ├── sounds.py                # Sons et audio
│   ├── sprite_generator.py      # Générateur de sprites pixel art
│   └── sprite_manager.py        # Gestionnaire de sprites
├── map/
│   ├── tile.py                  # Tuiles (7 types)
│   └── game_map.py              # Carte 128x128
├── ui/
│   ├── hud.py                   # Interface utilisateur complète
│   └── menus.py                 # Menus (principal, pause, victoire, défaite)
└── assets/
    ├── sprites/                 # Sprites pixel art générés
    │   ├── warrior.png          # 32x32
    │   ├── archer.png           # 32x32
    │   ├── knight.png           # 32x32
    │   ├── mage.png             # 32x32
    │   ├── healer.png           # 32x32
    │   ├── scout.png            # 32x32
    │   ├── town_hall.png        # 64x64
    │   ├── barracks.png         # 48x48
    │   ├── farm.png             # 48x48
    │   ├── tower.png            # 48x48
    │   ├── mine.png             # 48x48
    │   ├── lumber_mill.png      # 48x48
    │   ├── temple.png           # 64x64
    │   └── workshop.png         # 48x48
    ├── sounds/                  # (à créer)
    └── maps/                    # (à créer)
```

## Fonctionnalités implémentées

### Gameplay
- ✅ Carte 128x128 tuiles avec terrain varié
- ✅ Caméra RTS (WASD + zoom molette)
- ✅ Sélection d'unités (clic gauche)
- ✅ Déplacement et attaque (clic droit)
- ✅ Récolte de ressources (or, bois, nourriture)
- ✅ Construction de bâtiments
- ✅ Production d'unités
- ✅ Héros avec niveaux et compétences
- ✅ Brouillard de guerre
- ✅ IA ennemie autonome
- ✅ Système de victoire/défaite

### Interface
- ✅ Menu principal
- ✅ HUD complet (ressources, sélection, minimap)
- ✅ Boutons de production (1, 2, 3)
- ✅ Boutons de compétences (Espace, Q, E, R)
- ✅ Écran de mission
- ✅ Menu pause
- ✅ Écrans victoire/défaite

### Technique
- ✅ Sauvegarde/Chargement JSON
- ✅ Campagne de 4 missions
- ✅ Particules et effets visuels
- ✅ Sprites pixel art 16-bit générés
- ✅ Optimisations (cache, QuadTree)

## Contrôles

| Touche | Action |
|--------|--------|
| WASD / Flèches | Déplacer la caméra |
| Molette | Zoom avant/arrière |
| Clic gauche | Sélectionner une unité |
| Clic droit | Déplacer / Attaquer / Récolter |
| 1, 2, 3 | Produire Warrior, Archer, Knight |
| Espace | Compétence 1 (Frappe dévastatrice) |
| Q | Compétence 2 (Bouclier magique) |
| E | Compétence 3 (Cri de guerre) |
| R | Compétence 4 (Météore) |
| ESC | Pause |
| F5 | Sauvegarder rapidement |
| F9 | Charger la dernière sauvegarde |

## Lancement

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Faction du joueur: Les Gardiens d'Aube

Unités disponibles:
- **Guerrier** - Unité terrestre de base
- **Archer** - Unité à distance
- **Chevalier** - Unité blindée
- **Mage** - Unité magique
- **Soigneur** - Soutien et soin
- **Éclaireur** - Unité rapide

Bâtiments disponibles:
- **Hôtel de Ville** - Bâtiment principal
- **Caserne** - Production d'unités terrestres
- **Ferme** - Augmente la population max
- **Tour défensive** - Attaque à distance
- **Mine** - Collecte d'or
- **Scierie** - Améliore la récolte de bois
- **Temple** - Pour les héros
- **Atelier** - Production spécialisée

## Ennemis: La Légion des Cendres

L'IA ennemie construit sa base, produit des unités et attaque le joueur.

## Campagne

4 missions progressives:
1. **Premier Contact** - Tuer 5 ennemis, construire une caserne
2. **Expansion** - Produire 10 unités, construire une tour
3. **Contre-Attaque** - Survivre 120s, tuer 15 ennemis
4. **Conquête** - Détruire 3 bases ennemies

## Technologies utilisées

- Python 3.11
- Pygame 2.6
- Algorithmes: A* Pathfinding, QuadTree
- Format: JSON pour les sauvegardes

## Prochaines améliorations possibles

- Sons et musique
- Animations de sprites
- Multiplayer local
- Éditeur de cartes
- Mode sandbox illimité
- Différents niveaux de difficulté
