# Tests et checklist TV

## Automatisé prévu

`primeflix-tv-starter/tests/test_api.py` couvre essai, doublon/réinstallation, expiration, lecture 403, code incorrect, activation mensuelle et annuelle, renouvellement annuel depuis une échéance future, limites de mois calendaire, code déjà utilisé, listes admin, refus non-admin, révocation/restauration.

Commande : depuis le starter, `python -m pip install -r server/requirements.txt pytest httpx` puis `python -m pytest tests -q`. Résultat exécuté : **3 passed** dans l'environnement du développeur ; un avertissement de dépréciation Starlette/httpx reste affiché.

Console : `npm run build` dans `apps/admin` réussi. Client TV : `npx tsc --noEmit` réussi avant intégration du squelette natif et bundle Metro Android généré avec `--max-workers 1`. Le squelette Android TV est maintenant intégré ; son installation npm doit être réalignée sur React Native TV 0.83 avant de compiler l'APK. Aucun test sur téléviseur effectué.

## Vérification physique à exécuter

- Installer première fois en ligne : essai 10:00 environ, fermer/réouvrir et vérifier que le temps ne repart pas.
- Simuler 600 s serveur ; l'écran de code doit remplacer le catalogue et l'endpoint lecture répondre 403.
- Essayer code invalide, mensuel, annuel, code déjà utilisé et renouvellement avant échéance ; vérifier sur appareils liés.
- Effacer/réinstaller : aucun nouvel essai. Vérifier récupération par support puis token renouvelé.
- Couper internet : erreur claire, nouvelle lecture refusée ; rétablir le réseau et rafraîchir l'accès.
- Télécommande : toutes flèches/OK/Retour, clavier code, focus après retour, aucun toucher requis.
- Capture et contrôle des marges 5 %, textes et focus à 1280×720, 1920×1080 et 3840×2160.

Aucune TV/émulateur n'a été testée dans cette session.
