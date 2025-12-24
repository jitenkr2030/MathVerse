const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const url = 'https://in62sxnlupxj.space.minimax.io';
  
  console.log(`Navigating to: ${url}`);
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    console.log('Page loaded successfully\n');
    
    // Get the actual HTML content
    const htmlContent = await page.content();
    console.log('=== Raw HTML (first 2000 chars) ===');
    console.log(htmlContent.substring(0, 2000));
    console.log('====================================\n');
    
    // Get all h1, h2, h3 elements
    const headings = await page.evaluate(() => {
      const result = {};
      ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
        const elements = document.querySelectorAll(tag);
        result[tag] = Array.from(elements).map(el => ({
          text: el.textContent.trim(),
          tagName: el.tagName
        }));
      });
      return result;
    });
    
    console.log('=== All Heading Elements ===');
    Object.keys(headings).forEach(tag => {
      if (headings[tag].length > 0) {
        console.log(`\n${tag} elements:`);
        headings[tag].forEach((h, index) => {
          console.log(`  [${index + 1}] "${h.text}"`);
        });
      }
    });
    console.log('\n=============================\n');
    
    // Get the page title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Check if main content exists
    const mainContent = await page.locator('main, #__next, .landing-page, header, footer').count();
    console.log(`Main content containers found: ${mainContent}`);
    
    // Get body content structure
    const bodyStructure = await page.evaluate(() => {
      return {
        innerHTML: document.body.innerHTML.substring(0, 500),
        childElementCount: document.body.childElementCount
      };
    });
    
    console.log(`\nBody has ${bodyStructure.childElementCount} child elements`);
    console.log('Body content (first 500 chars):');
    console.log(bodyStructure.innerHTML);
    
    // Take a new screenshot
    await page.screenshot({ path: 'verification.png', fullPage: true });
    console.log('\nScreenshot saved as: verification.png');
    
  } catch (error) {
    console.error('Error during test execution:', error.message);
  }
  
  await browser.close();
  console.log('Test completed');
})();
