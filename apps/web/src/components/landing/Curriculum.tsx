import React, { useState } from 'react';
import { Check, BookOpen, Calculator, FunctionSquare, TrendingUp, GraduationCap } from 'lucide-react';

interface CurriculumLevel {
  id: string;
  name: string;
  ageRange: string;
  icon: React.ElementType;
  color: string;
  topics: string[];
  coursesCount: number;
  formula: string;
}

const levels: CurriculumLevel[] = [
  {
    id: 'primary',
    name: 'Primary School',
    ageRange: 'Ages 6-11',
    icon: BookOpen,
    color: 'emerald',
    topics: ['Counting & Numbers', 'Basic Arithmetic', 'Shapes & Geometry', 'Introduction to Fractions'],
    coursesCount: 12,
    formula: '+',
  },
  {
    id: 'secondary',
    name: 'Secondary School',
    ageRange: 'Ages 12-16',
    icon: Calculator,
    color: 'blue',
    topics: ['Algebra Basics', 'Trigonometry', 'Geometry Proofs', 'Linear Equations'],
    coursesCount: 24,
    formula: '×',
  },
  {
    id: 'senior',
    name: 'Senior Secondary',
    ageRange: 'Ages 17-18',
    icon: FunctionSquare,
    color: 'violet',
    topics: ['Calculus (Limits & Derivatives)', 'Advanced Functions', 'Vector Mathematics', 'Probability & Stats'],
    coursesCount: 18,
    formula: '∫',
  },
  {
    id: 'undergraduate',
    name: 'Undergraduate',
    ageRange: '18+ years',
    icon: TrendingUp,
    color: 'amber',
    topics: ['Linear Algebra', 'Multivariable Calculus', 'Differential Equations', 'Discrete Mathematics'],
    coursesCount: 32,
    formula: '∑',
  },
  {
    id: 'postgraduate',
    name: 'Postgraduate',
    ageRange: '21+ years',
    icon: GraduationCap,
    color: 'rose',
    topics: ['Abstract Algebra', 'Real Analysis', 'Topology', 'Number Theory'],
    coursesCount: 16,
    formula: '∂',
  },
];

const Curriculum: React.FC = () => {
  const [activeTab, setActiveTab] = useState('primary');

  const activeLevel = levels.find(l => l.id === activeTab) || levels[0];

  const getColorValues = (color: string) => {
    const colors: Record<string, { bg: string; border: string; text: string }> = {
      emerald: { bg: '#10B981', border: 'rgba(16, 185, 129, 0.3)', text: '#10B981' },
      blue: { bg: '#3B82F6', border: 'rgba(59, 130, 246, 0.3)', text: '#3B82F6' },
      violet: { bg: '#8B5CF6', border: 'rgba(139, 92, 246, 0.3)', text: '#8B5CF6' },
      amber: { bg: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)', text: '#F59E0B' },
      rose: { bg: '#F43F5E', border: 'rgba(244, 63, 94, 0.3)', text: '#F43F5E' },
    };
    return colors[color] || colors.emerald;
  };

  const colorValues = getColorValues(activeLevel.color);

  return (
    <section id="curriculum" className="curriculum-section section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header">
          <div className="section-badge">
            <GraduationCap size={16} />
            <span>Comprehensive Curriculum</span>
          </div>
          <h2 className="section-title">
            Learn at your own <span className="hero-gradient">pace and level</span>
          </h2>
          <p className="section-subtitle">
            From elementary school fundamentals to advanced postgraduate research, 
            MathVerse has structured content for every stage of your mathematical journey.
          </p>
        </div>

        {/* Level Tabs */}
        <div className="level-tabs">
          {levels.map((level) => (
            <button
              key={level.id}
              onClick={() => setActiveTab(level.id)}
              className={`level-tab ${activeTab === level.id ? 'active' : ''}`}
            >
              {level.name}
            </button>
          ))}
        </div>

        {/* Content Panel */}
        <div className="curriculum-grid">
          {/* Left: Level Info */}
          <div className="curriculum-content glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px' }}>
              <div className="curriculum-icon">
                <activeLevel.icon size={40} />
              </div>
              <div>
                <h3 className="curriculum-title">{activeLevel.name}</h3>
                <p style={{ fontSize: '14px', color: '#A1A1AA' }}>{activeLevel.ageRange}</p>
              </div>
            </div>

            <p className="curriculum-subtitle">
              Master essential mathematical concepts with our animated lessons, 
              interactive exercises, and AI-powered tutoring. Every topic is 
              broken down into digestible segments with visual explanations.
            </p>

            {/* Topics List */}
            <div style={{ marginBottom: '32px' }}>
              <h4 style={{ fontWeight: '600', color: 'white', marginBottom: '16px' }}>Key Topics Covered:</h4>
              <div className="curriculum-topics">
                {activeLevel.topics.map((topic, index) => (
                  <div key={index} className="curriculum-topic">
                    <svg className="curriculum-topic-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 6 9 17l-5-5" />
                    </svg>
                    <span>{topic}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '24px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <div>
                <span style={{ fontSize: '32px', fontWeight: '800', color: 'white' }}>{activeLevel.coursesCount}</span>
                <span style={{ color: '#71717A', marginLeft: '8px' }}>courses available</span>
              </div>
              <a
                href={`/courses?level=${activeLevel.id}`}
                style={{
                  padding: '14px 28px',
                  background: colorValues.bg,
                  borderRadius: '14px',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '15px',
                  textDecoration: 'none',
                  transition: 'all 0.3s ease'
                }}
              >
                Explore Courses
              </a>
            </div>
          </div>

          {/* Right: Visual */}
          <div className="curriculum-visual" style={{ borderColor: colorValues.border }}>
            <span>{activeLevel.formula}</span>
          </div>
        </div>

        {/* All Levels Overview */}
        <div style={{ marginTop: '60px', display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
          {levels.map((level) => {
            const levelColor = getColorValues(level.color);
            return (
              <div
                key={level.id}
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '16px',
                  padding: '20px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ 
                  width: '44px', 
                  height: '44px', 
                  background: `${levelColor.bg}20`, 
                  borderRadius: '12px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  margin: '0 auto 12px'
                }}>
                  <level.icon size={22} style={{ color: levelColor.text }} />
                </div>
                <div style={{ fontWeight: '700', fontSize: '20px', color: 'white' }}>{level.coursesCount}</div>
                <div style={{ fontSize: '13px', color: '#71717A', marginTop: '4px' }}>{level.name}</div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Curriculum;
