"""US-06 : choisir une carte de vote sans voir celles des autres (CU-02 étape 1)."""
import pytest

from conftest import BACKLOG_OK, configurer, envoyer_backlog


@pytest.fixture
def salle(client):
    """Backlog chargé et deux joueurs configurés."""
    envoyer_backlog(client, BACKLOG_OK)
    configurer(client, ["Alice", "Bob"])
    return client


def voter(client, joueur, carte):
    return client.post("/api/vote", json={"joueur": joueur, "carte": carte})


def test_us06_vote_valide_est_enregistre(salle):
    assert voter(salle, "Alice", 5).status_code == 200
    joueurs = {j["nom"]: j["a_vote"] for j in salle.get("/api/etat").get_json()["joueurs"]}
    assert joueurs == {"Alice": True, "Bob": False}


def test_us06_la_valeur_du_vote_reste_cachee_avant_revelation(salle):
    """CU-02 ext. 1a : les votes ne sont pas visibles avant la révélation."""
    voter(salle, "Alice", 13)
    etat = salle.get("/api/etat").get_json()
    # Seules les clés « nom » et « a_vote » sont exposées : jamais la carte.
    assert set(etat["joueurs"][0]) == {"nom", "a_vote"}
    assert etat["votes"] is None
    assert etat["revele"] is False


def test_us06_un_joueur_peut_changer_sa_carte_avant_revelation(salle):
    voter(salle, "Alice", 3)
    assert voter(salle, "Alice", 8).status_code == 200


@pytest.mark.parametrize("carte", [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "?", "cafe"])
def test_us06_toutes_les_cartes_du_jeu_sont_acceptees(salle, carte):
    assert voter(salle, "Alice", carte).status_code == 200


@pytest.mark.parametrize("carte", [4, -1, "5", "abc", None, True, 5.0, [5], {"a": 1}])
def test_us06_carte_hors_jeu_refusee(salle, carte):
    rep = voter(salle, "Alice", carte)
    assert rep.status_code == 400
    assert rep.get_json()["erreur"] == "Carte invalide."


def test_us06_joueur_inconnu(salle):
    assert voter(salle, "Zoe", 5).status_code == 404


def test_us06_vote_sans_backlog_charge(client):
    configurer(client, ["Alice", "Bob"])
    assert voter(client, "Alice", 5).status_code == 409


def test_us06_corps_json_absent_ou_invalide(salle):
    assert salle.post("/api/vote", data="pas du json").status_code == 400
    assert salle.post("/api/vote", json=[1, 2]).status_code == 400


def test_us06_le_jeu_de_cartes_est_expose(salle):
    cartes = salle.get("/api/etat").get_json()["cartes"]
    assert 5 in cartes and "cafe" in cartes


def test_us06_nouveau_backlog_efface_les_votes_en_cours(salle):
    voter(salle, "Alice", 5)
    envoyer_backlog(salle, BACKLOG_OK)
    joueurs = salle.get("/api/etat").get_json()["joueurs"]
    assert not any(j["a_vote"] for j in joueurs)
