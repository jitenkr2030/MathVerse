import api from './api';

export interface Course {
  id: number;
  title: string;
  description?: string;
  level: string;
  subject: string;
  price: number;
  is_free: boolean;
  thumbnail_url?: string;
  is_published: boolean;
  creator_id: number;
  created_at: string;
  updated_at?: string;
  enrollment_count?: number;
  duration?: string;
}

export interface CourseFilters {
  skip?: number;
  limit?: number;
  level?: string;
  subject?: string;
  is_free?: boolean;
  search?: string;
  sort_by?: string;
  order?: 'asc' | 'desc';
  page?: number;
}

export interface CourseCreate {
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
  duration?: string;
  video_url?: string;
  order_index: number;
  is_completed?: boolean;
  course_id?: number;
}

export const courseService = {
  getCourses: async (filters: CourseFilters = {}): Promise<Course[]> => {
    const response = await api.get('/api/courses', { params: filters });
    return response.data;
  },

  getCourse: async (courseId: number): Promise<Course> => {
    const response = await api.get(`/api/courses/${courseId}`);
    return response.data;
  },

  getLessons: async (courseId: number): Promise<Lesson[]> => {
    const response = await api.get(`/api/courses/${courseId}/lessons`);
    return response.data;
  },

  createCourse: async (courseData: CourseCreate): Promise<Course> => {
    const response = await api.post('/api/courses', courseData);
    return response.data;
  },

  updateCourse: async (courseId: number, courseData: Partial<CourseCreate>): Promise<Course> => {
    const response = await api.put(`/api/courses/${courseId}`, courseData);
    return response.data;
  },

  deleteCourse: async (courseId: number): Promise<void> => {
    await api.delete(`/api/courses/${courseId}`);
  },

  enrollCourse: async (courseId: number): Promise<void> => {
    await api.post(`/api/courses/${courseId}/enroll`);
  },

  enrollInCourse: async (courseId: number): Promise<void> => {
    await api.post(`/api/courses/${courseId}/enroll`);
  },

  updateLessonProgress: async (lessonId: number, progress: { last_position: number; completion_percentage: number }): Promise<void> => {
    await api.put(`/api/lessons/${lessonId}/progress`, progress);
  },

  getEnrolledCourses: async (): Promise<Course[]> => {
    const response = await api.get('/api/courses/enrolled');
    return response.data;
  },

  getLesson: async (lessonId: number): Promise<Lesson> => {
    const response = await api.get(`/api/lessons/${lessonId}`);
    return response.data;
  },

  getNextLesson: async (lessonId: number): Promise<Lesson | null> => {
    const response = await api.get(`/api/lessons/${lessonId}/next`);
    return response.data;
  },

  getPreviousLesson: async (lessonId: number): Promise<Lesson | null> => {
    const response = await api.get(`/api/lessons/${lessonId}/previous`);
    return response.data;
  },

  completeLesson: async (lessonId: number): Promise<void> => {
    await api.post(`/api/lessons/${lessonId}/complete`);
  },
};