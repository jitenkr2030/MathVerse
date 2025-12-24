const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const url = 'https://wr2ifrnk1v3d.space.minimax.io';
  
  console.log(`\n=== Testing Landing Page: ${url} ===\n`);
  
  // Track console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  try {
    // Navigate to the page
    console.log('1. Loading page...');
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('   ✓ Page loaded successfully\n');
    
    // Check for key elements
    console.log('2. Checking key elements...');
    
    // Check navbar
    const navbar = await page.$('.navbar');
    console.log(`   ${navbar ? '✓' : '✗'} Navbar found`);
    
    // Check hero section
    const hero = await page.$('.hero-section');
    console.log(`   ${hero ? '✓' : '✗'} Hero section found`);
    
    // Check features section
    const features = await page.$('.features-section');
    console.log(`   ${features ? '✓' : '✗'} Features section found`);
    
    // Check curriculum section
    const curriculum = await page.$('.curriculum-section');
    console.log(`   ${curriculum ? '✓' : '✗'} Curriculum section found`);
    
    // Check testimonials section
    const testimonials = await page.$('.testimonials-section');
    console.log(`   ${testimonials ? '✓' : '✗'} Testimonials section found`);
    
    // Check pricing section
    const pricing = await page.$('.pricing-section');
    console.log(`   ${pricing ? '✓' : '✗'} Pricing section found`);
    
    // Check CTA section
    const cta = await page.$('.cta-section');
    console.log(`   ${cta ? '✓' : '✗'} CTA section found`);
    
    // Check footer
    const footer = await page.$('.footer');
    console.log(`   ${footer ? '✓' : '✗'} Footer found\n`);
    
    // Check CSS is applied by examining computed styles
    console.log('3. Verifying CSS styles are applied...');
    
    const heroTitle = await page.$('.hero-title');
    if (heroTitle) {
      const fontFamily = await heroTitle.evaluate(el => getComputedStyle(el).fontFamily);
      console.log(`   ${fontFamily !== 'serif' ? '✓' : '✗'} Hero title font: ${fontFamily}`);
    }
    
    const heroSection = await page.$('.hero-section');
    if (heroSection) {
      const backgroundColor = await heroSection.evaluate(el => getComputedStyle(el).backgroundColor);
      console.log(`   ${backgroundColor !== 'rgba(0, 0, 0, 0)' ? '✓' : '✗'} Hero background: ${backgroundColor}`);
    }
    
    const featureCards = await page.$$('.feature-card');
    console.log(`   ${featureCards.length > 0 ? '✓' : '✗'} Feature cards found: ${featureCards.length}`);
    
    // Check for console errors
    console.log('4. Checking for console errors...');
    if (consoleErrors.length === 0) {
      console.log('   ✓ No console errors detected\n');
    } else {
      console.log(`   ✗ Found ${consoleErrors.length} console error(s):`);
      consoleErrors.forEach(err => console.log(`     - ${err}`));
      console.log('');
    }
    
    // Get page title
    const title = await page.title();
    console.log(`5. Page title: "${title}"\n`);
    
    console.log('=== Verification Complete ===\n');
    
  } catch (error) {
    console.error('Error during testing:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
