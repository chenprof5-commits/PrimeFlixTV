# Blocages et éléments externes

- Vérifications : tests API **3 passés** ; build Vite admin réussi ; `npx tsc --noEmit` TV réussi après correction de la résolution de tsconfig.
- Le développeur a compilé et ouvert l'APK debug dans BlueStacks. L'écran « Unable to load script » a montré que le build debug ne contenait pas encore le bundle ; `app/build.gradle` a été ajusté pour l'embarquer dans les prochains APK debug et limiter Metro à un worker. Une nouvelle compilation dans l'environnement de l'agent s'arrête sur CMake à cause des restrictions de sous-processus ; la reconstruction doit être faite dans le PowerShell du développeur.
- L'application Android appelait l'URL fictive `https://licences.example.invalid` : aucun essai serveur ne pouvait donc être démarré. `access()` tente maintenant l'enregistrement si aucun jeton n'est stocké, y compris après le rétablissement d'Internet. Il faut encore remplacer l'URL d'API par l'URL HTTPS Vercel puis reconstruire l'APK.
- SDK Platform 36, Build Tools 36.0.0 et NDK 27.1.12297006 sont installés et les licences SDK ont été acceptées. Le Gradle wrapper est fourni par le template.
- Aucun domaine, certificat HTTPS, secret de déploiement, compte administrateur initial ni PostgreSQL d'exécution fourni.
- Cible d'hébergement précisée : Vercel. Il manque l'URL PostgreSQL managée/poolée et les URL publiques Vercel API/console pour configurer `DATABASE_URL`, `ADMIN_ORIGINS` et `API_BASE`. Sans ces éléments, le dashboard ne peut pas produire de code de production et l'application ne peut pas démarrer son essai de 10 minutes.
- Aucun backend/catalogue de médias autorisés n'a été fourni. La démo ne protège pas ni ne distribue de flux tiers ; le contrôle réel devra être intégré au serveur vidéo détenu par l'équipe.
- Aucune clé de signature d'entreprise fournie ; aucun APK release signé ne peut être fabriqué.
