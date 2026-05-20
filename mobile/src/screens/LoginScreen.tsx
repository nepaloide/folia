import React, { useEffect } from 'react';
import { StyleSheet, Text, TouchableOpacity, View, ActivityIndicator } from 'react-native';
import { useGoogleSignIn } from '../modules/auth/useGoogleSignIn';
import { setToken } from '../modules/auth/authStorage';

interface LoginScreenProps {
  onAuthChange: () => void;
}

export default function LoginScreen({ onAuthChange }: LoginScreenProps) {
  const { promptAsync, request, authResponse, isLoading, error } = useGoogleSignIn({
    clientId: 'placeholder-local-dev',
  });

  useEffect(() => {
    if (!authResponse) return;

    (async () => {
      await setToken(authResponse.access_token);
      onAuthChange();
    })();
  }, [authResponse, onAuthChange]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Folía</Text>
      <Text style={styles.subtitle}>Tu diario de plantas</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TouchableOpacity
        style={[styles.button, (!request || isLoading) && styles.buttonDisabled]}
        disabled={!request || isLoading}
        onPress={promptAsync}
        activeOpacity={0.8}
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Sign in with Google</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 48,
  },
  button: {
    flexDirection: 'row',
    backgroundColor: '#4285F4',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 240,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  error: {
    color: '#d32f2f',
    marginBottom: 16,
    textAlign: 'center',
  },
});
