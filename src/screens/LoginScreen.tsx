import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, StatusBar, Image } from 'react-native';
import { Text, TextInput, Button, Surface } from 'react-native-paper';
import { useDispatch } from 'react-redux';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';

import { setCredentials } from '../store/slices/authSlice';
import { setUserProfile } from '../store/slices/userSlice';
import { AuthService } from '../services/MatchService';

export default function LoginScreen() {
  const dispatch = useDispatch();
  const route = useRoute<any>();
  const [email, setEmail] = useState(route.params?.email || '');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigation = useNavigation<any>();

  const handleLogin = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await AuthService.login(email, password);
      if (response.success) {
        if (Platform.OS !== 'web') {
          await import('expo-secure-store').then(SecureStore =>
            SecureStore.setItemAsync('auth_token', response.data.token)
          );
        } else {
          localStorage.setItem('auth_token', response.data.token);
        }

        dispatch(setCredentials(response.data));
        if (response.data.profile) {
          dispatch(setUserProfile(response.data.profile));
        }
        navigation.reset({
          index: 0,
          routes: [{ name: 'Main' }],
        });
      }
    } catch (err) {
      setError('Đăng nhập thất bại. Kiểm tra lại email / mật khẩu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <View style={styles.content}>
          <View style={styles.header}>
            <Image
              source={require('../../assets/logo-scoreflow.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>

          <Surface style={styles.formCard} elevation={4}>
            <TextInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              style={styles.input}
              autoCapitalize="none"
              keyboardType="email-address"
              textColor="#fff"
              theme={{
                colors: {
                  primary: '#3B82F6',
                  outline: 'rgba(255,255,255,0.2)',
                  background: 'rgba(30, 41, 59, 0.5)',
                  onSurfaceVariant: '#94A3B8',
                }
              }}
            />
            <TextInput
              label="Password"
              value={password}
              onChangeText={setPassword}
              mode="outlined"
              style={styles.input}
              secureTextEntry
              textColor="#fff"
              theme={{
                colors: {
                  primary: '#3B82F6',
                  outline: 'rgba(255,255,255,0.2)',
                  background: 'rgba(30, 41, 59, 0.5)',
                  onSurfaceVariant: '#94A3B8',
                }
              }}
            />

            {error ? <Text style={styles.error}>{error}</Text> : null}

            <Button
              mode="contained"
              onPress={handleLogin}
              loading={loading}
              disabled={loading}
              style={styles.button}
              contentStyle={styles.buttonContent}
              buttonColor="#3B82F6"
            >
              Đăng nhập
            </Button>

            <Button
              mode="text"
              onPress={() => navigation.navigate('Register')}
              style={styles.textButton}
              textColor="#94A3B8"
            >
              Tạo tài khoản mới
            </Button>
          </Surface>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  keyboardView: {
    flex: 1,
    justifyContent: 'center',
  },
  content: {
    padding: 20,
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 200,
    height: 60,
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
  },
  formCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  input: {
    marginBottom: 16,
    backgroundColor: 'transparent',
  },
  button: {
    marginTop: 8,
    borderRadius: 12,
  },
  buttonContent: {
    height: 48,
  },
  textButton: {
    marginTop: 16,
  },
  error: {
    color: '#EF4444',
    marginBottom: 16,
    textAlign: 'center',
  },
});
