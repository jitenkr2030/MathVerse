import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Play, Sparkles, TrendingUp, Users } from 'lucide-react';

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
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 math-grid" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: '1s' }} />
      
      {/* Floating Math Elements */}
      <div className="absolute top-32 right-[15%] hidden xl:block animate-float">
        <div className="text-4xl font-bold text-indigo-200/30 equation">∑</div>
      </div>
      <div className="absolute top-48 left-[10%] hidden xl:block animate-float" style={{ animationDelay: '0.5s' }}>
        <div className="text-3xl font-bold text-sky-200/30 equation">π</div>
      </div>
      <div className="absolute bottom-32 right-[20%] hidden xl:block animate-float" style={{ animationDelay: '1.5s' }}>
        <div className="text-3xl font-bold text-indigo-200/30 equation">∞</div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div className={`transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border border-indigo-200 rounded-full mb-8">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-700">New: AI-Powered Tutoring</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 leading-tight mb-6">
              See the Beauty of{' '}
              <span className="gradient-text">Mathematics</span>
              <br />
              in Motion
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-slate-600 mb-8 max-w-xl">
              Transform abstract concepts into stunning visualizations. From calculus to 
              linear algebra, MathVerse makes math intuitive, engaging, and beautiful.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <button
                onClick={onGetStarted}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all duration-200 shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 btn-shine group"
              >
                Start Learning Free
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </button>
              <button className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-700 font-semibold rounded-xl border-2 border-slate-200 hover:border-indigo-300 hover:text-indigo-600 transition-all duration-200">
                <Play className="w-5 h-5" />
                Watch Demo
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl sm:text-3xl font-bold text-slate-900">{stat.value}</div>
                  <div className="text-sm text-slate-500">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Social Proof */}
            <div className="mt-8 pt-8 border-t border-slate-200">
              <p className="text-sm text-slate-500 mb-4">Trusted by students from</p>
              <div className="flex flex-wrap gap-6 text-slate-400 font-semibold text-sm">
                <span>MIT</span>
                <span>Stanford</span>
                <span>Harvard</span>
                <span>Cambridge</span>
                <span>+ 500 schools</span>
              </div>
            </div>
          </div>

          {/* Right Visual */}
          <div className={`relative transform transition-all duration-1000 delay-300 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            {/* Main Card */}
            <div className="relative bg-white rounded-3xl shadow-2xl shadow-indigo-500/20 overflow-hidden border border-slate-200">
              {/* Browser Chrome */}
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-50 border-b border-slate-200">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <div className="flex-1 mx-4">
                  <div className="bg-white rounded-lg px-3 py-1 text-sm text-slate-500">
                    mathverse.app/learn/calculus/derivatives
                  </div>
                </div>
              </div>

              {/* Content Preview */}
              <div className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 min-h-[400px] relative">
                {/* Math Animation Preview */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl text-white mb-4 equation animate-float">f(x) = x²</div>
                    <div className="text-4xl text-indigo-400 mb-4 animate-pulse-glow equation">f'(x) = 2x</div>
                    <div className="w-48 h-48 mx-auto border-2 border-indigo-500/50 rounded-full flex items-center justify-center relative">
                      <div className="absolute inset-0 border-2 border-indigo-500/30 rounded-full animate-ping" />
                      <svg className="w-24 h-24 text-indigo-400" viewBox="0 0 100 100">
                        <path
                          d="M 10 90 Q 50 10 90 90"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                          className="animate-pulse"
                        />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Floating UI Elements */}
                <div className="absolute top-4 right-4 bg-green-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
                  Live Preview
                </div>
                <div className="absolute bottom-4 left-4 right-4 flex gap-2">
                  <div className="flex-1 bg-white/10 backdrop-blur rounded-lg px-3 py-2 text-white text-sm">
                    <span className="text-slate-400">Progress:</span> 75%
                  </div>
                  <div className="w-24 bg-white/10 backdrop-blur rounded-lg px-3 py-2 text-green-400 text-sm font-semibold">
                    +50 XP
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Badge */}
            <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl shadow-xl p-4 flex items-center gap-3 animate-float">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900">+23%</div>
                <div className="text-xs text-slate-500">Learning Streak</div>
              </div>
            </div>

            {/* Floating Badge 2 */}
            <div className="absolute -top-4 -right-4 bg-white rounded-2xl shadow-xl p-4 flex items-center gap-3 animate-float" style={{ animationDelay: '0.5s' }}>
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900">1,234</div>
                <div className="text-xs text-slate-500">Online Now</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-slate-300 rounded-full flex items-start justify-center p-1">
          <div className="w-1.5 h-3 bg-slate-400 rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
};

export default Hero;
