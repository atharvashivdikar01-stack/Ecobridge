export type DatabaseHealth = {
  connected: boolean;
  checkedAt: string;
};

export function databaseHealth(connected: boolean): DatabaseHealth {
  return { connected, checkedAt: new Date().toISOString() };
}
