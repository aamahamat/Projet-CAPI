"""Moteur de la partie de planning poker (aucune dépendance à Flask).

Une seule salle, gardée en mémoire. Ce module doit rester testable sans
lancer l'interface (le moteur de règles de la séance 2 viendra ici).
"""

# Jeu de cartes (constante modifiable). "?" = je ne sais pas, "cafe" = pause.
CARTES = (0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "?", "cafe")

MIN_JOUEURS = 2
MAX_JOUEURS = 10
LONGUEUR_MAX_PSEUDO = 30


class ErreurPartie(Exception):
    """Erreur métier ; `statut` est le code HTTP à renvoyer."""

    def __init__(self, message, statut=400):
        super().__init__(message)
        self.message = message
        self.statut = statut


class Partie:
    def __init__(self):
        self.projet = None
        self.fonctionnalites = []
        self.index_courant = 0
        self.joueurs = []
        self.votes = {}  # pseudo -> carte (cachée jusqu'à la révélation)
        self.revele = False

    # --- Joueurs (CU-01 étape 1 : configuration de la salle) ---------
    def configurer_joueurs(self, nombre, pseudos):
        """Définit les joueurs. Remet à zéro les votes en cours."""
        if isinstance(nombre, bool) or not isinstance(nombre, int):
            raise ErreurPartie("Le nombre de joueurs doit être un entier.")
        if not MIN_JOUEURS <= nombre <= MAX_JOUEURS:
            raise ErreurPartie(
                f"Le nombre de joueurs doit être compris entre {MIN_JOUEURS} et {MAX_JOUEURS}."
            )
        if not isinstance(pseudos, list) or len(pseudos) != nombre:
            raise ErreurPartie(f"Il faut exactement {nombre} pseudos.")

        propres = []
        vus = set()
        for numero, pseudo in enumerate(pseudos, start=1):
            if not isinstance(pseudo, str) or not pseudo.strip():
                raise ErreurPartie(f"Joueur {numero} : le pseudo est obligatoire.")
            pseudo = pseudo.strip()
            if len(pseudo) > LONGUEUR_MAX_PSEUDO:
                raise ErreurPartie(
                    f"Joueur {numero} : {LONGUEUR_MAX_PSEUDO} caractères maximum."
                )
            if pseudo.casefold() in vus:
                raise ErreurPartie(f"Le pseudo « {pseudo} » est utilisé deux fois.")
            vus.add(pseudo.casefold())
            propres.append(pseudo)

        self.joueurs = propres
        self._reinitialiser_votes()

    # --- US-04 : backlog ---------------------------------------------
    def definir_backlog(self, backlog):
        """Reçoit un backlog déjà validé (voir backlog.charger_backlog)."""
        self.projet = backlog["projet"]
        self.fonctionnalites = backlog["fonctionnalites"]
        self.index_courant = 0
        self._reinitialiser_votes()

    def fonctionnalite_courante(self):
        if not self.fonctionnalites:
            return None
        return self.fonctionnalites[self.index_courant]

    # --- US-06 : vote caché ------------------------------------------
    def voter(self, joueur, carte):
        """Enregistre (ou remplace) le vote caché d'un joueur."""
        if self.fonctionnalite_courante() is None:
            raise ErreurPartie("Aucun backlog chargé : impossible de voter.", 409)
        if joueur not in self.joueurs:
            raise ErreurPartie(f"Joueur inconnu : « {joueur} ».", 404)
        if self.revele:
            raise ErreurPartie("Les votes sont déjà révélés.", 409)
        # bool est un sous-type de int en Python : True == 1, on le refuse.
        if isinstance(carte, bool) or not isinstance(carte, (int, str)) or carte not in CARTES:
            raise ErreurPartie("Carte invalide.")
        self.votes[joueur] = carte

    # --- CU-02 étape 2 : révélation ----------------------------------
    def reveler(self):
        """Révèle les votes ; exige que tous les joueurs aient voté."""
        if self.fonctionnalite_courante() is None:
            raise ErreurPartie("Aucun backlog chargé.", 409)
        if not self.joueurs:
            raise ErreurPartie("Aucun joueur configuré.", 409)
        manquants = [nom for nom in self.joueurs if nom not in self.votes]
        if manquants:
            raise ErreurPartie(
                "En attente du vote de : " + ", ".join(manquants) + ".", 409
            )
        self.revele = True

    # --- Vue publique ------------------------------------------------
    def etat(self):
        """Les valeurs des votes ne sont exposées qu'après la révélation."""
        return {
            "projet": self.projet,
            "fonctionnalite": self.fonctionnalite_courante(),
            "numero": self.index_courant + 1 if self.fonctionnalites else None,
            "total": len(self.fonctionnalites),
            "cartes": list(CARTES),
            "joueurs": [
                {"nom": nom, "a_vote": nom in self.votes} for nom in self.joueurs
            ],
            "revele": self.revele,
            "votes": (
                {nom: self.votes[nom] for nom in self.joueurs} if self.revele else None
            ),
        }

    def _reinitialiser_votes(self):
        self.votes = {}
        self.revele = False
