# Mountain_Roy - Étape 2: Carte et Caméra

## Fichiers créis/modifiés pour l'Étape 2

### Nouveaux fichiers :
- `map/tile.py` - Classe Tile (types de tuiles)
- `map/game_map.py` - Génération et rendu de la carte 128x128
- `core/camera.py` - Système de caméra RTS

### Fichiers modifiés :
- `core/game.py` - Intégration caméra et carte

## Ce qui fonctionne maintenant

1. ✅ **Carte générée** avec herbe, forêts, eau, montagnes, chemins, mines d'or, arbres
2. ✅ **Caméra déplaçable** avec WASD ou flèches directionnelles
3. ✅ **Zoom** avec la molette de la souris (+/-)
4. ✅ Les ressources s'affichent toujours en haut

## Pour lancer le jeu

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Prochaines étapes

- Étape 3 : Unités et sélection
- Étape 4 : Déplacement et pathfinding
- Étape 5 : Combat