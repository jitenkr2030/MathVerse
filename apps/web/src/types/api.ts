/**
 * Shared TypeScript Types for MathVerse API
 * 
 * These types are generated from Python Pydantic models
 * to ensure consistency between frontend and backend.
 */

// User Types
export enum UserRole {
  STUDENT = 'student',
  TEACHER = 'teacher',
  ADMIN = 'admin',
  CREATOR = 'creator',
}

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
  updated_at?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  full_name: string;
  password: string;
  role?: UserRole;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

// Course Types
export enum ContentLevel {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  SENIOR_SECONDARY = 'senior_secondary',
  UNDERGRADUATE = 'undergraduate',
  POSTGRADUATE = 'postgraduate',
}

export interface Course {
  id: number;
  title: string;
  description?: string;
  thumbnail_url?: string;
  level: ContentLevel;
  subject?: string;
  price: number;
  is_free: boolean;
  is_published: boolean;
  creator_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CourseCreate {
  title: string;
  description?: string;
  thumbnail_url?: string;
  level: ContentLevel;
  subject?: string;
  price?: number;
  is_free?: boolean;
}

export interface CourseUpdate {
  title?: string;
  description?: string;
  thumbnail_url?: string;
  level?: ContentLevel;
  subject?: string;
  price?: number;
  is_free?: boolean;
  is_published?: boolean;
}

// Lesson Types
export interface Lesson {
  id: number;
  title: string;
  description?: string;
  course_id: number;
  video_url?: string;
  duration?: number;
  order_index: number;
  is_free: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LessonCreate {
  title: string;
  description?: string;
  video_url?: string;
  duration?: number;
  order_index: number;
  is_free?: boolean;
}

// Concept Types
export interface Concept {
  id: number;
  name: string;
  description?: string;
  difficulty_level: number;
  educational_level?: ContentLevel;
  content?: string;
  diagram_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface Prerequisite {
  id: number;
  concept_id: number;
  prerequisite_id: number;
  strength: number;
}

// Quiz Types
export interface Quiz {
  id: number;
  title: string;
  description?: string;
  lesson_id: number;
  questions: QuizQuestion[];
  passing_score: number;
  time_limit?: number;
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
}

export interface QuizAttempt {
  id: number;
  user_id: number;
  quiz_id: number;
  answers: Record<string, number>;
  score: number;
  passed: boolean;
  completed_at: string;
  created_at: string;
}

// Progress Types
export interface Progress {
  id: number;
  user_id: number;
  lesson_id?: number;
  course_id: number;
  completion_percentage: number;
  time_spent: number;
  last_accessed?: string;
  mastery_level: number;
  created_at: string;
  updated_at?: string;
}

export interface ProgressUpdate {
  lesson_id?: number;
  completion_percentage?: number;
  time_spent?: number;
  mastery_level?: number;
}

// Enrollment Types
export interface Enrollment {
  id: number;
  user_id: number;
  course_id: number;
  enrolled_at: string;
}

// Payment Types
export enum PaymentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
}

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

export interface PaymentCreate {
  course_id: number;
  currency?: string;
}

export interface PaymentIntent {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

// Subscription Types
export enum SubscriptionTier {
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
  LIFETIME = 'lifetime',
}

export interface Subscription {
  id: number;
  user_id: number;
  tier: SubscriptionTier;
  starts_at: string;
  expires_at: string;
  is_active: boolean;
}

export interface SubscriptionCreate {
  tier: SubscriptionTier;
}

// Creator Types
export interface CreatorEarnings {
  total_earnings: number;
  pending_earnings: number;
  paid_earnings: number;
  this_month_earnings: number;
  transactions: Transaction[];
}

export interface Transaction {
  id: number;
  course_id: number;
  course_title: string;
  amount: number;
  currency: string;
  date: string;
}

export interface CourseSales {
  course_id: number;
  course_title: string;
  sales_count: number;
  total_revenue: number;
  unique_buyers: number;
  revenue_share: string;
}

// Recommendation Types
export interface Recommendation {
  course_id: number;
  score: number;
  reason: string;
}

export interface RecommendationRequest {
  user_id: number;
  course_id?: number;
  limit?: number;
}

export interface UserPreferences {
  preferred_topics: string[];
  difficulty_level: ContentLevel;
  learning_goals: string[];
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export interface MessageResponse {
  message: string;
  detail?: string;
}

// Health Check Types
export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'error';
  service: string;
  details?: Record<string, any>;
}

export interface ServicesHealth {
  status: 'healthy' | 'degraded' | 'error';
  services: Record<string, boolean>;
}

// Content Search Types
export interface ContentSearchRequest {
  query: string;
  filters?: {
    level?: ContentLevel;
    subject?: string;
    is_free?: boolean;
  };
  page?: number;
  limit?: number;
}

export interface CurriculumNode {
  id: number;
  title: string;
  level: ContentLevel;
  children?: CurriculumNode[];
}

// Animation Types
export interface AnimationRenderRequest {
  scene_type: 'basic' | 'graph' | 'proof' | '3d';
  content: string;
  parameters?: Record<string, any>;
  quality?: 'low' | 'medium' | 'high';
}

export interface AnimationRenderJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  video_url?: string;
  thumbnail_url?: string;
  error?: string;
}

// Video Processing Types
export interface VideoProcessRequest {
  source_url: string;
  output_format?: string;
  quality?: '480p' | '720p' | '1080p' | '4k';
  thumbnail?: boolean;
}

export interface VideoProcessJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  video_url?: string;
  error?: string;
}
