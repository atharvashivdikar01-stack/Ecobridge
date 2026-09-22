import React, { useEffect, useRef, useState } from 'react';
import { Alert, Button, FlatList, SafeAreaView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as Location from 'expo-location';
import { t } from '../../packages/i18n/src';
import { api, Lot, LotPayload } from './src/api/client';
import { enqueueLot, getPendingLots, PendingLot, syncPendingLots } from './src/offline/queue';
import { clearTokens, getTokens, saveTokens } from './src/storage/tokens';

type Screen = 'login' | 'dashboard' | 'create' | 'detail';
const label = (key: string): string => t(`collector.${key}`);

function ErrorBanner({ message }: { message: string | null }): React.ReactElement | null {
  return message ? <Text style={styles.error}>{message}</Text> : null;
}

function Login({ onLogin }: { onLogin: () => void }): React.ReactElement {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [name, setName] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const send = async (): Promise<void> => {
    try { setError(null); await api.sendOtp(phone); setSent(true); } catch (e) { setError(e instanceof Error ? e.message : label('networkError')); }
  };
  const verify = async (): Promise<void> => {
    try {
      setError(null);
      const tokens = await api.verifyOtp(phone, otp, name);
      await saveTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token });
      onLogin();
    } catch (e) { setError(e instanceof Error ? e.message : label('networkError')); }
  };
  return <View style={styles.center}><Text style={styles.title}>{label('title')}</Text><Text style={styles.subtitle}>{label('loginHint')}</Text>
    <TextInput style={styles.input} placeholder={label('phone')} keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
    {!sent ? <Button title={label('sendOtp')} onPress={send} disabled={phone.length < 10} /> : <>
      <TextInput style={styles.input} placeholder={label('name')} value={name} onChangeText={setName} />
      <TextInput style={styles.input} placeholder={label('otp')} keyboardType="number-pad" value={otp} onChangeText={setOtp} maxLength={6} />
      <Button title={label('verify')} onPress={verify} disabled={otp.length !== 6} />
    </>}
    <ErrorBanner message={error} />
  </View>;
}

function Dashboard({ onCreate, onDetail }: { onCreate: () => void; onDetail: (lot: Lot) => void }): React.ReactElement {
  const [lots, setLots] = useState<Lot[]>([]);
  const [pending, setPending] = useState<PendingLot[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = async (): Promise<void> => {
    try { setError(null); const result = await api.listLots(); setLots(result.lots); } catch (e) { setError(e instanceof Error ? e.message : label('networkError')); }
    setPending(await getPendingLots());
  };
  useEffect(() => { void load(); }, []);
  const sync = async (): Promise<void> => { const result = await syncPendingLots(); setPending(result.failed); await load(); if (result.failed.length) setError(label('syncError')); };
  return <View style={styles.screen}><Text style={styles.title}>{label('dashboard')}</Text><Button title={label('newLot')} onPress={onCreate} />
    <View style={styles.row}><Text>{label('pending')}: {pending.length}</Text><Button title={label('sync')} onPress={sync} disabled={!pending.length} /></View>
    <ErrorBanner message={error} /><Text style={styles.section}>{label('history')}</Text>
    <FlatList data={lots} keyExtractor={(item) => item.id} ListEmptyComponent={<Text>{label('noLots')}</Text>}
      renderItem={({ item }) => <TouchableOpacity style={styles.card} onPress={() => onDetail(item)}><Text style={styles.cardTitle}>{item.lot_code}</Text><Text>{item.status} · {item.total_estimated_weight_kg} kg</Text></TouchableOpacity>} />
  </View>;
}

function CreateLot({ onSaved }: { onSaved: () => void }): React.ReactElement {
  const [weight, setWeight] = useState('');
  const [hazard, setHazard] = useState('NORMAL');
  const [location, setLocation] = useState<Location.LocationObjectCoords | null>(null);
  const [cameraPermission, requestCameraPermission] = useCameraPermissions();
  const [cameraOpen, setCameraOpen] = useState(false);
  const camera = useRef<CameraView>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const locate = async (): Promise<void> => {
    const permission = await Location.requestForegroundPermissionsAsync();
    if (permission.status !== Location.PermissionStatus.GRANTED) { setError(label('locationDenied')); return; }
    setLocation((await Location.getCurrentPositionAsync({})).coords);
  };
  const capture = async (): Promise<void> => {
    if (!cameraPermission?.granted) { const result = await requestCameraPermission(); if (!result.granted) { setError(label('cameraDenied')); return; } }
    setCameraOpen(true);
  };
  const takePhoto = async (): Promise<void> => { const result = await camera.current?.takePictureAsync({ quality: 0.6 }); if (result?.uri) { setPhoto(result.uri); setCameraOpen(false); } };
  const save = async (): Promise<void> => {
    const numericWeight = Number(weight);
    if (!numericWeight || numericWeight <= 0) { setError(label('weightRequired')); return; }
    const payload: LotPayload = { lot_code: `EB-${Date.now()}`, offline_created_at: new Date().toISOString(), origin_latitude: location?.latitude, origin_longitude: location?.longitude, items: [{ material_id: 'other-ewaste', estimated_weight_kg: numericWeight, quantity: 1, unit: 'KG', detected_hazard: hazard }], images: photo ? [{ image_url: photo, latitude: location?.latitude, longitude: location?.longitude, captured_at: new Date().toISOString() }] : [] };
    await enqueueLot(payload); onSaved();
  };
  if (cameraOpen) return <View style={styles.camera}><CameraView ref={camera} style={StyleSheet.absoluteFill} facing="back" /><Button title={label('takePhoto')} onPress={takePhoto} /></View>;
  return <View style={styles.screen}><Text style={styles.title}>{label('newLot')}</Text><Text style={styles.warning}>{label('hazardWarning')}</Text>
    <TextInput style={styles.input} placeholder={label('weight')} keyboardType="decimal-pad" value={weight} onChangeText={setWeight} />
    <TextInput style={styles.input} placeholder={label('hazard')} value={hazard} onChangeText={setHazard} />
    <Button title={location ? label('locationReady') : label('captureLocation')} onPress={locate} /><Button title={photo ? label('photoReady') : label('capturePhoto')} onPress={capture} /><Button title={label('saveOffline')} onPress={save} /><ErrorBanner message={error} />
  </View>;
}

function Detail({ lot, onBack }: { lot: Lot; onBack: () => void }): React.ReactElement {
  return <View style={styles.screen}><Button title={label('back')} onPress={onBack} /><Text style={styles.title}>{lot.lot_code}</Text><Text>{label('status')}: {lot.status}</Text><Text>{label('weight')}: {lot.total_estimated_weight_kg} kg</Text><Text>{label('value')}: ₹{lot.estimated_value}</Text><Text style={styles.section}>{label('items')}</Text>{lot.items.map((item, index) => <Text key={`${item.material_name}-${index}`}>{item.material_name}: {item.estimated_weight_kg} kg ({item.detected_hazard})</Text>)}</View>;
}

export default function App(): React.ReactElement {
  const [screen, setScreen] = useState<Screen>('login');
  const [selected, setSelected] = useState<Lot | null>(null);
  useEffect(() => { void getTokens().then((tokens) => { if (tokens) setScreen('dashboard'); }); }, []);
  if (screen === 'login') return <SafeAreaView style={styles.container}><Login onLogin={() => setScreen('dashboard')} /></SafeAreaView>;
  if (screen === 'create') return <SafeAreaView style={styles.container}><CreateLot onSaved={() => setScreen('dashboard')} /></SafeAreaView>;
  if (screen === 'detail' && selected) return <SafeAreaView style={styles.container}><Detail lot={selected} onBack={() => setScreen('dashboard')} /></SafeAreaView>;
  return <SafeAreaView style={styles.container}><Dashboard onCreate={() => setScreen('create')} onDetail={(lot) => { setSelected(lot); setScreen('detail'); }} /><Button title={label('signOut')} onPress={() => { void clearTokens(); setScreen('login'); }} /></SafeAreaView>;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f7faf8' }, screen: { flex: 1, padding: 20 }, center: { flex: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 28, fontWeight: '700', color: '#125c3b', marginBottom: 8 }, subtitle: { marginBottom: 20, color: '#43534b' }, input: { borderWidth: 1, borderColor: '#b8c8bf', borderRadius: 8, padding: 12, marginVertical: 8, backgroundColor: '#fff' },
  error: { color: '#a51d2d', marginVertical: 12 }, warning: { backgroundColor: '#fff0c2', color: '#6b4d00', padding: 12, marginBottom: 12 }, row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginVertical: 12 },
  section: { fontSize: 18, fontWeight: '600', marginTop: 18, marginBottom: 8 }, card: { backgroundColor: '#fff', padding: 16, borderRadius: 8, marginBottom: 10 }, cardTitle: { fontWeight: '700', color: '#125c3b' },
  camera: { flex: 1, justifyContent: 'flex-end', padding: 24 }
});
