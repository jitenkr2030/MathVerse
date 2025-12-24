const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const url = 'https://625bjbqiyeks.space.minimax.io';
  
  console.log(`\n=== Diagnosing Landing Page Layout ===\n`);
  
  try {
    // Navigate to the page
    console.log('1. Loading page...');
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('   Page loaded\n');
    
    // Check layout structure
    console.log('2. Checking Layout Structure...\n');
    
    // Check page width and overflow
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    const hasHorizontalScroll = await page.evaluate(() => document.body.scrollWidth > window.innerWidth);
    console.log('   Body width: ' + bodyWidth + 'px, Viewport: ' + viewportWidth + 'px');
    console.log('   Horizontal scroll: ' + (hasHorizontalScroll ? 'YES (issue!)' : 'No'));
    
    // Check main container
    const mainContainer = await page.$('.landing-page');
    if (mainContainer) {
      const containerRect = await mainContainer.boundingBox();
      console.log('   Main container: ' + (containerRect ? 'Found (' + containerRect.width.toFixed(0) + 'x' + containerRect.height.toFixed(0) + ')' : 'Not found'));
    }
    
    // Check section alignment
    console.log('\n3. Checking Section Structure...\n');
    
    const sections = [
      '.navbar',
      '.hero-section', 
      '.features-section',
      '.curriculum-section',
      '.testimonials-section',
      '.pricing-section',
      '.cta-section',
      '.footer'
    ];
    
    for (const section of sections) {
      const el = await page.$(section);
      if (el) {
        const rect = await el.boundingBox();
        const styles = await el.evaluate(el => getComputedStyle(el));
        console.log('   ' + section + ':');
        console.log('     - Size: ' + (rect ? rect.width.toFixed(0) + 'x' + rect.height.toFixed(0) : 'N/A'));
        console.log('     - Display: ' + styles.display + ', Position: ' + styles.position);
        console.log('     - Visibility: ' + styles.visibility);
      } else {
        console.log('   ' + section + ': NOT FOUND');
      }
    }
    
    // Check for hidden elements with display:none
    console.log('\n4. Checking for Hidden Elements...');
    const allSections = await page.$$('section');
    console.log('   Total section elements: ' + allSections.length);
    
    // Check CSS file loading
    console.log('\n5. Checking CSS Loading...');
    const cssLinks = await page.$$eval('link[rel="stylesheet"]', links => 
      links.map(link => ({
        href: link.href,
        loaded: link.sheet !== null
      }))
    );
    
    cssLinks.forEach((css, i) => {
      console.log('   CSS ' + (i + 1) + ': ' + css.href.substring(0, 80) + '...');
      console.log('     Loaded: ' + (css.loaded ? 'YES' : 'NO'));
    });
    
    // Check for layout issues
    console.log('\n6. Common Layout Issues...');
    
    // Check if body has proper box-sizing
    const bodyBoxSizing = await page.evaluate(() => {
      const el = document.body;
      return getComputedStyle(el).boxSizing;
    });
    console.log('   Body box-sizing: ' + bodyBoxSizing);
    
    // Check navbar visibility and position
    const navbar = await page.$('.navbar');
    if (navbar) {
      const navStyles = await navbar.evaluate(el => ({
        position: getComputedStyle(el).position,
        top: getComputedStyle(el).top,
        zIndex: getComputedStyle(el).zIndex,
        backgroundColor: getComputedStyle(el).backgroundColor
      }));
      console.log('   Navbar position: ' + navStyles.position + ', z-index: ' + navStyles.zIndex);
      console.log('   Navbar background: ' + navStyles.backgroundColor);
    }
    
    // Check hero visual
    const heroVisual = await page.$('.hero-visual');
    if (heroVisual) {
      const heroVisualRect = await heroVisual.boundingBox();
      console.log('   Hero visual: ' + (heroVisualRect ? 'Found (' + heroVisualRect.width.toFixed(0) + 'x' + heroVisualRect.height.toFixed(0) + ')' : 'Not visible'));
    }
    
    // Check for console errors related to layout
    console.log('\n7. Console Errors...');
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Wait a moment to catch any errors
    await page.waitForTimeout(2000);
    
    if (errors.length === 0) {
      console.log('   No console errors detected');
    } else {
      console.log('   Found ' + errors.length + ' error(s):');
      errors.forEach(err => console.log('     - ' + err));
    }
    
    console.log('\n=== Diagnosis Complete ===\n');
    
  } catch (error) {
    console.error('Error during diagnosis:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
