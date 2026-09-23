export interface AdminSummaryData {
  collectors_active: number;
  verified_recyclers: number;
  lots_created: number;
  transactions: number;
  formalized_ewaste_kg: number;
  traceable_lots_pct: number;
  traceable_lots_count: number;
  total_disbursed_inr: number;
  database_engine?: string;
  live_status?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: { code: string; message: string } | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export const adminApi = {
  getSummary: async (): Promise<AdminSummaryData> => {
    const res = await fetch(`${API_BASE}/admin/summary`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json: ApiResponse<AdminSummaryData> = await res.json();
    return json.data;
  },

  getLots: async () => {
    const res = await fetch(`${API_BASE}/admin/lots`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data.items;
  },

  getCollectors: async () => {
    const res = await fetch(`${API_BASE}/admin/collectors`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data.items;
  },

  getRecyclers: async () => {
    const res = await fetch(`${API_BASE}/admin/recyclers`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data.items;
  },

  getTransactions: async () => {
    const res = await fetch(`${API_BASE}/admin/transactions`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data.items;
  },
};
