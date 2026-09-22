import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, Lot, LotPayload } from '../api/client';
const KEY = 'ecobridge.pendingLots';
export type PendingLot = { id: string; payload: LotPayload; state: 'pending' | 'failed'; attempts: number; error?: string };
export async function getPendingLots(): Promise<PendingLot[]> { const raw = await AsyncStorage.getItem(KEY); return raw ? JSON.parse(raw) as PendingLot[] : []; }
async function save(value: PendingLot[]): Promise<void> { await AsyncStorage.setItem(KEY, JSON.stringify(value)); }
export async function enqueueLot(payload: LotPayload): Promise<void> { const record = { id: payload.lot_code, payload, state: 'pending' as const, attempts: 0 }; await save([...(await getPendingLots()).filter((item) => item.id !== record.id), record]); }
export async function syncPendingLots(): Promise<{ synced: Lot[]; failed: PendingLot[] }> {
  const failed: PendingLot[] = []; const synced: Lot[] = [];
  for (const record of await getPendingLots()) {
    try { record.attempts += 1; synced.push(await api.createLot(record.payload)); } catch (error) { record.state = 'failed'; record.error = error instanceof Error ? error.message : 'Sync failed'; failed.push(record); }
  }
  await save(failed); return { synced, failed };
}
