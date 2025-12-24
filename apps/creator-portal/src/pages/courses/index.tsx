import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { CreatorLayout } from '../../components/Layout';
import { useCourseStore, useAuthStore } from '../../store';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Select } from '../../components/ui/Input';

interface Course {
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
  revenue?: number;
}

export default function CoursesPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const { courses, setCourses } = useCourseStore();
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchCourses = async () => {
      setIsLoading(true);
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 500));

        const mockCourses: Course[] = [
          {
            id: 1,
            title: 'Calculus Fundamentals',
            description: 'Master the basics of calculus including limits, derivatives, and integrals',
            level: 'intermediate',
            subject: 'Calculus',
            price: 49.99,
            is_free: false,
            is_published: true,
            thumbnail_url: '',
            lessons_count: 24,
            enrollment_count: 892,
            average_rating: 4.9,
            created_at: '2024-01-15',
            revenue: 8920,
          },
          {
            id: 2,
            title: 'Algebra Basics',
            description: 'Build a strong foundation in algebra with practical examples',
            level: 'beginner',
            subject: 'Algebra',
            price: 0,
            is_free: true,
            is_published: true,
            thumbnail_url: '',
            lessons_count: 15,
            enrollment_count: 654,
            average_rating: 4.8,
            created_at: '2024-02-20',
            revenue: 0,
          },
          {
            id: 3,
            title: 'Statistics 101',
            description: 'Learn statistical analysis and probability theory',
            level: 'intermediate',
            subject: 'Statistics',
            price: 39.99,
            is_free: false,
            is_published: true,
            thumbnail_url: '',
            lessons_count: 20,
            enrollment_count: 423,
            average_rating: 4.7,
            created_at: '2024-03-10',
            revenue: 2115,
          },
          {
            id: 4,
            title: 'Linear Algebra',
            description: 'Explore vectors, matrices, and linear transformations',
            level: 'advanced',
            subject: 'Linear Algebra',
            price: 59.99,
            is_free: false,
            is_published: false,
            thumbnail_url: '',
            lessons_count: 18,
            enrollment_count: 0,
            average_rating: 0,
            created_at: '2024-04-05',
            revenue: 0,
          },
        ];

        setCourses(mockCourses as any);
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourses();
  }, [setCourses]);

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  const filteredCourses = courses.filter((course: Course) => {
    const matchesFilter = filter === 'all' ||
      (filter === 'published' && course.is_published) ||
      (filter === 'draft' && !course.is_published) ||
      (filter === 'free' && course.is_free) ||
      (filter === 'paid' && !course.is_free);

    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.subject.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (course: Course) => {
    if (course.is_published) {
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
    <CreatorLayout title="Courses - Creator Portal">
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Courses</h1>
            <p className="text-gray-600 mt-1">Manage and create your courses</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link href="/courses/new">
              <Button>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Course
              </Button>
            </Link>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search courses..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <svg
                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
              <Select
                options={[
                  { value: 'all', label: 'All Courses' },
                  { value: 'published', label: 'Published' },
                  { value: 'draft', label: 'Drafts' },
                  { value: 'free', label: 'Free' },
                  { value: 'paid', label: 'Paid' },
                ]}
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full sm:w-48"
              />
            </div>
          </CardContent>
        </Card>

        {/* Courses Grid */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : filteredCourses.length === 0 ? (
          <Card className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No courses found</h3>
            <p className="mt-1 text-gray-500">Get started by creating your first course.</p>
            <div className="mt-6">
              <Link href="/courses/new">
                <Button>Create Course</Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course: Course) => (
              <Card key={course.id} hover className="overflow-hidden">
                <div className="relative h-40 bg-gradient-to-br from-indigo-500 to-purple-600">
                  {course.thumbnail_url ? (
                    <img
                      src={course.thumbnail_url}
                      alt={course.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <svg className="h-16 w-16 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                  )}
                  <div className="absolute top-3 right-3">
                    {getStatusBadge(course)}
                  </div>
                  {course.is_free && (
                    <div className="absolute top-3 left-3">
                      <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-medium">
                        Free
                      </span>
                    </div>
                  )}
                </div>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-indigo-600 uppercase">
                      {course.subject}
                    </span>
                    <span className="text-xs text-gray-500">{course.level}</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">
                    {course.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {course.description}
                  </p>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>{course.lessons_count || 0} lessons</span>
                    <span>{course.enrollment_count || 0} students</span>
                    {course.average_rating > 0 && (
                      <span className="flex items-center">
                        <span className="text-yellow-500 mr-1">★</span>
                        {course.average_rating.toFixed(1)}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <span className="font-semibold text-gray-900">
                      {course.is_free ? 'Free' : `$${course.price}`}
                    </span>
                    <div className="flex space-x-2">
                      <Link href={`/courses/${course.id}`}>
                        <Button variant="ghost" size="sm">Edit</Button>
                      </Link>
                      <Link href={`/courses/${course.id}/lessons`}>
                        <Button variant="outline" size="sm">Lessons</Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </CreatorLayout>
  );
}
