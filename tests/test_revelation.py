"""Révélation des votes (CU-02 étape 2)."""
import pytest

from conftest import BACKLOG_OK, configurer, envoyer_backlog


@pytest.fixture
def salle(client):
    envoyer_backlog(client, BACKLOG_OK)
    configurer(client, ["Alice", "Bob"])
    return client


def voter(client, joueur, carte):
    return client.post("/api/vote", json={"joueur": joueur, "carte": carte})


def test_revelation_refusee_tant_que_tous_n_ont_pas_vote(salle):
    voter(salle, "Alice", 5)
    rep = salle.post("/api/revelation")
    assert rep.status_code == 409
    assert "Bob" in rep.get_json()["erreur"]
    assert salle.get("/api/etat").get_json()["votes"] is None


def test_revelation_affiche_tous_les_votes(salle):
    voter(salle, "Bob", 8)
    voter(salle, "Alice", 5)
    assert salle.post("/api/revelation").status_code == 200
    etat = salle.get("/api/etat").get_json()
    assert etat["revele"] is True
    assert etat["votes"] == {"Alice": 5, "Bob": 8}


def test_revelation_est_repetable_sans_changer_les_votes(salle):
    voter(salle, "Alice", 5)
    voter(salle, "Bob", 5)
    salle.post("/api/revelation")
    assert salle.post("/api/revelation").status_code == 200
    assert salle.get("/api/etat").get_json()["votes"] == {"Alice": 5, "Bob": 5}


def test_revelation_plus_de_vote_possible_apres(salle):
    voter(salle, "Alice", 5)
    voter(salle, "Bob", 5)
    salle.post("/api/revelation")
    assert voter(salle, "Alice", 8).status_code == 409
    assert salle.get("/api/etat").get_json()["votes"]["Alice"] == 5


def test_revelation_sans_backlog(client):
    configurer(client, ["Alice", "Bob"])
    assert client.post("/api/revelation").status_code == 409


def test_revelation_sans_joueurs(client):
    envoyer_backlog(client, BACKLOG_OK)
    assert client.post("/api/revelation").status_code == 409
