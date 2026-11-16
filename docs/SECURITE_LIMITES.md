# Sécurité et limites actuelles

- Les droits d'essai/abonnement sont décidés par l'API et une réponse serveur expirée refuse l'autorisation de lecture.
- L'API de démonstration n'est PAS le serveur de streaming. Aucun média protégé ou flux tiers n'est intégré ; `/v1/playback/authorize` ne protège une vidéo que si le fournisseur vidéo appelle cette décision avant d'émettre un jeton ou média court.
- `ANDROID_ID`/fingerprint auto-déclaré est forgeable et réinstallations/appareils peuvent partager des contraintes constructeur. Le support réémet un jeton sans recréer l'essai. Pas d'attestation matérielle.
- Jetons et codes ne sont stockés qu'en hash HMAC côté serveur ; code en clair uniquement dans la réponse unique d'émission. Jeton TV dans Keychain Android, pas encore vérifié sur matériel.
- Protection de débit actuelle est mémoire par processus et rudimentaire. Pas suffisante contre botnets ou multi-instance.
- Admin MVP par clé partagée, pas de session, RBAC, MFA, CORS, révocation de clé ni protection CSRF de console. Utiliser seulement localement derrière HTTPS jusqu'à remplacement.
- SQLite pour tests/démo ; PostgreSQL avec Compose est cible, non vérifié ici. Le conteneur applique Alembic avant le démarrage ; l'application ne crée plus les tables implicitement.
- Le client échoue fermé lorsqu'il ne peut pas vérifier. L'essai est basé sur heure serveur, il n'est pas renouvelé par un enregistrement en doublon.
- Aucun secret, prix, paiement, contenu ou licence tiers n'est inclus.
