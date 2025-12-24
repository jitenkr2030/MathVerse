import { api } from './api';
import { UserStats, User } from '@/types';

export const userService = {
  async getProfile(): Promise<User> {
    return api.get<User>('/api/users/profile');
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    return api.put<User>('/api/users/profile', data);
  },

  async getStats(): Promise<UserStats> {
    return api.get<UserStats>('/api/users/stats');
  },

  async getEnrollments(page = 1, perPage = 20, includeCompleted = false): Promise<any> {
    return api.get('/api/users/enrollments', {
      page,
      per_page: perPage,
      include_completed: includeCompleted,
    });
  },

  async deleteAccount(): Promise<void> {
    await api.delete('/api/users/account');
  },
};

export default userService;
