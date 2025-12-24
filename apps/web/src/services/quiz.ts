import { api } from './api';
import { Quiz, QuizAttempt, QuizSubmission } from '@/types';

export const quizService = {
  async getQuiz(quizId: number): Promise<Quiz> {
    const response = await api.get<Quiz>(`/api/quizzes/${quizId}`);
    return response.data;
  },

  async getQuizPreview(quizId: number): Promise<Quiz> {
    const response = await api.get<Quiz>(`/api/quizzes/${quizId}/preview`);
    return response.data;
  },

  async createQuiz(data: Partial<Quiz>): Promise<Quiz> {
    const response = await api.post<Quiz>('/api/quizzes/', data);
    return response.data;
  },

  async updateQuiz(quizId: number, data: Partial<Quiz>): Promise<Quiz> {
    const response = await api.put<Quiz>(`/api/quizzes/${quizId}`, data);
    return response.data;
  },

  async deleteQuiz(quizId: number): Promise<void> {
    await api.delete(`/api/quizzes/${quizId}`);
  },

  async submitQuizAttempt(quizId: number, submission: QuizSubmission): Promise<QuizAttempt> {
    const response = await api.post<QuizAttempt>(`/api/quizzes/${quizId}/attempt`, submission);
    return response.data;
  },

  async getQuizAttempts(quizId: number): Promise<QuizAttempt[]> {
    const response = await api.get<QuizAttempt[]>(`/api/quizzes/${quizId}/attempts`);
    return response.data;
  },

  async getBestAttempt(quizId: number): Promise<{ best_attempt: QuizAttempt | null; message?: string }> {
    const response = await api.get(`/api/quizzes/${quizId}/best-attempt`);
    return response.data;
  },

  // Questions
  async addQuestion(quizId: number, data: Partial<any>): Promise<any> {
    const response = await api.post(`/api/quizzes/${quizId}/questions`, data);
    return response.data;
  },
};

export default quizService;
