"""Configuration de la salle : nombre de joueurs et pseudos (CU-01 étape 1)."""
import pytest

from conftest import BACKLOG_OK, configurer, envoyer_backlog


def test_salle_joueurs_valides_sont_enregistres(client):
    assert configurer(client, ["Alice", "Bob", "Chloé"]).status_code == 201
    noms = [j["nom"] for j in client.get("/api/etat").get_json()["joueurs"]]
    assert noms == ["Alice", "Bob", "Chloé"]


def test_salle_les_pseudos_sont_nettoyes(client):
    configurer(client, ["  Alice  ", "Bob"])
    noms = [j["nom"] for j in client.get("/api/etat").get_json()["joueurs"]]
    assert noms == ["Alice", "Bob"]


@pytest.mark.parametrize("nombre", [0, 1, 11, -3])
def test_salle_nombre_hors_bornes(client, nombre):
    rep = client.post("/api/joueurs", json={"nombre": nombre, "pseudos": ["A"] * max(nombre, 0)})
    assert rep.status_code == 400


@pytest.mark.parametrize("nombre", ["3", 3.0, True, None])
def test_salle_nombre_de_mauvais_type(client, nombre):
    rep = client.post("/api/joueurs", json={"nombre": nombre, "pseudos": ["A", "B", "C"]})
    assert rep.status_code == 400


def test_salle_nombre_different_du_nombre_de_pseudos(client):
    rep = client.post("/api/joueurs", json={"nombre": 3, "pseudos": ["Alice", "Bob"]})
    assert rep.status_code == 400
    assert "3 pseudos" in rep.get_json()["erreur"]


@pytest.mark.parametrize("pseudos", [["Alice", ""], ["Alice", "   "], ["Alice", 7], ["Alice", None]])
def test_salle_pseudo_vide_ou_invalide(client, pseudos):
    assert configurer(client, pseudos).status_code == 400


def test_salle_pseudo_en_double_sans_tenir_compte_de_la_casse(client):
    rep = configurer(client, ["Alice", "alice"])
    assert rep.status_code == 400
    assert "deux fois" in rep.get_json()["erreur"]


def test_salle_pseudo_trop_long(client):
    assert configurer(client, ["A" * 31, "Bob"]).status_code == 400


def test_salle_pseudos_pas_une_liste(client):
    rep = client.post("/api/joueurs", json={"nombre": 2, "pseudos": "Alice,Bob"})
    assert rep.status_code == 400


def test_salle_corps_json_absent_ou_invalide(client):
    assert client.post("/api/joueurs", data="pas du json").status_code == 400
    assert client.post("/api/joueurs", json=[1, 2]).status_code == 400


def test_salle_reconfigurer_efface_les_votes_en_cours(client):
    envoyer_backlog(client, BACKLOG_OK)
    configurer(client, ["Alice", "Bob"])
    client.post("/api/vote", json={"joueur": "Alice", "carte": 5})
    configurer(client, ["Alice", "Bob", "Chloé"])
    joueurs = client.get("/api/etat").get_json()["joueurs"]
    assert not any(j["a_vote"] for j in joueurs)
