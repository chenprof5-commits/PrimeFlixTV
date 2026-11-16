# Audit technique de NetMirrorTV.apk

## Méthode et intégrité

Inspection en lecture seule avec Android SDK `apkanalyzer` ; aucun fichier n'a été extrait ni modifié. SHA-256 : `E99229EA8D49B217EF59B6E20C31CBE3DE0D0E297C679A98445044BA20AD0DBA`.

## Constats vérifiés

- Package `app.netmirror.newtv`, version `1` / `1.0`, min SDK 24, target SDK 34, compilé avec SDK 35.
- Manifeste : `INTERNET`, accès état réseau, tactile non requis, `LEANBACK_LAUNCHER` optionnel, activité paysage/rotation autorisée et bannière TV.
- APK contient `assets/index.android.bundle`, DEX, Hermes, React Native, React Codegen et bibliothèques natives `armeabi-v7a`, `arm64-v8a`, `x86`, `x86_64` ; React Native/Hermes est donc un constat étayé.
- L'activité déclare `MainActivity`, lanceur Android standard et Leanback, ainsi qu'une prise en charge de configuration Android courante.
- Le binaire mesure 60 837 005 octets.

## Limites

L'inventaire ne permet pas de confirmer les bibliothèques JS exactes, les droits sur les ressources, le DRM, les services distants ou les capacités de lecture. Aucun bytecode ou bundle n'a été décompilé. Modifier le bundle Hermes compilé est fragile (format/outils/version, source maps et modules natifs absents), ne permet pas une refonte maintenable et pourrait compromettre les signatures ou droits tiers. Une reconstruction indépendante est retenue.
