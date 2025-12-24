const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const url = 'https://625bjbqiyeks.space.minimax.io';
  
  console.log(`\n=== Detailed Visual Analysis ===\n`);
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Check if CSS classes are being applied
    console.log('1. Checking CSS Class Application...\n');
    
    const checks = [
      { selector: '.landing-page', prop: 'backgroundColor' },
      { selector: '.navbar', prop: 'backgroundColor' },
      { selector: '.hero-section', prop: 'backgroundColor' },
      { selector: '.hero-title', prop: 'color' },
      { selector: '.hero-subtitle', prop: 'color' },
      { selector: '.feature-card', prop: 'backgroundColor' },
      { selector: '.feature-title', prop: 'color' },
      { selector: '.pricing-card', prop: 'backgroundColor' },
      { selector: '.cta-section', prop: 'backgroundColor' },
      { selector: '.footer', prop: 'backgroundColor' },
    ];
    
    for (const check of checks) {
      const element = await page.$(check.selector);
      if (element) {
        const value = await element.evaluate((el, prop) => getComputedStyle(el)[prop], check.prop);
        console.log('   ' + check.selector + ':');
        console.log('     ' + check.prop + ': ' + value.substring(0, 60));
      } else {
        console.log('   ' + check.selector + ': NOT FOUND');
      }
    }
    
    // Check grid/flex layouts
    console.log('\n2. Checking Grid/Flex Layouts...\n');
    
    const heroContent = await page.$('.hero-content');
    if (heroContent) {
      const display = await heroContent.evaluate(el => getComputedStyle(el).display);
      const flexDirection = await heroContent.evaluate(el => getComputedStyle(el).flexDirection);
      const justifyContent = await heroContent.evaluate(el => getComputedStyle(el).justifyContent);
      console.log('   .hero-content:');
      console.log('     display: ' + display);
      console.log('     flex-direction: ' + flexDirection);
      console.log('     justify-content: ' + justifyContent);
    }
    
    const featuresGrid = await page.$('.features-grid');
    if (featuresGrid) {
      const display = await featuresGrid.evaluate(el => getComputedStyle(el).display);
      const gridTemplateColumns = await featuresGrid.evaluate(el => getComputedStyle(el).gridTemplateColumns);
      const gap = await featuresGrid.evaluate(el => getComputedStyle(el).gap);
      console.log('   .features-grid:');
      console.log('     display: ' + display);
      console.log('     grid-template-columns: ' + gridTemplateColumns.substring(0, 60));
      console.log('     gap: ' + gap);
    }
    
    const pricingGrid = await page.$('.pricing-grid');
    if (pricingGrid) {
      const display = await pricingGrid.evaluate(el => getComputedStyle(el).display);
      const gridTemplateColumns = await pricingGrid.evaluate(el => getComputedStyle(el).gridTemplateColumns);
      console.log('   .pricing-grid:');
      console.log('     display: ' + display);
      console.log('     grid-template-columns: ' + gridTemplateColumns.substring(0, 60));
    }
    
    // Check for specific layout issues
    console.log('\n3. Checking for Common Issues...\n');
    
    // Check text visibility
    const heroTitle = await page.$('.hero-title');
    if (heroTitle) {
      const color = await heroTitle.evaluate(el => getComputedStyle(el).color);
      const fontSize = await heroTitle.evaluate(el => getComputedStyle(el).fontSize);
      const fontWeight = await heroTitle.evaluate(el => getComputedStyle(el).fontWeight);
      console.log('   Hero Title:');
      console.log('     color: ' + color);
      console.log('     font-size: ' + fontSize);
      console.log('     font-weight: ' + fontWeight);
    }
    
    // Check if buttons have proper styling
    const primaryButtons = await page.$$('.btn-primary, .cta-button-primary');
    console.log('   Primary buttons found: ' + primaryButtons.length);
    
    if (primaryButtons.length > 0) {
      const btn = primaryButtons[0];
      const bgColor = await btn.evaluate(el => getComputedStyle(el).backgroundColor);
      console.log('     button background: ' + bgColor.substring(0, 50));
    }
    
    // Check navigation links
    const navLinks = await page.$$('.nav-link');
    console.log('   Navigation links found: ' + navLinks.length);
    
    console.log('\n=== Analysis Complete ===\n');
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
