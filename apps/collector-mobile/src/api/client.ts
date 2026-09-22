import { clearTokens, getTokens, saveTokens, Tokens } from '../storage/tokens';

const API_URL = (process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000/api/v1').replace(/\/$/, '');
export class ApiError extends Error {
  constructor(message: string, readonly status?: number) { super(message); this.name = 'ApiError'; }
}
type ApiEnvelope<T> = { success?: boolean; data: T; error?: { message?: string } };

async function request<T>(path: string, init: RequestInit = {}, authenticated = true): Promise<T> {
  const tokens = authenticated ? await getTokens() : null;
  const headers = new Headers(init.headers);
  headers.set('Content-Type', 'application/json');
  if (tokens) headers.set('Authorization', `Bearer ${tokens.accessToken}`);
  let response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 401 && tokens?.refreshToken) {
    const refreshed = await refresh(tokens.refreshToken);
    if (refreshed) { headers.set('Authorization', `Bearer ${refreshed.accessToken}`); response = await fetch(`${API_URL}${path}`, { ...init, headers }); }
  }
  if (!response.ok) throw new ApiError((await response.text()) || `Request failed (${response.status})`, response.status);
  const envelope = (await response.json()) as ApiEnvelope<T>;
  if (envelope.success === false || !envelope.data) throw new ApiError(envelope.error?.message || 'The server returned an invalid response.');
  return envelope.data;
}
async function refresh(refreshToken: string): Promise<Tokens | null> {
  try {
    const data = await request<{ access_token: string; refresh_token: string }>('/auth/token/refresh', { method: 'POST', body: JSON.stringify({ refresh_token: refreshToken }) }, false);
    const tokens = { accessToken: data.access_token, refreshToken: data.refresh_token };
    await saveTokens(tokens); return tokens;
  } catch { await clearTokens(); return null; }
}
export type LotItem = { material_id: string; estimated_weight_kg: number; quantity: number; unit: string; detected_hazard: string; notes?: string };
export type LotPayload = { lot_code: string; origin_latitude?: number; origin_longitude?: number; offline_created_at: string; items: LotItem[]; images: Array<{ image_url: string; latitude?: number; longitude?: number; captured_at: string }> };
export type Lot = { id: string; lot_code: string; status: string; total_estimated_weight_kg: number; estimated_value: number; offline_created_at: string; origin_latitude?: number; origin_longitude?: number; items: Array<{ material_name: string; estimated_weight_kg: number; detected_hazard: string }> };
export const api = {
  sendOtp: (phone: string) => request<{ message: string }>('/auth/otp/send', { method: 'POST', body: JSON.stringify({ phone }) }, false),
  verifyOtp: (phone: string, otp: string, fullName: string) => request<{ access_token: string; refresh_token: string; user: { full_name: string; preferred_language: string } }>('/auth/otp/verify', { method: 'POST', body: JSON.stringify({ phone, otp, full_name: fullName, preferred_language: 'en' }) }, false),
  listLots: () => request<{ lots: Lot[]; total: number }>('/lots'),
  getLot: (id: string) => request<Lot>(`/lots/${encodeURIComponent(id)}`),
  createLot: (payload: LotPayload) => request<Lot>('/lots', { method: 'POST', body: JSON.stringify(payload) })
};
