import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
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

interface CreatorStats {
  totalCourses: number;
  publishedCourses: number;
  totalStudents: number;
  totalEarnings: number;
  averageRating: number;
  totalViews: number;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,
      login: (user, token) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('creator-token', token);
        }
        set({ user, token, isAuthenticated: true, isLoading: false });
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('creator-token');
        }
        set({ user: null, token: null, isAuthenticated: false, isLoading: false });
      },
      updateUser: (userData) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      },
      checkAuth: async () => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('creator-token') : null;
        if (!token) {
          set({ isAuthenticated: false, isLoading: false });
          return;
        }

        try {
          const response = await fetch('/api/creators/me', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const user = await response.json();
            set({ user, token, isAuthenticated: true, isLoading: false });
          } else {
            localStorage.removeItem('creator-token');
            set({ user: null, token: null, isAuthenticated: false, isLoading: false });
          }
        } catch (error) {
          localStorage.removeItem('creator-token');
          set({ user: null, token: null, isAuthenticated: false, isLoading: false });
        }
      },
    }),
    {
      name: 'mathverse-creator-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

interface Course {
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
  lessons_count?: number;
  enrollment_count?: number;
  average_rating?: number;
}

interface CourseState {
  courses: Course[];
  currentCourse: Course | null;
  isLoading: boolean;
  setCourses: (courses: Course[]) => void;
  setCurrentCourse: (course: Course | null) => void;
  addCourse: (course: Course) => void;
  updateCourse: (id: number, updates: Partial<Course>) => void;
  deleteCourse: (id: number) => void;
}

export const useCourseStore = create<CourseState>()((set, get) => ({
  courses: [],
  currentCourse: null,
  isLoading: false,
  setCourses: (courses) => set({ courses }),
  setCurrentCourse: (course) => set({ currentCourse: course }),
  addCourse: (course) => {
    const courses = get().courses;
    set({ courses: [course, ...courses] });
  },
  updateCourse: (id, updates) => {
    const courses = get().courses;
    const updatedCourses = courses.map((course) =>
      course.id === id ? { ...course, ...updates } : course
    );
    set({ courses: updatedCourses });
  },
  deleteCourse: (id) => {
    const courses = get().courses;
    set({ courses: courses.filter((course) => course.id !== id) });
  },
}));

interface CreatorState {
  stats: CreatorStats;
  setStats: (stats: CreatorStats) => void;
}

export const useCreatorStore = create<CreatorState>()((set) => ({
  stats: {
    totalCourses: 0,
    publishedCourses: 0,
    totalStudents: 0,
    totalEarnings: 0,
    averageRating: 0,
    totalViews: 0,
  },
  setStats: (stats) => set({ stats }),
}));
