import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface Animation {
  id: number;
  title: string;
  scene_class: string;
  status: 'draft' | 'processing' | 'completed' | 'failed';
  quality: string;
  duration: number;
  created_at: string;
  thumbnail_url?: string;
  render_time?: number;
}

export default function AnimationsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [animations, setAnimations] = useState<Animation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchAnimations = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const mockAnimations: Animation[] = [
          {
            id: 1,
            title: 'Derivative Visualization',
            scene_class: 'DerivativeScene',
            status: 'completed',
            quality: '1080p',
            duration: 120,
            created_at: '2024-01-15',
            thumbnail_url: '',
            render_time: 45,
          },
          {
            id: 2,
            title: 'Integral Animation',
            scene_class: 'IntegralScene',
            status: 'processing',
            quality: '1080p',
            duration: 180,
            created_at: '2024-01-20',
          },
          {
            id: 3,
            title: 'Trigonometry Circle',
            scene_class: 'TrigCircle',
            status: 'completed',
            quality: '720p',
            duration: 90,
            created_at: '2024-01-18',
            thumbnail_url: '',
            render_time: 30,
          },
          {
            id: 4,
            title: 'Vector Addition',
            scene_class: 'VectorScene',
            status: 'failed',
            quality: '1080p',
            duration: 150,
            created_at: '2024-01-22',
          },
          {
            id: 5,
            title: 'Probability Tree',
            scene_class: 'ProbabilityTree',
            status: 'draft',
            quality: '1080p',
            duration: 200,
            created_at: '2024-01-25',
          },
        ];

        setAnimations(mockAnimations);
      } catch (error) {
        console.error('Error fetching animations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnimations();
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

  const filteredAnimations = animations.filter((anim) => {
    if (filter === 'all') return true;
    return anim.status === filter;
  });

  const getStatusBadge = (status: Animation['status']) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    const labels = {
      draft: 'Draft',
      processing: 'Processing',
      completed: 'Completed',
      failed: 'Failed',
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const stats = {
    total: animations.length,
    completed: animations.filter((a) => a.status === 'completed').length,
    processing: animations.filter((a) => a.status === 'processing').length,
    failed: animations.filter((a) => a.status === 'failed').length,
  };

  return (
    <CreatorLayout title="Animations - Creator Portal">
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Animations</h1>
            <p className="text-gray-600 mt-1">Create and manage your Manim animations</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link href="/animations/new">
              <Button>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Animation
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="pt-4">
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">Total Animations</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              <p className="text-sm text-gray-500">Completed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-2xl font-bold text-blue-600">{stats.processing}</p>
              <p className="text-sm text-gray-500">Processing</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
              <p className="text-sm text-gray-500">Failed</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex space-x-2 mb-6 overflow-x-auto pb-2">
          {(['all', 'draft', 'processing', 'completed', 'failed'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                filter === status
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Animations Grid */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : filteredAnimations.length === 0 ? (
          <Card className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No animations found</h3>
            <p className="mt-1 text-gray-500">Create your first animation to get started.</p>
            <div className="mt-6">
              <Link href="/animations/new">
                <Button>Create Animation</Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAnimations.map((animation) => (
              <Card key={animation.id} hover className="overflow-hidden">
                <div className="relative h-40 bg-gradient-to-br from-purple-500 to-pink-600">
                  {animation.thumbnail_url ? (
                    <img
                      src={animation.thumbnail_url}
                      alt={animation.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <svg className="h-16 w-16 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  )}
                  <div className="absolute top-3 right-3">
                    {getStatusBadge(animation.status)}
                  </div>
                  {animation.status === 'processing' && (
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-2 border-white border-t-transparent"></div>
                    </div>
                  )}
                </div>
                <CardContent className="pt-4">
                  <h3 className="font-semibold text-gray-900 mb-1">{animation.title}</h3>
                  <p className="text-sm text-gray-500 mb-3 font-mono text-xs">
                    {animation.scene_class}
                  </p>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>{animation.duration}s</span>
                    <span>{animation.quality}</span>
                    {animation.render_time && (
                      <span>{animation.render_time}s render</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <span className="text-xs text-gray-400">
                      {new Date(animation.created_at).toLocaleDateString()}
                    </span>
                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm">
                        Preview
                      </Button>
                      {animation.status === 'completed' && (
                        <Button variant="outline" size="sm">
                          Download
                        </Button>
                      )}
                      {animation.status === 'failed' && (
                        <Button variant="danger" size="sm">
                          Retry
                        </Button>
                      )}
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
