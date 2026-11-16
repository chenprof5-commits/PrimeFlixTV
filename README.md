# PrimeFlix TV

Reconstruction indépendante Android TV + API FastAPI/PostgreSQL + console web admin. Le starter conservé dans `primeflix-tv-starter/` constitue le serveur de licence de référence ; l'app TV source commence dans `apps/tv/`.

## Démarrage API

```powershell
cd primeflix-tv-starter
Copy-Item .env.example .env
# Générer des valeurs différentes et aléatoires pour chaque secret du fichier .env.
python -m pip install -r server/requirements.txt
docker compose up --build
```

Le service local est limité à `127.0.0.1:8000`. En production, l'API FastAPI et la console Vite sont déployées comme projets Vercel séparés ; l'API utilise une base PostgreSQL managée et les variables Vercel. Voir [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md).

## Publier sur GitHub

Depuis PowerShell, lancer `Set-ExecutionPolicy -Scope Process Bypass -Force` puis `.scripts\publish-github.ps1`. Le script vérifie la cible `chenprof5-commits/PrimeFlixTV`, exclut les secrets et fichiers générés, puis commit et pousse la branche `main`. Il ne force jamais le push.

## TV et console

`apps/tv/` utilise React Native TV 0.83. Pour installer les dépendances, lancer `npm install` dans ce dossier. Avant de compiler l'APK, remplacer `API_BASE` dans `apps/tv/src/api.ts` par l'URL HTTPS publique de l'API déployée. `apps/admin/` est une application web Vite ; `npm install && npm run dev`.

Le catalogue est fictif, aucun serveur de contenus n'étant fourni. `/v1/playback/authorize` protège l'autorisation délivrée par cette API, mais seule une intégration au serveur qui sert réellement les médias peut protéger une lecture. Voir [docs/SECURITE_LIMITES.md](docs/SECURITE_LIMITES.md).

## Tests / build

```powershell
cd primeflix-tv-starter
python -m pip install -r server/requirements.txt pytest httpx
python -m pytest tests -q
```

Build de développement Android depuis `apps/tv` : `npx react-native run-android`. Une release doit être signée avec le keystore et les secrets de l'entreprise, jamais avec une clé incluse ici. Parcours et limites : `docs/TESTS_TV.md`, `docs/DEPLOIEMENT.md`.

## État

Prototype en cours, non prêt pour la production. Les dépendances manquantes à cette session et l'absence de backend média sont consignées dans [docs/BLOCKERS.md](docs/BLOCKERS.md).
