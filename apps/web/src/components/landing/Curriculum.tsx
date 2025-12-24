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
  },
  {
    id: 'secondary',
    name: 'Secondary School',
    ageRange: 'Ages 12-16',
    icon: Calculator,
    color: 'blue',
    topics: ['Algebra Basics', 'Trigonometry', 'Geometry Proofs', 'Linear Equations'],
    coursesCount: 24,
  },
  {
    id: 'senior',
    name: 'Senior Secondary',
    ageRange: 'Ages 17-18',
    icon: FunctionSquare,
    color: 'violet',
    topics: ['Calculus (Limits & Derivatives)', 'Advanced Functions', 'Vector Mathematics', 'Probability & Stats'],
    coursesCount: 18,
  },
  {
    id: 'undergraduate',
    name: 'Undergraduate',
    ageRange: '18+ years',
    icon: TrendingUp,
    color: 'amber',
    topics: ['Linear Algebra', 'Multivariable Calculus', 'Differential Equations', 'Discrete Mathematics'],
    coursesCount: 32,
  },
  {
    id: 'postgraduate',
    name: 'Postgraduate',
    ageRange: '21+ years',
    icon: GraduationCap,
    color: 'rose',
    topics: ['Abstract Algebra', 'Real Analysis', 'Topology', 'Number Theory'],
    coursesCount: 16,
  },
];

const Curriculum: React.FC = () => {
  const [activeTab, setActiveTab] = useState('primary');

  const activeLevel = levels.find(l => l.id === activeTab) || levels[0];

  return (
    <section id="curriculum" className="section-py bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-sky-50 border border-sky-200 rounded-full mb-6">
            <GraduationCap className="w-4 h-4 text-sky-600" />
            <span className="text-sm font-medium text-sky-700">Comprehensive Curriculum</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Learn at your own{' '}
            <span className="gradient-text">pace and level</span>
          </h2>
          <p className="text-lg text-slate-600">
            From elementary school fundamentals to advanced postgraduate research, 
            MathVerse has structured content for every stage of your mathematical journey.
          </p>
        </div>

        {/* Level Tabs */}
        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {levels.map((level) => (
            <button
              key={level.id}
              onClick={() => setActiveTab(level.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                activeTab === level.id
                  ? `bg-${level.color}-600 text-white shadow-lg shadow-${level.color}-500/30`
                  : 'bg-white text-slate-600 border border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <level.icon className="w-5 h-5" />
              {level.name}
            </button>
          ))}
        </div>

        {/* Content Panel */}
        <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
          <div className="grid lg:grid-cols-2">
            {/* Left: Level Info */}
            <div className="p-8 lg:p-12">
              <div className="flex items-center gap-4 mb-6">
                <div className={`w-16 h-16 bg-${activeLevel.color}-100 rounded-2xl flex items-center justify-center`}>
                  <activeLevel.icon className={`w-8 h-8 text-${activeLevel.color}-600`} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900">{activeLevel.name}</h3>
                  <p className="text-slate-500">{activeLevel.ageRange}</p>
                </div>
              </div>

              <p className="text-slate-600 mb-8">
                Master essential mathematical concepts with our animated lessons, 
                interactive exercises, and AI-powered tutoring. Every topic is 
                broken down into digestible segments with visual explanations.
              </p>

              {/* Topics List */}
              <div className="space-y-4 mb-8">
                <h4 className="font-semibold text-slate-900">Key Topics Covered:</h4>
                <div className="grid sm:grid-cols-2 gap-3">
                  {activeLevel.topics.map((topic, index) => (
                    <div key={index} className="flex items-center gap-2 text-slate-600">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span>{topic}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-slate-200">
                <div>
                  <span className="text-3xl font-bold text-slate-900">{activeLevel.coursesCount}</span>
                  <span className="text-slate-500 ml-2">courses available</span>
                </div>
                <a
                  href={`/courses?level=${activeLevel.id}`}
                  className={`inline-flex items-center gap-2 px-6 py-3 bg-${activeLevel.color}-600 text-white font-semibold rounded-xl hover:bg-${activeLevel.color}-700 transition-colors`}
                >
                  Explore Courses
                </a>
              </div>
            </div>

            {/* Right: Visual */}
            <div className={`bg-gradient-to-br from-${activeLevel.color}-500 to-${activeLevel.color}-600 p-8 lg:p-12 flex items-center justify-center relative overflow-hidden`}>
              {/* Background patterns */}
              <div className="absolute inset-0 opacity-10">
                <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                    <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" strokeWidth="0.5" />
                  </pattern>
                  <rect width="100" height="100" fill="url(#grid)" />
                </svg>
              </div>

              {/* Floating math elements */}
              <div className="relative z-10 text-center text-white">
                <div className="text-8xl mb-4 font-bold equation animate-float">
                  {activeLevel.id === 'primary' && '+'}
                  {activeLevel.id === 'secondary' && 'x'}
                  {activeLevel.id === 'senior' && '∫'}
                  {activeLevel.id === 'undergraduate' && '∑'}
                  {activeLevel.id === 'postgraduate' && '∂'}
                </div>
                <div className="text-xl font-medium opacity-90">
                  {activeLevel.name}
                </div>
                <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur rounded-full text-sm">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  {activeLevel.coursesCount} courses available
                </div>
              </div>

              {/* Decorative circles */}
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full" />
              <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-white/10 rounded-full" />
            </div>
          </div>
        </div>

        {/* All Levels Overview */}
        <div className="mt-16 grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {levels.map((level) => (
            <div
              key={level.id}
              className="bg-white rounded-xl p-4 border border-slate-200 text-center hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className={`w-10 h-10 mx-auto mb-3 bg-${level.color}-100 rounded-lg flex items-center justify-center`}>
                <level.icon className={`w-5 h-5 text-${level.color}-600`} />
              </div>
              <div className="font-semibold text-slate-900 text-sm">{level.coursesCount}</div>
              <div className="text-xs text-slate-500">{level.name}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Curriculum;
