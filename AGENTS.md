# Règles du dépôt PrimeFlix TV

- Respecter `CODEX_ORDRES_PRIMEFLIX_TV.md`, `AGENTS_PRIMEFLIX_TV.md` et les notes `docs/`.
- Ne pas réutiliser de code, médias, clés, URL ou secrets de NetMirrorTV.apk ; l'APK de référence est en lecture seule.
- Le backend décide des droits ; aucun accès vidéo ne doit reposer uniquement sur l'interface cliente. Ne pas présenter le catalogue démo comme un catalogue autorisé.
- Aucun prix inventé, paiement intégré ou auto-renouvellement. Les codes sont émis après confirmation manuelle.
- UTC serveur, essai unique 600 s, mois calendaires mensuel/annuel, codes hashés et usage atomique.
- Ne jamais committer `.env`, clés d'admin, codes, jetons ou keystore. Logs sans secrets.
- Documenter chaque limite, valider les entrées et exécuter les vérifications réellement disponibles.
