import React, { useState } from 'react';
import { Check, Sparkles, Star, Zap } from 'lucide-react';

interface PricingTier {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  highlighted?: boolean;
  icon: React.ElementType;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started with basic math concepts',
    features: [
      'Access to 50+ free courses',
      'Basic animated lessons',
      'Community forum access',
      'Progress tracking',
      'Mobile app access',
    ],
    cta: 'Get Started Free',
    icon: Star,
  },
  {
    name: 'Premium',
    price: '$9.99',
    period: 'month',
    description: 'For serious learners who want full access',
    features: [
      'Unlimited course access',
      'All animated content',
      'AI tutor assistance',
      'Certificate of completion',
      'Offline downloads',
      'Priority support',
    ],
    cta: 'Start Free Trial',
    highlighted: true,
    icon: Zap,
  },
  {
    name: 'Team',
    price: '$49.99',
    period: 'month',
    description: 'For schools, tutors, and study groups',
    features: [
      'Everything in Premium',
      'Up to 25 student accounts',
      'Teacher dashboard',
      'Custom learning paths',
      'Analytics & reporting',
      'Dedicated support',
    ],
    cta: 'Contact Sales',
    icon: Sparkles,
  },
];

const Pricing: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  return (
    <section id="pricing" className="section-py bg-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-50 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-full mb-6">
            <Zap className="w-4 h-4 text-amber-600" />
            <span className="text-sm font-medium text-amber-700">Simple Pricing</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Invest in your{' '}
            <span className="gradient-text">mathematical future</span>
          </h2>
          <p className="text-lg text-slate-600">
            Choose the plan that fits your learning goals. All plans include access 
            to our world-class animation engine and AI tutor.
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="flex justify-center mb-16">
          <div className="inline-flex items-center gap-4 bg-slate-100 p-1 rounded-2xl">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-6 py-2 rounded-xl font-medium transition-all duration-200 ${
                billingPeriod === 'monthly'
                  ? 'bg-white text-indigo-600 shadow-lg'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-6 py-2 rounded-xl font-medium transition-all duration-200 ${
                billingPeriod === 'yearly'
                  ? 'bg-white text-indigo-600 shadow-lg'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Yearly
              <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 items-center">
          {pricingTiers.map((tier, index) => (
            <div
              key={tier.name}
              className={`relative bg-white rounded-3xl p-8 border-2 transition-all duration-300 ${
                tier.highlighted
                  ? 'border-indigo-500 shadow-2xl shadow-indigo-500/20 scale-105 z-10'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              {/* Highlight Badge */}
              {tier.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="inline-flex items-center gap-1 px-4 py-1.5 bg-indigo-600 text-white text-sm font-semibold rounded-full">
                    <Sparkles className="w-4 h-4" />
                    Most Popular
                  </div>
                </div>
              )}

              {/* Header */}
              <div className="text-center mb-8">
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4 ${
                  tier.highlighted ? 'bg-indigo-100' : 'bg-slate-100'
                }`}>
                  <tier.icon className={`w-7 h-7 ${
                    tier.highlighted ? 'text-indigo-600' : 'text-slate-600'
                  }`} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{tier.name}</h3>
                <p className="text-slate-500 text-sm">{tier.description}</p>
              </div>

              {/* Price */}
              <div className="text-center mb-8">
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-5xl font-bold text-slate-900">
                    {billingPeriod === 'yearly' && tier.price !== '$0'
                      ? `$${(parseFloat(tier.price.replace('$', '')) * 0.8).toFixed(2)}`
                      : tier.price}
                  </span>
                  {tier.price !== '$0' && (
                    <span className="text-slate-500">/{billingPeriod === 'yearly' ? 'mo' : tier.period}</span>
                  )}
                </div>
                {billingPeriod === 'yearly' && tier.price !== '$0' && (
                  <div className="text-sm text-slate-500 mt-1">
                    Billed ${(parseFloat(tier.price.replace('$', '')) * 0.8 * 12).toFixed(0)} yearly
                  </div>
                )}
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {tier.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-slate-600 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <a
                href={tier.name === 'Team' ? '/contact' : `/register?plan=${tier.name.toLowerCase()}`}
                className={`w-full inline-flex items-center justify-center py-4 rounded-xl font-semibold transition-all duration-200 ${
                  tier.highlighted
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-500/30 btn-shine'
                    : 'bg-slate-100 text-slate-900 hover:bg-slate-200'
                }`}
              >
                {tier.cta}
              </a>
            </div>
          ))}
        </div>

        {/* Money Back Guarantee */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-green-50 border border-green-200 rounded-full">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <Check className="w-4 h-4 text-white" />
            </div>
            <span className="text-green-800 font-medium">
              30-day money-back guarantee • No questions asked
            </span>
          </div>
        </div>

        {/* FAQ Preview */}
        <div className="mt-16 text-center">
          <p className="text-slate-500 mb-4">Have questions about pricing?</p>
          <a href="/pricing-faq" className="text-indigo-600 font-semibold hover:text-indigo-700">
            View Pricing FAQ →
          </a>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
