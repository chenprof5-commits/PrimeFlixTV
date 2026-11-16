/**
 * EXEMPLE D'INTÉGRATION : à incorporer dans un projet React Native Android TV.
 * Ne peut pas être injecté directement dans un APK Hermes déjà compilé.
 * Requiert un deviceToken enregistré et stocké de manière sûre par l'application.
 */
import React, {useCallback, useEffect, useRef, useState} from 'react';
import {
  Animated, ActivityIndicator, Pressable, StyleSheet, Text,
  TextInput, useWindowDimensions, View,
} from 'react-native';

type Access = {
  status: 'trial' | 'active' | 'expired';
  allowed: boolean;
  trial_seconds_remaining: number;
  subscription_expires_at: string | null;
};

type Props = {
  apiBaseUrl: string; // ex. https://licences.votredomaine.tld
  deviceToken: string; // NE PAS coder en dur
  children: React.ReactNode;
};

function TvButton({title, onPress, disabled = false}: {
  title: string; onPress: () => void; disabled?: boolean;
}) {
  const scale = useRef(new Animated.Value(1)).current;
  const focused = useRef(new Animated.Value(0)).current;
  function focus(isFocused: boolean) {
    Animated.parallel([
      Animated.spring(scale, {
        toValue: isFocused ? 1.055 : 1,
        useNativeDriver: true, speed: 22, bounciness: 5,
      }),
      Animated.timing(focused, {
        toValue: isFocused ? 1 : 0,
        duration: 160,
        useNativeDriver: false,
      }),
    ]).start();
  }
  const backgroundColor = focused.interpolate({
    inputRange: [0, 1], outputRange: ['#25283A', '#E50914'],
  });
  return (
    <Pressable onPress={onPress} disabled={disabled}
      onFocus={() => focus(true)} onBlur={() => focus(false)}
      accessibilityRole="button">
      <Animated.View style={[styles.button, {backgroundColor, transform: [{scale}]}]}>
        <Text style={styles.buttonText}>{title}</Text>
      </Animated.View>
    </Pressable>
  );
}

export default function PrimeFlixAccessGate({apiBaseUrl, deviceToken, children}: Props) {
  const {width, height} = useWindowDimensions();
  const [access, setAccess] = useState<Access | null>(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [message, setMessage] = useState('');
  const [redeeming, setRedeeming] = useState(false);
  const base = apiBaseUrl.replace(/\/$/, '');

  const refresh = useCallback(async () => {
    try {
      const response = await fetch(`${base}/v1/access`, {
        headers: {Authorization: `Bearer ${deviceToken}`},
      });
      if (!response.ok) {throw new Error('Connexion ou appareil non reconnu.');}
      const status = (await response.json()) as Access;
      setAccess(status);
      setMessage('');
    } catch {
      // Fail-closed : pas d'accès sans validation serveur.
      setAccess(null);
      setMessage('Impossible de vérifier votre accès. Réessayez.');
    } finally {
      setLoading(false);
    }
  }, [base, deviceToken]);

  useEffect(() => {
    void refresh();
    const interval = setInterval(() => {void refresh();}, 15000);
    return () => clearInterval(interval);
  }, [refresh]);

  async function redeem() {
    setRedeeming(true);
    setMessage('');
    try {
      const response = await fetch(`${base}/v1/activate`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${deviceToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({code: code.trim().toUpperCase()}),
      });
      if (!response.ok) {throw new Error('Code invalide ou déjà utilisé.');}
      await refresh();
    } catch {
      setMessage('Activation impossible. Vérifiez le code ou votre connexion.');
    } finally {
      setRedeeming(false);
    }
  }

  if (!loading && access?.allowed) {
    // ATTENTION : ceci protège l'interface, pas les flux. Le serveur vidéo doit
    // vérifier l'accès à chaque délivrance du contenu/jeton de streaming.
    return <>{children}</>;
  }
  const padH = Math.max(24, Math.round(width * 0.05));
  const padV = Math.max(18, Math.round(height * 0.05));
  return (
    <View style={[styles.root, {paddingHorizontal: padH, paddingVertical: padV}]}>
      <Text style={styles.brand}>PRIMEFLIX TV</Text>
      <View style={styles.panel}>
        <Text style={styles.title}>
          {loading ? 'Vérification de votre accès' : 'Bienvenue sur PrimeFlix TV'}
        </Text>
        {loading ? <ActivityIndicator size="large" color="#E50914" /> : (
          <>
            <Text style={styles.description}>
              {access?.status === 'expired'
                ? 'Votre essai de 10 minutes est terminé. Activez votre abonnement.'
                : 'Connectez-vous pour valider votre abonnement.'}
            </Text>
            <View style={styles.plans}>
              <Text style={styles.plan}>Formule mensuelle</Text>
              <Text style={styles.plan}>Formule annuelle</Text>
            </View>
            <Text style={styles.caption}>
              Après paiement auprès de votre distributeur, saisissez le code reçu.
            </Text>
            <TextInput
              value={code} onChangeText={setCode} autoCapitalize="characters"
              autoCorrect={false} placeholder="PFM-XXXXX-XXXXX-XXXXX-XXXXX"
              placeholderTextColor="#9B9CAC" style={styles.input}
              accessibilityLabel="Code d'activation" />
            <TvButton title={redeeming ? 'Activation...' : 'Activer mon abonnement'}
              onPress={() => {void redeem();}} disabled={redeeming || !code.trim()} />
            <TvButton title="Réessayer la connexion" onPress={() => {void refresh();}} />
            {!!message && <Text style={styles.error}>{message}</Text>}
          </>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {flex: 1, backgroundColor: '#0B0E17', justifyContent: 'space-around'},
  brand: {fontWeight: '900', color: '#E50914', fontSize: 34, letterSpacing: 2},
  panel: {alignSelf: 'center', width: '85%', maxWidth: 850, gap: 18},
  title: {color: '#FFFFFF', fontSize: 32, fontWeight: '800'},
  description: {color: '#E4E5ED', fontSize: 21, lineHeight: 30},
  plans: {flexDirection: 'row', gap: 18, flexWrap: 'wrap'},
  plan: {backgroundColor: '#242838', color: 'white', overflow: 'hidden',
    borderRadius: 12, padding: 16, fontSize: 20},
  caption: {color: '#C4C6D1', fontSize: 18},
  input: {color: 'white', backgroundColor: '#1B1D2A', fontSize: 23,
    borderColor: '#56586C', borderWidth: 2, borderRadius: 12, padding: 15},
  button: {alignItems: 'center', borderRadius: 12, paddingVertical: 18, paddingHorizontal: 25},
  buttonText: {color: 'white', fontWeight: '800', fontSize: 20},
  error: {color: '#FFD2D2', fontSize: 18},
});
