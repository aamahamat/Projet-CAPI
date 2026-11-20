"""Moteur de règles de validation d'une fonctionnalité (séance 2).

Logique pure : aucune dépendance à Flask, donc testable sans lancer l'interface.

Principe (énoncé, fonctionnalité 5) :
- au tour 1, toutes les règles se jouent à l'unanimité ;
- à partir du tour 2, la règle choisie s'applique.

"""
from dataclasses import dataclass
from typing import Optional, Sequence, Union

from .partie import CARTES

STRICT = "strict"
MEDIANE = "mediane"
MOYENNE = "moyenne"
REGLES = (STRICT, MEDIANE, MOYENNE)

# Cartes numériques du jeu : celles de partie.CARTES, sans "?" ni "cafe".
CARTES_NUMERIQUES = tuple(c for c in CARTES if isinstance(c, int))

Carte = Union[int, str]


@dataclass(frozen=True)
class Resultat:
    #Réponse du moteur pour un tour de vote.

    statut: bool  # True = fonctionnalité validée, False = revote
    valeur_choisie: Optional[int] = None  # carte retenue si validée, sinon None


_REVOTE = Resultat(statut=False)


def evaluer_vote(votes: Sequence[Carte], regle: str, tour: int) -> Resultat:
    """Applique la règle aux votes révélés d'un tour.

    Args:
        votes: une carte par joueur (entier, ou "?" / "cafe").
        regle: "strict", "mediane" ou "moyenne".
        tour:  numéro du tour pour cette fonctionnalité, à partir de 1.

    Returns:
        Resultat(True, carte) si validé, Resultat(False) pour un revote.

    Raises:
        ValueError: liste de votes vide, tour < 1 ou règle inconnue.
    """
    if not votes:
        raise ValueError("Aucun vote à évaluer.")
    if tour < 1:
        raise ValueError("Le numéro de tour commence à 1.")
    if regle not in REGLES:
        raise ValueError(f"Règle inconnue : {regle!r}.")

    # DÉCISION : une carte non numérique ("?", "cafe") empêche toute validation,
    # quelle que soit la règle ou le tour : on revote.
    if any(not isinstance(vote, int) for vote in votes):
        return _REVOTE

    # Tour 1, ou règle stricte : unanimité obligatoire.
    if tour == 1 or regle == STRICT:
        return _unanimite(votes)

    if regle == MEDIANE:
        return _valider(_mediane(votes))
    return _valider(sum(votes) / len(votes))


def _unanimite(votes: Sequence[int]) -> Resultat:
    #Validé seulement si tous les votes sont identiques.
    if len(set(votes)) == 1:
        return Resultat(statut=True, valeur_choisie=votes[0])
    return _REVOTE


def _mediane(votes: Sequence[int]) -> float:
    #Valeur centrale ; pour un nombre pair de votes, moyenne des deux du milieu.
    tries = sorted(votes)
    milieu = len(tries) // 2
    if len(tries) % 2 == 1:
        return tries[milieu]
    return (tries[milieu - 1] + tries[milieu]) / 2


def _valider(valeur: float) -> Resultat:
    """Valide en ramenant la valeur calculée à une carte du jeu.

    DÉCISION : carte la plus proche ; à égale distance de deux cartes, on prend
    la plus haute (choix prudent). Remplacer `-carte` par `carte` pour la plus basse.
    """
    carte = min(CARTES_NUMERIQUES, key=lambda c: (abs(c - valeur), -c))
    return Resultat(statut=True, valeur_choisie=carte)
