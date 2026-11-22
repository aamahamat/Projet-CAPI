# AI_LOG.md : journal d'usage de l'IA

> À placer à la racine du dépôt. À remplir **au fil de l'eau**, pas en fin de projet. Une entrée par tâche (pas par message), en 5 lignes.
> Rappel : l'IA est autorisée pour le **code de production** et la **configuration d'outils** uniquement. Qui a fait la demande, les fichiers touchés et les commits se retrouvent dans l'historique Git : ne les recopiez pas.

## Outils utilisés (à remplir une fois)

| Outil | Modèle (si connu) | Mode (autocomplétion, chat, agent) |
|---|---|---|
| Claude | Sonnet 5.5 | Mode chat | Fichier d'instructions pour agent versionné (`CLAUDE.md`, `AGENTS.md`...) : non

## Entrées

### 2026-11-21 : Workflow CI GitHub Actions (R2)

- **Demande (résumé fidèle)** : écrire .github/workflows/ci.yml (push et PR vers main, installation, pytest), plus des explications sur la CI, les PR et le badge.
- **Résultat** : <modifié>
- **Ce que nous avons vérifié** : <Nous avons vérifier le run dans l'onglet Actions, et nous avons trouvé en rouge comme l'a demandé l'enseignant>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <nous avons changer les commentaires du YAML en les réecrivant avec nos mots>

### 2026-11-22 : Moteur de règles de validation et intégration dans la boucle de vote (US-01, US-02, US-03)

- **Demande (résumé fidèle)** : nous avons implémenter 'src/capi/regles.py' ('evaluer_vote', règles strict, médiane, moyenne, majorités) à partir de nos tests 'tests/test_integration.py', fournis comme spécification avec interdiction de les modifier ; puis brancher le moteur dans `partie.py` et `routes.py` (verdict après révélation, nouveau tour, fonctionnalité suivante, choix de la règle) et nous avons enfin mis à jour la page web.
- **Résultat** : <légèrement modifié>
- **Ce que nous avons vérifié** : <Nous avons testé 'py -m pytest' en local, nous donne 92 tests réussis ; CI verte (lien du run dans R2) ; lecture ligne à ligne de regles.py par le copilote>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <nous avons gardé test_integration.py dans tests parce qu'il contient les fonctions de nos CA »>

### 2026-11-21 : Modification interface(app.js/app.css)

- **Demande (résumé fidèle)** : Modifie le l'interface de l'application afin que ce soit plus ergonimique
- **Résultat** : <legerement modifié>
- **Ce que nous avons vérifié** : <Nous avons verifié que le workflow n'a pas changé et que la logique derriere reste la meme>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <nous avons changer les couleurs et les positions car les couleurs ne correspondaient pas et le contraste ne tenait pas>

## Bilan (à compléter en séance 4, 3 lignes)

- Nombre d'entrées et de propositions rejetées ou corrigées : 
- Tâches où l'IA a fait gagner du temps : 
- Tâches où l'IA a fait perdre du temps :
