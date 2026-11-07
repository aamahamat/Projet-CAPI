from flask import Flask, jsonify

from .partie import Partie
from .routes import bp


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # backlog JSON : 1 Mo max
    app.config["PARTIE"] = Partie()
    app.register_blueprint(bp)

    @app.errorhandler(413)
    def trop_gros(_erreur):
        return jsonify(erreur="Fichier trop volumineux (1 Mo maximum)."), 413

    return app
