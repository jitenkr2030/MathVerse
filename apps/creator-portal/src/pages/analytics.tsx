import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface AnalyticsData {
  views: number;
  enrollments: number;
  completionRate: number;
  revenue: number;
  ratings: number;
  studentGrowth: { date: string; count: number }[];
  revenueGrowth: { date: string; amount: number }[];
  topLessons: { title: string; views: number; completionRate: number }[];
  studentLocations: { country: string; count: number }[];
}

export default function AnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [period, setPeriod] = useState('30days');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const mockData: AnalyticsData = {
          views: 45892,
          enrollments: 127,
          completionRate: 73,
          revenue: 8920,
          ratings: 4.8,
          studentGrowth: [
            { date: '2024-01-01', count: 2200 },
            { date: '2024-01-08', count: 2320 },
            { date: '2024-01-15', count: 2380 },
            { date: '2024-01-22', count: 2420 },
            { date: '2024-01-29', count: 2456 },
          ],
          revenueGrowth: [
            { date: '2024-01-01', amount: 1200 },
            { date: '2024-01-08', amount: 1450 },
            { date: '2024-01-15', amount: 1680 },
            { date: '2024-01-22', amount: 1820 },
            { date: '2024-01-29', amount: 2150 },
          ],
          topLessons: [
            { title: 'Introduction to Limits', views: 1256, completionRate: 85 },
            { title: 'The Power Rule', views: 892, completionRate: 78 },
            { title: 'Chain Rule Explained', views: 654, completionRate: 72 },
            { title: 'Product Rule', views: 543, completionRate: 68 },
            { title: 'Quotient Rule', views: 432, completionRate: 65 },
          ],
          studentLocations: [
            { country: 'United States', count: 892 },
            { country: 'India', count: 456 },
            { country: 'United Kingdom', count: 234 },
            { country: 'Canada', count: 189 },
            { country: 'Australia', count: 156 },
          ],
        };

        setData(mockData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [period]);

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  if (!data) {
    return null;
  }

  const stats = [
    { label: 'Total Views', value: data.views.toLocaleString(), change: '+12%' },
    { label: 'Enrollments', value: data.enrollments.toString(), change: '+8%' },
    { label: 'Completion Rate', value: `${data.completionRate}%`, change: '+5%' },
    { label: 'Revenue', value: `$${data.revenue.toLocaleString()}`, change: '+15%' },
  ];

  return (
    <CreatorLayout title="Analytics - Creator Portal">
      <div className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600 mt-1">Track your course performance</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <div className="flex space-x-2">
              {(['7days', '30days', '90days', 'year'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    period === p
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                  }`}
                >
                  {p === '7days' ? '7 Days' : p === '30days' ? '30 Days' : p === '90days' ? '90 Days' : '1 Year'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <p className="text-sm text-green-600 mt-2">{stat.change} vs last period</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Student Growth Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Student Growth</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between space-x-2">
                {data.studentGrowth.map((item, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-indigo-500 rounded-t transition-all hover:bg-indigo-600"
                      style={{
                        height: `${(item.count / 2500) * 100}%`,
                        minHeight: '4px',
                      }}
                    />
                    <span className="text-xs text-gray-500 mt-2 truncate">
                      {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Revenue Growth Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Growth</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end justify-between space-x-2">
                {data.revenueGrowth.map((item, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-green-500 rounded-t transition-all hover:bg-green-600"
                      style={{
                        height: `${(item.amount / 2500) * 100}%`,
                        minHeight: '4px',
                      }}
                    />
                    <span className="text-xs text-gray-500 mt-2 truncate">
                      {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Lessons */}
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Lessons</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.topLessons.map((lesson, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-semibold text-sm">
                        {index + 1}
                      </span>
                      <span className="font-medium text-gray-900">{lesson.title}</span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{lesson.views.toLocaleString()} views</span>
                      <span>{lesson.completionRate}% completion</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Student Locations */}
          <Card>
            <CardHeader>
              <CardTitle>Student Locations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.studentLocations.map((location, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{getCountryFlag(location.country)}</span>
                      <span className="text-gray-900">{location.country}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full"
                          style={{ width: `${(location.count / 892) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-500 w-16 text-right">
                        {location.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </CreatorLayout>
  );
}

function getCountryFlag(country: string): string {
  const flags: Record<string, string> = {
    'United States': '🇺🇸',
    'India': '🇮🇳',
    'United Kingdom': '🇬🇧',
    'Canada': '🇨🇦',
    'Australia': '🇦🇺',
  };
  return flags[country] || '🌍';
}
