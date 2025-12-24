import React from 'react';
import { 
  Video, 
  Brain, 
  Layers, 
  Code, 
  Trophy, 
  Smartphone,
  Zap,
  Target,
  Sparkles
} from 'lucide-react';

interface Feature {
  name: string;
  description: string;
  icon: React.ElementType;
  color: string;
}

const features: Feature[] = [
  {
    name: 'Animated Math Concepts',
    description: 'Watch complex mathematical proofs and concepts come to life with stunning Manim-powered animations that make abstract ideas tangible.',
    icon: Video,
    color: 'indigo',
  },
  {
    name: 'AI-Powered Tutor',
    description: 'Get instant personalized help with our specialized math AI. It understands your learning style and adapts explanations accordingly.',
    icon: Brain,
    color: 'sky',
  },
  {
    name: 'Visual Knowledge Graph',
    description: 'Navigate your learning journey through an interactive map that shows connections between concepts and tracks your mastery.',
    icon: Layers,
    color: 'violet',
  },
  {
    name: 'Creator Studio',
    description: 'Build your own mathematical animations with our browser-based Python editor. No setup required, just create and share.',
    icon: Code,
    color: 'amber',
  },
  {
    name: 'Gamified Progress',
    description: 'Earn badges, maintain learning streaks, and climb leaderboards as you master new mathematical concepts.',
    icon: Trophy,
    color: 'emerald',
  },
  {
    name: 'Cross-Platform Sync',
    description: 'Learn seamlessly across web and mobile. Your progress, preferences, and achievements sync instantly everywhere.',
    icon: Smartphone,
    color: 'rose',
  },
];

const Features: React.FC = () => {
  return (
    <section id="features" className="section-py bg-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-100 rounded-full blur-3xl opacity-50" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-sky-100 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border border-indigo-200 rounded-full mb-6">
            <Zap className="w-4 h-4 text-indigo-600" />
            <span className="text-sm font-medium text-indigo-700">Powerful Features</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Everything you need to{' '}
            <span className="gradient-text">master mathematics</span>
          </h2>
          <p className="text-lg text-slate-600">
            We combine cutting-edge animation technology with proven pedagogical methods 
            to create the most effective math learning platform ever built.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.name}
              className={`group relative bg-white rounded-2xl p-8 border border-slate-200 card-hover reveal ${
                index >= 3 ? 'lg:mt-8' : ''
              }`}
            >
              {/* Hover gradient border effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-indigo-500 to-sky-500 opacity-0 group-hover:opacity-10 transition-opacity duration-300" />

              {/* Icon */}
              <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-${feature.color}-50 mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-7 h-7 text-${feature.color}-600`} />
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors">
                {feature.name}
              </h3>
              <p className="text-slate-600 leading-relaxed">
                {feature.description}
              </p>

              {/* Arrow indicator */}
              <div className="absolute bottom-8 right-8 opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-1">
                <Arrow className="w-5 h-5 text-indigo-600" />
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-slate-500 mb-4">Want to see all features?</p>
          <a
            href="/features"
            className="inline-flex items-center gap-2 text-indigo-600 font-semibold hover:text-indigo-700 transition-colors"
          >
            View Full Feature List
            <Arrow className="w-4 h-4" />
          </a>
        </div>
      </div>
    </section>
  );
};

const Arrow: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
  </svg>
);

export default Features;
