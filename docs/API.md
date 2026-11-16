# API de licences

Base locale : `http://127.0.0.1:8000`; production : HTTPS obligatoire. JSON UTF-8, horodatages ISO-8601 UTC.

| Méthode | Route | Auth | Fonction |
|---|---|---|---|
| POST | `/v1/devices/register` | aucune | Enregistre fingerprint auto-déclaré et démarre l'essai de 600 s ; doublon 409. Jeton révélé une fois. |
| GET | `/v1/access` | Bearer appareil | Retourne `trial`, `active` ou `expired`, restant essai et échéance. |
| POST | `/v1/activate` | Bearer appareil | `{"code":"PFM-…"}` ou `PFY`; usage unique, 400 invalide, 409 réutilisé. |
| POST | `/v1/playback/authorize` | Bearer appareil | Autorisation contrôlée côté serveur ; 403 après échéance/révocation. N'émet aucun média. |
| POST | `/v1/admin/codes` | `X-Admin-Key` | Émet quantité bornée de codes mensuels/annuels, code clair retourné une fois. |
| GET | `/v1/admin/devices`, `/codes`, `/audit` | admin | Liste pseudonymisée appareils, métadonnées codes et journal. Jamais les hashes/code clair. |
| POST | `/v1/admin/codes/{id}/revoke` | admin | Révoque code non consommé. |
| POST | `/v1/admin/devices/{id}/revoke`, `/restore` | admin | Révoque/rétablit l'accès d'un appareil. |
| POST | `/v1/admin/devices/reissue-token` | admin | Réassociation après support ; l'essai et l'abonnement sont conservés. |

Mensuel = 1 mois calendaire ; annuel = 12. En renouvellement avant échéance, calcul depuis l'échéance existante. L'émission est faite uniquement après paiement confirmé manuellement. La limitation actuelle est mémoire/processus et doit être remplacée par Redis ou équivalent derrière proxy pour une production multi-instance.
