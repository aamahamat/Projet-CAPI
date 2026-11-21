# AI_LOG.md : journal d'usage de l'IA

> À placer à la racine du dépôt. À remplir **au fil de l'eau**, pas en fin de projet. Une entrée par tâche (pas par message), en 5 lignes.
> Rappel : l'IA est autorisée pour le **code de production** et la **configuration d'outils** uniquement. Qui a fait la demande, les fichiers touchés et les commits se retrouvent dans l'historique Git : ne les recopiez pas.

## Outils utilisés (à remplir une fois)

| Outil | Modèle (si connu) | Mode (autocomplétion, chat, agent) |
|---|---|---|
| Claude | Sonnet 5.5 | Mode chat |

Fichier d'instructions pour agent versionné (`CLAUDE.md`, `AGENTS.md`...) : non

## Entrées

### 2026-11-07 : Squelette Flask, chargement du backlog JSON et choix d'une carte (US-04, US-06)

- **Demande (résumé fidèle)** : implémenter US-04 et US-06 avec Flask, à partir de R0.md et R1.md (CU-01 extension 2a, CU-02 étape 1). Aucun code existant fourni.
- **Résultat** : <accepté tel quel / modifié / rejeté>
- **Ce que nous avons vérifié** : <ex. : pytest (71 tests), essai manuel dans le navigateur, lecture ligne à ligne>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <ce que vous avez modifié et la raison, ou « rien »>

### 2026-11-07 : Alignement sur l'objectif du sprint 1 : saisie des joueurs, format de backlog de l'énoncé, révélation des votes (US-04, US-06)

- **Demande (résumé fidèle)** : fournir l'énoncé du sprint 1 et demander de s'y conformer : nombre de joueurs et pseudos, backlog `projet` / `fonctionnalites`, affichage de la première fonctionnalité, vote caché puis révélation.
- **Résultat** : <accepté tel quel / modifié / rejeté>
- **Ce que nous avons vérifié** : <à compléter>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <à compléter>

### 2026-11-20 : Table de décision puis tests

- **Demande (résumé fidèle)** : *******************************
- **Résultat** : <modifié>
- **Ce que nous avons vérifié** : *******************************
- **Ce que nous avons changé ou rejeté, et pourquoi** : *************************************

### 2026-11-21 : Workflow CI GitHub Actions (R2)

- **Demande (résumé fidèle)** : écrire .github/workflows/ci.yml (push et PR vers main, installation, pytest), plus des explications sur la CI, les PR et le badge.
- **Résultat** : <modifié>
- **Ce que nous avons vérifié** : <Nous avons vérifier le run dans l'onglet Actions, et nous avons trouvé en rouge>
- **Ce que nous avons changé ou rejeté, et pourquoi** : <nous avons changer les commentaires du YAML en les réecrivant avec nos mots>

## Bilan (à compléter en séance 4, 3 lignes)

- Nombre d'entrées et de propositions rejetées ou corrigées :
- Tâches où l'IA a fait gagner du temps :
- Tâches où l'IA a fait perdre du temps :
