# Guide opérateur

## Générer un code pour un client

1. Vérifier le paiement manuellement, puis choisir la formule promise.
2. Ouvrir la console d'administration en HTTPS et saisir l'URL de l'API Vercel et la clé administrateur.
3. Dans **Codes**, choisir **Mensuel · 1 mois calendaire** ou **Annuel · 12 mois calendaires**, puis la quantité (généralement 1).
4. Cliquer **Confirmer le paiement et générer**, confirmer, puis copier les codes affichés et les transmettre au client. Le serveur conserve uniquement leur empreinte : un code perdu ne peut pas être affiché de nouveau.
5. Si un code est perdu, révoquer le code encore inutilisé et en générer un nouveau après vérification du paiement.

Le code s'active sur le premier appareil qui le saisit et ne peut servir qu'une fois. Le renouvellement se fait en générant un code de la formule souhaitée et en le saisissant sur l'appareil ; une échéance encore future est prolongée.

## Gestion des accès

Consulter les appareils/états et l'historique des opérations. Révoquer un code non utilisé depuis **Codes** ; pour stopper un abonnement actif, utiliser **Révoquer** sur l'appareil. **Restaurer** annule une révocation administrative.

Les codes ne seront réels et utilisables par les clients que si l'API est déployée avec une base PostgreSQL persistante et si l'APK pointe vers cette même API. Une base SQLite locale de test ne doit pas servir à créer les codes de production.

Limites : l'API MVP utilise une clé partagée, pas de comptes, rôles, MFA ni rotation UI ; l'interface n'offre pas encore export CSV. Établir ces contrôles avant accès de plusieurs opérateurs.
