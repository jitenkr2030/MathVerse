import React from 'react';
import { Video, Brain, Layers, Code, Trophy, Smartphone, Zap } from 'lucide-react';

interface Feature {
  name: string;
  description: string;
  icon: React.ElementType;
}

const features: Feature[] = [
  {
    name: 'Animated Math Concepts',
    description: 'Watch complex mathematical proofs and concepts come to life with stunning Manim-powered animations that make abstract ideas tangible.',
    icon: Video,
  },
  {
    name: 'AI-Powered Tutor',
    description: 'Get instant personalized help with our specialized math AI. It understands your learning style and adapts explanations accordingly.',
    icon: Brain,
  },
  {
    name: 'Visual Knowledge Graph',
    description: 'Navigate your learning journey through an interactive map that shows connections between concepts and tracks your mastery.',
    icon: Layers,
  },
  {
    name: 'Creator Studio',
    description: 'Build your own mathematical animations with our browser-based Python editor. No setup required, just create and share.',
    icon: Code,
  },
  {
    name: 'Gamified Progress',
    description: 'Earn badges, maintain learning streaks, and climb leaderboards as you master new mathematical concepts.',
    icon: Trophy,
  },
  {
    name: 'Cross-Platform Sync',
    description: 'Learn seamlessly across web and mobile. Your progress, preferences, and achievements sync instantly everywhere.',
    icon: Smartphone,
  },
];

const Features: React.FC = () => {
  return (
    <section id="features" className="features-section section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header">
          <div className="section-badge">
            <Zap size={16} />
            <span>Powerful Features</span>
          </div>
          <h2 className="section-title">
            Everything you need to master <span className="hero-gradient">mathematics</span>
          </h2>
          <p className="section-subtitle">
            We combine cutting-edge animation technology with proven pedagogical methods 
            to create the most effective math learning platform ever built.
          </p>
        </div>

        {/* Features Grid */}
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={feature.name} className="feature-card">
              <div className="feature-icon">
                <feature.icon size={32} />
              </div>
              <h3 className="feature-title">{feature.name}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div style={{ marginTop: '60px', textAlign: 'center' }}>
          <p style={{ fontSize: '15px', color: '#71717A', marginBottom: '16px' }}>Want to see all features?</p>
          <a href="/features" style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '8px', 
            color: '#A78BFA', 
            fontWeight: '600',
            textDecoration: 'none',
            fontSize: '15px'
          }}>
            View Full Feature List
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
};

export default Features;
