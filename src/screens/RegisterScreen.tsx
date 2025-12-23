import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, StatusBar, Alert, Image } from 'react-native';
import { Text, TextInput, Button, Surface } from 'react-native-paper';
import { useDispatch } from 'react-redux';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { setCredentials } from '../store/slices/authSlice';
import { AuthService } from '../services/MatchService';
import { RootStackParamList } from '../navigation/AppNavigator';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export default function RegisterScreen() {
    const navigation = useNavigation<NavigationProp>();
    const dispatch = useDispatch();

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleRegister = async () => {
        if (!name || !email || !password || !confirmPassword) {
            setError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await AuthService.register(email, password, name);
            if (response.success) {
                Alert.alert('Registration Successful', 'Please check your email to verify your account before logging in.', [
                    {
                        text: 'OK', onPress: () => {
                            navigation.replace('Login', { email: email });
                        }
                    }
                ]);
            } else {
                setError(response.message || 'Registration failed');
            }
        } catch (err: any) {
            setError(err.message || 'Registration failed. Please try again.');
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
                            label="Full Name"
                            value={name}
                            onChangeText={setName}
                            mode="outlined"
                            style={styles.input}
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

                        <TextInput
                            label="Confirm Password"
                            value={confirmPassword}
                            onChangeText={setConfirmPassword}
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
                            onPress={handleRegister}
                            loading={loading}
                            disabled={loading}
                            style={styles.button}
                            contentStyle={styles.buttonContent}
                            buttonColor="#3B82F6"
                        >
                            Đăng ký
                        </Button>

                        <Button
                            mode="text"
                            onPress={() => navigation.goBack()}
                            style={styles.textButton}
                            textColor="#94A3B8"
                        >
                            Đã có tài khoản? Đăng nhập ngay
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
        marginBottom: 30,
    },
    logo: {
        width: 180,
        height: 50,
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
