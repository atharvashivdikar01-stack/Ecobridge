import React, { useEffect, useState } from 'react';
import { Button, SafeAreaView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api, Lot, LotPayload } from './src/api/client';
import { enqueueLot, getPendingLots, syncPendingLots } from './src/offline/queue';

export default function App(): React.ReactElement {
  const [weight, setWeight] = useState(''); const [lots, setLots] = useState<Lot[]>([]); const [pending, setPending] = useState(0); const [materialId, setMaterialId] = useState<string | null>(null); const [message, setMessage] = useState('');
  const refresh = async (): Promise<void> => { try { setLots((await api.listLots()).lots); } catch { /* offline history remains visible */ } setMaterialId(await api.cacheDefaultMaterial()); setPending((await getPendingLots()).length); };
  useEffect(() => { void refresh(); }, []);
  const saveOffline = async (): Promise<void> => {
    const kilograms = Number(weight); if (!kilograms || kilograms <= 0) { setMessage('Enter a positive weight.'); return; } if (!materialId) { setMessage('Open the app online once to cache the material taxonomy.'); return; }
    const code = `EB-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
    const payload: LotPayload = { lot_code: code, offline_created_at: new Date().toISOString(), items: [{ material_id: materialId, estimated_weight_kg: kilograms, quantity: 1, unit: 'KG', detected_hazard: 'NORMAL' }], images: [] };
    await enqueueLot(payload); setWeight(''); setMessage(`Saved offline as ${code}`); await refresh();
  };
  const sync = async (): Promise<void> => { const result = await syncPendingLots(); setMessage(`${result.synced.length} lot(s) synchronized${result.failed.length ? `; ${result.failed.length} remain queued` : ''}`); await refresh(); };
  return <SafeAreaView style={styles.container}><View style={styles.content}><Text style={styles.title}>EcoBridge Collector</Text><Text>Lots are saved on this device before sync.</Text><TextInput style={styles.input} placeholder="Estimated weight (kg)" keyboardType="decimal-pad" value={weight} onChangeText={setWeight} /><Button title="Save lot offline" onPress={saveOffline} /><View style={styles.spacer} /><Button title={`Sync queued lots (${pending})`} onPress={sync} disabled={!pending} /><Text style={styles.message}>{message}</Text><Text style={styles.heading}>Synced lots</Text>{lots.map((lot) => <Text key={lot.id}>{lot.lot_code} · {lot.status} · {lot.total_estimated_weight_kg} kg</Text>)}</View></SafeAreaView>;
}
const styles = StyleSheet.create({ container: { flex: 1, backgroundColor: '#f7faf8' }, content: { padding: 24, gap: 12 }, title: { fontSize: 26, fontWeight: '700', color: '#125c3b' }, input: { borderWidth: 1, borderColor: '#b8c8bf', borderRadius: 8, padding: 12, backgroundColor: '#fff' }, spacer: { height: 8 }, message: { color: '#125c3b', marginTop: 8 }, heading: { fontSize: 18, fontWeight: '600', marginTop: 18 } });
