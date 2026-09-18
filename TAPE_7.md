# Mountain_Roy - Étape 7: Brouillard de Guerre

## Fichiers créis/modifiés pour l'Étape 7

### Nouveaux fichiers :
- `systems/fog_of_war.py` - Système de brouillard de guerre

### Fichiers modifiés :
- `core/game.py` - Intègre le brouillard de guerre

## Ce qui fonctionne maintenant

1. ✅ **Brouillard de guerre** - Zones jamais explorées (noir) et explorées mais invisibles (gris foncé)
2. ✅ **Vision dynamique** - Les unités et bâtiments révèlent la carte autour d'eux
3. ✅ **Entités cachées** - Les ennemis et ressources ne sont visibles que si proches
4. ✅ **Minimap mise à jour** - Affiche la carte explorée

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

## Prochaines étapes

- Étape 8 : IA ennemie
- Étape 9 : Sauvegarde/Chargement
- Étape 10 : Campagne et missions
