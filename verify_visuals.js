const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const url = 'https://in62sxnlupxj.space.minimax.io';
  
  console.log(`Navigating to: ${url}`);
  
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 30000 });
    
    console.log('Page loaded successfully');
    
    // Locate the h1 element with the specific text
    const h1Element = await page.locator('h1:has-text("Animation-First Mathematics Learning Platform")');
    
    // Check if the element exists
    const elementCount = await h1Element.count();
    console.log(`Found ${elementCount} matching h1 elements`);
    
    if (elementCount > 0) {
      // Get the first matching element
      const element = h1Element.first();
      
      // Get computed CSS color property
      const color = await page.evaluate(() => {
        const h1 = document.querySelector('h1');
        if (h1) {
          const computed = window.getComputedStyle(h1);
          return {
            color: computed.color,
            fontSize: computed.fontSize,
            fontFamily: computed.fontFamily,
            fontWeight: computed.fontWeight,
            backgroundColor: computed.backgroundColor,
            padding: computed.padding,
            margin: computed.margin
          };
        }
        return null;
      });
      
      if (color) {
        console.log('\n=== Computed CSS Properties ===');
        console.log(`color: ${color.color}`);
        console.log(`fontSize: ${color.fontSize}`);
        console.log(`fontFamily: ${color.fontFamily}`);
        console.log(`fontWeight: ${color.fontWeight}`);
        console.log(`backgroundColor: ${color.backgroundColor}`);
        console.log(`padding: ${color.padding}`);
        console.log(`margin: ${color.margin}`);
        console.log('==============================\n');
      } else {
        console.log('Could not get computed styles - element not found in DOM');
      }
      
      // Take full-page screenshot
      const screenshotPath = 'verification.png';
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Full-page screenshot saved as: ${screenshotPath}`);
      
    } else {
      console.log('ERROR: h1 element with specified text not found!');
      // Take screenshot anyway to see current state
      await page.screenshot({ path: 'verification.png', fullPage: true });
      console.log('Screenshot taken to show current page state');
    }
    
    // Additional diagnostic: Check if any stylesheets are loaded
    const stylesheets = await page.evaluate(() => {
      const links = document.querySelectorAll('link[rel="stylesheet"]');
      return Array.from(links).map(link => ({
        href: link.href,
        loaded: link.sheet ? 'loaded' : 'not loaded',
        disabled: link.disabled
      }));
    });
    
    console.log('\n=== Stylesheet Analysis ===');
    console.log(`Number of stylesheets: ${stylesheets.length}`);
    stylesheets.forEach((sheet, index) => {
      console.log(`\nStylesheet ${index + 1}:`);
      console.log(`  href: ${sheet.href}`);
      console.log(`  status: ${sheet.loaded}`);
      console.log(`  disabled: ${sheet.disabled}`);
    });
    console.log('============================\n');
    
    // Check for console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Wait a moment to catch any delayed errors
    await page.waitForTimeout(2000);
    
    if (consoleErrors.length > 0) {
      console.log('=== Console Errors ===');
      consoleErrors.forEach(error => console.log(`ERROR: ${error}`));
      console.log('======================\n');
    } else {
      console.log('No console errors detected');
    }
    
  } catch (error) {
    console.error('Error during test execution:', error.message);
  }
  
  await browser.close();
  console.log('Test completed');
})();
