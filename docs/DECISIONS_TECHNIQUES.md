# Décisions techniques

1. Garder le prototype FastAPI comme base et le faire évoluer dans `primeflix-tv-starter/` afin de préserver ses contrats d'API.
2. Construire une application neuve en `react-native-tvos` avec package propre ; aucun contenu, secret, code ou identifiant n'est repris de l'APK de référence.
3. UTC serveur comme source de vérité, essai unique de 600 secondes et mois calendaires ; renouvellement calculé depuis l'échéance future.
4. Paiement hors application confirmé manuellement. L'écran TV indique que le tarif est communiqué par le distributeur. Aucun paiement, prix ou renouvellement automatique simulé.
5. L'API de licence refuse toute nouvelle lecture sans droit valide. Aucun serveur de médias n'étant fourni, le catalogue reste démo locale et ne contient aucune URL de flux tiers.
6. Identifiant d'appareil envoyé par le client n'est pas une preuve matérielle ; la récupération après réinstallation doit passer par le support administrateur.
7. Les builds et essais device réels sont annoncés uniquement après exécution effective. Pas de secret dans le dépôt ; release signée par l'entreprise hors de ce dépôt.
