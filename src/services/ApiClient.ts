import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// TODO: Thay YOUR_IP bằng IP máy của bạn (chạy: ipconfig)
// Ví dụ: 'http://192.168.1.100:8000/api/v1'
// TODO: Thay YOUR_IP bằng IP máy của bạn (chạy: ipconfig) ở dòng dưới
// Ví dụ: const API_BASE_URL = 'http://192.168.1.5:8000/api/v1';
// Production Render URL
const API_BASE_URL = 'https://scoreflow-backend-5wu8.onrender.com/api/v1';
const API_TIMEOUT = 15000; // Tăng timeout cho production

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        try {
          let token: string | null = null;
          if (Platform.OS !== 'web') {
            token = await SecureStore.getItemAsync('auth_token');
          } else {
            // On web, we can use localStorage or just skip for now
            token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
          }

          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.log('Error getting token:', error);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, logout user
          try {
            if (Platform.OS !== 'web') {
              await SecureStore.deleteItemAsync('auth_token');
            } else {
              if (typeof localStorage !== 'undefined') localStorage.removeItem('auth_token');
            }
          } catch (err) {
            console.log('Error deleting token:', err);
          }
          // Dispatch logout action or navigate to login
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();
