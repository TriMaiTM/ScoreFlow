import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export class NotificationService {
  static async initialize() {
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'Default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    const token = await this.registerForPushNotificationsAsync();
    if (token) {
      await AsyncStorage.setItem('push_token', token);
      // Send token to backend
      // await apiClient.post('/users/push-token', { token });
    }

    return token;
  }

  static async registerForPushNotificationsAsync(): Promise<string | undefined> {
    let token;

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    if (Device.isDevice) {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return;
      }
      
      token = (await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      })).data;
    } else {
      console.log('Must use physical device for Push Notifications');
    }

    return token;
  }

  static async scheduleMatchNotification(
    matchId: number,
    homeTeam: string,
    awayTeam: string,
    matchDate: Date,
    type: 'before' | 'start' | 'goal' | 'end'
  ) {
    let trigger;
    let title = '';
    let body = '';

    switch (type) {
      case 'before':
        // 30 minutes before match
        trigger = new Date(matchDate.getTime() - 30 * 60 * 1000);
        title = '⚽ Match Starting Soon';
        body = `${homeTeam} vs ${awayTeam} starts in 30 minutes`;
        break;
      case 'start':
        trigger = matchDate;
        title = '🏁 Match Started';
        body = `${homeTeam} vs ${awayTeam} has started`;
        break;
      case 'goal':
        // Immediate notification (from backend webhook)
        title = '⚽ GOAL!';
        body = `Goal in ${homeTeam} vs ${awayTeam}`;
        return await Notifications.scheduleNotificationAsync({
          content: { title, body },
          trigger: null, // Immediate
        });
      case 'end':
        title = '🏁 Match Ended';
        body = `${homeTeam} vs ${awayTeam} has finished`;
        break;
    }

    if (trigger instanceof Date && trigger > new Date()) {
      return await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data: { matchId, type },
        },
        trigger,
      });
    }
  }

  static async cancelMatchNotifications(matchId: number) {
    const scheduledNotifications = await Notifications.getAllScheduledNotificationsAsync();
    
    for (const notification of scheduledNotifications) {
      if (notification.content.data?.matchId === matchId) {
        await Notifications.cancelScheduledNotificationAsync(notification.identifier);
      }
    }
  }

  static async cancelAllNotifications() {
    await Notifications.cancelAllScheduledNotificationsAsync();
  }

  static addNotificationReceivedListener(
    callback: (notification: Notifications.Notification) => void
  ) {
    return Notifications.addNotificationReceivedListener(callback);
  }

  static addNotificationResponseReceivedListener(
    callback: (response: Notifications.NotificationResponse) => void
  ) {
    return Notifications.addNotificationResponseReceivedListener(callback);
  }
}
