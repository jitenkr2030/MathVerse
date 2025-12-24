import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Play, TrendingUp, Users, Sparkles } from 'lucide-react';

interface HeroProps {
  onGetStarted?: () => void;
}

const Hero: React.FC<HeroProps> = ({ onGetStarted }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const stats = [
    { value: '50K+', label: 'Active Learners' },
    { value: '500+', label: 'Video Lessons' },
    { value: '95%', label: 'Completion Rate' },
  ];

  return (
    <section className="hero-section">
      {/* Animated Background */}
      <div className="animated-bg">
        <div className="floating-orb orb-1" />
        <div className="floating-orb orb-2" />
        <div className="floating-orb orb-3" />
        <div className="math-grid" />
      </div>

      <div className="hero-container">
        {/* Left Content */}
        <div className="hero-content">
          {/* Badge */}
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            <span>New: AI-Powered Tutoring</span>
          </div>

          {/* Headline */}
          <h1 className="hero-title">
            Experience Math<br />
            <span className="hero-gradient">Like Never Before</span>
          </h1>

          {/* Subheadline */}
          <p className="hero-subtitle">
            Watch abstract mathematical concepts come to life with stunning animations. 
            From calculus to linear algebra, master mathematics through visual storytelling.
          </p>

          {/* CTA Buttons */}
          <div className="hero-buttons">
            <button onClick={onGetStarted} className="btn btn-primary btn-glow">
              Start Learning Free
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14"/>
                <path d="m12 5 7 7-7 7"/>
              </svg>
            </button>
            <button className="btn btn-secondary">
              <Play className="w-5 h-5" />
              Watch Demo
            </button>
          </div>

          {/* Stats */}
          <div className="hero-stats">
            {stats.map((stat, index) => (
              <div key={index} className="hero-stat">
                <div className="hero-stat-number">{stat.value}</div>
                <div className="hero-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Social Proof */}
          <div style={{ marginTop: '32px', paddingTop: '32px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <p style={{ fontSize: '14px', color: '#71717A', marginBottom: '16px' }}>Trusted by students from</p>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', fontSize: '14px', fontWeight: '600', color: '#52525B' }}>
              <span>MIT</span>
              <span>Stanford</span>
              <span>Harvard</span>
              <span>Cambridge</span>
              <span>+ 500 schools</span>
            </div>
          </div>
        </div>

        {/* Right Visual */}
        <div className="hero-visual">
          <div className="hero-card">
            {/* Browser Chrome */}
            <div className="hero-card-header">
              <div className="hero-card-dot red" />
              <div className="hero-card-dot yellow" />
              <div className="hero-card-dot green" />
              <div className="hero-card-url">mathverse.app/learn/calculus/derivatives</div>
            </div>

            {/* Content Preview */}
            <div className="hero-card-content">
              <div className="math-animation">
                <div className="math-formula">f(x) = x²</div>
                <div className="math-derivative">f'(x) = 2x</div>
              </div>
            </div>

            {/* Stats Bar */}
            <div className="hero-card-stats">
              <div className="hero-card-stat">
                <div className="hero-card-stat-value">75%</div>
                <div className="hero-card-stat-label">Progress</div>
              </div>
              <div className="hero-card-stat">
                <div className="hero-card-stat-value">+50</div>
                <div className="hero-card-stat-label">XP Earned</div>
              </div>
              <div className="hero-card-stat">
                <div className="hero-card-stat-value">12</div>
                <div className="hero-card-stat-label">Day Streak</div>
              </div>
            </div>
          </div>

          {/* Floating Badge */}
          <div className="glass-card" style={{ position: 'absolute', bottom: '-20px', left: '-30px', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #10B981, #059669)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <TrendingUp size={24} color="white" />
              </div>
              <div>
                <div style={{ fontWeight: '700', fontSize: '18px', color: 'white' }}>+23%</div>
                <div style={{ fontSize: '13px', color: '#A1A1AA' }}>Learning Streak</div>
              </div>
            </div>
          </div>

          {/* Floating Badge 2 */}
          <div className="glass-card" style={{ position: 'absolute', top: '-20px', right: '-30px', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Users size={24} color="white" />
              </div>
              <div>
                <div style={{ fontWeight: '700', fontSize: '18px', color: 'white' }}>1,234</div>
                <div style={{ fontSize: '13px', color: '#A1A1AA' }}>Online Now</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
