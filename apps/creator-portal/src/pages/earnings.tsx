import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { CreatorLayout } from '../components/Layout';
import { useAuthStore } from '../store';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

interface Transaction {
  id: number;
  type: 'enrollment' | 'payout' | 'refund' | 'bonus';
  course_title?: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  description: string;
  created_at: string;
}

interface EarningsStats {
  totalEarnings: number;
  pendingBalance: number;
  availableBalance: number;
  thisMonthEarnings: number;
  lastMonthEarnings: number;
  totalStudents: number;
}

export default function EarningsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<EarningsStats>({
    totalEarnings: 0,
    pendingBalance: 0,
    availableBalance: 0,
    thisMonthEarnings: 0,
    lastMonthEarnings: 0,
    totalStudents: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [timeFilter, setTimeFilter] = useState('month');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchEarnings = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));

        const mockStats: EarningsStats = {
          totalEarnings: 15420.50,
          pendingBalance: 2340.00,
          availableBalance: 4580.50,
          thisMonthEarnings: 2150.00,
          lastMonthEarnings: 1890.00,
          totalStudents: 2456,
        };

        const mockTransactions: Transaction[] = [
          {
            id: 1,
            type: 'enrollment',
            course_title: 'Calculus Fundamentals',
            amount: 49.99,
            status: 'completed',
            description: 'New enrollment - John Doe',
            created_at: '2024-01-25T10:30:00Z',
          },
          {
            id: 2,
            type: 'payout',
            amount: -2000.00,
            status: 'completed',
            description: 'Payout to bank account ****4532',
            created_at: '2024-01-24T14:00:00Z',
          },
          {
            id: 3,
            type: 'enrollment',
            course_title: 'Algebra Basics',
            amount: 0,
            status: 'completed',
            description: 'New enrollment (Free course)',
            created_at: '2024-01-23T16:45:00Z',
          },
          {
            id: 4,
            type: 'enrollment',
            course_title: 'Statistics 101',
            amount: 39.99,
            status: 'completed',
            description: 'New enrollment - Jane Smith',
            created_at: '2024-01-22T09:15:00Z',
          },
          {
            id: 5,
            type: 'bonus',
            amount: 100.00,
            status: 'completed',
            description: 'Course milestone bonus - 500 students',
            created_at: '2024-01-20T11:00:00Z',
          },
          {
            id: 6,
            type: 'refund',
            amount: -49.99,
            status: 'completed',
            description: 'Refund - Calculus Fundamentals',
            created_at: '2024-01-19T08:30:00Z',
          },
          {
            id: 7,
            type: 'enrollment',
            course_title: 'Calculus Fundamentals',
            amount: 49.99,
            status: 'pending',
            description: 'New enrollment - Mike Johnson',
            created_at: '2024-01-28T13:20:00Z',
          },
        ];

        setStats(mockStats);
        setTransactions(mockTransactions);
      } catch (error) {
        console.error('Error fetching earnings:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEarnings();
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getTransactionIcon = (type: Transaction['type']) => {
    const icons = {
      enrollment: (
        <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
      payout: (
        <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      refund: (
        <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      ),
      bonus: (
        <svg className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
        </svg>
      ),
    };
    return (
      <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
        {icons[type]}
      </div>
    );
  };

  return (
    <CreatorLayout title="Earnings - Creator Portal">
      <div className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Earnings</h1>
            <p className="text-gray-600 mt-1">Track your revenue and manage payouts</p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Button>
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Request Payout
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Total Earnings</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{formatCurrency(stats.totalEarnings)}</p>
              <p className="text-sm text-green-600 mt-2">+{formatCurrency(stats.thisMonthEarnings)} this month</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Available Balance</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{formatCurrency(stats.availableBalance)}</p>
              <p className="text-sm text-gray-500 mt-2">Ready for payout</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Pending Balance</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">{formatCurrency(stats.pendingBalance)}</p>
              <p className="text-sm text-gray-500 mt-2">Processing enrollments</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Total Students</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalStudents.toLocaleString()}</p>
              <p className="text-sm text-green-600 mt-2">+{Math.floor(stats.totalStudents * 0.05)} this week</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Transaction History</CardTitle>
                <div className="flex space-x-2">
                  {(['week', 'month', 'year', 'all'] as const).map((period) => (
                    <button
                      key={period}
                      onClick={() => setTimeFilter(period)}
                      className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                        timeFilter === period ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {period.charAt(0).toUpperCase() + period.slice(1)}
                    </button>
                  ))}
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {transactions.map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-4">
                          {getTransactionIcon(transaction.type)}
                          <div>
                            <p className="font-medium text-gray-900">{transaction.description}</p>
                            <p className="text-sm text-gray-500">{formatDate(transaction.created_at)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {transaction.amount >= 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                          </p>
                          <span className={`text-xs ${
                            transaction.status === 'completed' ? 'text-green-600' :
                            transaction.status === 'pending' ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {transaction.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Payout Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Bank Account</p>
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900">****4532</p>
                      <button className="text-sm text-indigo-600 hover:text-indigo-700">Edit</button>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Payout Schedule</p>
                    <p className="font-medium text-gray-900">Monthly (1st of each month)</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Minimum Payout</p>
                    <p className="font-medium text-gray-900">$100.00</p>
                  </div>
                  <div className="p-4 bg-indigo-50 rounded-lg">
                    <p className="text-sm text-indigo-600 mb-1">Creator Share</p>
                    <p className="text-2xl font-bold text-indigo-600">70%</p>
                    <p className="text-xs text-indigo-500 mt-1">of course revenue</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </CreatorLayout>
  );
}
