import React from 'react';
import { motion } from 'framer-motion';

interface CTASectionProps {
  onGetStarted?: () => void;
}

const CTASection: React.FC<CTASectionProps> = ({ onGetStarted }) => {
  const handlePrimaryClick = () => {
    if (onGetStarted) {
      onGetStarted();
    } else {
      console.log('Primary CTA clicked');
    }
  };

  const handleSecondaryClick = () => {
    console.log('Watch Demo clicked');
  };
  return (
    <section className="cta-section">
      <div className="cta-background">
        <div className="cta-shapes">
          <div className="cta-shape cta-shape-1"></div>
          <div className="cta-shape cta-shape-2"></div>
          <div className="cta-shape cta-shape-3"></div>
          <div className="cta-shape cta-shape-4"></div>
        </div>
      </div>
      
      <div className="cta-container">
        <motion.div 
          className="cta-content"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <div className="cta-badge">
            <span className="cta-badge-icon">✦</span>
            <span>Start Your Journey</span>
          </div>
          
          <h2 className="cta-title">
            Ready to Discover the
            <span className="cta-highlight"> Beauty of Mathematics</span>
          </h2>
          
          <p className="cta-description">
            Join thousands of students who are transforming their understanding 
            of mathematics through our interactive, visual approach to learning.
          </p>
          
          <div className="cta-stats">
            <div className="cta-stat">
              <span className="cta-stat-number">10K+</span>
              <span className="cta-stat-label">Active Students</span>
            </div>
            <div className="cta-stat-divider"></div>
            <div className="cta-stat">
              <span className="cta-stat-number">500+</span>
              <span className="cta-stat-label">Interactive Lessons</span>
            </div>
            <div className="cta-stat-divider"></div>
            <div className="cta-stat">
              <span className="cta-stat-number">95%</span>
              <span className="cta-stat-label">Success Rate</span>
            </div>
          </div>
          
          <div className="cta-buttons">
            <button className="cta-button-primary" onClick={handlePrimaryClick}>
              <span>Start Free Trial</span>
              <svg className="cta-button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>
            <button className="cta-button-secondary" onClick={handleSecondaryClick}>
              <svg className="cta-button-play" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <span>Watch Demo</span>
            </button>
          </div>
          
          <div className="cta-trust">
            <div className="cta-avatars">
              <div className="cta-avatar cta-avatar-1">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='35' r='25' fill='%23f4a261'/%3E%3Ccircle cx='50' cy='110' r='60' fill='%23f4a261'/%3E%3C/svg%3E" alt="User" />
              </div>
              <div className="cta-avatar cta-avatar-2">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='35' r='25' fill='%2326a69a'/%3E%3Ccircle cx='50' cy='110' r='60' fill='%2326a69a'/%3E%3C/svg%3E" alt="User" />
              </div>
              <div className="cta-avatar cta-avatar-3">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='35' r='25' fill='%237c3aed'/%3E%3Ccircle cx='50' cy='110' r='60' fill='%237c3aed'/%3E%3C/svg%3E" alt="User" />
              </div>
              <div className="cta-avatar cta-avatar-4">
                <span className="cta-avatar-more">+</span>
              </div>
            </div>
            <p className="cta-trust-text">
              <span className="cta-trust-strong">Trusted by 10,000+</span> students worldwide
            </p>
          </div>
        </motion.div>
      </div>
      
      <div className="cta-glow"></div>
    </section>
  );
};

export default CTASection;
