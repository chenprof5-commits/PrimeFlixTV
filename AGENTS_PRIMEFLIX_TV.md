# Règles permanentes pour Codex — Projet PrimeFlix TV

- Respecter `CODEX_ORDRES_PRIMEFLIX_TV.md` comme cahier des charges.
- Ne jamais utiliser le binaire NetMirrorTV.apk autrement que comme référence technique en lecture seule, et ne pas copier de contenus ou secrets protégés. Reconstruire indépendamment lorsque le projet source manque.
- Livrer des changements testables et documentés ; ne pas se limiter à une proposition de plan. Toute commande de test/build déclarée réussie doit réellement avoir été exécutée.
- L'application cible Android TV et la télécommande D-pad ; aucun parcours critique ne doit nécessiter un écran tactile.
- Le serveur est seul juge de l'essai de 600 secondes, de la validité et des expirations des codes. N'embarquer aucune clé admin dans le client.
- Les codes mensuels correspondent à 1 mois calendaire, annuels à 12 mois calendaires. Le paiement est contrôlé manuellement par l'équipe : pas de prix inventés ni de fausse passerelle de paiement.
- Toujours protéger l'accès aux flux autorisés côté serveur, ou indiquer explicitement que l'intégration n'est pas possible sans backend de contenus.
- Jamais de secrets en dépôt, journaux, captures ou artefacts diffusés. Prévoir `.env.example`, migrations, tests et documentation.
- Reporter les blocages dans `docs/BLOCKERS.md` et poursuivre les parties indépendantes. Expliquer toute limitation d'émulation, signature et build.
