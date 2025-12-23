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
}

export interface CourseFilters {
  skip?: number;
  limit?: number;
  level?: string;
  subject?: string;
  is_free?: boolean;
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

export const courseService = {
  getCourses: async (filters: CourseFilters = {}): Promise<Course[]> => {
    const response = await api.get('/api/courses', { params: filters });
    return response.data;
  },

  getCourse: async (courseId: number): Promise<Course> => {
    const response = await api.get(`/api/courses/${courseId}`);
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
};