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
    <section id="pricing" className="pricing-section section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header">
          <div className="section-badge">
            <Zap size={16} />
            <span>Simple Pricing</span>
          </div>
          <h2 className="section-title">
            Invest in your <span className="hero-gradient">mathematical future</span>
          </h2>
          <p className="section-subtitle">
            Choose the plan that fits your learning goals. All plans include access 
            to our world-class animation engine and AI tutor.
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="pricing-toggle">
          <button
            onClick={() => setBillingPeriod('monthly')}
            className={`pricing-toggle-btn ${billingPeriod === 'monthly' ? 'active' : ''}`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingPeriod('yearly')}
            className={`pricing-toggle-btn ${billingPeriod === 'yearly' ? 'active' : ''}`}
          >
            Yearly
            <span className="pricing-savings">Save 20%</span>
          </button>
        </div>

        {/* Pricing Cards */}
        <div className="pricing-grid">
          {pricingTiers.map((tier) => (
            <div
              key={tier.name}
              className={`pricing-card ${tier.highlighted ? 'popular' : ''}`}
            >
              {tier.highlighted && (
                <div className="pricing-badge">
                  Most Popular
                </div>
              )}

              {/* Header */}
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div className="pricing-icon">
                  <tier.icon size={28} />
                </div>
                <h3 className="pricing-name">{tier.name}</h3>
                <p className="pricing-description">{tier.description}</p>
              </div>

              {/* Price */}
              <div className="pricing-price">
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: '4px' }}>
                  <span className="pricing-amount">
                    {billingPeriod === 'yearly' && tier.price !== '$0'
                      ? `$${(parseFloat(tier.price.replace('$', '')) * 0.8).toFixed(2)}`
                      : tier.price}
                  </span>
                  {tier.price !== '$0' && (
                    <span className="pricing-period">/{billingPeriod === 'yearly' ? 'mo' : tier.period}</span>
                  )}
                </div>
                {billingPeriod === 'yearly' && tier.price !== '$0' && (
                  <div style={{ fontSize: '14px', color: '#71717A', marginTop: '8px' }}>
                    Billed ${(parseFloat(tier.price.replace('$', '')) * 0.8 * 12).toFixed(0)} yearly
                  </div>
                )}
              </div>

              {/* Features */}
              <ul className="pricing-features">
                {tier.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="pricing-feature">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 6 9 17l-5-5" />
                    </svg>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <a
                href={tier.name === 'Team' ? '/contact' : `/register?plan=${tier.name.toLowerCase()}`}
                className={`pricing-btn btn ${tier.highlighted ? 'btn-accent' : 'btn-secondary'}`}
              >
                {tier.cta}
              </a>
            </div>
          ))}
        </div>

        {/* Money Back Guarantee */}
        <div style={{ marginTop: '60px', textAlign: 'center' }}>
          <div style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '12px', 
            padding: '16px 24px', 
            background: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: '50px'
          }}>
            <div style={{ 
              width: '24px', 
              height: '24px', 
              background: '#10B981', 
              borderRadius: '50%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center' 
            }}>
              <Check size={14} color="white" />
            </div>
            <span style={{ color: '#10B981', fontWeight: '600', fontSize: '15px' }}>
              30-day money-back guarantee • No questions asked
            </span>
          </div>
        </div>

        {/* FAQ Preview */}
        <div style={{ marginTop: '40px', textAlign: 'center' }}>
          <p style={{ fontSize: '15px', color: '#71717A', marginBottom: '12px' }}>Have questions about pricing?</p>
          <a href="/pricing-faq" style={{ color: '#A78BFA', fontWeight: '600', textDecoration: 'none', fontSize: '15px' }}>
            View Pricing FAQ →
          </a>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
