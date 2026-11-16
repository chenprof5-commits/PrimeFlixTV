# Client Android TV

Le dossier `android/` est créé à partir du template officiel React Native TV 0.83. Le projet cible `tv.primeflix.app`, affiche PrimeFlix TV et déclare le lanceur Leanback en paysage.

## Installer et compiler

Après modification de `package.json`, régénérer les dépendances et le verrouillage avec `npm install` depuis ce dossier. Puis vérifier `npx tsc --noEmit`.

L'Android SDK doit contenir Platform 36, Build Tools 36 et NDK 27.1.12297006 (ou ajuster la version NDK dans `android/build.gradle` à une version compatible déjà installée). Le build APK debug embarque le bundle JavaScript pour démarrer sans Metro :

```powershell
Set-Location android
.\gradlew.bat assembleDebug
```

APK attendu : `android/app/build/outputs/apk/debug/app-debug.apk`. Le wrapper Gradle est fourni : Gradle global n'est pas requis. Exécution sur appareil TV connecté : depuis la racine de l'app, `npm run android`.

Avant le build fonctionnel, remplacer l'URL exemple dans `src/api.ts` par l'URL HTTPS Vercel de l'API de licences. L'essai de 10 minutes commence quand l'API enregistre l'appareil ; si le premier lancement est hors ligne, l'application retente l'enregistrement quand l'utilisateur réessaie ou lors des contrôles périodiques. Le catalogue et le lecteur restent des démonstrations tant qu'aucun serveur de contenus autorisés n'est raccordé.
