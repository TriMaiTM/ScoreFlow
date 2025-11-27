import React from 'react';
import { View, StyleSheet, StatusBar, Image, Dimensions } from 'react-native';
import { Text, Button, Surface } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

export default function OnboardingScreen() {
  const navigation = useNavigation<any>();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />
      <LinearGradient
        colors={['#0F172A', '#1E293B', '#0F172A']}
        style={StyleSheet.absoluteFill}
      />

      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoText}>⚽</Text>
        </View>

        <Text style={styles.title}>ScoreFlow</Text>
        <Text style={styles.subtitle}>
          Live scores, AI predictions, and real-time match updates in one place.
        </Text>

        <Surface style={styles.card} elevation={4}>
          <Text style={styles.cardText}>
            Track your favorite teams and never miss a goal!
          </Text>
          <Button
            mode="contained"
            onPress={() => navigation.replace('Login')}
            style={styles.button}
            contentStyle={styles.buttonContent}
            buttonColor="#3B82F6"
          >
            Get Started
          </Button>
        </Surface>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  logoContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(59, 130, 246, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.5)',
  },
  logoText: {
    fontSize: 48,
  },
  title: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 48,
    paddingHorizontal: 20,
    lineHeight: 24,
  },
  card: {
    width: '100%',
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  cardText: {
    color: '#CBD5E1',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 24,
  },
  button: {
    borderRadius: 12,
  },
  buttonContent: {
    height: 56,
  },
});
