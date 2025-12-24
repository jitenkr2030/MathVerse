import React, { useState } from 'react';
import Link from 'next/link';
import { Menu, X, ArrowRight } from 'lucide-react';

interface NavbarProps {
  onLogin?: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onLogin }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navLinks = [
    { href: '#features', label: 'Features' },
    { href: '#curriculum', label: 'Curriculum' },
    { href: '#pricing', label: 'Pricing' },
    { href: '/courses', label: 'Browse Courses' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link href="/" className="nav-logo">
          <div className="logo-icon">∫</div>
          <span className="logo-text">MathVerse</span>
        </Link>
        
        <div className="nav-links">
          {navLinks.map((link) => (
            <a key={link.label} href={link.href} className="nav-link">
              {link.label}
            </a>
          ))}
        </div>
        
        <div className="nav-actions">
          <button onClick={onLogin} className="btn btn-secondary">
            Log in
          </button>
          <Link href="/register" className="btn btn-primary btn-glow">
            Get Started
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14"/>
              <path d="m12 5 7 7-7 7"/>
            </svg>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="lg:hidden p-2"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="lg:hidden absolute top-full left-0 right-0" style={{ background: '#0F0F23', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ padding: '24px' }}>
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                style={{
                  display: 'block',
                  padding: '16px 0',
                  color: '#A1A1AA',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
                }}
                onClick={() => setIsMenuOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div style={{ paddingTop: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button
                onClick={() => {
                  if (onLogin) onLogin();
                  setIsMenuOpen(false);
                }}
                style={{
                  width: '100%',
                  padding: '14px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  color: 'white',
                  fontWeight: '600'
                }}
              >
                Log in
              </button>
              <Link
                href="/register"
                style={{
                  width: '100%',
                  padding: '14px',
                  background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
                  borderRadius: '12px',
                  color: 'white',
                  fontWeight: '600',
                  textAlign: 'center'
                }}
                onClick={() => setIsMenuOpen(false)}
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
