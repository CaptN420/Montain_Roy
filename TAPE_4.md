# Mountain_Roy - Étape 4: Déplacement et Pathfinding

## Fichiers créis/modifiés pour l'Étape 4

### Nouveaux fichiers :
- `systems/pathfinding.py` - Algorithme A* pour le pathfinding
- `systems/movement.py` - Système de mouvement des unités
- `systems/combat.py` - Logique de combat

### Fichiers modifiés :
- `core/game.py` - Intègre les systèmes de mouvement et combat

## Ce qui fonctionne maintenant

1. ✅ **Clic droit** pour déplacer une unité sélectionnée
2. ✅ **Clic droit sur un ennemi** pour attaquer
3. ✅ Les unités se déplacent vers leur cible
4. ✅ Combat automatique quand l'ennemi est à portée
5. ✅ Les unités cherchent des cibles automatiquement

## Pour lancer le jeu

```bash
cd C:\Users\celes\Documents\Hermes-Workspace\Mountain_Roy
python main.py
```

## Contrôles

- **WASD** ou **Flèches** : Déplacer la caméra
- **Molette** : Zoom avant/arrière
- **Clic gauche** : Sélectionner une unité alliée
- **Clic droit** : Déplacer l'unité ou attaquer un ennemi

## Prochaines étapes

- Étape 5 : Système de ressources et récolte
- Étape 6 : Construction de bâtiments
- Étape 7 : Production d'unités
- Étape 8 : Interface complète
- Étape 9 : Brouillard de guerre
- Étape 10 : IA ennemie
