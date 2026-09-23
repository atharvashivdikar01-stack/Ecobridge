import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = (process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000/api/v1').replace(/\/$/, '');
export type LotPayload = { lot_code: string; offline_created_at: string; items: [{ material_id: string; estimated_weight_kg: number; quantity: number; unit: string; detected_hazard: string }]; images: [] };
export type Lot = { id: string; lot_code: string; status: string; total_estimated_weight_kg: number; estimated_value: number };
const MATERIAL_KEY = 'ecobridge.defaultMaterialId';

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers); headers.set('Content-Type', 'application/json');
  const token = await SecureStore.getItemAsync('ecobridge.access_token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error?.message || `Request failed (${response.status})`);
  return (body.data ?? body) as T;
}
export const api = {
  listLots: () => request<{ lots: Lot[] }>('/lots'),
  cacheDefaultMaterial: async (): Promise<string | null> => {
    const cached = await AsyncStorage.getItem(MATERIAL_KEY);
    try {
      const taxonomy = await request<{ categories: Array<{ materials: Array<{ id: string }> }> }>('/lots/taxonomy/materials');
      const id = taxonomy.categories[0]?.materials[0]?.id;
      if (id) await AsyncStorage.setItem(MATERIAL_KEY, id);
      return id || cached;
    } catch {
      return cached || process.env.EXPO_PUBLIC_DEFAULT_MATERIAL_ID || null;
    }
  },
  createLot: (payload: LotPayload) => request<Lot>('/lots', { method: 'POST', headers: { 'Idempotency-Key': payload.lot_code }, body: JSON.stringify(payload) }),
};
