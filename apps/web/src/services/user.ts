import { api } from './api';
import { UserStats, User } from '@/types';

export const userService = {
  async getProfile(): Promise<User> {
    const response = await api.get<User>('/api/users/profile');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/api/users/profile', data);
    return response.data;
  },

  async getStats(): Promise<UserStats> {
    const response = await api.get<UserStats>('/api/users/stats');
    return response.data;
  },

  async getEnrollments(page = 1, perPage = 20, includeCompleted = false): Promise<any> {
    const response = await api.get('/api/users/enrollments', {
      params: {
        page,
        per_page: perPage,
        include_completed: includeCompleted,
      },
    });
    return response.data;
  },

  async deleteAccount(): Promise<void> {
    await api.delete('/api/users/account');
  },
};

export default userService;
