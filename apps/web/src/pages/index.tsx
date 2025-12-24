import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuthStore } from '../store';

// Landing page components
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Curriculum from '../components/landing/Curriculum';
import Pricing from '../components/landing/Pricing';
import Testimonials from '../components/landing/Testimonials';
import CTASection from '../components/landing/CTASection';
import Footer from '../components/landing/Footer';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      router.push('/dashboard');
    } else {
      router.push('/register');
    }
  };

  const handleLogin = () => {
    router.push('/login');
  };

  return (
    <>
      <Head>
        <title>MathVerse - Animation-First Mathematics Learning Platform</title>
        <meta name="description" content="Transform your math learning experience with beautiful animations and interactive visualizations" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="landing-page">
        <Navbar onLogin={handleLogin} />
        <Hero onGetStarted={handleGetStarted} />
        <Features />
        <Curriculum />
        <Testimonials />
        <Pricing />
        <CTASection onGetStarted={handleGetStarted} />
        <Footer />
      </div>
    </>
  );
}
