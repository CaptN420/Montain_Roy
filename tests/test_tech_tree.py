"""Tests pour le système de recherche technologique (priorité #1).

Avant corrections, plusieurs bugs documentés:
1. Le coût n'est jamais débité (les ressources ne changent pas au lancement).
2. `all_technologies` est une variable de classe partagée entre instances.
3. Une tech finie reste dans current_research et est re-ajoutée à chaque frame (doublons).
4. `start_research(None)` autorise implicitement 9999 ressources.
5. Sauvegarde/restauration incomplète.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from systems.tech_tree import TechTree, Technology, TechRequirement


class FakeResources:
    """Ressources provisionnées pour simuler l'économie."""

    def __init__(self, gold=1000, wood=1000, food=1000):
        self.gold = gold
        self.wood = wood
        self.food = food
        self.spent = {}  # trace des paiments

    def can_afford(self, cost):
        return (self.gold >= cost.get("gold", 0) and
                self.wood >= cost.get("wood", 0) and
                self.food >= cost.get("food", 0))

    def pay_cost(self, cost):
        self.started_at = (self.gold, self.wood, self.food)
        self.gold -= cost.get("gold", 0)
        self.wood -= cost.get("wood", 0)
        self.food -= cost.get("food", 0)
        self.spent["cost"] = dict(cost)
        self.spent["before"] = self.started_at
        self.spent["after"] = (self.gold, self.wood, self.food)

    def snapshot(self):
        return {
            "gold": self.gold, "wood": self.wood, "food": self.food,
            "payments": list(self.spent.values())
        }


def test_technologies_sont_des_instances_pas_partagees():
    """Deux TechTree distincts ne doivent pas partager l'état des technologies."""
    t1 = TechTree()
    t2 = TechTree()
    # Rechercher dans t1 ne doit pas affecter t2
    t1.get_technology("iron_working").researched = True
    assert t2.get_technology("iron_working").researched is False, \
        "L'état d'une technologie doit être propre à chaque instance"


def test_start_research_debite_le_cout_exactement_une_fois():
    """Lancer une recherche doit débiter le coût exactement une fois."""
    tree = TechTree()
    resources = FakeResources()
    tech = tree.get_technology("iron_working")  # 150 or, 0 bois, 0 nourriture
    assert resources.gold == 1000

    ok = tree.start_research("iron_working", resources)

    assert ok
    assert resources.gold == 1000 - tech.cost["gold"], \
        "Le coût doit être débité au lancement"


def test_start_research_sans_ressources_est_refuse():
    """start_research() sans ressources doit être refusé, pas 9999 gratuits."""
    tree = TechTree()
    # appeler sans l'argument resources (positionnel) -> doit être refusé
    assert tree.start_research("iron_working") is False


def test_tech_terminee_ne_reste_pas_active():
    """Après complétion, une tech ne doit pas être re-déverrouillée chaque frame."""
    tree = TechTree()
    resources = FakeResources()
    tree.start_research("iron_working", resources)  # débite 150 or
    tech = tree.get_technology("iron_working")

    # Simuler complétion
    tech.research_progress = tech.research_time
    calls = 0
    for _ in range(5):
        tree.update(0.1)
        calls += 1

    # La tech doit apparaître UNE SEULE fois dans unlocked_techs
    count = tree.unlocked_techs.count("iron_working")
    assert count == 1, f"expected 1 occurrence, got {count}"
    # La recherche active doit être vidée
    assert tree.current_research is None, "la recherche active doit être vidée"


def test_to_dict_from_dict_conserve_etat():
    """Sérialisation/restauration doit conserver recherches et progression."""
    tree = TechTree()
    resources = FakeResources()
    tree.start_research("iron_working", resources)
    # progression partielle
    tree.update(5.0)  # ~5s sur 30

    data = tree.to_dict()
    assert data["current_research"] == "iron_working"

    restored = TechTree.from_dict(data)
    assert restored.get_technology("iron_working").research_progress == pytest.approx(5.0, abs=0.6), \
        "la progression doit être restaurée"
    assert restored.current_research is not None, "la recherche en cours doit être restaurée"


def test_technologie_recherchee_restauree():
    """Une tech marquée recherchée doit être restaurée comme déverrouillée."""
    tree = TechTree()
    tech = tree.get_technology("mining")
    tech.researched = True
    tree.unlocked_techs.append("mining")

    data = tree.to_dict()
    restored = TechTree.from_dict(data)
    assert "mining" in restored.unlocked_techs
    assert restored.get_technology("mining").researched is True