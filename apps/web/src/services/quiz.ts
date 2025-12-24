import { api } from './api';
import { Quiz, QuizAttempt, QuizSubmission } from '@/types';

export const quizService = {
  async getQuiz(quizId: number): Promise<Quiz> {
    return api.get<Quiz>(`/api/quizzes/${quizId}`);
  },

  async getQuizPreview(quizId: number): Promise<Quiz> {
    return api.get<Quiz>(`/api/quizzes/${quizId}/preview`);
  },

  async createQuiz(data: Partial<Quiz>): Promise<Quiz> {
    return api.post<Quiz>('/api/quizzes/', data);
  },

  async updateQuiz(quizId: number, data: Partial<Quiz>): Promise<Quiz> {
    return api.put<Quiz>(`/api/quizzes/${quizId}`, data);
  },

  async deleteQuiz(quizId: number): Promise<void> {
    await api.delete(`/api/quizzes/${quizId}`);
  },

  async submitQuizAttempt(quizId: number, submission: QuizSubmission): Promise<QuizAttempt> {
    return api.post<QuizAttempt>(`/api/quizzes/${quizId}/attempt`, submission);
  },

  async getQuizAttempts(quizId: number): Promise<QuizAttempt[]> {
    return api.get<QuizAttempt[]>(`/api/quizzes/${quizId}/attempts`);
  },

  async getBestAttempt(quizId: number): Promise<{ best_attempt: QuizAttempt | null; message?: string }> {
    return api.get(`/api/quizzes/${quizId}/best-attempt`);
  },

  // Questions
  async addQuestion(quizId: number, data: Partial<any>): Promise<any> {
    return api.post(`/api/quizzes/${quizId}/questions`, data);
  },
};

export default quizService;
