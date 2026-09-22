export type DashboardSummary = {
  company_name: string;
  is_verified: boolean;
  operating_status?: string;
  cpcb_registration_no?: string;
  available_lots_count?: number;
  pending_handovers_count?: number;
  total_weight_recycled_kg?: number;
  total_payouts_inr?: number;
  completed_transactions_count?: number;
};

export type AvailableMaterialItem = {
  lot_id: string;
  lot_code: string;
  material_name: string;
  category_name: string;
  collector_name: string;
  collector_phone: string;
  status: string;
  estimated_weight_kg: number;
  verified_weight_kg?: number;
  ai_classification: string;
  ai_confidence_score?: number;
  detected_hazard: string;
  hazard_severity: string;
  benchmark_price_per_kg: number;
  min_price_per_kg: number;
  max_price_per_kg: number;
  agreed_price_per_kg?: number;
  created_at: string;
  final_value?: number;
  safety_advisory?: string;
  required_ppe?: string[];
  origin_address?: string;
  latitude?: number;
  longitude?: number;
};

export type RecyclerTransaction = {
  lot_id: string;
  reference_number: string;
  collector_name: string;
  collector_phone: string;
  material_name: string;
  verified_weight_kg: number;
  agreed_price_per_kg: number;
  total_amount: number;
  payment_method: string;
  custody_hash?: string;
  weighbridge_slip?: string;
};

export type LedgerResponse = {
  total_transactions: number;
  total_volume_kg: number;
  total_disbursed_inr: number;
  transactions: RecyclerTransaction[];
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set('Content-Type', 'application/json');
  if (typeof window !== 'undefined') {
    const token = window.localStorage.getItem('ecobridge_access_token');
    if (token) headers.set('Authorization', `Bearer ${token}`);
  }
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body?.message || body?.detail || `Request failed (${response.status})`);
  }
  return (body?.data ?? body) as T;
}

function normalizeMaterial(item: Partial<AvailableMaterialItem> & { lot_id: string }): AvailableMaterialItem {
  return {
    lot_id: item.lot_id,
    lot_code: item.lot_code || item.lot_id.slice(0, 8).toUpperCase(),
    material_name: item.material_name || 'Mixed e-waste',
    category_name: item.category_name || 'Unclassified',
    collector_name: item.collector_name || 'Collector',
    collector_phone: item.collector_phone || '',
    status: item.status || 'COLLECTED',
    estimated_weight_kg: Number(item.estimated_weight_kg || 0),
    verified_weight_kg: item.verified_weight_kg,
    ai_classification: item.ai_classification || item.material_name || 'Pending classification',
    ai_confidence_score: item.ai_confidence_score,
    detected_hazard: item.detected_hazard || 'NORMAL',
    hazard_severity: item.hazard_severity || 'Standard',
    benchmark_price_per_kg: Number(item.benchmark_price_per_kg || 0),
    min_price_per_kg: Number(item.min_price_per_kg || 0),
    max_price_per_kg: Number(item.max_price_per_kg || 0),
    agreed_price_per_kg: item.agreed_price_per_kg,
    created_at: item.created_at || new Date().toISOString(),
    final_value: item.final_value,
    safety_advisory: item.safety_advisory,
    required_ppe: item.required_ppe || [],
    origin_address: item.origin_address,
    latitude: item.latitude,
    longitude: item.longitude,
  };
}

export const api = {
  getDashboard: async () => request<DashboardSummary>('/recycler-portal/dashboard'),
  getMaterials: async (params?: { status?: string; hazardous_only?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.hazardous_only) query.set('hazardous_only', 'true');
    const result = await request<{ items: Partial<AvailableMaterialItem>[] }>(
      `/recycler-portal/materials${query.toString() ? `?${query}` : ''}`,
    );
    return { ...result, items: (result.items || []).map((item) => normalizeMaterial(item as AvailableMaterialItem)) };
  },
  getMaterialDetail: async (id: string) => {
    const result = await api.getMaterials();
    const item = result.items.find((entry) => entry.lot_id === id);
    if (!item) throw new Error('Material lot not found');
    return item;
  },
  acceptOffer: (lotId: string, agreedPrice: number, notes?: string) =>
    request<AvailableMaterialItem>(`/recycler-portal/lots/${lotId}/accept`, {
      method: 'POST',
      body: JSON.stringify({ agreed_price_per_kg: agreedPrice, notes }),
    }).then((result) => normalizeMaterial({ ...result, lot_id: lotId })),
  handover: (lotId: string, payload: { weighbridge_slip_number: string; weighbridge_gross_kg: number; weighbridge_tare_kg: number; verified_weight_kg: number; scale_calibration_id: string }) =>
    request<AvailableMaterialItem>(`/recycler-portal/lots/${lotId}/handover`, { method: 'POST', body: JSON.stringify(payload) }),
  recordPayment: (lotId: string, payload: { payment_method: string; amount: number; gateway_reference?: string; notes?: string }) =>
    request<RecyclerTransaction>(`/recycler-portal/lots/${lotId}/payment`, {
      method: 'POST',
      body: JSON.stringify({ ...payload, gateway_reference: payload.gateway_reference || `CASH-${Date.now()}` }),
    }).then((result) => ({ ...result, reference_number: result.reference_number || result.weighbridge_slip || lotId })),
  getLedger: () => request<LedgerResponse>('/recycler-portal/ledger'),
  demoLogin: async (role: 'VERIFIED_RECYCLER' | 'UNVERIFIED_RECYCLER') => {
    const result = await request<{ access_token: string; refresh_token?: string }>('/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ role }),
    });
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('ecobridge_access_token', result.access_token);
      if (result.refresh_token) window.localStorage.setItem('ecobridge_refresh_token', result.refresh_token);
    }
    return result;
  },
};

export function getStoredUser() {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem('ecobridge_access_token');
}

export function logout() {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem('ecobridge_access_token');
    window.localStorage.removeItem('ecobridge_refresh_token');
    window.location.assign('/login');
  }
}
