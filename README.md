# CAPI – Planning poker

Application Flask d'estimation de backlog en planning poker.

## Lancer l'application

```bash
flask --app src/capi run --debug
```

Puis ouvrir http://127.0.0.1:5000 :

1. saisir le nombre de joueurs, cliquer sur « Saisir les pseudos », puis « Valider les joueurs » ;
2. charger `exemples/backlog_exemple.json` : la première fonctionnalité s'affiche ;
3. chaque joueur choisit son pseudo puis sa carte (les votes restent cachés) ;
4. quand tous ont voté, cliquer sur « Révéler les votes ».
