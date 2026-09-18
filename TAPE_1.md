# Mountain_Roy - Étape 1: Moteur et fenêtre

## Fichiers créés

### `settings.py`
Configuration globale du jeu : dimensions de l'écran, FPS, couleurs, noms des factions.

### `core/game.py`
Classe principale `Game` avec :
- Initialisation Pygame
- Boucle de jeu (60 FPS)
- Gestion des événements (quitter avec ESC)
- Mise à jour et rendu
- Affichage des ressources (Or, Bois, Nourriture)

### `main.py`
Point d'entrée pour lancer le jeu.

## Comment lancer

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Ce qui fonctionne maintenant

1. ✅ Fenêtre de jeu (1024x768)
2. ✅ Boucle de jeu à 60 FPS
3. ✅ Fond vert (herbe)
4. ✅ Affichage des ressources en haut
5. ✅ Quitter avec ESC ou croix

## Prochaines étapes

- Étape 2 : Carte et caméra
- Étape 3 : Unités et sélection
- Étape 4 : Déplacement et pathfinding
