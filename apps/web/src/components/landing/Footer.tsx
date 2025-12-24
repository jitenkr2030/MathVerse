import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  Twitter, 
  Github, 
  Linkedin, 
  Youtube, 
  Mail, 
  ArrowRight,
  Sparkles
} from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: 'Features', href: '/features', icon: Sparkles },
      { label: 'Pricing', href: '/pricing' },
      { label: 'For Schools', href: '/education' },
      { label: 'For Creators', href: '/creator' },
      { label: 'API Documentation', href: '/docs' },
    ],
    resources: [
      { label: 'Math Blog', href: '/blog' },
      { label: 'Help Center', href: '/help' },
      { label: 'Community', href: '/community' },
      { label: 'Tutorials', href: '/tutorials' },
      { label: 'Research', href: '/research' },
    ],
    company: [
      { label: 'About Us', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Press Kit', href: '/press' },
      { label: 'Contact', href: '/contact' },
      { label: 'Partners', href: '/partners' },
    ],
    legal: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Service', href: '/terms' },
      { label: 'Cookie Policy', href: '/cookies' },
      { label: 'GDPR', href: '/gdpr' },
    ],
  };

  const socialLinks = [
    { icon: Twitter, href: 'https://twitter.com/mathverse', label: 'Twitter' },
    { icon: Github, href: 'https://github.com/mathverse', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com/company/mathverse', label: 'LinkedIn' },
    { icon: Youtube, href: 'https://youtube.com/mathverse', label: 'YouTube' },
  ];

  const FooterLinkColumn: React.FC<{ 
    title: string; 
    links: { label: string; href: string; icon?: React.ElementType }[] 
  }> = ({ title, links }) => (
    <motion.div 
      className="footer-column"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="footer-column-title">{title}</h3>
      <ul className="footer-links">
        {links.map((link, index) => (
          <motion.li 
            key={link.label}
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Link href={link.href} className="footer-link">
              {link.icon && <link.icon className="footer-link-icon" />}
              <span>{link.label}</span>
              <ArrowRight className="footer-link-arrow" />
            </Link>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );

  return (
    <footer className="footer">
      {/* Background decoration */}
      <div className="footer-bg">
        <div className="footer-gradient"></div>
        <div className="footer-pattern"></div>
      </div>
      
      {/* Main Footer Content */}
      <div className="footer-container">
        {/* Newsletter Section */}
        <motion.div 
          className="footer-newsletter"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="footer-newsletter-content">
            <div className="footer-brand">
              <Link href="/" className="footer-logo">
                <div className="footer-logo-icon">
                  <span className="footer-logo-symbol">∫</span>
                </div>
                <span className="footer-logo-text">MathVerse</span>
              </Link>
              <p className="footer-tagline">
                Making mathematics beautiful, intuitive, and accessible through 
                world-class animation technology.
              </p>
            </div>
            
            <div className="footer-newsletter-form">
              <div className="footer-newsletter-input-wrapper">
                <Mail className="footer-newsletter-icon" />
                <input
                  type="email"
                  placeholder="Enter your email for updates"
                  className="footer-newsletter-input"
                />
                <button className="footer-newsletter-button">
                  <span>Subscribe</span>
                  <ArrowRight className="footer-newsletter-button-icon" />
                </button>
              </div>
              <p className="footer-newsletter-note">
                Join 25,000+ educators and students. No spam, ever.
              </p>
            </div>
          </div>
        </motion.div>
        
        {/* Links Section */}
        <div className="footer-links-section">
          <div className="footer-links-grid">
            <FooterLinkColumn title="Product" links={footerLinks.product} />
            <FooterLinkColumn title="Resources" links={footerLinks.resources} />
            <FooterLinkColumn title="Company" links={footerLinks.company} />
            
            {/* Social Column */}
            <motion.div 
              className="footer-column footer-social-column"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h3 className="footer-column-title">Connect</h3>
              <div className="footer-social-links">
                {socialLinks.map((social, index) => (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="footer-social-link"
                    aria-label={social.label}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <social.icon className="footer-social-icon" />
                  </motion.a>
                ))}
              </div>
              <div className="footer-contact">
                <p className="footer-contact-text">Questions? Reach us at</p>
                <a href="mailto:hello@mathverse.io" className="footer-contact-email">
                  hello@mathverse.io
                </a>
              </div>
            </motion.div>
          </div>
        </div>
        
        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <div className="footer-copyright">
              <span className="footer-copyright-symbol">©</span>
              <span className="footer-copyright-year">{currentYear}</span>
              <span className="footer-copyright-text">MathVerse Education Inc.</span>
              <span className="footer-copyright-divider">|</span>
              <span className="footer-copyright-rights">All rights reserved</span>
            </div>
            
            <div className="footer-legal">
              {footerLinks.legal.map((link, index) => (
                <React.Fragment key={link.label}>
                  <Link href={link.href} className="footer-legal-link">
                    {link.label}
                  </Link>
                  {index < footerLinks.legal.length - 1 && (
                    <span className="footer-legal-divider">•</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
