import React from 'react';
import Link from 'next/link';
import { ArrowRight, Code, Users, DollarSign, Sparkles, Play } from 'lucide-react';

interface CTASectionProps {
  onGetStarted?: () => void;
}

const CTASection: React.FC<CTASectionProps> = () => {
  return (
    <section id="creators" className="section-py bg-slate-900 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-sky-600/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-4xl">
          <svg className="w-full h-full opacity-5" viewBox="0 0 400 400">
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" />
            </pattern>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/20 border border-indigo-500/30 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-sm font-medium text-indigo-300">Creator Program</span>
            </div>
            
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
              Are you a{' '}
              <span className="bg-gradient-to-r from-indigo-400 to-sky-400 bg-clip-text text-transparent">
                Math Creator?
              </span>
            </h2>
            
            <p className="text-lg text-slate-300 mb-8">
              Turn your mathematical expertise into income. Use our browser-based 
              Manim animation studio to create stunning visualizations and sell 
              courses to students worldwide.
            </p>

            {/* Features List */}
            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-500/20 rounded-lg flex items-center justify-center">
                  <Code className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <div className="font-semibold text-white">Browser-Based Studio</div>
                  <div className="text-sm text-slate-400">No installation required</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <div className="font-semibold text-white">70% Revenue Share</div>
                  <div className="text-sm text-slate-400">Industry-leading creator rates</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <div className="font-semibold text-white">Global Audience</div>
                  <div className="text-sm text-slate-400">Reach 50,000+ active learners</div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/creator/register"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all duration-200 shadow-lg shadow-indigo-500/30 btn-shine group"
              >
                Become a Creator
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <button className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-200">
                <Play className="w-5 h-5" />
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="mt-8 pt-8 border-t border-white/10">
              <div className="grid grid-cols-3 gap-8">
                <div>
                  <div className="text-2xl font-bold text-white">$2.5M</div>
                  <div className="text-sm text-slate-400">Paid to Creators</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">1,200+</div>
                  <div className="text-sm text-slate-400">Active Creators</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">4.9★</div>
                  <div className="text-sm text-slate-400">Creator Rating</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Visual - Code Preview */}
          <div className="relative">
            <div className="bg-slate-800 rounded-2xl shadow-2xl overflow-hidden border border-slate-700">
              {/* Window Controls */}
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-700">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="flex-1 text-center text-sm text-slate-400 font-mono">
                  creator-studio.py
                </div>
              </div>

              {/* Code Content */}
              <div className="p-6 font-mono text-sm overflow-x-auto">
                <div className="space-y-3">
                  <div className="flex">
                    <span className="text-slate-500 w-6">1</span>
                    <span><span className="text-purple-400">class</span> <span className="text-yellow-400">DerivativeAnimation</span>(<span className="text-sky-400">Scene</span>):</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">2</span>
                    <span className="pl-4"><span className="text-purple-400">def</span> <span className="text-blue-400">construct</span>(<span className="text-sky-400">self</span>):</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">3</span>
                    <span className="pl-8"><span className="text-sky-400">self</span>.<span className="text-yellow-400">axes</span> = <span className="text-yellow-400">Axes</span>()</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">4</span>
                    <span className="pl-8"><span className="text-sky-400">self</span>.<span className="text-yellow-400">graph</span> = <span className="text-sky-400">self</span>.axes.<span className="text-yellow-400">plot</span>(</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">5</span>
                    <span className="pl-12"><span className="text-sky-400">lambda</span> x: x**<span className="text-green-400">2</span>)</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">6</span>
                    <span className="pl-8"><span className="text-sky-400">self</span>.add(<span className="text-sky-400">self</span>.graph)</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">7</span>
                    <span className="pl-4"><span className="text-purple-400">def</span> <span className="text-blue-400">animate_tangent</span>(<span className="text-sky-400">self</span>):</span>
                  </div>
                  <div className="flex">
                    <span className="text-slate-500 w-6">8</span>
                    <span className="pl-12">...</span>
                  </div>
                </div>
              </div>

              {/* Floating Preview Window */}
              <div className="absolute bottom-4 right-4 bg-slate-900 rounded-lg border border-slate-700 p-2 shadow-xl">
                <div className="w-32 h-24 bg-gradient-to-br from-indigo-600/30 to-sky-600/30 rounded flex items-center justify-center">
                  <svg className="w-16 h-16" viewBox="0 0 100 100">
                    <path
                      d="M 10 90 Q 50 10 90 90"
                      fill="none"
                      stroke="#6366F1"
                      strokeWidth="3"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Decorative Elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-br from-indigo-500 to-sky-500 rounded-2xl rotate-12 opacity-20" />
            <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl -rotate-12 opacity-20" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
