import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { courseService, Course, CourseFilters } from '../services/courses';
import { useCourseStore } from '../store';
import Layout from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Input';

export default function CoursesPage() {
  const router = useRouter();
  const { courses, setCourses, isLoading } = useCourseStore();
  const [filters, setFilters] = useState<CourseFilters>({
    search: '',
    level: '',
    subject: '',
    sort_by: 'created_at',
    order: 'desc',
    page: 1,
    limit: 12,
  });
  const [totalPages, setTotalPages] = useState(1);
  const [isFetching, setIsFetching] = useState(true);

  const subjects = [
    { value: '', label: 'All Subjects' },
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
    { value: '', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  const sortOptions = [
    { value: 'created_at', label: 'Newest' },
    { value: 'popularity', label: 'Most Popular' },
    { value: 'price', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'title', label: 'Title: A-Z' },
  ];

  useEffect(() => {
    const fetchCourses = async () => {
      setIsFetching(true);
      try {
        const response = await courseService.getCourses(filters);
        setCourses(response);
        // In a real app, you'd get total pages from the response
        setTotalPages(Math.ceil(response.length / 12));
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setIsFetching(false);
      }
    };

    fetchCourses();
  }, [filters, setCourses]);

  const handleFilterChange = (key: keyof CourseFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Search is already triggered by useEffect
  };

  return (
    <Layout title="Browse Courses - MathVerse">
      <div className="bg-gray-50 min-h-screen">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-extrabold text-gray-900">Browse Courses</h1>
            <p className="mt-2 text-gray-600">
              Discover our comprehensive collection of mathematics courses
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Filters */}
          <Card className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <form onSubmit={handleSearch} className="md:col-span-2">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search courses..."
                    className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                  />
                  <svg
                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
              </form>

              <Select
                options={subjects}
                value={filters.subject || ''}
                onChange={(e) => handleFilterChange('subject', e.target.value)}
              />

              <Select
                options={levels}
                value={filters.level || ''}
                onChange={(e) => handleFilterChange('level', e.target.value)}
              />
            </div>
          </Card>

          {/* Sort and Results Count */}
          <div className="flex justify-between items-center mb-6">
            <p className="text-gray-600">
              {isFetching ? 'Loading...' : `${courses.length} courses found`}
            </p>
            <Select
              options={sortOptions}
              value={`${filters.sort_by}|${filters.order}`}
              onChange={(e) => {
                const [sort_by, order] = e.target.value.split('|');
                setFilters((prev) => ({ ...prev, sort_by, order }));
              }}
              className="w-48"
            />
          </div>

          {/* Course Grid */}
          {isFetching ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : courses.length === 0 ? (
            <Card className="text-center py-16">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">No courses found</h3>
              <p className="mt-1 text-gray-500">
                Try adjusting your search or filter to find what you are looking for.
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {courses.map((course) => (
                <Card
                  key={course.id}
                  hover
                  onClick={() => router.push(`/courses/${course.id}`)}
                  className="overflow-hidden"
                >
                  <div className="relative h-48 bg-gradient-to-br from-indigo-500 to-purple-600">
                    {course.thumbnail_url ? (
                      <img
                        src={course.thumbnail_url}
                        alt={course.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <svg
                          className="h-16 w-16 text-white/50"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                          />
                        </svg>
                      </div>
                    )}
                    <div className="absolute top-3 left-3">
                      <span className="bg-white/90 backdrop-blur-sm text-gray-800 px-2 py-1 rounded text-xs font-medium">
                        {course.level}
                      </span>
                    </div>
                    {course.is_free && (
                      <div className="absolute top-3 right-3">
                        <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-medium">
                          Free
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-indigo-600 uppercase tracking-wide">
                        {course.subject}
                      </span>
                      {course.enrollment_count && (
                        <span className="text-xs text-gray-500">
                          {course.enrollment_count} students
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                      {course.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {course.description}
                    </p>
                    <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                      <span className="text-lg font-bold text-gray-900">
                        {course.is_free ? 'Free' : `$${course.price}`}
                      </span>
                      <span className="text-indigo-600 text-sm font-medium flex items-center">
                        View Details
                        <svg
                          className="ml-1 h-4 w-4"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-12">
              <nav className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={filters.page === 1}
                  onClick={() => setFilters((prev) => ({ ...prev, page: prev.page! - 1 }))}
                >
                  Previous
                </Button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setFilters((prev) => ({ ...prev, page }))}
                    className={`px-4 py-2 rounded-lg text-sm font-medium ${
                      filters.page === page
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  disabled={filters.page === totalPages}
                  onClick={() => setFilters((prev) => ({ ...prev, page: prev.page! + 1 }))}
                >
                  Next
                </Button>
              </nav>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
