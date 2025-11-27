import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

export class CacheService {
  private static readonly CACHE_PREFIX = '@scoreflow_cache:';

  static async set<T>(
    key: string,
    data: T,
    ttl: number = 5 * 60 * 1000 // Default 5 minutes
  ): Promise<void> {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
    };
    await AsyncStorage.setItem(
      `${this.CACHE_PREFIX}${key}`,
      JSON.stringify(entry)
    );
  }

  static async get<T>(key: string): Promise<T | null> {
    try {
      const value = await AsyncStorage.getItem(`${this.CACHE_PREFIX}${key}`);
      if (!value) return null;

      const entry: CacheEntry<T> = JSON.parse(value);
      const now = Date.now();

      // Check if cache is expired
      if (now - entry.timestamp > entry.ttl) {
        await this.delete(key);
        return null;
      }

      return entry.data;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }

  static async delete(key: string): Promise<void> {
    await AsyncStorage.removeItem(`${this.CACHE_PREFIX}${key}`);
  }

  static async clear(): Promise<void> {
    const keys = await AsyncStorage.getAllKeys();
    const cacheKeys = keys.filter((key) => key.startsWith(this.CACHE_PREFIX));
    await AsyncStorage.multiRemove(cacheKeys);
  }

  static async isOnline(): Promise<boolean> {
    const netInfo = await NetInfo.fetch();
    return netInfo.isConnected ?? false;
  }
}

// Offline queue for actions that need to be synced
export class OfflineQueue {
  private static readonly QUEUE_KEY = '@scoreflow_offline_queue';

  static async addToQueue(action: {
    type: string;
    payload: unknown;
    timestamp: number;
  }): Promise<void> {
    const queue = await this.getQueue();
    queue.push(action);
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
  }

  static async getQueue(): Promise<Array<{
    type: string;
    payload: unknown;
    timestamp: number;
  }>> {
    try {
      const value = await AsyncStorage.getItem(this.QUEUE_KEY);
      return value ? JSON.parse(value) : [];
    } catch {
      return [];
    }
  }

  static async clearQueue(): Promise<void> {
    await AsyncStorage.removeItem(this.QUEUE_KEY);
  }

  static async processQueue(
    processor: (action: { type: string; payload: unknown }) => Promise<void>
  ): Promise<void> {
    const queue = await this.getQueue();
    
    for (const action of queue) {
      try {
        await processor(action);
      } catch (error) {
        console.error('Failed to process queued action:', error);
        // Keep failed actions in queue
        return;
      }
    }

    await this.clearQueue();
  }
}
