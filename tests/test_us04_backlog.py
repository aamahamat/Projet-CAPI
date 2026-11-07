"""US-04 : charger le backlog au format JSON (CU-01 étape 2 et extension 2a)."""
from conftest import BACKLOG_OK, envoyer_backlog


def test_us04_backlog_valide_est_charge(client):
    rep = envoyer_backlog(client, BACKLOG_OK)
    assert rep.status_code == 201
    assert rep.get_json()["total"] == 2


def test_us04_la_premiere_fonctionnalite_est_affichee(client):
    envoyer_backlog(client, BACKLOG_OK)
    etat = client.get("/api/etat").get_json()
    assert etat["projet"] == "Bibliothèque en ligne"
    assert etat["numero"] == 1
    assert etat["total"] == 2
    assert etat["fonctionnalite"]["id"] == "F1"
    assert etat["fonctionnalite"]["titre"] == "Rechercher un livre par titre"


def test_us04_projet_et_id_sont_facultatifs(client):
    rep = envoyer_backlog(client, {"fonctionnalites": [{"titre": "A"}, {"titre": "B"}]})
    assert rep.status_code == 201
    etat = client.get("/api/etat").get_json()
    assert etat["projet"] is None
    assert etat["fonctionnalite"]["id"] == "F1"


def test_us04_difficulte_deja_renseignee_est_acceptee(client):
    rep = envoyer_backlog(client, {"fonctionnalites": [{"titre": "A", "difficulte": 5}]})
    assert rep.status_code == 201


def test_us04_json_syntaxiquement_invalide(client):
    rep = envoyer_backlog(client, "{ pas du json")
    assert rep.status_code == 400
    assert "JSON" in rep.get_json()["erreur"]


def test_us04_fichier_non_utf8(client):
    assert envoyer_backlog(client, b"\xff\xfe\x00").status_code == 400


def test_us04_racine_pas_un_objet(client):
    assert envoyer_backlog(client, [{"titre": "A"}]).status_code == 400


def test_us04_fonctionnalites_absentes_vides_ou_mal_typees(client):
    for contenu in ({}, {"fonctionnalites": []}, {"fonctionnalites": "F1"}):
        assert envoyer_backlog(client, contenu).status_code == 400, contenu


def test_us04_projet_de_mauvais_type(client):
    for projet in ("", "  ", 5):
        contenu = {"projet": projet, "fonctionnalites": [{"titre": "A"}]}
        assert envoyer_backlog(client, contenu).status_code == 400, projet


def test_us04_element_pas_un_objet(client):
    rep = envoyer_backlog(client, {"fonctionnalites": ["Rechercher"]})
    assert rep.status_code == 400
    assert "Fonctionnalité 1" in rep.get_json()["erreur"]


def test_us04_titre_manquant_ou_vide(client):
    for element in ({"id": "F1"}, {"titre": "   "}, {"titre": 3}):
        rep = envoyer_backlog(client, {"fonctionnalites": [element]})
        assert rep.status_code == 400, element


def test_us04_id_invalide_ou_en_double(client):
    for ids in ([{"titre": "A", "id": ""}], [{"titre": "A", "id": 1}],
                [{"titre": "A", "id": "F1"}, {"titre": "B", "id": "F1"}]):
        assert envoyer_backlog(client, {"fonctionnalites": ids}).status_code == 400, ids


def test_us04_difficulte_de_mauvais_type(client):
    for valeur in ("difficile", True, [1]):
        contenu = {"fonctionnalites": [{"titre": "A", "difficulte": valeur}]}
        assert envoyer_backlog(client, contenu).status_code == 400, valeur


def test_us04_aucun_fichier_envoye(client):
    rep = client.post("/api/backlog", data={}, content_type="multipart/form-data")
    assert rep.status_code == 400


def test_us04_backlog_invalide_ne_remplace_pas_le_precedent(client):
    """CU-01 2a2 : après une erreur, on peut reprendre sans perdre l'état."""
    envoyer_backlog(client, BACKLOG_OK)
    envoyer_backlog(client, "pas du json")
    assert client.get("/api/etat").get_json()["total"] == 2


def test_us04_fichier_trop_gros(client):
    gros = b'{"fonctionnalites": [' + b'{"titre": "x"},' * 100000 + b'{"titre": "x"}]}'
    assert envoyer_backlog(client, gros).status_code == 413
