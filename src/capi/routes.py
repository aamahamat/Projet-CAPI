from flask import Blueprint, current_app, jsonify, render_template, request

from .backlog import BacklogInvalide, charger_backlog
from .partie import ErreurPartie

bp = Blueprint("capi", __name__)


def _partie():
    return current_app.config["PARTIE"]


def _corps_json(exemple):
    donnees = request.get_json(silent=True)
    if not isinstance(donnees, dict):
        raise ErreurPartie(f"Corps JSON attendu : {exemple}")
    return donnees


@bp.errorhandler(ErreurPartie)
def erreur_partie(erreur):
    return jsonify(erreur=erreur.message), erreur.statut


@bp.get("/")
def accueil():
    return render_template("index.html")


@bp.get("/api/etat")
def etat():
    return jsonify(_partie().etat())


@bp.post("/api/joueurs")
def configurer_joueurs():
    """Saisie du nombre de joueurs et de leurs pseudos."""
    donnees = _corps_json('{"nombre": 3, "pseudos": ["Alice", "Bob", "Chloé"]}')
    _partie().configurer_joueurs(donnees.get("nombre"), donnees.get("pseudos"))
    return jsonify(message="Joueurs enregistrés."), 201


@bp.post("/api/backlog")
def charger():
    """US-04 : l'organisateur envoie un fichier JSON (champ « fichier »)."""
    fichier = request.files.get("fichier")
    if fichier is None or not fichier.filename:
        raise ErreurPartie("Aucun fichier reçu (champ « fichier »).")
    try:
        backlog = charger_backlog(fichier.read())
    except BacklogInvalide as exc:
        # CU-01 ext. 2a : message d'erreur, l'ancien backlog reste inchangé.
        raise ErreurPartie(str(exc)) from exc
    _partie().definir_backlog(backlog)
    return jsonify(
        message="Backlog chargé.", total=len(backlog["fonctionnalites"])
    ), 201


@bp.post("/api/vote")
def voter():
    """US-06 : un joueur choisit une carte pour la fonctionnalité courante."""
    donnees = _corps_json('{"joueur": "Alice", "carte": 5}')
    _partie().voter(donnees.get("joueur"), donnees.get("carte"))
    return jsonify(message="Vote enregistré."), 200


@bp.post("/api/revelation")
def reveler():
    """Révèle les votes une fois que tous les joueurs ont voté."""
    _partie().reveler()
    return jsonify(message="Votes révélés."), 200
