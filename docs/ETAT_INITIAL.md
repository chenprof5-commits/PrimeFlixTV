# État initial

- Le dépôt contenait le prototype `primeflix-tv-starter` avec un service FastAPI/SQLAlchemy, un test API, un composant React Native d'exemple, Docker Compose et deux documents de cadrage.
- Le service crée les appareils, démarre un essai serveur de 600 s, calcule l'expiration calendaire, valide un code à usage unique et expose une autorisation de lecture. La réémission de jeton invalidait l'ancien et conservait l'essai.
- Lacunes du prototype : pas de console admin, journal d'audit, révocation, limitations de débit, migrations Alembic ni client TV complet ; auth admin par clé statique et catalogue/streaming absent.
- Tests de départ : `python -m pytest primeflix-tv-starter/tests/test_api.py -q` échoue à la collecte car `fastapi` n'est pas installé dans l'environnement. Aucun test n'a pu valider le prototype.
- Outils : `apkanalyzer`, Python, Node/npm et Java sont présents ; `aapt`, `jadx`, `apktool` et Docker ne sont pas trouvés par `Get-Command`. Aucune compilation Android n'est attestée.
- APK : identité/permissions constatées dans [AUDIT_APK.md](AUDIT_APK.md).
