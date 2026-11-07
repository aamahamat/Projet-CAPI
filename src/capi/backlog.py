"""Chargement et validation du backlog au format JSON (US-04).

Format attendu (voir README) :

    {
      "projet": "Bibliothèque en ligne",          (facultatif)
      "fonctionnalites": [
        {"id": "F1", "titre": "Rechercher un livre par titre"}
      ]
    }

Par fonctionnalité :
  - "titre"      : texte non vide (obligatoire)
  - "id"         : texte non vide, unique (facultatif ; "F1", "F2"... par défaut)
  - "difficulte" : null ou un nombre (facultatif ; servira à l'export final)
"""
import json


class BacklogInvalide(ValueError):
    """Le backlog fourni ne respecte pas le format attendu (CU-01, extension 2a)."""


def charger_backlog(contenu):
    """Valide le contenu JSON (bytes ou str) et renvoie le backlog normalisé.

    Renvoie {"projet": str | None, "fonctionnalites": [{"id", "titre", "difficulte"}]}.
    Lève BacklogInvalide avec un message lisible si le format est incorrect.
    """
    try:
        if isinstance(contenu, bytes):
            contenu = contenu.decode("utf-8")
        donnees = json.loads(contenu)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BacklogInvalide("Le fichier n'est pas un JSON valide (UTF-8).") from exc

    if not isinstance(donnees, dict):
        raise BacklogInvalide(
            "Le backlog doit être un objet JSON avec une clé « fonctionnalites »."
        )

    projet = donnees.get("projet")
    if projet is not None and (not isinstance(projet, str) or not projet.strip()):
        raise BacklogInvalide("« projet » doit être un texte non vide.")

    liste = donnees.get("fonctionnalites")
    if not isinstance(liste, list) or not liste:
        raise BacklogInvalide("« fonctionnalites » doit être une liste non vide.")

    fonctionnalites = []
    identifiants = set()
    for numero, element in enumerate(liste, start=1):
        if not isinstance(element, dict):
            raise BacklogInvalide(
                f"Fonctionnalité {numero} : un objet JSON est attendu."
            )

        titre = element.get("titre")
        if not isinstance(titre, str) or not titre.strip():
            raise BacklogInvalide(
                f"Fonctionnalité {numero} : le champ « titre » est obligatoire."
            )

        identifiant = element.get("id", f"F{numero}")
        if not isinstance(identifiant, str) or not identifiant.strip():
            raise BacklogInvalide(
                f"Fonctionnalité {numero} : « id » doit être un texte non vide."
            )
        identifiant = identifiant.strip()
        if identifiant in identifiants:
            raise BacklogInvalide(
                f"Fonctionnalité {numero} : l'id « {identifiant} » est déjà utilisé."
            )
        identifiants.add(identifiant)

        difficulte = element.get("difficulte")
        if difficulte is not None and (
            isinstance(difficulte, bool) or not isinstance(difficulte, (int, float))
        ):
            raise BacklogInvalide(
                f"Fonctionnalité {numero} : « difficulte » doit être null ou un nombre."
            )

        fonctionnalites.append(
            {"id": identifiant, "titre": titre.strip(), "difficulte": difficulte}
        )

    return {
        "projet": projet.strip() if projet else None,
        "fonctionnalites": fonctionnalites,
    }
