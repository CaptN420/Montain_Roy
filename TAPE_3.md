# Mountain_Roy - Étape 3: Unités et Sélection

## Fichiers créis/modifiés pour l'Étape 3

### Nouveaux fichiers :
- `entities/unit.py` - Classe de base Unit (stats, mouvement, combat)
- `entities/hero.py` - Classe Hero (niveaux, mana, compétences)
- `entities/building.py` - Classes Building + spécialisées (TownHall, Barracks, etc.)
- `entities/unit_types.py` - Types d'unités (Warrior, Archer, Knight, Mage, Healer, SiegeEngine, Scout)

### Fichiers modifiés :
- `core/game.py` - Intègre les unités et la sélection

## Ce qui fonctionne maintenant

1. ✅ **Héros** (cercle doré) visible sur la carte
2. ✅ **Unités alliées** (cercles bleus) et **ennemies** (rouges)
3. ✅ **Sélection** par clic gauche sur une unité
4. ✅ Barre de vie affichée sur les unités
5. ✅ Les unités mortes sont supprimées automatiquement

## Pour lancer le jeu

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Contrôles

- **WASD** ou **Flèches** : Déplacer la caméra
- **Molette** : Zoom avant/arrière  
- **Clic gauche** : Sélectionner une unité alliée

## Prochaines étapes

- Étape 4 : Déplacement et pathfinding
- Étape 5 : Combat
- Étape 6 : Ressources et récolte
