import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, Lot, LotPayload } from '../api/client';
const KEY = 'ecobridge.pendingLots';
export type PendingLot = { id: string; payload: LotPayload; state: 'pending' | 'syncing' | 'failed'; attempts: number; error?: string };
export async function getPendingLots(): Promise<PendingLot[]> {
  const raw = await AsyncStorage.getItem(KEY); return raw ? (JSON.parse(raw) as PendingLot[]) : [];
}
async function save(records: PendingLot[]): Promise<void> { await AsyncStorage.setItem(KEY, JSON.stringify(records)); }
export async function enqueueLot(payload: LotPayload): Promise<PendingLot> {
  const record: PendingLot = { id: payload.lot_code, payload, state: 'pending', attempts: 0 };
  await save([...(await getPendingLots()).filter((item) => item.id !== record.id), record]); return record;
}
export async function syncPendingLots(): Promise<{ synced: Lot[]; failed: PendingLot[] }> {
  const records = await getPendingLots(); const synced: Lot[] = []; const failed: PendingLot[] = [];
  for (const record of records) {
    try { record.state = 'syncing'; record.attempts += 1; synced.push(await api.createLot(record.payload)); }
    catch (error) { record.state = 'failed'; record.error = error instanceof Error ? error.message : 'Unable to sync this lot.'; failed.push(record); }
  }
  await save(failed); return { synced, failed };
}
