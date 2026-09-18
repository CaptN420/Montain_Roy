# Mountain_Roy - Étape 14: Sprites Pixel Art 16-bit

## Fichiers créis/modifiés pour l'Étape 14

### Nouveaux fichiers :
- `systems/sprite_generator.py` - Générateur de sprites pixel art (32x32 et 64x64)
- `systems/sprite_manager.py` - Gestionnaire et rendu des sprites

## Ce qui fonctionne maintenant

### Sprites générés automatiquement
1. ✅ **Unités** (32x32):
   - Warrior - Guerrier avec épée et armure
   - Archer - Archer avec arc et capuche verte
   - Knight - Chevalier à cheval avec bouclier
   - Mage - Mage avec bâton magique violet
   - Healer - Soigneur avec croix rouge
   - Scout - Éclaireur avec dagues

2. ✅ **Bâtiments** (48x48 ou 64x64):
   - Town Hall - Hôtel de Ville avec toit rouge
   - Barracks - Caserne
   - Farm - Ferme
   - Tower - Tour défensive
   - Mine - Mine avec entrée
   - Lumber Mill - Scierie
   - Temple - Temple avec croix dorée
   - Workshop - Atelier

### Système de sprites
1. ✅ **SpriteManager** - Chargement et rendu des sprites PNG
2. ✅ **AnimationManager** - Gestion des animations
3. ✅ **SpriteRenderer** - Rendu optimisé avec cache
4. ✅ **Fallback automatique** - Génère des sprites si les fichiers n'existent pas

## Pour générer les sprites

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python systems/sprite_generator.py
```

Ou lancer le jeu, il générera automatiquement les sprites dans `assets/sprites/`.

## Structure des assets

```
Mountain_Roy/assets/
├── sprites/
│   ├── warrior_player.png      # 32x32
│   ├── archer_player.png       # 32x32
│   ├── knight_player.png       # 32x32
│   ├── mage_player.png         # 32x32
│   ├── healer_player.png       # 32x32
│   ├── scout_player.png        # 32x32
│   ├── town_hall_player.png    # 64x64
│   ├── barracks_player.png     # 48x48
│   ├── farm_player.png         # 48x48
│   ├── tower_player.png        # 48x48
│   ├── mine_player.png         # 48x48
│   ├── lumber_mill_player.png  # 48x48
│   ├── temple_player.png       # 64x64
│   └── workshop_player.png     # 48x48
├── sounds/                     # (à créer)
│   ├── shoot.wav
│   ├── hit.wav
│   └── ...
└── maps/                       # (à créer)
    └── campaign.json
```

## Style pixel art

- **Résolution**: 32x32 pour les unités, 48x48/64x64 pour les bâtiments
- **Palette**: Couleurs limitées style 16-bit
- **Détails**: Casques, armures, armes, accessoires distinctifs
- **Factions**: Même design pour player/enemy (changement de couleur via tint)

## Pour lancer le jeu

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Résumé des 14 étapes complétées

| Étape | Contenu |
|-------|---------|
| 1 | Moteur et fenêtre |
| 2 | Carte et caméra |
| 3 | Unités et sélection |
| 4 | Déplacement et pathfinding |
| 5 | Ressources et récolte |
| 6 | Interface complète (HUD) |
| 7 | Brouillard de guerre |
| 8 | IA ennemie |
| 9 | Sauvegarde/Chargement |
| 10 | Campagne et missions |
| 11 | Optimisation et finition |
| 12 | Sons et effets visuels |
| 13 | (Optionnel) |
| 14 | Sprites pixel art 16-bit |

Le jeu Mountain_Roy est maintenant complet avec:
- ✅ Moteur RTS fonctionnel
- ✅ 7 types d'unités
- ✅ 8 types de bâtiments
- ✅ IA ennemie
- ✅ Campagne de 4 missions
- ✅ Système de sauvegarde
- ✅ Brouillard de guerre
- ✅ Sprites pixel art générés
