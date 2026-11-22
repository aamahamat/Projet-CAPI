/* Interface du planning poker.
   Parle à l'API Flask (/api/...) ; toute la logique de jeu reste côté serveur.

   Organisation du fichier :
     1. constantes et état
     2. utilitaires (alerte, appels API)
     3. étapes et stepper
     4. étape 1 : joueurs
     5. étape 2 : backlog
     6. étape 3 : vote et révélation
     7. thème et démarrage
*/
"use strict";

/* ============================ 1. Constantes et état ============================ */

const JSON_HEADERS = { "Content-Type": "application/json" };
const DUREE_ALERTE_MS = 4000;
const LONGUEUR_MAX_PSEUDO = 30; // même valeur que partie.LONGUEUR_MAX_PSEUDO côté serveur

// Libellés des règles. La liste des règles vient du serveur : une règle qui n'est pas
// ici s'affiche simplement avec son nom (voir libelleRegle).
const LIBELLES_REGLES = {
  strict: "Strict (unanimité)",
  mediane: "Médiane",
  moyenne: "Moyenne",
  majorite_absolue: "Majorité absolue",
  majorite_relative: "Majorité relative",
};

let etat = null;           // dernier état renvoyé par /api/etat
let etapeForcee = null;    // étape choisie à la main dans le stepper (sinon calculée)
let etapeAffichee = null;  // pour détecter un changement d'étape
let joueurActif = null;    // pseudo du joueur qui est en train de voter
let minuteurAlerte = null;

const $ = (id) => document.getElementById(id);
const symbole = (carte) => (carte === "cafe" ? "☕" : String(carte));
const libelleCarte = (carte) => (carte === "cafe" ? "café" : String(carte));
const libelleRegle = (nom) => LIBELLES_REGLES[nom] ?? nom;

/* ============================ 2. Utilitaires ============================ */

/** Affiche un message flottant qui disparaît tout seul. */
function afficherAlerte(texte, succes) {
  const zone = $("alerte");
  if (!texte) { zone.classList.add("d-none"); return; }
  zone.textContent = texte;
  zone.className = "alert alert-flottante " + (succes ? "alert-success" : "alert-danger");
  zone.setAttribute("role", succes ? "status" : "alert"); // une erreur est annoncée plus fort
  clearTimeout(minuteurAlerte);
  minuteurAlerte = setTimeout(() => zone.classList.add("d-none"), DUREE_ALERTE_MS);
}

/**
 * Appelle l'API. Affiche l'erreur du serveur le cas échéant et renvoie true si tout va bien.
 * `messageSucces` : texte à montrer en cas de succès (null = ne rien afficher).
 */
async function appel(url, options, messageSucces = null) {
  try {
    const reponse = await fetch(url, options);
    const donnees = await reponse.json();
    if (!reponse.ok) {
      afficherAlerte(donnees.erreur || "Une erreur est survenue.", false);
      return false;
    }
    if (messageSucces) afficherAlerte(messageSucces, true);
    return true;
  } catch (erreur) {
    afficherAlerte("Le serveur est injoignable.", false);
    return false;
  }
}

async function chargerEtat() {
  etat = await (await fetch("/api/etat")).json();
}

/** Recharge l'état depuis le serveur puis redessine l'écran. */
async function rafraichir() {
  try {
    await chargerEtat();
  } catch (erreur) {
    afficherAlerte("Impossible de lire l'état de la partie.", false);
    return;
  }
  afficher();
}

/* ============================ 3. Étapes et stepper ============================ */

/** Étape la plus avancée accessible : joueurs, puis backlog, puis vote. */
function etapeMax() {
  if (!etat.joueurs.length) return 1;
  if (!etat.fonctionnalite) return 2;
  return 3;
}

function afficher() {
  const max = etapeMax();
  const etape = etapeForcee && etapeForcee <= max ? etapeForcee : max;

  for (const i of [1, 2, 3]) $("etape-" + i).hidden = i !== etape;
  dessinerStepper(etape, max);

  if (etape !== etapeAffichee) {
    etapeAffichee = etape;
    if (etape === 1) preparerFormulaireJoueurs();
  }
  if (etape === 3) dessinerVote();
}

function dessinerStepper(actif, max) {
  for (const bouton of $("stepper").querySelectorAll("button")) {
    const n = Number(bouton.dataset.etape);
    bouton.disabled = n > max;
    bouton.classList.toggle("est-actif", n === actif);
    bouton.classList.toggle("est-fait", n < actif);
    if (n === actif) bouton.setAttribute("aria-current", "step");
    else bouton.removeAttribute("aria-current");
  }
}

$("stepper").addEventListener("click", (evenement) => {
  const bouton = evenement.target.closest("button[data-etape]");
  if (!bouton) return;
  etapeForcee = Number(bouton.dataset.etape);
  afficher();
});

/* ============================ 4. Étape 1 : joueurs ============================ */

/** Nombre de joueurs saisi, ramené entre le min et le max du champ. */
function nombreSaisi() {
  const champ = $("nombre");
  const min = Number(champ.min), max = Number(champ.max);
  return Math.min(max, Math.max(min, parseInt(champ.value, 10) || min));
}

/** (Re)crée un champ pseudo par joueur en conservant ce qui a déjà été tapé. */
function genererChamps(nombre, valeursInitiales = []) {
  const zone = $("pseudos");
  const saisis = [...zone.querySelectorAll("input")].map((champ) => champ.value);
  zone.replaceChildren();

  for (let i = 0; i < nombre; i++) {
    const colonne = document.createElement("div");
    colonne.className = "col-sm-6";

    const label = document.createElement("label");
    label.className = "form-label small text-body-secondary mb-1";
    label.htmlFor = "pseudo-" + i;
    label.textContent = "Joueur " + (i + 1);

    const champ = document.createElement("input");
    champ.id = "pseudo-" + i;
    champ.className = "form-control";
    champ.required = true;
    champ.maxLength = LONGUEUR_MAX_PSEUDO;
    champ.autocomplete = "off";
    champ.placeholder = "Pseudo du joueur " + (i + 1);
    champ.value = saisis[i] ?? valeursInitiales[i] ?? "";

    colonne.append(label, champ);
    zone.append(colonne);
  }
}

/** Au retour sur l'étape 1, préremplit avec les joueurs déjà enregistrés. */
function preparerFormulaireJoueurs() {
  const existants = etat.joueurs.map((joueur) => joueur.nom);
  const nombre = existants.length || 3;
  $("nombre").value = nombre;
  $("pseudos").replaceChildren();
  genererChamps(nombre, existants);
  remplirRegles();
}

/** Liste déroulante des règles, avec celle déjà choisie présélectionnée. */
function remplirRegles() {
  const liste = $("regle");
  liste.replaceChildren();
  for (const nom of etat.regles) {
    const option = document.createElement("option");
    option.value = nom;
    option.textContent = libelleRegle(nom);
    option.selected = nom === etat.regle;
    liste.append(option);
  }
}

function changerNombre(ecart) {
  $("nombre").value = Math.min(Number($("nombre").max), Math.max(Number($("nombre").min), nombreSaisi() + ecart));
  genererChamps(nombreSaisi());
}

$("nombre").addEventListener("input", () => genererChamps(nombreSaisi()));
$("moins").addEventListener("click", () => changerNombre(-1));
$("plus").addEventListener("click", () => changerNombre(1));

$("form-joueurs").addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const pseudos = [...$("pseudos").querySelectorAll("input")].map((champ) => champ.value);
  const ok = await appel(
    "/api/joueurs",
    { method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ nombre: pseudos.length, pseudos }) },
    "Joueurs enregistrés."
  );
  if (!ok) return;

  // La règle est enregistrée juste après les joueurs (deux routes distinctes côté serveur).
  const regleOk = await appel(
    "/api/regle",
    { method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ regle: $("regle").value }) }
  );
  if (!regleOk) return;

  etapeForcee = null;
  joueurActif = null; // le serveur a remis les votes à zéro
  await rafraichir();
});

/* ============================ 5. Étape 2 : backlog ============================ */

$("form-backlog").addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const fichier = $("fichier").files[0];
  if (!fichier) return;
  const formulaire = new FormData();
  formulaire.append("fichier", fichier);

  const ok = await appel("/api/backlog", { method: "POST", body: formulaire }, "Backlog chargé.");
  if (!ok) return;
  etapeForcee = null;
  await rafraichir();
});

/* ============================ 6. Étape 3 : vote et révélation ============================ */

function premierSansVote() {
  return etat.joueurs.find((joueur) => !joueur.a_vote)?.nom ?? null;
}

function dessinerVote() {
  const fonctionnalite = etat.fonctionnalite;
  $("feature-id").textContent = fonctionnalite.id;
  $("feature-titre").textContent = fonctionnalite.titre;
  $("projet").textContent = etat.projet ?? "";
  $("feature-position").textContent = `Fonctionnalité ${etat.numero} sur ${etat.total}`;
  $("badge-tour").textContent = "Tour " + etat.tour;
  $("info-regle").textContent = etat.tour === 1
    ? "Premier tour : l'unanimité est requise, quelle que soit la règle."
    : `Règle appliquée : ${libelleRegle(etat.regle)}.`;

  const pourcentage = Math.round((etat.numero / etat.total) * 100);
  $("barre-feature").style.width = pourcentage + "%";
  $("barre-feature").parentElement.setAttribute("aria-valuenow", pourcentage);

  // Le joueur actif doit exister ; sinon on prend le premier qui n'a pas voté.
  if (!etat.joueurs.some((joueur) => joueur.nom === joueurActif)) {
    joueurActif = premierSansVote() ?? etat.joueurs[0]?.nom ?? null;
  }

  // Backlog terminé : on remplace la zone de vote par le récapitulatif.
  $("zone-jeu").hidden = etat.terminee;
  $("zone-fin").hidden = !etat.terminee;
  if (etat.terminee) { dessinerRecap(); return; }

  dessinerJoueurs();
  dessinerCartes();
  dessinerBoutonReveler();
  dessinerResultats();
}

/** Récapitulatif de fin de partie : la difficulté retenue pour chaque fonctionnalité. */
function dessinerRecap() {
  const liste = $("recap");
  liste.replaceChildren();
  for (const fonctionnalite of etat.estimations) {
    const ligne = document.createElement("li");
    ligne.className = "list-group-item d-flex justify-content-between align-items-center";

    const titre = document.createElement("span");
    titre.textContent = `${fonctionnalite.id} – ${fonctionnalite.titre}`;

    const valeur = document.createElement("span");
    valeur.className = "badge text-bg-primary fs-6";
    valeur.textContent = fonctionnalite.difficulte ?? "?";

    ligne.append(titre, valeur);
    liste.append(ligne);
  }
}

/** Une pastille par joueur : on clique sur son pseudo pour voter à sa place. */
function dessinerJoueurs() {
  const zone = $("joueurs");
  zone.replaceChildren();

  for (const joueur of etat.joueurs) {
    const actif = joueur.nom === joueurActif && !etat.revele;
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.disabled = etat.revele;
    bouton.className = "btn " + (actif ? "btn-primary" : joueur.a_vote ? "btn-outline-success" : "btn-outline-secondary");
    bouton.textContent = (joueur.a_vote ? "✓ " : "") + joueur.nom;
    bouton.setAttribute("aria-pressed", String(actif));
    bouton.addEventListener("click", () => { joueurActif = joueur.nom; dessinerVote(); });
    zone.append(bouton);
  }
}

function dessinerCartes() {
  $("zone-vote").hidden = etat.revele;
  $("titre-vote").textContent = joueurActif ? `${joueurActif}, choisis ta carte` : "";

  const zone = $("cartes");
  zone.replaceChildren();
  for (const carte of etat.cartes) {
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.className = "carte-poker" + (typeof carte === "string" ? " carte-speciale" : "");
    bouton.textContent = symbole(carte);
    bouton.dataset.coin = symbole(carte);
    bouton.setAttribute("aria-label", "Carte " + libelleCarte(carte));
    bouton.addEventListener("click", () => voter(carte));
    zone.append(bouton);
  }
}

async function voter(carte) {
  const votant = joueurActif;
  const ok = await appel(
    "/api/vote",
    { method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ joueur: votant, carte }) }
  );
  if (!ok) return;

  await chargerEtat();
  const suivant = premierSansVote();
  // On ne montre jamais quelle carte a été choisie : le prochain joueur est peut-être à côté.
  afficherAlerte(
    suivant
      ? `Vote de ${votant} enregistré. À ${suivant} de jouer !`
      : `Vote de ${votant} enregistré. Tout le monde a voté : révélez les cartes !`,
    true
  );
  joueurActif = suivant ?? votant;
  dessinerVote();
}

function dessinerBoutonReveler() {
  const ontVote = etat.joueurs.filter((joueur) => joueur.a_vote).length;
  const total = etat.joueurs.length;
  const complet = ontVote === total;

  $("zone-reveler").hidden = etat.revele;
  $("reveler").disabled = !complet;
  $("reveler").textContent = complet
    ? "Révéler les votes"
    : `Révéler les votes (${ontVote}/${total} ont voté)`;
}

function dessinerResultats() {
  $("zone-resultats").hidden = !etat.revele;
  const zone = $("resultats");
  zone.replaceChildren();
  if (!etat.revele) return;
  dessinerVerdict();

  for (const [nom, carte] of Object.entries(etat.votes)) {
    const bloc = document.createElement("div");
    bloc.className = "resultat";

    const visuel = document.createElement("div");
    visuel.className = "carte-poker carte-revelee";
    visuel.textContent = symbole(carte);
    visuel.dataset.coin = symbole(carte);
    visuel.setAttribute("aria-label", `${nom} a joué ${libelleCarte(carte)}`);

    const legende = document.createElement("div");
    legende.className = "resultat-nom";
    legende.textContent = nom;

    bloc.append(visuel, legende);
    zone.append(bloc);
  }
}

/** Verdict du moteur de règles (validé ou revote) et libellé du bouton « suite ». */
function dessinerVerdict() {
  const resultat = etat.resultat;
  const derniere = etat.numero === etat.total;

  const verdict = $("verdict");
  verdict.className = "alert mb-3 " + (resultat.valide ? "alert-success" : "alert-warning");
  verdict.textContent = resultat.valide
    ? `Validé : ${symbole(resultat.valeur)}. ${resultat.motif}`
    : `Pas de validation. ${resultat.motif}`;

  $("continuer").textContent = resultat.valide
    ? (derniere ? "Terminer le backlog" : "Fonctionnalité suivante")
    : `Revoter (tour ${etat.tour + 1})`;
}

$("reveler").addEventListener("click", async () => {
  const ok = await appel("/api/revelation", { method: "POST" });
  if (ok) await rafraichir();
});

/** Après la révélation : fonctionnalité suivante si validée, sinon nouveau tour. */
$("continuer").addEventListener("click", async () => {
  const valide = etat.resultat.valide;
  const ok = await appel(
    "/api/suite",
    { method: "POST" },
    valide ? "Estimation enregistrée." : "Nouveau tour : discutez, puis votez à nouveau."
  );
  if (!ok) return;
  joueurActif = null; // les votes ont été remis à zéro
  await rafraichir();
});

/* ============================ 7. Thème et démarrage ============================ */

$("theme-toggle").addEventListener("click", () => {
  const racine = document.documentElement;
  const nouveau = racine.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
  racine.setAttribute("data-bs-theme", nouveau);
  try { localStorage.setItem("theme", nouveau); } catch (erreur) { /* stockage indisponible : pas grave */ }
});

rafraichir();