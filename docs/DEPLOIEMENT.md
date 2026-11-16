# Déploiement

## Développement

Depuis `primeflix-tv-starter`, copier `.env.example` vers `.env`, remplacer chaque valeur par un secret aléatoire distinct, puis `docker compose up --build`. Le port API est limité à localhost. Docker indisponible durant l'audit, ce flux n'a pas été exécuté.

Console locale : dans `apps/admin`, `npm install` puis `npm run dev`; saisir la clé admin et l'URL API. `ADMIN_ORIGINS` restreint CORS (par défaut loopback Vite uniquement).

## Vercel (hébergement retenu)

Déployer l'API et la console comme deux projets Vercel reliés au même dépôt :

1. **API FastAPI** : créer un projet Vercel avec Root Directory `primeflix-tv-starter/server`. `app.py` expose l'objet FastAPI `app`, et `requirements.txt` est dans ce dossier ; le runtime Python Vercel sert FastAPI sans Docker ni commande Uvicorn.
2. **PostgreSQL** : Vercel ne fournit plus sa propre base Postgres ; créer une base via une intégration PostgreSQL du Marketplace (Neon est l'intégration native proposée par Vercel) et la rattacher au projet API. Vercel peut alors injecter l'URL de connexion dans les variables du projet. L'API convertit les préfixes `postgres://` et `postgresql://` en `postgresql+psycopg://` pour utiliser le pilote installé. Privilégier l'URL avec pooler. SQLite n'est pas adapté au stockage persistant partagé de Vercel.
3. **Variables API** : vérifier `DATABASE_URL`, puis définir `ADMIN_KEY`, `CODE_PEPPER`, `TOKEN_PEPPER` et `DEVICE_PEPPER` avec des valeurs aléatoires distinctes dans les variables du projet API. Ajouter les variables aux environnements Production et Preview. Définir `ADMIN_ORIGINS` à l'origine exacte de la console déployée, par exemple `https://nom-projet.vercel.app`, puis redéployer l'API.
4. **Migrations** : avant le premier déploiement, appliquer Alembic une fois à la base configurée avec `python -m alembic upgrade head`, depuis le dossier API. La variable de base et les quatre secrets sont requis par l'import de l'application.
5. **Console web** : créer un second projet Vercel avec Root Directory `apps/admin`. Vercel détecte Vite et construit `dist`. Saisir l'URL publique de l'API dans l'écran de connexion de la console.
6. **Client TV** : après le premier déploiement de l'API, remplacer `API_BASE` dans `apps/tv/src/api.ts` par son URL Vercel, puis reconstruire le bundle/APK.

Vercel prend en charge directement FastAPI avec son runtime Python. Les fonctions sont sans état durable ; utiliser le pooler PostgreSQL du fournisseur pour réutiliser les connexions. [Runtime Python](https://vercel.com/docs/functions/runtimes/python), [guide FastAPI](https://vercel.com/kb/guide/ship-a-fastapi-app-on-vercel), [connexions base de données](https://vercel.com/kb/guide/connection-pooling-with-functions).

Le plan Hobby est réservé à l'usage personnel non commercial ; pour un service d'abonnement commercial, choisir une offre autorisant cet usage. [Plan Hobby](https://vercel.com/docs/plans/hobby).

## Docker local

Docker Compose reste utile en développement pour démarrer PostgreSQL et l'API localement. Copier `.env.example` vers `.env`, renseigner les variables puis lancer `docker compose up --build`. Le déploiement Vercel n'utilise pas cette image.

## APK

Le template Android TV est intégré dans `apps/tv/android/`. Après `npm install` dans `apps/tv` et configuration de `API_BASE`, lancer `cd apps/tv/android; .\gradlew.bat assembleDebug`. L'APK debug est généré dans `android/app/build/outputs/apk/debug/app-debug.apk`. Vérifier `adb install` sur téléviseur. Release : fournir le keystore de l'entreprise hors dépôt via variables/secrets CI et utiliser `assembleRelease` après configuration de signature de production.
