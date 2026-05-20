/**
 * Unit tests for authStorage.ts
 *
 * Covers:
 *   - setToken saves to SecureStore with correct key
 *   - getToken returns saved token
 *   - getToken returns null on error
 *   - removeToken deletes from SecureStore
 *   - Roundtrip: set → get → remove → get returns null
 *
 * Requires Jest with mocked expo-secure-store.
 */

import * as SecureStore from 'expo-secure-store';
import { getToken, setToken, removeToken } from '../authStorage';

// ── Mock expo-secure-store ─────────────────────────────────────────────

jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

const mockedSecureStore = SecureStore as jest.Mocked<typeof SecureStore>;

const TOKEN_KEY = 'folia_auth_token';

beforeEach(() => {
  jest.clearAllMocks();
});

// ── setToken ───────────────────────────────────────────────────────────

describe('setToken', () => {
  it('TP-1: saves token to SecureStore with correct key', async () => {
    await setToken('test-jwt-token');

    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledTimes(1);
    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith(
      TOKEN_KEY,
      'test-jwt-token',
    );
  });

  it('TP-1: stores an empty string token', async () => {
    await setToken('');

    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith(TOKEN_KEY, '');
  });
});

// ── getToken ───────────────────────────────────────────────────────────

describe('getToken', () => {
  it('TP-1: returns saved token from SecureStore', async () => {
    mockedSecureStore.getItemAsync.mockResolvedValue('stored-jwt');

    const token = await getToken();

    expect(token).toBe('stored-jwt');
    expect(mockedSecureStore.getItemAsync).toHaveBeenCalledWith(TOKEN_KEY);
  });

  it('TP-1: returns null when no token is stored', async () => {
    mockedSecureStore.getItemAsync.mockResolvedValue(null);

    const token = await getToken();

    expect(token).toBeNull();
  });

  it('TP-1: returns null when SecureStore throws an error', async () => {
    mockedSecureStore.getItemAsync.mockRejectedValue(
      new Error('Keychain read failed'),
    );

    const token = await getToken();

    expect(token).toBeNull();
  });
});

// ── removeToken ────────────────────────────────────────────────────────

describe('removeToken', () => {
  it('TP-1: deletes token from SecureStore', async () => {
    await removeToken();

    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledTimes(1);
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith(TOKEN_KEY);
  });

  it('TP-1: does not throw when removing non-existent token', async () => {
    mockedSecureStore.deleteItemAsync.mockResolvedValue(undefined);

    await expect(removeToken()).resolves.toBeUndefined();
  });
});

// ── Roundtrip ──────────────────────────────────────────────────────────

describe('token roundtrip', () => {
  it('TP-1: set → get → remove → get returns null', async () => {
    // Simulate the full lifecycle
    mockedSecureStore.getItemAsync
      .mockResolvedValueOnce('roundtrip-token')  // after set, the get returns it
      .mockResolvedValueOnce(null);               // after remove, the get returns null

    await setToken('roundtrip-token');
    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith(
      TOKEN_KEY,
      'roundtrip-token',
    );

    const stored = await getToken();
    expect(stored).toBe('roundtrip-token');

    await removeToken();
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith(TOKEN_KEY);

    const afterRemove = await getToken();
    expect(afterRemove).toBeNull();
  });
});
