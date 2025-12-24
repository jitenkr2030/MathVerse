import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Input, Select, Textarea } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';

interface CreateCourseForm {
  title: string;
  description: string;
  level: string;
  subject: string;
  price: number;
  is_free: boolean;
  thumbnail_url: string;
}

const subjects = [
  { value: 'algebra', label: 'Algebra' },
  { value: 'geometry', label: 'Geometry' },
  { value: 'calculus', label: 'Calculus' },
  { value: 'statistics', label: 'Statistics' },
  { value: 'probability', label: 'Probability' },
  { value: 'number_theory', label: 'Number Theory' },
  { value: 'linear_algebra', label: 'Linear Algebra' },
  { value: 'differential_equations', label: 'Differential Equations' },
];

const levels = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

export default function NewCoursePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CreateCourseForm>({
    defaultValues: {
      is_free: false,
      price: 0,
    },
  });

  const isFree = watch('is_free');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const onSubmit = async (data: CreateCourseForm) => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Navigate to courses page after creation
      router.push('/courses');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create course');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  return (
    <CreatorLayout title="Create Course - Creator Portal">
      <div className="p-6">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Link href="/courses" className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center mb-4">
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Courses
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Create New Course</h1>
            <p className="text-gray-600 mt-1">Fill in the details to create your new course</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <Card className="mb-6">
              <CardContent className="pt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
                
                <div className="space-y-6">
                  <Input
                    label="Course Title"
                    placeholder="e.g., Calculus Fundamentals"
                    error={errors.title?.message}
                    {...register('title', {
                      required: 'Title is required',
                      minLength: {
                        value: 5,
                        message: 'Title must be at least 5 characters',
                      },
                      maxLength: {
                        value: 100,
                        message: 'Title must be less than 100 characters',
                      },
                    })}
                  />

                  <Textarea
                    label="Description"
                    placeholder="Describe what students will learn in this course..."
                    rows={4}
                    error={errors.description?.message}
                    {...register('description', {
                      required: 'Description is required',
                      minLength: {
                        value: 20,
                        message: 'Description must be at least 20 characters',
                      },
                    })}
                  />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Select
                      label="Subject"
                      options={subjects}
                      error={errors.subject?.message}
                      {...register('subject', {
                        required: 'Subject is required',
                      })}
                    />

                    <Select
                      label="Level"
                      options={levels}
                      error={errors.level?.message}
                      {...register('level', {
                        required: 'Level is required',
                      })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="mb-6">
              <CardContent className="pt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Pricing</h2>
                
                <div className="space-y-6">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_free"
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      {...register('is_free')}
                    />
                    <label htmlFor="is_free" className="ml-2 block text-sm text-gray-900">
                      Make this course free
                    </label>
                  </div>

                  {!isFree && (
                    <Input
                      label="Price ($)"
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="49.99"
                      error={errors.price?.message}
                      {...register('price', {
                        required: !isFree ? 'Price is required' : false,
                        min: {
                          value: 0,
                          message: 'Price must be positive',
                        },
                        valueAsNumber: true,
                      })}
                    />
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="mb-6">
              <CardContent className="pt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Course Thumbnail</h2>
                
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-600">
                      Drag and drop an image, or click to select
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Recommended size: 1280x720 (16:9 aspect ratio)
                    </p>
                    <input
                      type="text"
                      placeholder="Or paste image URL..."
                      className="mt-4 w-full max-w-md mx-auto px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      {...register('thumbnail_url')}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex items-center justify-end space-x-4">
              <Link href="/courses">
                <Button variant="outline" type="button">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" isLoading={isSubmitting}>
                Create Course
              </Button>
            </div>
          </form>
        </div>
      </div>
    </CreatorLayout>
  );
}
