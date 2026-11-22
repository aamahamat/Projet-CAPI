"""Moteur de règles de validation des votes (aucune dépendance à Flask).

Point d'entrée : evaluer_vote(votes, regle, tour) -> ResultatVote.

Principes :
  - Au tour 1, quelle que soit la règle, on exige l'unanimité.
  - À partir du tour 2, on applique la règle choisie.
  - Une carte spéciale ("?", "cafe") empêche toujours la validation :
    on revote.
  - Ajouter une règle = écrire une fonction décorée par @regle("nom").
    Aucune règle existante, ni evaluer_vote, n'est à modifier.
"""
from collections import Counter
from dataclasses import dataclass
from statistics import mean, median

# Cartes qui portent une valeur d'effort. Source unique : partie.py s'en sert.
CARTES_NUMERIQUES = (0, 1, 2, 3, 5, 8, 13, 20, 40, 100)
CARTES_SPECIALES = ("?", "cafe")


@dataclass(frozen=True)
class ResultatVote:
    statut: bool          # True : fonctionnalité validée ; False : on revote
    valeur_choisie: object  # la carte retenue si validée, sinon None
    motif: str            # explication courte, affichée aux joueurs


# nom de la règle -> fonction(votes_numeriques) -> valeur retenue ou None
REGLES = {}


def regle(nom):
    """Décorateur : enregistre une règle sous `nom`."""
    def enregistrer(fonction):
        REGLES[nom] = fonction
        return fonction
    return enregistrer


def _carte_la_plus_proche(valeur):
    """Arrondit à la carte numérique la plus proche (à égalité : la plus haute)."""
    return min(CARTES_NUMERIQUES, key=lambda carte: (abs(carte - valeur), -carte))


def _unanimite(votes):
    return votes[0] if len(set(votes)) == 1 else None


@regle("strict")
def regle_stricte(votes):
    return _unanimite(votes)


@regle("mediane")
def regle_mediane(votes):
    return _carte_la_plus_proche(median(votes))


@regle("moyenne")
def regle_moyenne(votes):
    return _carte_la_plus_proche(mean(votes))


@regle("majorite_absolue")
def regle_majorite_absolue(votes):
    valeur, nombre = Counter(votes).most_common(1)[0]
    return valeur if nombre > len(votes) / 2 else None


@regle("majorite_relative")
def regle_majorite_relative(votes):
    classement = Counter(votes).most_common(2)
    if len(classement) == 2 and classement[0][1] == classement[1][1]:
        return None  # égalité en tête : pas de gagnant
    return classement[0][0]


def evaluer_vote(votes, nom_regle, tour):
    """Décide si la fonctionnalité est validée ou si l'on revote.

    Lève ValueError si la liste est vide, si la règle est inconnue, si le tour
    est invalide ou si une carte est inconnue.
    """
    if not votes:
        raise ValueError("Aucun vote à évaluer.")
    if nom_regle not in REGLES:
        raise ValueError(f"Règle inconnue : « {nom_regle} ».")
    if isinstance(tour, bool) or not isinstance(tour, int) or tour < 1:
        raise ValueError("Le tour doit être un entier supérieur ou égal à 1.")

    for vote in votes:
        est_nombre = isinstance(vote, (int, float)) and not isinstance(vote, bool)
        if not est_nombre and vote not in CARTES_SPECIALES:
            raise ValueError(f"Carte inconnue : {vote!r}.")

    if any(vote in CARTES_SPECIALES for vote in votes if isinstance(vote, str)):
        return ResultatVote(False, None, "Carte spéciale jouée : on revote.")

    if tour == 1:
        valeur = _unanimite(votes)
        if valeur is None:
            return ResultatVote(False, None, "Pas d'unanimité au premier tour : discussion et revote.")
        return ResultatVote(True, valeur, "Unanimité au premier tour.")

    valeur = REGLES[nom_regle](votes)
    if valeur is None:
        return ResultatVote(False, None, f"La règle « {nom_regle} » ne départage pas : on revote.")
    return ResultatVote(True, valeur, f"Validé par la règle « {nom_regle} ».")
