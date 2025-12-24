// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  created_at: string;
}

export type UserRole = 'student' | 'teacher' | 'creator' | 'admin';

// Authentication Types
export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Course Types
export interface Course {
  id: number;
  title: string;
  description?: string;
  level: CourseLevel;
  subject: string;
  thumbnail_url?: string;
  creator_id: number;
  price: number;
  is_free: boolean;
  is_published: boolean;
  created_at: string;
  updated_at?: string;
  lessons_count?: number;
  enrollments_count?: number;
  average_rating?: number;
}

export type CourseLevel = 'primary' | 'secondary' | 'senior_secondary' | 'undergraduate' | 'postgraduate';

export interface CourseFilters {
  level?: CourseLevel;
  subject?: string;
  is_free?: boolean;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface PaginatedCourses {
  courses: Course[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Lesson Types
export interface Lesson {
  id: number;
  title: string;
  description?: string;
  content?: string;
  course_id: number;
  video_url?: string;
  video_duration?: number;
  animation_scene_path?: string;
  animation_class?: string;
  is_published: boolean;
  order_index: number;
  created_at: string;
  updated_at?: string;
  quizzes?: Quiz[];
  progress?: LessonProgress;
}

export interface LessonPreview {
  id: number;
  title: string;
  description?: string;
  video_duration?: number;
  order_index: number;
  is_completed: boolean;
}

// Quiz Types
export interface Quiz {
  id: number;
  title: string;
  description?: string;
  lesson_id: number;
  time_limit?: number;
  passing_score: number;
  questions: Question[];
  created_at: string;
}

export interface Question {
  id: number;
  quiz_id: number;
  question_text: string;
  question_type: QuestionType;
  options?: QuestionOption[];
  explanation?: string;
  points: number;
  order_index: number;
}

export interface QuestionOption {
  id: string;
  text: string;
  is_correct: boolean;
}

export type QuestionType = 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'fill_blank';

export interface QuizAttempt {
  id: number;
  user_id: number;
  quiz_id: number;
  score: number;
  total_points: number;
  percentage: number;
  passed: boolean;
  started_at: string;
  completed_at?: string;
  answers: QuizAnswer[];
}

export interface QuizAnswer {
  question_id: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  points: number;
  explanation?: string;
}

export interface QuizSubmission {
  answers: Record<string, string>;
}

// Progress Types
export interface LessonProgress {
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

export interface CourseProgress {
  course_id: number;
  course_title: string;
  total_lessons: number;
  completed_lessons: number;
  progress_percentage: number;
  last_accessed_lesson?: {
    id: number;
    title: string;
    last_position: number;
  };
  estimated_time_remaining: number;
}

export interface UserStats {
  total_courses_enrolled: number;
  total_courses_completed: number;
  total_lessons_completed: number;
  total_quizzes_passed: number;
  total_learning_time: number;
  average_quiz_score: number;
  current_streak: number;
  longest_streak: number;
}

// Payment Types
export interface Payment {
  id: number;
  user_id: number;
  course_id: number;
  amount: number;
  currency: string;
  status: PaymentStatus;
  payment_method: string;
  stripe_payment_intent_id?: string;
  created_at: string;
}

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled';

export interface Subscription {
  id: number;
  user_id: number;
  tier: SubscriptionTier;
  starts_at: string;
  expires_at: string;
  is_active: boolean;
}

export type SubscriptionTier = 'free' | 'premium' | 'institutional';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  detail?: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
  additional_info?: Record<string, unknown>;
}

// Navigation Types
export interface NavItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
}

// Animation Types
export interface AnimationRenderRequest {
  lesson_id: number;
  scene_path: string;
  scene_class: string;
  quality: string;
  output_format: string;
  voiceover_text?: string;
}

export interface AnimationRenderJob {
  job_id: string;
  status: string;
  estimated_time: number;
  created_at: string;
}
