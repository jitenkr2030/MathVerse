import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuthStore } from '../store';

// Landing page components
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Curriculum from '../components/landing/Curriculum';
import Testimonials from '../components/landing/Testimonials';
import Pricing from '../components/landing/Pricing';
import AppPreview from '../components/landing/AppPreview';
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
        <title>MathVerse - Where Math Comes Alive</title>
        <meta name="description" content="Experience mathematics like never before with stunning animations, interactive visualizations, and AI-powered learning." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="landing-page">
        <Navbar onLogin={handleLogin} />
        <Hero onGetStarted={handleGetStarted} />
        <Features />
        <Curriculum />
        <Testimonials />
        <Pricing />
        <AppPreview />
        <CTASection onGetStarted={handleGetStarted} />
        <Footer />
      </div>
    </>
  );
}
