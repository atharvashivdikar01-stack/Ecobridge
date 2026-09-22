export type SyncState = 'pending' | 'syncing' | 'synced' | 'failed';

export type SyncRecord<T> = { id: string; payload: T; state: SyncState; attempts: number };
