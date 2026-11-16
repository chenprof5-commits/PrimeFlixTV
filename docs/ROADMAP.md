# Feuille de route

1. Installer les dépendances Python/Node/Android dans un environnement dédié et exécuter les tests API/clients/builds.
2. Remplacer la clé admin partagée par OIDC/session MFA, rôles, CSRF, CORS strict et limitation Redis distribuée.
3. Exécuter les migrations Alembic au démarrage contrôlé/CI plutôt que `create_all` et tester PostgreSQL/concurrence réelle.
4. Générer le squelette natif `react-native-tvos`, intégrer la configuration d'API HTTPS et valider APK/launcher D-pad sur téléviseurs ciblés.
5. Ajouter backend de contenus détenu/autorisés, contrôle d'accès lors de chaque émission de flux/jeton court, catalogue et lecteur de démo sans données fictives en production.
6. Ajouter filtres/recherche et CSV admin expurgé, clés d'émission à expiration, procédure support et rotation des secrets.
7. Revue juridique marque/contenus, politique de confidentialité et distribution sideload/Play applicable avant version commerciale.
