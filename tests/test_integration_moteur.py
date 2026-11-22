"""Intégration du moteur de règles dans la boucle de vote, et cas limites du
moteur non couverts par tests/test_regles.py (que nous ne modifions pas)."""
import pytest

from capi import regles
from capi.regles import evaluer_vote
from conftest import BACKLOG_OK, configurer, envoyer_backlog


# --- Moteur seul -----------------------------------------------------------

def test_liste_de_votes_vide_est_refusee():
    with pytest.raises(ValueError):
        evaluer_vote([], "strict", 1)


def test_regle_inconnue_ou_tour_invalide():
    with pytest.raises(ValueError):
        evaluer_vote([5, 5], "inconnue", 1)
    for tour in (0, -1, True, "2"):
        with pytest.raises(ValueError):
            evaluer_vote([5, 5], "strict", tour)


def test_carte_inconnue_refusee():
    with pytest.raises(ValueError):
        evaluer_vote([5, "abc"], "strict", 2)


def test_premier_tour_unanimite_quelle_que_soit_la_regle():
    for nom in regles.REGLES:
        assert evaluer_vote([5, 5, 5], nom, 1).valeur_choisie == 5
        assert evaluer_vote([3, 8, 5], nom, 1).statut is False


def test_mediane_au_tour_2():
    resultat = evaluer_vote([3, 8, 5], "mediane", 2)
    assert (resultat.statut, resultat.valeur_choisie) == (True, 5)


def test_moyenne_arrondie_a_la_carte_la_plus_proche():
    # moyenne de 3, 8, 21 = 10.67 -> carte la plus proche : 8
    resultat = evaluer_vote([3, 8, 20], "moyenne", 2)
    assert (resultat.statut, resultat.valeur_choisie) == (True, 8)


def test_majorites():
    assert evaluer_vote([5, 5, 8], "majorite_absolue", 2).valeur_choisie == 5
    assert evaluer_vote([5, 8, 13], "majorite_absolue", 2).statut is False
    assert evaluer_vote([5, 5, 8, 13], "majorite_relative", 2).valeur_choisie == 5
    assert evaluer_vote([5, 5, 8, 8], "majorite_relative", 2).statut is False


def test_ajouter_une_regle_ne_modifie_pas_les_autres():
    avant = dict(regles.REGLES)

    @regles.regle("toujours_un")
    def toujours_un(votes):
        return 1

    try:
        assert evaluer_vote([3, 8], "toujours_un", 2).valeur_choisie == 1
        assert all(regles.REGLES[nom] is f for nom, f in avant.items())
    finally:
        del regles.REGLES["toujours_un"]


# --- Boucle de vote --------------------------------------------------------

@pytest.fixture
def salle(client):
    envoyer_backlog(client, BACKLOG_OK)
    configurer(client, ["Alice", "Bob"])
    return client


def jouer(client, cartes):
    for joueur, carte in zip(["Alice", "Bob"], cartes):
        assert client.post("/api/vote", json={"joueur": joueur, "carte": carte}).status_code == 200
    assert client.post("/api/revelation").status_code == 200
    return client.get("/api/etat").get_json()


def test_unanimite_valide_et_enregistre_la_difficulte(salle):
    etat = jouer(salle, [5, 5])
    assert etat["resultat"]["valide"] is True
    assert etat["resultat"]["valeur"] == 5
    assert etat["fonctionnalite"]["difficulte"] == 5


def test_desaccord_au_tour_1_lance_un_nouveau_tour(salle):
    etat = jouer(salle, [3, 8])
    assert etat["resultat"]["valide"] is False
    assert etat["fonctionnalite"]["difficulte"] is None
    assert salle.post("/api/suite").status_code == 200
    etat = salle.get("/api/etat").get_json()
    assert etat["tour"] == 2 and etat["revele"] is False and etat["numero"] == 1
    assert not any(j["a_vote"] for j in etat["joueurs"])


def test_tour_2_applique_la_regle_choisie(salle):
    assert salle.post("/api/regle", json={"regle": "moyenne"}).status_code == 200
    jouer(salle, [3, 8])
    salle.post("/api/suite")
    etat = jouer(salle, [3, 13])  # moyenne 8
    assert etat["resultat"] == {"valide": True, "valeur": 8, "motif": etat["resultat"]["motif"]}


def test_carte_speciale_force_un_nouveau_tour(salle):
    jouer(salle, [5, 5])  # fonctionnalité 1 validée
    salle.post("/api/suite")
    etat = jouer(salle, ["?", "?"])
    assert etat["resultat"]["valide"] is False


def test_validation_passe_a_la_fonctionnalite_suivante_puis_termine(salle):
    jouer(salle, [5, 5])
    salle.post("/api/suite")
    etat = salle.get("/api/etat").get_json()
    assert etat["numero"] == 2 and etat["tour"] == 1
    jouer(salle, [8, 8])
    salle.post("/api/suite")
    etat = salle.get("/api/etat").get_json()
    assert etat["terminee"] is True
    assert salle.post("/api/vote", json={"joueur": "Alice", "carte": 5}).status_code == 409


def test_suite_avant_revelation_refusee(salle):
    assert salle.post("/api/suite").status_code == 409


def test_regle_inconnue_refusee_par_l_api(salle):
    assert salle.post("/api/regle", json={"regle": "magique"}).status_code == 400
