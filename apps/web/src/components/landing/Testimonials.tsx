import React from 'react';
import { Star, Quote, User } from 'lucide-react';

interface Testimonial {
  id: number;
  name: string;
  role: string;
  content: string;
  rating: number;
  avatar?: string;
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    name: 'Sarah Chen',
    role: 'Computer Science Student, MIT',
    content: 'MathVerse completely changed how I understand linear algebra. The animations make abstract concepts tangible. I went from struggling with matrices to actually enjoying them!',
    rating: 5,
  },
  {
    id: 2,
    name: 'Dr. James Wilson',
    role: 'High School Math Teacher',
    content: 'I use MathVerse in my classroom every day. The visual explanations help students who struggle with traditional teaching methods. My students test scores improved by 23%.',
    rating: 5,
  },
  {
    id: 3,
    name: 'Maria Garcia',
    role: 'Parent & Homeschooler',
    content: 'My daughter used to hate math. Now she asks to use MathVerse during her free time! The gamified approach keeps her engaged, and I love that I can track her progress.',
    rating: 5,
  },
  {
    id: 4,
    name: 'Alex Thompson',
    role: 'Physics Undergraduate',
    content: 'The calculus section is exceptional. The way they animate derivatives and integrals made everything click. It\'s like having a personal tutor available 24/7.',
    rating: 5,
  },
  {
    id: 5,
    name: 'Professor Lisa Park',
    role: 'Mathematics Department Head',
    content: 'I recommend MathVerse to all my undergraduate students. The visual approach complements traditional textbook learning perfectly, and the AI tutor provides just-in-time help.',
    rating: 5,
  },
  {
    id: 6,
    name: 'Michael Brown',
    role: 'Self-Taught Developer',
    content: 'Coming back to math after years away was intimidating. MathVerse\'s structured curriculum and clear animations made it accessible. Now I\'m confident tackling machine learning.',
    rating: 5,
  },
];

const Testimonials: React.FC = () => {
  return (
    <section className="section-py bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-full mb-6">
            <Star className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-700">Loved by Learners</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Trusted by{' '}
            <span className="gradient-text">50,000+ students</span>
          </h2>
          <p className="text-lg text-slate-600">
            Join thousands of satisfied learners who have transformed their relationship 
            with mathematics through MathVerse.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={testimonial.id}
              className={`bg-white rounded-2xl p-6 border border-slate-200 card-hover reveal ${
                index >= 3 ? 'lg:mt-6' : ''
              }`}
            >
              {/* Rating */}
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
                ))}
              </div>

              {/* Quote */}
              <div className="relative mb-4">
                <Quote className="w-8 h-8 text-indigo-200 absolute -top-1 -left-1" />
                <p className="text-slate-600 leading-relaxed pl-6">
                  {testimonial.content}
                </p>
              </div>

              {/* Author */}
              <div className="flex items-center gap-3 pt-4 border-t border-slate-100">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-sky-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {testimonial.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <div className="font-semibold text-slate-900">{testimonial.name}</div>
                  <div className="text-sm text-slate-500">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-16 grid sm:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-indigo-600 mb-2">4.9/5</div>
            <div className="flex justify-center mb-2">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
              ))}
            </div>
            <div className="text-slate-500">Average Rating</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-indigo-600 mb-2">98%</div>
            <div className="text-slate-500">Would Recommend</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-indigo-600 mb-2">4.8M</div>
            <div className="text-slate-500">Lessons Completed</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
