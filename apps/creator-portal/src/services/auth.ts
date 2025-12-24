import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role?: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/creators/login', credentials);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('creator-token', response.access_token);
    }
    
    return response;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/creators/register', data);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('creator-token', response.access_token);
    }
    
    return response;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/creators/logout');
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('creator-token');
      }
    }
  },

  async getCurrentUser(): Promise<User> {
    return api.get<User>('/creators/me');
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    return api.put<User>('/creators/me', data);
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/creators/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('creator-token');
  },

  isAuthenticated(): boolean {
    return this.getToken() !== null;
  },
};

export default authService;
