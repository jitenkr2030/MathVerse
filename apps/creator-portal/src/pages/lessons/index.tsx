import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface Lesson {
  id: number;
  title: string;
  course_title: string;
  course_id: number;
  duration: number;
  is_published: boolean;
  has_video: boolean;
  has_animation: boolean;
  has_quiz: boolean;
  views: number;
  completion_rate: number;
  created_at: string;
}

export default function LessonsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchLessons = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const mockLessons: Lesson[] = [
          {
            id: 1,
            title: 'Introduction to Limits',
            course_title: 'Calculus Fundamentals',
            course_id: 1,
            duration: 900,
            is_published: true,
            has_video: true,
            has_animation: true,
            has_quiz: true,
            views: 1256,
            completion_rate: 85,
            created_at: '2024-01-15',
          },
          {
            id: 2,
            title: 'The Power Rule',
            course_title: 'Calculus Fundamentals',
            course_id: 1,
            duration: 720,
            is_published: true,
            has_video: true,
            has_animation: true,
            has_quiz: false,
            views: 892,
            completion_rate: 78,
            created_at: '2024-01-18',
          },
          {
            id: 3,
            title: 'Chain Rule Explained',
            course_title: 'Calculus Fundamentals',
            course_id: 1,
            duration: 1100,
            is_published: false,
            has_video: true,
            has_animation: true,
            has_quiz: true,
            views: 0,
            completion_rate: 0,
            created_at: '2024-01-22',
          },
          {
            id: 4,
            title: 'Solving Linear Equations',
            course_title: 'Algebra Basics',
            course_id: 2,
            duration: 600,
            is_published: true,
            has_video: true,
            has_animation: false,
            has_quiz: true,
            views: 654,
            completion_rate: 92,
            created_at: '2024-02-05',
          },
          {
            id: 5,
            title: 'Quadratic Formula',
            course_title: 'Algebra Basics',
            course_id: 2,
            duration: 840,
            is_published: true,
            has_video: true,
            has_animation: true,
            has_quiz: true,
            views: 543,
            completion_rate: 71,
            created_at: '2024-02-10',
          },
        ];

        setLessons(mockLessons);
      } catch (error) {
        console.error('Error fetching lessons:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLessons();
  }, []);

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  const filteredLessons = lessons.filter((lesson) => {
    if (filter === 'all') return true;
    if (filter === 'published') return lesson.is_published;
    if filter === 'draft') return !lesson.is_published;
    if (filter === 'with-animation') return lesson.has_animation;
    if (filter === 'with-quiz') return lesson.has_quiz;
    return true;
  });

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = (isPublished: boolean) => {
    if (isPublished) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Published
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        Draft
      </span>
    );
  };

  return (
    <CreatorLayout title="Lessons - Creator Portal">
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Lessons</h1>
            <p className="text-gray-600 mt-1">Manage your lesson content</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link href="/lessons/new">
              <Button>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Lesson
              </Button>
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-6">
          {(['all', 'published', 'draft', 'with-animation', 'with-quiz'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === status
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {status === 'with-animation' ? 'With Animation' : status === 'with-quiz' ? 'With Quiz' : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Lessons Table */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : filteredLessons.length === 0 ? (
          <Card className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No lessons found</h3>
            <p className="mt-1 text-gray-500">Create your first lesson to get started.</p>
            <div className="mt-6">
              <Link href="/lessons/new">
                <Button>Create Lesson</Button>
              </Link>
            </div>
          </Card>
        ) : (
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-500 border-b">
                    <th className="pb-3 font-medium pr-4">Lesson</th>
                    <th className="pb-3 font-medium pr-4">Course</th>
                    <th className="pb-3 font-medium pr-4">Content</th>
                    <th className="pb-3 font-medium pr-4">Stats</th>
                    <th className="pb-3 font-medium pr-4">Status</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredLessons.map((lesson) => (
                    <tr key={lesson.id} className="hover:bg-gray-50">
                      <td className="py-4 pr-4">
                        <div>
                          <Link href={`/lessons/${lesson.id}`} className="font-medium text-gray-900 hover:text-indigo-600">
                            {lesson.title}
                          </Link>
                          <p className="text-sm text-gray-500 mt-1">{formatDuration(lesson.duration)}</p>
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <Link href={`/courses/${lesson.course_id}`} className="text-sm text-indigo-600 hover:text-indigo-800">
                          {lesson.course_title}
                        </Link>
                      </td>
                      <td className="py-4 pr-4">
                        <div className="flex space-x-2">
                          {lesson.has_video && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-800">
                              Video
                            </span>
                          )}
                          {lesson.has_animation && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-800">
                              Animation
                            </span>
                          )}
                          {lesson.has_quiz && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-green-100 text-green-800">
                              Quiz
                            </span>
                          )}
                          {!lesson.has_video && !lesson.has_animation && !lesson.has_quiz && (
                            <span className="text-xs text-gray-400">No content</span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        <div className="text-sm">
                          <span className="text-gray-600">{lesson.views} views</span>
                          {lesson.completion_rate > 0 && (
                            <span className="ml-3 text-green-600">{lesson.completion_rate}% completion</span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 pr-4">
                        {getStatusBadge(lesson.is_published)}
                      </td>
                      <td className="py-4">
                        <div className="flex space-x-2">
                          <Link href={`/lessons/${lesson.id}/edit`}>
                            <Button variant="ghost" size="sm">Edit</Button>
                          </Link>
                          <Button variant="ghost" size="sm">Preview</Button>
                          <Button variant="ghost" size="sm">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </CreatorLayout>
  );
}
