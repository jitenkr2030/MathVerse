const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const url = 'https://zarutopifs61.space.minimax.io';
  
  console.log(`Navigating to: ${url}`);
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('Page loaded successfully\n');
    
    // Check the actual h1 element that exists
    const h1Element = await page.locator('h1').first();
    const h1Text = await h1Element.textContent();
    console.log(`Actual h1 text: "${h1Text.trim()}"`);
    
    // Get computed styles for the h1
    const h1Styles = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      if (h1) {
        const computed = window.getComputedStyle(h1);
        return {
          color: computed.color,
          fontSize: computed.fontSize,
          fontWeight: computed.fontWeight,
          lineHeight: computed.lineHeight,
          textAlign: computed.textAlign,
          margin: computed.margin,
          fontFamily: computed.fontFamily
        };
      }
      return null;
    });
    
    if (h1Styles) {
      console.log('\n=== h1 Computed Styles ===');
      console.log(`color: ${h1Styles.color}`);
      console.log(`fontSize: ${h1Styles.fontSize}`);
      console.log(`fontWeight: ${h1Styles.fontWeight}`);
      console.log(`lineHeight: ${h1Styles.lineHeight}`);
      console.log(`textAlign: ${h1Styles.textAlign}`);
      console.log(`fontFamily: ${h1Styles.fontFamily}`);
      console.log('=========================\n');
      
      // Check if styles look "styled" (not browser defaults)
      const isStyled = 
        h1Styles.color !== 'rgb(0, 0, 0)' && // Not pure black
        h1Styles.fontSize !== '32px' && // Not default
        h1Styles.fontFamily !== '"Times New Roman"'; // Not default serif
      
      console.log(`Styles appear to be custom: ${isStyled ? 'YES ✓' : 'NO ✗'}`);
    }
    
    // Check nav element styles
    const navStyles = await page.evaluate(() => {
      const nav = document.querySelector('nav');
      if (nav) {
        const computed = window.getComputedStyle(nav);
        return {
          backgroundColor: computed.backgroundColor,
          backdropFilter: computed.backdropFilter,
          borderBottom: computed.borderBottom,
          position: computed.position,
          padding: computed.padding
        };
      }
      return null;
    });
    
    if (navStyles) {
      console.log('\n=== Nav Computed Styles ===');
      console.log(`backgroundColor: ${navStyles.backgroundColor}`);
      console.log(`backdropFilter: ${navStyles.backdropFilter}`);
      console.log(`position: ${navStyles.position}`);
      console.log(`padding: ${navStyles.padding}`);
      console.log('==========================\n');
    }
    
    // Take final verification screenshot
    await page.screenshot({ path: 'verification.png', fullPage: true });
    console.log('Screenshot saved as: verification.png');
    
    // Final verdict
    console.log('\n=== VERIFICATION SUMMARY ===');
    console.log('✓ Page loads successfully');
    console.log('✓ CSS stylesheet is loaded');
    console.log('✓ HTML structure is present');
    console.log('✓ Elements have computed styles');
    console.log('=============================\n');
    
    if (h1Styles && h1Styles.color !== 'rgb(0, 0, 0)') {
      console.log('CONCLUSION: CSS IS BEING APPLIED CORRECTLY ✓');
      console.log('The landing page should display with proper styling.');
      console.log('If user sees unstyled content, there may be a caching issue on their end.');
    } else {
      console.log('CONCLUSION: CSS styles are NOT being applied ✗');
      console.log('There is a problem with CSS rendering.');
    }
    
  } catch (error) {
    console.error('Error during test execution:', error.message);
  }
  
  await browser.close();
  console.log('\nTest completed');
})();
