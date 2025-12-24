import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface DashboardStats {
  totalCourses: number;
  publishedCourses: number;
  totalStudents: number;
  totalEarnings: number;
  averageRating: number;
  totalViews: number;
  recentEnrollments: number;
  pendingPayouts: number;
}

export default function CreatorDashboard() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    totalCourses: 0,
    publishedCourses: 0,
    totalStudents: 0,
    totalEarnings: 0,
    averageRating: 0,
    totalViews: 0,
    recentEnrollments: 0,
    pendingPayouts: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!isAuthenticated) return;

      setIsLoading(true);
      try {
        // Simulate API call - replace with actual API
        await new Promise((resolve) => setTimeout(resolve, 500));

        setStats({
          totalCourses: 12,
          publishedCourses: 8,
          totalStudents: 2456,
          totalEarnings: 15420.50,
          averageRating: 4.8,
          totalViews: 45892,
          recentEnrollments: 127,
          pendingPayouts: 2340.00,
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated]);

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  const statCards = [
    {
      title: 'Total Courses',
      value: stats.totalCourses,
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      color: 'bg-indigo-100 text-indigo-600',
      change: '+2 this month',
      changeType: 'positive',
    },
    {
      title: 'Total Students',
      value: stats.totalStudents.toLocaleString(),
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      color: 'bg-green-100 text-green-600',
      change: '+127 this week',
      changeType: 'positive',
    },
    {
      title: 'Total Earnings',
      value: `$${stats.totalEarnings.toLocaleString()}`,
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-yellow-100 text-yellow-600',
      change: '+15% vs last month',
      changeType: 'positive',
    },
    {
      title: 'Average Rating',
      value: stats.averageRating.toFixed(1),
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      ),
      color: 'bg-purple-100 text-purple-600',
      change: '+0.2 improvement',
      changeType: 'positive',
    },
  ];

  const recentActivity = [
    { type: 'enrollment', message: 'New enrollment in "Calculus Fundamentals"', time: '2 hours ago', icon: '👤' },
    { type: 'review', message: 'New 5-star review on "Algebra Basics"', time: '5 hours ago', icon: '⭐' },
    { type: 'payout', message: 'Payout of $1,250.00 processed', time: '1 day ago', icon: '💰' },
    { type: 'course', message: 'Course "Statistics 101" published', time: '2 days ago', icon: '📚' },
    { type: 'comment', message: 'New question in "Calculus Fundamentals"', time: '3 days ago', icon: '💬' },
  ];

  const topCourses = [
    { title: 'Calculus Fundamentals', students: 892, rating: 4.9, revenue: 8920 },
    { title: 'Algebra Basics', students: 654, rating: 4.8, revenue: 3270 },
    { title: 'Statistics 101', students: 423, rating: 4.7, revenue: 2115 },
    { title: 'Linear Algebra', students: 298, rating: 4.9, revenue: 1490 },
  ];

  return (
    <CreatorLayout title="Dashboard - Creator Portal">
      <div className="p-6">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Creator'}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here is an overview of your creator dashboard
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className={`h-12 w-12 rounded-lg ${stat.color} flex items-center justify-center`}>
                    {stat.icon}
                  </div>
                  <span
                    className={`text-sm font-medium ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {stat.change}
                  </span>
                </div>
                <div className="mt-4">
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-500 mt-1">{stat.title}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Courses */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Top Performing Courses</CardTitle>
                <Link href="/courses">
                  <Button variant="outline" size="sm">View All</Button>
                </Link>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-sm text-gray-500 border-b">
                        <th className="pb-3 font-medium">Course</th>
                        <th className="pb-3 font-medium">Students</th>
                        <th className="pb-3 font-medium">Rating</th>
                        <th className="pb-3 font-medium">Revenue</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {topCourses.map((course, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="py-4">
                            <Link href={`/courses/${index + 1}`} className="font-medium text-gray-900 hover:text-indigo-600">
                              {course.title}
                            </Link>
                          </td>
                          <td className="py-4 text-gray-600">{course.students.toLocaleString()}</td>
                          <td className="py-4">
                            <div className="flex items-center">
                              <span className="text-yellow-500 mr-1">★</span>
                              <span className="text-gray-900">{course.rating}</span>
                            </div>
                          </td>
                          <td className="py-4 text-gray-900 font-medium">${course.revenue.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <span className="text-xl">{activity.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">{activity.message}</p>
                        <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Link href="/courses/new" className="block">
                    <Button fullWidth variant="primary">
                      Create New Course
                    </Button>
                  </Link>
                  <Link href="/animations/new" className="block">
                    <Button fullWidth variant="outline">
                      Upload Animation
                    </Button>
                  </Link>
                  <Link href="/earnings" className="block">
                    <Button fullWidth variant="ghost">
                      Request Payout
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </CreatorLayout>
  );
}
