import api from './api';

export interface Course {
  id: number;
  title: string;
  description?: string;
  level: string;
  subject: string;
  price: number;
  is_free: boolean;
  is_published: boolean;
  thumbnail_url?: string;
  lessons_count?: number;
  enrollment_count?: number;
  average_rating?: number;
  created_at: string;
  updated_at?: string;
}

export interface CourseFilters {
  search?: string;
  level?: string;
  subject?: string;
  is_published?: boolean;
  is_free?: boolean;
  page?: number;
  limit?: number;
}

export interface CreateCourseData {
  title: string;
  description?: string;
  level: string;
  subject: string;
  price?: number;
  is_free?: boolean;
  thumbnail_url?: string;
}

export interface Lesson {
  id: number;
  title: string;
  description?: string;
  course_id: number;
  video_url?: string;
  animation_scene_path?: string;
  animation_class?: string;
  content?: string;
  duration: number;
  order_index: number;
  is_published: boolean;
  is_free_preview: boolean;
}

export interface Animation {
  id: number;
  title: string;
  scene_class: string;
  scene_path: string;
  status: 'draft' | 'queued' | 'processing' | 'completed' | 'failed';
  quality: string;
  duration: number;
  thumbnail_url?: string;
  render_time?: number;
  output_url?: string;
  created_at: string;
  updated_at?: string;
}

export const creatorService = {
  // Courses
  async getCourses(filters?: CourseFilters): Promise<Course[]> {
    return api.get<Course[]>('/creators/courses', filters);
  },

  async getCourse(courseId: number): Promise<Course> {
    return api.get<Course>(`/creators/courses/${courseId}`);
  },

  async createCourse(data: CreateCourseData): Promise<Course> {
    return api.post<Course>('/creators/courses', data);
  },

  async updateCourse(courseId: number, data: Partial<Course>): Promise<Course> {
    return api.put<Course>(`/creators/courses/${courseId}`, data);
  },

  async deleteCourse(courseId: number): Promise<void> {
    await api.delete(`/creators/courses/${courseId}`);
  },

  async publishCourse(courseId: number): Promise<Course> {
    return api.post<Course>(`/creators/courses/${courseId}/publish`);
  },

  async unpublishCourse(courseId: number): Promise<Course> {
    return api.post<Course>(`/creators/courses/${courseId}/unpublish`);
  },

  // Lessons
  async getLessons(courseId: number): Promise<Lesson[]> {
    return api.get<Lesson[]>(`/creators/courses/${courseId}/lessons`);
  },

  async getLesson(lessonId: number): Promise<Lesson> {
    return api.get<Lesson>(`/creators/lessons/${lessonId}`);
  },

  async createLesson(courseId: number, data: Partial<Lesson>): Promise<Lesson> {
    return api.post<Lesson>(`/creators/courses/${courseId}/lessons`, data);
  },

  async updateLesson(lessonId: number, data: Partial<Lesson>): Promise<Lesson> {
    return api.put<Lesson>(`/creators/lessons/${lessonId}`, data);
  },

  async deleteLesson(lessonId: number): Promise<void> {
    await api.delete(`/creators/lessons/${lessonId}`);
  },

  async reorderLessons(courseId: number, lessonIds: number[]): Promise<void> {
    await api.post(`/creators/courses/${courseId}/lessons/reorder`, { lesson_ids: lessonIds });
  },

  // Animations
  async getAnimations(status?: string): Promise<Animation[]> {
    return api.get<Animation[]>('/creators/animations', status ? { status } : undefined);
  },

  async getAnimation(animationId: number): Promise<Animation> {
    return api.get<Animation>(`/creators/animations/${animationId}`);
  },

  async createAnimation(data: Partial<Animation>): Promise<Animation> {
    return api.post<Animation>('/creators/animations', data);
  },

  async updateAnimation(animationId: number, data: Partial<Animation>): Promise<Animation> {
    return api.put<Animation>(`/creators/animations/${animationId}`, data);
  },

  async deleteAnimation(animationId: number): Promise<void> {
    await api.delete(`/creators/animations/${animationId}`);
  },

  async renderAnimation(animationId: number): Promise<Animation> {
    return api.post<Animation>(`/creators/animations/${animationId}/render`);
  },

  // Earnings
  async getEarningsStats(period?: string): Promise<any> {
    return api.get('/creators/earnings/stats', { period });
  },

  async getTransactions(period?: string): Promise<any[]> {
    return api.get('/creators/earnings/transactions', { period });
  },

  async requestPayout(amount: number): Promise<any> {
    return api.post('/creators/earnings/payout', { amount });
  },

  // Analytics
  async getCourseAnalytics(courseId: number): Promise<any> {
    return api.get(`/creators/courses/${courseId}/analytics`);
  },

  async getOverallAnalytics(period?: string): Promise<any> {
    return api.get('/creators/analytics', { period });
  },

  // Upload
  async uploadFile(file: File, type: 'thumbnail' | 'video' | 'animation'): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const token = typeof window !== 'undefined' ? localStorage.getItem('creator-token') : null;

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  },
};

export default creatorService;
