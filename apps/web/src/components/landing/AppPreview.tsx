import React from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ZoomIn, 
  ChevronRight,
  MousePointer,
  Monitor,
  Tablet,
  Smartphone
} from 'lucide-react';

const AppPreview: React.FC = () => {
  return (
    <section id="app-preview" className="app-preview-section section">
      <div className="section-container">
        {/* Section Header */}
        <motion.div 
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="section-badge">
            <Monitor size={16} />
            <span>App Preview</span>
          </div>
          <h2 className="section-title">
            Experience MathVerse <span className="hero-gradient">Across All Devices</span>
          </h2>
          <p className="section-subtitle">
            Seamlessly learn on any device with our responsive, feature-rich application. 
            Switch from desktop to mobile without losing your progress.
          </p>
        </motion.div>

        {/* App Preview Card */}
        <motion.div 
          className="app-preview-card"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          {/* Browser Chrome */}
          <div className="app-preview-browser">
            <div className="browser-dots">
              <span className="browser-dot red"></span>
              <span className="browser-dot yellow"></span>
              <span className="browser-dot green"></span>
            </div>
            <div className="browser-url">
              https://app.mathverse.io/learn/calculus/derivatives
            </div>
          </div>

          {/* App Content */}
          <div className="app-preview-content">
            {/* Sidebar */}
            <div className="app-sidebar">
              <div className="app-logo">
                <div className="app-logo-icon">
                  <span>∫</span>
                </div>
              </div>
              <nav className="app-nav">
                <a href="#" className="app-nav-item active">
                  <Monitor size={20} />
                </a>
                <a href="#" className="app-nav-item">
                  <Smartphone size={20} />
                </a>
                <a href="#" className="app-nav-item">
                  <Tablet size={20} />
                </a>
              </nav>
              <div className="app-sidebar-footer">
                <div className="app-user-avatar">JD</div>
              </div>
            </div>

            {/* Main Content */}
            <div className="app-main">
              {/* Header */}
              <div className="app-header">
                <div className="app-breadcrumb">
                  <span>Calculus</span>
                  <ChevronRight size={16} />
                  <span>Derivatives</span>
                  <ChevronRight size={16} />
                  <span>Introduction</span>
                </div>
                <div className="app-progress">
                  <div className="app-progress-bar">
                    <div className="app-progress-fill" style={{ width: '65%' }}></div>
                  </div>
                  <span className="app-progress-text">65% Complete</span>
                </div>
              </div>

              {/* Math Visualization Area */}
              <div className="app-math-area">
                <div className="math-visualization">
                  <div className="math-equation">
                    <span className="math-formula-large">f(x) = x²</span>
                    <span className="math-derivative-arrow">→</span>
                    <span className="math-formula-large accent">f'(x) = 2x</span>
                  </div>
                  <div className="math-graph">
                    <svg viewBox="0 0 400 200" className="graph-svg">
                      {/* Grid lines */}
                      <line x1="50" y1="100" x2="350" y2="100" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                      <line x1="200" y1="20" x2="200" y2="180" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                      {/* Parabola */}
                      <path 
                        d="M 50 180 Q 200 20 350 180" 
                        fill="none" 
                        stroke="url(#gradient)" 
                        strokeWidth="3"
                      />
                      {/* Tangent line */}
                      <line 
                        x1="100" y1="140" 
                        x2="300" y2="60" 
                        stroke="#F97316" 
                        strokeWidth="2"
                        strokeDasharray="5,5"
                      />
                      {/* Gradient definition */}
                      <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#8B5CF6" />
                          <stop offset="100%" stopColor="#F97316" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </div>

                {/* Controls */}
                <div className="app-controls">
                  <motion.button 
                    className="app-control-btn"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <RotateCcw size={18} />
                    <span>Replay</span>
                  </motion.button>
                  <motion.button 
                    className="app-control-btn play"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Play size={18} />
                    <span>Play Animation</span>
                  </motion.button>
                  <motion.button 
                    className="app-control-btn"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <ZoomIn size={18} />
                    <span>Zoom</span>
                  </motion.button>
                </div>
              </div>

              {/* Interactive Elements */}
              <div className="app-interactive">
                <div className="interactive-hint">
                  <MousePointer size={16} />
                  <span>Drag the point to see how the derivative changes</span>
                </div>
                <div className="interactive-point"></div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Device Showcase */}
        <div className="device-showcase">
          <motion.div 
            className="device-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Monitor size={48} className="device-icon" />
            <h3 className="device-title">Desktop</h3>
            <p className="device-description">Full interactive experience with keyboard shortcuts and multi-window support</p>
          </motion.div>
          <motion.div 
            className="device-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Tablet size={48} className="device-icon" />
            <h3 className="device-title">Tablet</h3>
            <p className="device-description">Touch-optimized animations with Apple Pencil and stylus support</p>
          </motion.div>
          <motion.div 
            className="device-card"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Smartphone size={48} className="device-icon" />
            <h3 className="device-title">Mobile</h3>
            <p className="device-description">Offline access with spaced repetition and quick review modes</p>
          </motion.div>
        </div>

        {/* App Stats */}
        <div className="app-stats">
          <div className="app-stat">
            <span className="app-stat-number">10M+</span>
            <span className="app-stat-label">Active Learners</span>
          </div>
          <div className="app-stat">
            <span className="app-stat-number">50M+</span>
            <span className="app-stat-label">Lessons Completed</span>
          </div>
          <div className="app-stat">
            <span className="app-stat-number">4.9★</span>
            <span className="app-stat-label">App Store Rating</span>
          </div>
          <div className="app-stat">
            <span className="app-stat-number">99.9%</span>
            <span className="app-stat-label">Uptime SLA</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AppPreview;
