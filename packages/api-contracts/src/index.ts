export type ApiResponse<T> = { data: T; message?: string; success?: boolean };

export type LotStatus = 'COLLECTED' | 'ACCEPTED' | 'HANDED_OVER' | 'SETTLED';

/** Provider outcomes are explicit so clients never infer that money or data moved. */
export type ProviderOperationStatus =
  | 'CONFIRMED'
  | 'PENDING_PROVIDER_CONFIGURATION';

export type PaymentConfirmationContract = {
  lot_id: string;
  amount_inr: number;
  payment_method: string;
  status: ProviderOperationStatus;
  provider_configured: boolean;
  txn_reference: string | null;
  confirmed_at: string;
};

export type ReadinessContract = {
  status: 'READY';
  checks: Record<string, boolean>;
};

export const IDEMPOTENCY_KEY_HEADER = 'Idempotency-Key' as const;
