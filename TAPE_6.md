# Mountain_Roy - Étape 6: Interface Complète (HUD)

## Fichiers créis/modifiés pour l'Étape 6

### Nouveaux fichiers :
- `ui/hud.py` - Interface utilisateur (ressources, sélection, minimap, boutons)
- `ui/menus.py` - Menus (principal, pause, victoire, défaite)

### Fichiers modifiés :
- `core/game.py` - Intègre le HUD et les menus

## Ce qui fonctionne maintenant

1. ✅ **Menu principal** avec options
2. ✅ **Barre de ressources** en haut (Or, Bois, Nourriture, Population)
3. ✅ **Panneau de sélection** en bas (PV, Mana, Stats, Compétences)
4. ✅ **Minimap** dans le coin inférieur droit
5. ✅ **Boutons de production** (1, 2, 3 pour Warrior, Archer, Knight)
6. ✅ **Boutons de compétences** (Espace, Q, E, R pour le héros)
7. ✅ **Menu pause** (ESC)
8. ✅ **Écran victoire/défaite**

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

- Étape 7 : Brouillard de guerre
- Étape 8 : IA ennemie
- Étape 9 : Sauvegarde/Chargement
- Étape 10 : Campagne et missions
