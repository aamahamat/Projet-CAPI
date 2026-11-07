import io
import json

import pytest

from capi import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def envoyer_backlog(client, contenu, nom="backlog.json"):
    """Envoie `contenu` (str, bytes ou objet Python) comme fichier JSON."""
    if not isinstance(contenu, (str, bytes)):
        contenu = json.dumps(contenu)
    if isinstance(contenu, str):
        contenu = contenu.encode("utf-8")
    return client.post(
        "/api/backlog",
        data={"fichier": (io.BytesIO(contenu), nom)},
        content_type="multipart/form-data",
    )


def configurer(client, pseudos):
    return client.post(
        "/api/joueurs", json={"nombre": len(pseudos), "pseudos": pseudos}
    )


BACKLOG_OK = {
    "projet": "Bibliothèque en ligne",
    "fonctionnalites": [
        {"id": "F1", "titre": "Rechercher un livre par titre"},
        {"id": "F2", "titre": "Emprunter un livre disponible"},
    ],
}
