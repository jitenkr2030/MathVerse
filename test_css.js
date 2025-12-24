const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const consoleMessages = [];
  const consoleErrors = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
    consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });
  
  page.on('pageerror', error => {
    consoleErrors.push(`Page Error: ${error.message}`);
  });
  
  try {
    console.log('Navigating to: https://in62sxnlupxj.space.minimax.io');
    await page.goto('https://in62sxnlupxj.space.minimax.io', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Wait a bit for any async resources
    await page.waitForTimeout(2000);
    
    // Check if page has content
    const title = await page.title();
    console.log('Page Title:', title);
    
    // Check for the presence of key landing page elements
    const hasNavBar = await page.$('nav') !== null;
    const hasHeroSection = await page.$('section') !== null;
    const hasMathVerseText = await page.locator('text=MathVerse').count() > 0;
    
    console.log('Has Navigation Bar:', hasNavBar);
    console.log('Has Sections:', hasHeroSection);
    console.log('Has MathVerse Text:', hasMathVerseText);
    
    // Check if CSS file was loaded
    const cssLoaded = await page.evaluate(() => {
      const links = document.querySelectorAll('link[rel="stylesheet"]');
      return Array.from(links).map(link => link.href);
    });
    console.log('CSS Files Loaded:', cssLoaded.length);
    cssLoaded.forEach((href, i) => console.log(`  CSS ${i+1}: ${href}`));
    
    // Report any console errors
    if (consoleErrors.length > 0) {
      console.log('\n=== CONSOLE ERRORS ===');
      consoleErrors.forEach(err => console.log(err));
    } else {
      console.log('\n=== NO CONSOLE ERRORS ===');
    }
    
    console.log('\nTest completed successfully!');
    
  } catch (error) {
    console.error('Error during test:', error.message);
  } finally {
    await browser.close();
  }
})();
