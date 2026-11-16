# PrimeFlix TV — Architecture de référence

## Cible
Application Android TV, paysage 16:9 (720p/1080p/4K), entièrement navigable à la télécommande.

## Règles fonctionnelles
1. Premier lancement : création d'une identité d'installation/appareil reconnue par le serveur.
2. Démarrage du compte à rebours de 600 secondes selon l'horloge **du serveur**.
3. L'essai expire après 10 minutes écoulées, même si l'application a été fermée (choix MVP).
4. Après expiration, affichage de l'écran « Choisir une formule / Saisir mon code ».
5. Un code PFM = 1 mois calendaire ; un code PFY = 12 mois calendaires, à compter de l'activation.
6. Code à usage unique, lié à un appareil. Renouvellement depuis l'échéance existante si abonnement encore actif.
7. L'équipe confirme le paiement hors de ce service, puis émet le code d'activation depuis l'API administrateur.
8. L'autorisation doit aussi protéger **la livraison du contenu côté serveur**, sans quoi une APK modifiée peut contourner l'écran d'abonnement.

## API disponible
- POST `/v1/devices/register` — JSON `{"device_fingerprint":"ID_STABLE_DU_TERMINAL"}`. Renvoie un `device_token` à conserver avec soin.
- GET `/v1/access` — header `Authorization: Bearer TOKEN`. Réponse `status=trial|active|expired`, expiration, temps restant.
- POST `/v1/activate` — header d'appareil, JSON `{"code":"PFM-..."}`.
- POST `/v1/playback/authorize` — header d'appareil, refuse par HTTP 403 après expiration.
- POST `/v1/admin/codes` — header `X-Admin-Key`, JSON `{"plan":"monthly","quantity":1}` ou `yearly`.
- POST `/v1/admin/devices/reissue-token` — secours contrôlé après réinstallation, ne redémarre pas l'essai.

## Ergonomie Android TV
- Système de focus explicite avec D-pad: gauche, droite, haut, bas, OK et retour.
- Carte focus : animation légère 150–220 ms, agrandissement ~1,05x, ombre/contour net.
- Transitions entre écrans ~200–300 ms, sans animation bloquante.
- Interface avec dimensionnement relatif (`dp`, `sp`) et marges de sécurité de ~5 %.
- Écrans d'abonnement lisibles à 3 m; saisie du code possible à la télécommande.
- Tests prévus 1280×720, 1920×1080, 3840×2160.

## Limites à régler avant production
- **Source React Native absente** : ajouter le contrôle d'accès et modifier les animations du binaire Hermes nécessite en pratique de récupérer le projet ou reconstruire l'application.
- Identifiant d'appareil envoyé par le client = forgeable. Ajouter compte, appairage ou attestation selon les appareils et le niveau de risque.
- Pas de système de paiement intégré : émission des codes uniquement après validation manuelle du paiement par l'équipe.
- Protections manquantes : limitation de débit, audit d'émission, migration DB, sauvegardes chiffrées, journalisation, HTTPS/TLS via reverse proxy, gestion de révocation et de capacité par compte.
- Si diffusion via Google Play, vérifier l'obligation de Google Play Billing pour les services numériques et les exceptions applicables.
- Vérifier la titularité des droits sur le logiciel, son nom commercial et les contenus diffusés.
