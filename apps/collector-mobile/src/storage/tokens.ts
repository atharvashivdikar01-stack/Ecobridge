import * as SecureStore from 'expo-secure-store';

const ACCESS_TOKEN = 'ecobridge.accessToken';
const REFRESH_TOKEN = 'ecobridge.refreshToken';
export type Tokens = { accessToken: string; refreshToken: string };

export async function getTokens(): Promise<Tokens | null> {
  const [accessToken, refreshToken] = await Promise.all([SecureStore.getItemAsync(ACCESS_TOKEN), SecureStore.getItemAsync(REFRESH_TOKEN)]);
  return accessToken && refreshToken ? { accessToken, refreshToken } : null;
}
export async function saveTokens(tokens: Tokens): Promise<void> {
  await Promise.all([SecureStore.setItemAsync(ACCESS_TOKEN, tokens.accessToken), SecureStore.setItemAsync(REFRESH_TOKEN, tokens.refreshToken)]);
}
export async function clearTokens(): Promise<void> {
  await Promise.all([SecureStore.deleteItemAsync(ACCESS_TOKEN), SecureStore.deleteItemAsync(REFRESH_TOKEN)]);
}
