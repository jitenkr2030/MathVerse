import React from 'react';
import { Star, Quote } from 'lucide-react';

interface Testimonial {
  id: number;
  name: string;
  role: string;
  content: string;
  rating: number;
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
    <section className="testimonials-section section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header">
          <div className="section-badge">
            <Star size={16} />
            <span>Loved by Learners</span>
          </div>
          <h2 className="section-title">
            Trusted by <span className="hero-gradient">50,000+ students</span>
          </h2>
          <p className="section-subtitle">
            Join thousands of satisfied learners who have transformed their relationship 
            with mathematics through MathVerse.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="testimonials-grid">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="testimonial-card">
              {/* Rating */}
              <div className="testimonial-rating">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} size={20} />
                ))}
              </div>

              {/* Quote */}
              <p className="testimonial-content">
                {testimonial.content}
              </p>

              {/* Author */}
              <div className="testimonial-author">
                <div className="testimonial-avatar">
                  {testimonial.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <div className="testimonial-name">{testimonial.name}</div>
                  <div className="testimonial-role">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div style={{ marginTop: '80px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '40px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', fontWeight: '800', background: 'linear-gradient(135deg, #8B5CF6, #F97316)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>4.9/5</div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '4px', marginBottom: '8px' }}>
              {[...Array(5)].map((_, i) => (
                <Star key={i} size={20} style={{ fill: '#FBBF24', color: '#FBBF24' }} />
              ))}
            </div>
            <div style={{ color: '#71717A', fontSize: '15px' }}>Average Rating</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', fontWeight: '800', background: 'linear-gradient(135deg, #10B981, #059669)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>98%</div>
            <div style={{ color: '#71717A', fontSize: '15px', marginTop: '8px' }}>Would Recommend</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', fontWeight: '800', background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>4.8M</div>
            <div style={{ color: '#71717A', fontSize: '15px', marginTop: '8px' }}>Lessons Completed</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
