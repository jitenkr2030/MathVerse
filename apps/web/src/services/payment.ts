/**
 * Payment Service for MathVerse Web Application
 * 
 * This service handles payment processing, subscriptions,
 * and creator earnings tracking.
 */

import api from './api';

// Payment Types
export interface PaymentRequest {
  course_id: number;
  currency?: string;
}

export interface PaymentIntent {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

export interface Payment {
  id: number;
  user_id: number;
  course_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  payment_method: string;
  created_at: string;
}

export interface SubscriptionRequest {
  tier: 'monthly' | 'yearly' | 'lifetime';
}

export interface Subscription {
  id: number;
  user_id: number;
  tier: string;
  starts_at: string;
  expires_at: string;
  is_active: boolean;
}

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

// Payment Service Class
class PaymentService {
  /**
   * Get user's payment history
   */
  async getPayments(status_filter?: string): Promise<Payment[]> {
    const params = status_filter ? { status_filter } : undefined;
    return api.get<Payment[]>('/payments/', { params });
  }

  /**
   * Create a payment intent for course purchase
   */
  async createPayment(request: PaymentRequest): Promise<PaymentIntent> {
    return api.post<PaymentIntent>('/payments/', request);
  }

  /**
   * Confirm payment and enroll user
   */
  async confirmPayment(payment_id: number, payment_intent_id: string): Promise<Payment> {
    return api.post<Payment>(`/payments/${payment_id}/confirm`, { payment_intent_id });
  }

  /**
   * Create a premium subscription
   */
  async createSubscription(request: SubscriptionRequest): Promise<Subscription> {
    return api.post<Subscription>('/payments/subscription', request);
  }

  /**
   * Get user's current subscription
   */
  async getSubscription(): Promise<Subscription> {
    return api.get<Subscription>('/payments/subscription');
  }

  /**
   * Cancel user's subscription
   */
  async cancelSubscription(): Promise<{ message: string; detail: string }> {
    return api.delete<{ message: string; detail: string }>('/payments/subscription');
  }

  /**
   * Get creator earnings and transaction history
   */
  async getCreatorEarnings(): Promise<CreatorEarnings> {
    return api.get<CreatorEarnings>('/payments/earnings');
  }

  /**
   * Request payout for creator earnings
   */
  async requestPayout(): Promise<{ message: string; detail: string }> {
    return api.get<{ message: string; detail: string }>('/payments/earnings/payout');
  }

  /**
   * Get sales data for a specific course
   */
  async getCourseSales(course_id: number): Promise<CourseSales> {
    return api.get<CourseSales>(`/payments/sales/${course_id}`);
  }

  /**
   * Process Stripe payment completion (client-side)
   */
  async processStripePayment(
    stripe: any,
    elements: any,
    clientSecret: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement('card'),
        },
      });

      if (error) {
        return { success: false, error: error.message };
      }

      if (paymentIntent.status === 'succeeded') {
        return { success: true };
      }

      return { success: false, error: 'Payment not completed' };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  }

  /**
   * Format currency for display
   */
  formatCurrency(amount: number, currency: string = 'usd'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount);
  }

  /**
   * Check if user has active subscription
   */
  async hasActiveSubscription(): Promise<boolean> {
    try {
      await this.getSubscription();
      return true;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const paymentService = new PaymentService();
export default paymentService;
