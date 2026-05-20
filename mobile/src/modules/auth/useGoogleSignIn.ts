import { useEffect, useState } from 'react';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import type { AuthResponse } from '../../types';

WebBrowser.maybeCompleteAuthSession();

const API_BASE = 'http://localhost:8000/api/v1';

export interface GoogleSignInConfig {
  clientId?: string;
  androidClientId?: string;
  iosClientId?: string;
  webClientId?: string;
}

interface UseGoogleSignInResult {
  promptAsync: () => Promise<void>;
  request: ReturnType<typeof Google.useIdTokenAuthRequest>[0];
  authResponse: AuthResponse | null;
  isLoading: boolean;
  error: string | null;
}

export function useGoogleSignIn(
  config: GoogleSignInConfig,
  backendUrl?: string,
): UseGoogleSignInResult {
  const baseUrl = backendUrl ?? API_BASE;
  const [authResponse, setAuthResponse] = useState<AuthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [request, response, googlePrompt] = Google.useIdTokenAuthRequest({
    clientId: config.clientId,
    androidClientId: config.androidClientId,
    iosClientId: config.iosClientId,
    webClientId: config.webClientId,
  });

  const promptAsync = async () => {
    setError(null);
    setAuthResponse(null);
    setIsLoading(true);
    try {
      await googlePrompt();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start Google sign-in');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (response?.type !== 'success' || !response.params?.id_token) {
      return;
    }

    const idToken = response.params.id_token;

    (async () => {
      try {
        const res = await fetch(`${baseUrl}/auth/google`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id_token: idToken }),
        });

        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new Error(
            body?.detail ?? `Sign-in failed with status ${res.status}`,
          );
        }

        const data: AuthResponse = await res.json();
        setAuthResponse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication failed');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [response, baseUrl]);

  return { promptAsync, request, authResponse, isLoading, error };
}
