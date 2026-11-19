"""| 1 | mediane | 1 | 3, 8, 5 | revote | - | CA-02.1 |
| 2 | strict | 1 | 8, 8, 8 | validé | 3 | CA-03.1 |
| 3 | strict | 1 | 8, 8, 5|  revote | - | CA-01.1 |
| 5 | mediane  | 2 | 21, 8, ? | revote | - | CA-02.1 |
| 6 | strict | 2 | 8, 8, ? | revote | - | CA-03.1 |
| 8 | strict | 2 | ?, ?, 13 | revote | - | CA-01.1 |"""
from capi.regles import evaluer_vote

class Resultat:
    statut: bool
    valeur_choisie: int 


def test_CA_02_1_mediane_diff_val():
    votes = []
    vote_commun=0
    regle ="mediane"
    tour=1
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is False
    print("revoter")
    assert resultat.valeur_choisie is None


def test_CA_03_1_strict_equal_val():
    votes = []
    vote_commun=3
    regle ="strict"
    tour=1
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is True
    print("valider")
    assert resultat.valeur_choisie == 8

def test_CA_01_1_strict_diff_val():
    votes = []
    vote_commun=2
    regle ="mediane"
    tour=1
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is False
    print(f"revoter et choisir au prochain tour, les cartes des {vote_commun} votes communs")
    assert resultat.valeur_choisie is None

#car on a un vote identique en majorité donc ignorer le vote insignifiant de la carte "?" 
# et considerer l'unanimité sur les votes identiques au prochain vote
def test_CA_02_1_mediane_interrogation_val():
    votes = []
    vote_commun=0 
    carte_interro="?"
    regle ="mediane"
    tour=2
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is False
    print(f"revoter en remettant en cause la carte ({carte_interro})")
    assert resultat.valeur_choisie is None

#car les votes ne semblent pas etre proches et divergent tous donc appliquer 
# la moyenne et arrondir le resultat pour avoir la carte du vote.
def test_CA_03_1_strict_interrogation_equal_val():
    votes = []
    vote_commun=2
    carte_interro="?"
    regle ="strict"
    tour=2
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is False
    print(f"revoter en ignorant la carte ({carte_interro}) et choisir au prochain tour, les cartes des {vote_commun} votes communs ")
    assert resultat.valeur_choisie is None

#ce cas compte car les votes majoritaires sont des cartes "?", 
# donc la fonctionnalité semble etre difficile a estimer et pourrai prendre plus de temps. 
def test_CA_01_1_strict_two_interrogation_val():
    votes = []
    vote_commun=2
    carte_interro="?"
    regle ="strict"
    tour=2
    resultat = evaluer_vote(votes,regle,tour)
    assert resultat.statut is False
    print(f"revoter! mais estimation difficile passer au prochain ")
    assert resultat.valeur_choisie is None
