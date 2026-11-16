# PrimeFlix TV — Kit de démarrage (backend + spécification Android TV)

Ce dépôt est un **MVP technique testé**, pas un APK final. L'APK fourni est un binaire React Native/Hermes : le projet source n'est pas inclus. Ce serveur ne s'injecte pas automatiquement dans l'APK.

## Démarrage avec Docker Compose

1. Copier `.env.example` en `.env`.
2. Générer puis renseigner 5 secrets forts (`python -c "import secrets;print(secrets.token_urlsafe(32))"`).
3. Lancer `docker compose up --build -d`.
4. Placer un proxy HTTPS devant le service, le port n'étant accessible qu'en localhost (`127.0.0.1:8000`).
5. Documentation interactive locale : `http://127.0.0.1:8000/docs` (sur la machine serveur uniquement).

## Démonstration avec curl

### Générer un code mensuel (personnel autorisé uniquement)
```bash
curl -X POST 'http://127.0.0.1:8000/v1/admin/codes' \
  -H 'X-Admin-Key: VOTRE_ADMIN_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"plan":"monthly","quantity":1}'
```

### Enregistrer une TV (une seule fois)
```bash
curl -X POST 'http://127.0.0.1:8000/v1/devices/register' \
  -H 'Content-Type: application/json' \
  -d '{"device_fingerprint":"ANDROID_ID_TV"}'
```
La réponse contient `device_token`. Le téléphone/boîtier doit stocker ce jeton de façon sécurisée.

### Vérifier le statut
```bash
curl 'http://127.0.0.1:8000/v1/access' \
  -H 'Authorization: Bearer VOTRE_DEVICE_TOKEN'
```

### Activer l'abonnement
```bash
curl -X POST 'http://127.0.0.1:8000/v1/activate' \
  -H 'Authorization: Bearer VOTRE_DEVICE_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"code":"PFM-XXXXX-XXXXX-XXXXX-XXXXX"}'
```

## Tests
```bash
pip install -r server/requirements.txt pytest httpx
pytest -q
```

## Précisions importantes
- Les 10 minutes courent **depuis l'enregistrement** selon l'heure serveur (pas 10 minutes de lecture effective). Si vous préférez 10 minutes de visionnage effectif, il faut un mécanisme de consommation sur le backend vidéo.
- Chaque code est à usage unique et vaut pour un seul appareil. Mensuel = 1 mois calendaire, annuel = 12 mois calendaires.
- Le serveur **ne reçoit aucun paiement** et **ne transmet aucun contenu** : il ne sait gérer que les droits d'accès. Le contrôle doit également être imposé par les serveurs délivrant les films/chaînes.
- Ce kit requiert encore revue de sécurité et intégration au frontend Android TV avant un déploiement commercial.

Voir `docs/ARCHITECTURE.md` pour la conception des écrans et les limites du binaire initial.
