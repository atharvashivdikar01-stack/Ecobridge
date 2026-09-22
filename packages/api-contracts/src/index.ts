export type ApiResponse<T> = { data: T; message?: string; success?: boolean };

export type LotStatus = 'COLLECTED' | 'ACCEPTED' | 'HANDED_OVER' | 'SETTLED';
