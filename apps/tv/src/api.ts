import DeviceInfo from 'react-native-device-info';
import * as Keychain from 'react-native-keychain';

// Remplacer à la compilation par l'URL HTTPS de votre service de licences.
export const API_BASE = 'https://licences.example.invalid';
export type Access={status:'trial'|'active'|'expired';allowed:boolean;trial_seconds_remaining:number;subscription_expires_at:string|null;server_now:string};
const CREDS='primeflix.device-token';
async function token(){const credentials=await Keychain.getGenericPassword({service:CREDS});return credentials?credentials.password:null;}
export async function register():Promise<void>{
  const fingerprint=await DeviceInfo.getAndroidId();
  const r=await fetch(`${API_BASE}/v1/devices/register`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({device_fingerprint:fingerprint})});
  if(r.status===409)throw new Error('Appareil déjà enregistré. Connectez-vous au support pour récupérer votre accès.');
  if(!r.ok)throw new Error('Inscription impossible. Vérifiez votre connexion.');
  const data=await r.json();await Keychain.setGenericPassword('device',data.device_token,{service:CREDS,accessible:Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY});
}
export async function ensureRegistered():Promise<void>{
  // L'essai ne démarre que lors d'un enregistrement confirmé par le serveur.
  // Si l'appareil était hors ligne au premier lancement, les prochains appels
  // (y compris le bouton Réessayer) retentent l'inscription sans réinstallation.
  if(!(await token()))await register();
}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
  const t=await token();if(!t)throw new Error('Appareil non enregistré.');
  const r=await fetch(API_BASE+path,{...options,headers:{Authorization:`Bearer ${t}`,'content-type':'application/json',...(options.headers||{})}});
  if(!r.ok){if(r.status===403)throw new Error('Accès expiré. Saisissez un code d’activation.');if(r.status===401)throw new Error('Appareil non reconnu. Contactez le support.');throw new Error(`Service indisponible (${r.status}).`);}
  return r.json() as Promise<T>;
}
export async function access(){await ensureRegistered();return api<Access>('/v1/access');}
export async function activate(code:string){return api<Access & {plan:string}>('/v1/activate',{method:'POST',body:JSON.stringify({code})});}
export async function authorizePlayback(){return api<{allowed:boolean;status:string}>('/v1/playback/authorize',{method:'POST'});}
