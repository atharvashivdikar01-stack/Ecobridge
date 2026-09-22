// ECOBRIDGE Recycler Portal API Client

const API_BASE = typeof window !== 'undefined' ? '' : 'http://127.0.0.1:8000';

export interface UserSummary {
  id: string;
  phone: string;
  full_name: string;
  role: string;
  status: string;
  preferred_language: string;
  avatar_url?: string;
}

export interface AvailableMaterialItem {
  lot_id: string;
  lot_code: string;
  collector_id: string;
  collector_name: string;
  collector_phone: string;
  material_id: string;
  material_code: string;
  material_name: string;
  category_name: string;
  estimated_weight_kg: number;
  verified_weight_kg: number | null;
  ai_classification: string;
  ai_confidence_score: number | null;
  detected_hazard: string;
  hazard_severity: string;
  safety_advisory: string | null;
  required_ppe: string[];
  benchmark_price_per_kg: number;
  min_price_per_kg: number;
  max_price_per_kg: number;
  agreed_price_per_kg: number | null;
  final_value: number | null;
  currency: string;
  status: string;
  origin_address: string | null;
  latitude: number | null;
  longitude: number | null;
  thumbnail_url: string | null;
  images: string[];
  created_at: string;
}

export interface DashboardSummary {
  company_name: string;
  cpcb_registration_no: string;
  operating_status: string;
  is_verified: boolean;
  available_lots_count: number;
  pending_offers_count: number;
  pending_handovers_count: number;
  completed_transactions_count: number;
  total_weight_recycled_kg: number;
  total_payouts_inr: number;
}

export interface RecyclerTransaction {
  transaction_id: string;
  reference_number: string;
  lot_id: string;
  lot_code: string;
  collector_id: string;
  collector_name: string;
  collector_phone: string;
  material_name: string;
  verified_weight_kg: number;
  agreed_price_per_kg: number;
  total_amount: number;
  currency: string;
  payment_method: string;
  payment_status: string;
  gateway_reference: string | null;
  weighbridge_slip: string | null;
  custody_hash: string | null;
  handed_over_at: string | null;
  settled_at: string | null;
  created_at: string;
}

export interface RecyclerLedger {
  transactions: RecyclerTransaction[];
  total_volume_kg: number;
  total_disbursed_inr: number;
  total_transactions: number;
}

// Token management in browser
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('ecobridge_recycler_token');
}

export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('ecobridge_recycler_token', token);
  }
}

export function getStoredUser(): UserSummary | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem('ecobridge_recycler_user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user: UserSummary): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('ecobridge_recycler_user', JSON.stringify(user));
  }
}

export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('ecobridge_recycler_token');
    localStorage.removeItem('ecobridge_recycler_user');
    window.location.href = '/login';
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE}/api/v1${endpoint}`;
  try {
    const res = await fetch(url, { ...options, headers });
    const json = await res.json();
    if (!res.ok || json.success === false) {
      const errMsg = json?.error?.message || `Request failed with status ${res.status}`;
      throw new Error(errMsg);
    }
    return json.data as T;
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

// API methods
export const api = {
  demoLogin: async (role: 'VERIFIED_RECYCLER' | 'UNVERIFIED_RECYCLER' | 'COLLECTOR') => {
    const data = await request<{ access_token: string; user: UserSummary }>('/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ role }),
    });
    setToken(data.access_token);
    setStoredUser(data.user);
    return data;
  },

  getMe: async () => {
    return request<UserSummary>('/auth/me');
  },

  getDashboard: async () => {
    return request<DashboardSummary>('/recycler-portal/dashboard');
  },

  getMaterials: async (params?: { status?: string; material_type?: string; hazardous_only?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set('status', params.status);
    if (params?.material_type) q.set('material_type', params.material_type);
    if (params?.hazardous_only) q.set('hazardous_only', 'true');
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<{ items: AvailableMaterialItem[]; total: number }>(`/recycler-portal/materials${qs}`);
  },

  getMaterialDetail: async (lotId: string) => {
    return request<AvailableMaterialItem>(`/recycler-portal/materials/${lotId}`);
  },

  acceptOffer: async (lotId: string, agreedPricePerKg: number, notes?: string) => {
    return request<AvailableMaterialItem>(`/recycler-portal/lots/${lotId}/accept`, {
      method: 'POST',
      body: JSON.stringify({ agreed_price_per_kg: agreedPricePerKg, notes }),
    });
  },

  confirmHandover: async (
    lotId: string,
    payload: {
      weighbridge_slip_number: string;
      verified_weight_kg: number;
      weighbridge_gross_kg?: number;
      weighbridge_tare_kg?: number;
      scale_calibration_id?: string;
    }
  ) => {
    return request<AvailableMaterialItem>(`/recycler-portal/lots/${lotId}/handover`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  recordPayment: async (
    lotId: string,
    payload: {
      payment_method: 'CASH' | 'UPI' | 'IMPS' | 'BANK_TRANSFER';
      amount: number;
      gateway_reference?: string;
      notes?: string;
    }
  ) => {
    return request<RecyclerTransaction>(`/recycler-portal/lots/${lotId}/payment`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getLedger: async () => {
    return request<RecyclerLedger>('/recycler-portal/ledger');
  },
};
