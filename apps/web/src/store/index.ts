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
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => {
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
      updateUser: (userData) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      },
    }),
    {
      name: 'mathverse-auth',
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
  enrollment_count?: number;
}

interface CourseState {
  courses: Course[];
  currentCourse: Course | null;
  enrolledCourses: Course[];
  setCourses: (courses: Course[]) => void;
  setCurrentCourse: (course: Course) => void;
  setEnrolledCourses: (courses: Course[]) => void;
  addCourse: (course: Course) => void;
  updateCourse: (id: number, updates: Partial<Course>) => void;
}

export const useCourseStore = create<CourseState>()(
  persist(
    (set, get) => ({
      courses: [],
      currentCourse: null,
      enrolledCourses: [],
      setCourses: (courses) => set({ courses }),
      setCurrentCourse: (course) => set({ currentCourse: course }),
      setEnrolledCourses: (courses) => set({ enrolledCourses: courses }),
      addCourse: (course) => {
        const courses = get().courses;
        set({ courses: [...courses, course] });
      },
      updateCourse: (id, updates) => {
        const courses = get().courses;
        const updatedCourses = courses.map(course =>
          course.id === id ? { ...course, ...updates } : course
        );
        set({ courses: updatedCourses });
      },
    }),
    {
      name: 'mathverse-courses',
    }
  )
);

interface Progress {
  id: number;
  user_id: number;
  lesson_id: number;
  is_completed: boolean;
  completion_percentage: number;
  watch_time: number;
  last_position: number;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
}

interface ProgressState {
  progress: Record<number, Progress>;
  setProgress: (lessonId: number, progress: Progress) => void;
  updateProgress: (lessonId: number, updates: Partial<Progress>) => void;
  getProgress: (lessonId: number) => Progress | null;
}

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      progress: {},
      setProgress: (lessonId, progress) => {
        const currentProgress = get().progress;
        set({ progress: { ...currentProgress, [lessonId]: progress } });
      },
      updateProgress: (lessonId, updates) => {
        const currentProgress = get().progress;
        const existingProgress = currentProgress[lessonId];
        if (existingProgress) {
          set({
            progress: {
              ...currentProgress,
              [lessonId]: { ...existingProgress, ...updates }
            }
          });
        }
      },
      getProgress: (lessonId) => {
        const progress = get().progress;
        return progress[lessonId] || null;
      },
    }),
    {
      name: 'mathverse-progress',
    }
  )
);