import { API_BASE_URL } from '../config/api';
import type { UserResponse, LoginRequest, TokenResponse } from '../types/api';

// Re-export types for backward compatibility
export type { UserResponse, LoginRequest, TokenResponse };

// Re-export for compatibility
export type { UserResponse };

class ApiService {
  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setAuthTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  clearAuthTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const token = this.getAuthToken();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include',
      });

      if (response.status === 401) {
        // Token might be expired, try to refresh
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry the request with new token
          const newToken = this.getAuthToken();
          if (newToken) {
            headers['Authorization'] = `Bearer ${newToken}`;
            const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
              ...options,
              headers,
              credentials: 'include',
            });
            if (!retryResponse.ok) {
              const errorText = await retryResponse.text();
              throw new Error(`API error: ${retryResponse.statusText} - ${errorText}`);
            }
            return retryResponse.json();
          }
        }
        // If refresh failed, clear tokens and throw
        this.clearAuthTokens();
        throw new Error('Authentication failed');
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
      }

      return response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(`Network error: Unable to connect to ${API_BASE_URL}. Is the backend running?`);
      }
      throw error;
    }
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data: TokenResponse = await response.json();
    this.setAuthTokens(data.access_token, data.refresh_token);
    return data;
  }

  async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        return false;
      }

      const data: TokenResponse = await response.json();
      this.setAuthTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  async getCurrentUser(): Promise<UserResponse> {
    return this.request<UserResponse>('/auth/me');
  }

  async register(email: string, password: string, name: string): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(error.detail || 'Registration failed');
    }

    const data: TokenResponse = await response.json();
    this.setAuthTokens(data.access_token, data.refresh_token);
    return data;
  }

  async loginWithGoogle(googleToken: string): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/google/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ token: googleToken }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Google login failed' }));
      throw new Error(error.detail || 'Google login failed');
    }

    const data: TokenResponse = await response.json();
    this.setAuthTokens(data.access_token, data.refresh_token);
    return data;
  }

  // Generic API methods
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiService = new ApiService();

