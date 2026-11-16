# Écran d'activation Android TV (exemple React Native)

`PrimeFlixAccessGate.tsx` est un composant d'exemple pour un **nouveau projet React Native compatible TV**. Il inclut le focus télécommande animé, le dimensionnement selon l'écran et la saisie d'un code. Ce code **n'est pas connecté au binaire NetMirrorTV.apk**.

Intégration : après enregistrement de la TV via `POST /v1/devices/register`, persister le `device_token` avec un stockage adéquat, puis envelopper le navigateur de contenu :

```tsx
<PrimeFlixAccessGate apiBaseUrl="https://api.votre-domaine.tld" deviceToken={token}>
  <VotreNavigationTV />
</PrimeFlixAccessGate>
```

Pour rendre l'interface réellement sécurisée, le backend qui livre les flux doit également valider l'abonnement à chaque nouvelle lecture, idéalement avant l'émission d'une URL ou d'un jeton de lecture à durée limitée.

Cet exemple n'implémente pas le retour à la page précédente, les variantes accessibilité, ni la génération initiale du jeton. Il doit être testé avec les versions de React Native et les télécommandes de vos appareils cibles.
