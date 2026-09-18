# Mountain_Roy - Étape 5: Ressources et Récolte

## Fichiers créis/modifiés pour l'Étape 5

### Nouveaux fichiers :
- `systems/economy.py` - Système de ressources (or, bois, nourriture)
- `systems/construction.py` - Construction de bâtiments et production d'unités

### Fichiers modifiés :
- `core/game.py` - Intègre le système de ressources et récolte

## Ce qui fonctionne maintenant

1. ✅ **Ressources affichées** : Or, Bois, Nourriture, Population
2. ✅ **Noeuds de ressources** visibles (cercles jaunes = or, marron = bois)
3. ✅ **Clic droit sur une ressource** pour récolter
4. ✅ Les unités se déplacent vers les ressources et les récoltent
5. ✅ **Production d'unités** avec touches 1, 2, 3 (Warrior, Archer, Knight)

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

## Prochaines étapes

- Étape 6 : Interface complète (HUD)
- Étape 7 : Brouillard de guerre
- Étape 8 : IA ennemie
- Étape 9 : Sauvegarde/Chargement
- Étape 10 : Campagne et missions
