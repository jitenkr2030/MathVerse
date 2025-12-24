// Generate complete Tailwind CSS + Custom Landing Page CSS
const fs = require('fs');
const path = require('path');

// Read all source files
function getAllFiles(dirPath, arrayOfFiles) {
  const files = fs.readdirSync(dirPath);
  arrayOfFiles = arrayOfFiles || [];

  files.forEach((file) => {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
    } else {
      if (file.match(/\.(tsx?|jsx?)$/)) {
        arrayOfFiles.push(path.join(dirPath, "/", file));
      }
    }
  });

  return arrayOfFiles;
}

// Read all TSX/TS/JSX/JS files
const srcFiles = getAllFiles('./src/pages');
const componentFiles = getAllFiles('./src/components');

console.log(`Found ${srcFiles.length + componentFiles.length} source files`);

// Read and combine all files
const allContent = [...srcFiles, ...componentFiles]
  .map(file => {
    try {
      return fs.readFileSync(file, 'utf8');
    } catch (e) {
      return '';
    }
  })
  .join('\n');

// Extract all Tailwind class names
const classRegex = /className="([^"]+)"/g;
const matches = [...allContent.matchAll(classRegex)];

const allClasses = new Set();
matches.forEach(match => {
  const classes = match[1].split(/\s+/);
  classes.forEach(cls => {
    if (cls && cls.trim()) {
      allClasses.add(cls.trim());
    }
  });
});

console.log(`Found ${allClasses.size} unique class names`);

// Generate minimal CSS with just the classes we need
let css = `/* Auto-generated Tailwind CSS - ${new Date().toISOString()} */\n\n`;

// Base styles
css += `/* Base */\n`;
css += `*, ::before, ::after { box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e5e7eb; }\n`;
css += `::before, ::after { --tw-content: ''; }\n`;
css += `html { line-height: 1.5; -webkit-text-size-adjust: 100%; -moz-tab-size: 4; tab-size: 4; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif; font-feature-settings: normal; font-variation-settings: normal; }\n`;
css += `body { margin: 0; line-height: inherit; }\n`;
css += `hr { height: 0; color: inherit; border-top-width: 1px; }\n`;
css += `abbr:where([title]) { text-decoration: underline dotted; }\n`;
css += `h1, h2, h3, h4, h5, h6 { font-size: inherit; font-weight: inherit; }\n`;
css += `a { color: inherit; text-decoration: inherit; }\n`;
css += `b, strong { font-weight: bolder; }\n`;
css += `code, kbd, samp, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 1em; }\n`;
css += `small { font-size: 80%; }\n`;
css += `sub, sup { font-size: 75%; line-height: 0; position: relative; vertical-align: baseline; }\n`;
css += `sub { bottom: -0.25em; }\n`;
css += `sup { top: -0.5em; }\n`;
css += `table { text-indent: 0; border-color: inherit; border-collapse: collapse; }\n`;
css += `button, input, optgroup, select, textarea { font-family: inherit; font-feature-settings: inherit; font-variation-settings: inherit; font-size: 100%; font-weight: inherit; line-height: inherit; color: inherit; margin: 0; padding: 0; }\n`;
css += `button, select { text-transform: none; }\n`;
css += `button, [type='button'], [type='reset'], [type='submit'] { -webkit-appearance: button; background-image: none; }\n`;
css += `:-moz-focusring { outline: auto; }\n`;
css += `:-moz-ui-invalid { box-shadow: none; }\n`;
css += `progress { vertical-align: baseline; }\n`;
css += `::-webkit-inner-spin-button, ::-webkit-outer-spin-button { height: auto; }\n`;
css += `[type='search'] { -webkit-appearance: textfield; outline-offset: -2px; }\n`;
css += `::-webkit-search-decoration { -webkit-appearance: none; }\n`;
css += `::-webkit-file-upload-button { -webkit-appearance: button; font: inherit; }\n`;
css += `summary { display: list-item; }\n`;
css += `blockquote, dl, dd, h1, h2, h3, h4, h5, h6, hr, figure, p, pre { margin: 0; }\n`;
css += `fieldset { margin: 0; padding: 0; }\n`;
css += `legend { padding: 0; }\n`;
css += `ol, ul, menu { list-style: none; margin: 0; padding: 0; }\n`;
css += `dialog { padding: 0; }\n`;
css += `textarea { resize: vertical; }\n`;
css += `input::placeholder, textarea::placeholder { opacity: 1; color: #9ca3af; }\n`;
css += `button, [role="button"] { cursor: pointer; }\n`;
css += `:disabled { cursor: default; }\n`;
css += `img, svg, video, canvas, audio, iframe, embed, object { display: block; vertical-align: middle; }\n`;
css += `img, video { max-width: 100%; height: auto; }\n`;
css += `[hidden] { display: none; }\n\n`;

// Generate CSS for each class found
const generateUtilityCSS = (className) => {
  // Common utilities
  const utilities = {
    // Flexbox
    'flex': 'display: flex;',
    'inline-flex': 'display: inline-flex;',
    'grid': 'display: grid;',
    'block': 'display: block;',
    'inline-block': 'display: inline-block;',
    'hidden': 'display: none;',
    'items-center': 'align-items: center;',
    'items-start': 'align-items: flex-start;',
    'items-end': 'align-items: flex-end;',
    'justify-center': 'justify-content: center;',
    'justify-between': 'justify-content: space-between;',
    'justify-start': 'justify-content: flex-start;',
    'justify-end': 'justify-content: flex-end;',
    'flex-col': 'flex-direction: column;',
    'flex-row': 'flex-direction: row;',
    'flex-wrap': 'flex-wrap: wrap;',
    'flex-1': 'flex: 1 1 0%;',
    'flex-auto': 'flex: 1 1 auto;',
    'flex-initial': 'flex: 0 1 auto;',
    'flex-none': 'flex: none;',
    'gap-1': 'gap: 0.25rem;',
    'gap-2': 'gap: 0.5rem;',
    'gap-3': 'gap: 0.75rem;',
    'gap-4': 'gap: 1rem;',
    'gap-6': 'gap: 1.5rem;',
    'gap-8': 'gap: 2rem;',
    'space-x-2': 'margin-left: 0.5rem;',
    'space-x-4': 'margin-left: 1rem;',
    
    // Grid
    'grid-cols-2': 'grid-template-columns: repeat(2, minmax(0, 1fr));',
    'grid-cols-3': 'grid-template-columns: repeat(3, minmax(0, 1fr));',
    'grid-cols-4': 'grid-template-columns: repeat(4, minmax(0, 1fr));',
    
    // Spacing
    'p-1': 'padding: 0.25rem;',
    'p-2': 'padding: 0.5rem;',
    'p-3': 'padding: 0.75rem;',
    'p-4': 'padding: 1rem;',
    'p-6': 'padding: 1.5rem;',
    'p-8': 'padding: 2rem;',
    'px-2': 'padding-left: 0.5rem; padding-right: 0.5rem;',
    'px-3': 'padding-left: 0.75rem; padding-right: 0.75rem;',
    'px-4': 'padding-left: 1rem; padding-right: 1rem;',
    'px-6': 'padding-left: 1.5rem; padding-right: 1.5rem;',
    'px-8': 'padding-left: 2rem; padding-right: 2rem;',
    'py-1': 'padding-top: 0.25rem; padding-bottom: 0.25rem;',
    'py-2': 'padding-top: 0.5rem; padding-bottom: 0.5rem;',
    'py-3': 'padding-top: 0.75rem; padding-bottom: 0.75rem;',
    'py-4': 'padding-top: 1rem; padding-bottom: 1rem;',
    'py-8': 'padding-top: 2rem; padding-bottom: 2rem;',
    'pt-8': 'padding-top: 2rem;',
    'pb-8': 'padding-bottom: 2rem;',
    'm-0': 'margin: 0;',
    'm-2': 'margin: 0.5rem;',
    'mx-auto': 'margin-left: auto; margin-right: auto;',
    'mt-2': 'margin-top: 0.5rem;',
    'mt-4': 'margin-top: 1rem;',
    'mt-6': 'margin-top: 1.5rem;',
    'mt-8': 'margin-top: 2rem;',
    'mb-2': 'margin-bottom: 0.5rem;',
    'mb-4': 'margin-bottom: 1rem;',
    'mb-6': 'margin-bottom: 1.5rem;',
    'mb-8': 'margin-bottom: 2rem;',
    'ml-2': 'margin-left: 0.5rem;',
    'ml-4': 'margin-left: 1rem;',
    'mr-2': 'margin-right: 0.5rem;',
    'mr-4': 'margin-right: 1rem;',
    
    // Sizing
    'w-full': 'width: 100%;',
    'w-auto': 'width: auto;',
    'w-1/2': 'width: 50%;',
    'w-1/3': 'width: 33.333%;',
    'w-2/3': 'width: 66.666%;',
    'w-10': 'width: 2.5rem;',
    'w-12': 'width: 3rem;',
    'w-16': 'width: 4rem;',
    'w-20': 'width: 5rem;',
    'h-full': 'height: 100%;',
    'h-auto': 'height: auto;',
    'h-8': 'height: 2rem;',
    'h-10': 'height: 2.5rem;',
    'h-12': 'height: 3rem;',
    'h-16': 'height: 4rem;',
    'min-h-screen': 'min-height: 100vh;',
    'max-w-7xl': 'max-width: 80rem;',
    'max-w-3xl': 'max-width: 48rem;',
    'max-w-xl': 'max-width: 36rem;',
    'max-w-4xl': 'max-width: 56rem;',
    'max-w-5xl': 'max-width: 64rem;',
    'max-w-6xl': 'max-width: 72rem;',
    'max-w-full': 'max-width: 100%;',
    'max-h-full': 'max-height: 100%;',
    
    // Typography
    'text-xs': 'font-size: 0.75rem; line-height: 1rem;',
    'text-sm': 'font-size: 0.875rem; line-height: 1.25rem;',
    'text-base': 'font-size: 1rem; line-height: 1.5rem;',
    'text-lg': 'font-size: 1.125rem; line-height: 1.75rem;',
    'text-xl': 'font-size: 1.25rem; line-height: 1.75rem;',
    'text-2xl': 'font-size: 1.5rem; line-height: 2rem;',
    'text-3xl': 'font-size: 1.875rem; line-height: 2.25rem;',
    'text-4xl': 'font-size: 2.25rem; line-height: 2.5rem;',
    'text-5xl': 'font-size: 3rem; line-height: 1;',
    'text-6xl': 'font-size: 3.75rem; line-height: 1;',
    'font-normal': 'font-weight: 400;',
    'font-medium': 'font-weight: 500;',
    'font-semibold': 'font-weight: 600;',
    'font-bold': 'font-weight: 700;',
    'text-left': 'text-align: left;',
    'text-center': 'text-align: center;',
    'text-right': 'text-align: right;',
    'leading-tight': 'line-height: 1.25;',
    'leading-relaxed': 'line-height: 1.625;',
    'leading-normal': 'line-height: 1.5;',
    'tracking-tight': 'letter-spacing: -0.025em;',
    'tracking-wide': 'letter-spacing: 0.025em;',
    'text-transparent': 'color: transparent;',
    
    // Colors
    'text-white': 'color: #ffffff;',
    'text-black': 'color: #000000;',
    'text-gray-50': 'color: #f9fafb;',
    'text-gray-100': 'color: #f3f4f6;',
    'text-gray-200': 'color: #e5e7eb;',
    'text-gray-300': 'color: #d1d5db;',
    'text-gray-400': 'color: #9ca3af;',
    'text-gray-500': 'color: #6b7280;',
    'text-gray-600': 'color: #4b5563;',
    'text-gray-700': 'color: #374151;',
    'text-gray-800': 'color: #1f2937;',
    'text-gray-900': 'color: #111827;',
    'text-slate-900': 'color: #0f172a;',
    'text-slate-800': 'color: #1e293b;',
    'text-slate-700': 'color: #334155;',
    'text-slate-600': 'color: #475569;',
    'text-slate-500': 'color: #64748b;',
    'text-slate-400': 'color: #94a3b8;',
    'text-slate-300': 'color: #cbd5e1;',
    'text-indigo-50': 'color: #eef2ff;',
    'text-indigo-100': 'color: #e0e7ff;',
    'text-indigo-200': 'color: #c7d2fe;',
    'text-indigo-300': 'color: #a5b4fc;',
    'text-indigo-400': 'color: #818cf8;',
    'text-indigo-500': 'color: #6366f1;',
    'text-indigo-600': 'color: #4f46e5;',
    'text-indigo-700': 'color: #4338ca;',
    'text-indigo-800': 'color: #3730a3;',
    'text-indigo-900': 'color: #312e81;',
    'text-blue-50': 'color: #eff6ff;',
    'text-blue-100': 'color: #dbeafe;',
    'text-blue-500': 'color: #3b82f6;',
    'text-blue-600': 'color: #2563eb;',
    'text-blue-700': 'color: #1d4ed8;',
    'text-green-50': 'color: #f0fdf4;',
    'text-green-100': 'color: #dcfce7;',
    'text-green-400': 'color: #4ade80;',
    'text-green-500': 'color: #22c55e;',
    'text-green-600': 'color: #16a34a;',
    'text-green-700': 'color: #15803d;',
    'text-amber-400': 'color: #fbbf24;',
    'text-amber-500': 'color: #f59e0b;',
    'text-amber-600': 'color: #d97706;',
    'text-red-400': 'color: #f87171;',
    'text-red-500': 'color: #ef4444;',
    'text-red-600': 'color: #dc2626;',
    'text-violet-500': 'color: #8b5cf6;',
    'text-violet-600': 'color: #7c3aed;',
    'text-sky-400': 'color: #38bdf8;',
    'text-sky-500': 'color: #0ea5e9;',
    'text-emerald-500': 'color: #10b981;',
    'text-emerald-600': 'color: #059669;',
    'text-rose-500': 'color: #f43f5e;',
    'text-rose-600': 'color: #e11d48;',
    
    // Backgrounds
    'bg-white': 'background-color: #ffffff;',
    'bg-black': 'background-color: #000000;',
    'bg-gray-50': 'background-color: #f9fafb;',
    'bg-gray-100': 'background-color: #f3f4f6;',
    'bg-gray-200': 'background-color: #e5e7eb;',
    'bg-gray-800': 'background-color: #1f2937;',
    'bg-gray-900': 'background-color: #111827;',
    'bg-slate-50': 'background-color: #f8fafc;',
    'bg-slate-100': 'background-color: #f1f5f9;',
    'bg-slate-800': 'background-color: #1e293b;',
    'bg-slate-900': 'background-color: #0f172a;',
    'bg-indigo-50': 'background-color: #eef2ff;',
    'bg-indigo-100': 'background-color: #e0e7ff;',
    'bg-indigo-500': 'background-color: #6366f1;',
    'bg-indigo-600': 'background-color: #4f46e5;',
    'bg-indigo-700': 'background-color: #4338ca;',
    'bg-indigo-800': 'background-color: #3730a3;',
    'bg-blue-50': 'background-color: #eff6ff;',
    'bg-blue-100': 'background-color: #dbeafe;',
    'bg-blue-600': 'background-color: #2563eb;',
    'bg-green-50': 'background-color: #f0fdf4;',
    'bg-green-100': 'background-color: #dcfce7;',
    'bg-green-500': 'background-color: #22c55e;',
    'bg-green-600': 'background-color: #16a34a;',
    'bg-amber-50': 'background-color: #fffbeb;',
    'bg-amber-100': 'background-color: #fef3c7;',
    'bg-emerald-50': 'background-color: #ecfdf5;',
    'bg-emerald-100': 'background-color: #d1fae5;',
    'bg-emerald-600': 'background-color: #059669;',
    'bg-sky-50': 'background-color: #f0f9ff;',
    'bg-sky-100': 'background-color: #e0f2fe;',
    'bg-violet-50': 'background-color: #f5f3ff;',
    'bg-rose-50': 'background-color: #fff1f2;',
    'bg-transparent': 'background-color: transparent;',
    
    // Gradients
    'bg-gradient-to-r': 'background-image: linear-gradient(to right, var(--tw-gradient-stops));',
    'bg-gradient-to-br': 'background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));',
    'bg-gradient-to-tr': 'background-image: linear-gradient(to top right, var(--tw-gradient-stops));',
    'from-indigo-500': '--tw-gradient-from: #6366f1; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(99, 102, 241, 0));',
    'from-indigo-600': '--tw-gradient-from: #4f46e5; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(79, 70, 229, 0));',
    'to-purple-500': '--tw-gradient-to: #a855f7;',
    'to-purple-600': '--tw-gradient-to: #9333ea;',
    'to-sky-400': '--tw-gradient-to: #38bdf8;',
    'to-sky-500': '--tw-gradient-to: #0ea5e9;',
    'to-indigo-700': '--tw-gradient-to: #4338ca;',
    'to-emerald-500': '--tw-gradient-to: #10b981;',
    'via-sky-500': '--tw-gradient-via: #0ea5e9; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-via), var(--tw-gradient-to);',
    
    // Borders
    'border': 'border-width: 1px;',
    'border-2': 'border-width: 2px;',
    'border-4': 'border-width: 4px;',
    'border-8': 'border-width: 8px;',
    'border-none': 'border-style: none;',
    'border-gray-200': 'border-color: #e5e7eb;',
    'border-gray-300': 'border-color: #d1d5db;',
    'border-slate-200': 'border-color: #e2e8f0;',
    'border-slate-300': 'border-color: #cbd5e1;',
    'border-slate-700': 'border-color: #334155;',
    'border-indigo-500': 'border-color: #6366f1;',
    'border-indigo-600': 'border-color: #4f46e5;',
    'border-blue-500': 'border-color: #3b82f6;',
    'border-green-500': 'border-color: #22c55e;',
    'border-red-500': 'border-color: #ef4444;',
    'border-white': 'border-color: #ffffff;',
    
    // Border Radius
    'rounded': 'border-radius: 0.25rem;',
    'rounded-sm': 'border-radius: 0.125rem;',
    'rounded-md': 'border-radius: 0.375rem;',
    'rounded-lg': 'border-radius: 0.5rem;',
    'rounded-xl': 'border-radius: 0.75rem;',
    'rounded-2xl': 'border-radius: 1rem;',
    'rounded-3xl': 'border-radius: 1.5rem;',
    'rounded-full': 'border-radius: 9999px;',
    
    // Shadows
    'shadow': 'box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);',
    'shadow-md': 'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);',
    'shadow-lg': 'box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);',
    'shadow-xl': 'box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);',
    'shadow-2xl': 'box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);',
    'shadow-sm': 'box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);',
    'shadow-none': 'box-shadow: none;',
    'shadow-indigo-500/30': 'box-shadow: 0 0 15px 0 rgb(99 102 241 / 0.3);',
    'shadow-indigo-500/50': 'box-shadow: 0 0 25px 0 rgb(99 102 241 / 0.5);',
    'shadow-slate-200/50': 'box-shadow: 0 0 25px 0 rgb(148 163 184 / 0.5);',
    'shadow-xl/20': 'box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.2);',
    
    // Effects
    'opacity-0': 'opacity: 0;',
    'opacity-5': 'opacity: 0.05;',
    'opacity-10': 'opacity: 0.1;',
    'opacity-20': 'opacity: 0.2;',
    'opacity-30': 'opacity: 0.3;',
    'opacity-50': 'opacity: 0.5;',
    'opacity-80': 'opacity: 0.8;',
    'opacity-100': 'opacity: 1;',
    'overflow-hidden': 'overflow: hidden;',
    'overflow-visible': 'overflow: visible;',
    'overflow-auto': 'overflow: auto;',
    
    // Positioning
    'relative': 'position: relative;',
    'absolute': 'position: absolute;',
    'fixed': 'position: fixed;',
    'sticky': 'position: sticky;',
    'static': 'position: static;',
    'inset-0': 'inset: 0;',
    'top-0': 'top: 0;',
    'top-1/2': 'top: 50%;',
    'top-1/4': 'top: 25%;',
    'bottom-0': 'bottom: 0;',
    'bottom-1/4': 'bottom: 25%;',
    'left-0': 'left: 0;',
    'left-1/2': 'left: 50%;',
    'left-1/4': 'left: 25%;',
    'right-0': 'right: 0;',
    'right-1/2': 'right: 50%;',
    'right-1/4': 'right: 25%;',
    'z-0': 'z-index: 0;',
    'z-10': 'z-index: 10;',
    'z-20': 'z-index: 20;',
    'z-30': 'z-index: 30;',
    'z-40': 'z-index: 40;',
    'z-50': 'z-index: 50;',
    
    // Transforms
    'transform': 'transform: translateX(var(--tw-translate-x)) translateY(var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));',
    'scale-105': '--tw-scale-x: 1.05; --tw-scale-y: 1.05;',
    'scale-110': '--tw-scale-x: 1.1; --tw-scale-y: 1.1;',
    'rotate-12': '--tw-rotate: 12deg;',
    'rotate-45': '--tw-rotate: 45deg;',
    '-rotate-12': '--tw-rotate: -12deg;',
    'translate-x-0': '--tw-translate-x: 0px;',
    'translate-x-1/2': '--tw-translate-x: 50%;',
    '-translate-x-1/2': '--tw-translate-x: -50%;',
    'translate-y-0': '--tw-translate-y: 0px;',
    'translate-y-10': '--tw-translate-y: 2.5rem;',
    '-translate-y-10': '--tw-translate-y: -2.5rem;',
    'translate-y-1/2': '--tw-translate-y: 50%;',
    '-translate-y-1/2': '--tw-translate-y: -50%;',
    
    // Transitions
    'transition': 'transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;',
    'transition-all': 'transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;',
    'transition-colors': 'transition-property: color, background-color, border-color, text-decoration-color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;',
    'transition-shadow': 'transition-property: box-shadow; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;',
    'transition-transform': 'transition-property: transform; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms;',
    'duration-75': 'transition-duration: 75ms;',
    'duration-100': 'transition-duration: 100ms;',
    'duration-150': 'transition-duration: 150ms;',
    'duration-200': 'transition-duration: 200ms;',
    'duration-300': 'transition-duration: 300ms;',
    'duration-500': 'transition-duration: 500ms;',
    'duration-700': 'transition-duration: 700ms;',
    'duration-1000': 'transition-duration: 1000ms;',
    'ease-linear': 'transition-timing-function: linear;',
    'ease-in': 'transition-timing-function: cubic-bezier(0.4, 0, 1, 1);',
    'ease-out': 'transition-timing-function: cubic-bezier(0, 0, 0.2, 1);',
    'ease-in-out': 'transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);',
    
    // Hover states
    'hover:bg-indigo-700:hover': 'background-color: #4338ca;',
    'hover:bg-gray-100:hover': 'background-color: #f3f4f6;',
    'hover:bg-gray-50:hover': 'background-color: #f9fafb;',
    'hover:bg-white:hover': 'background-color: #ffffff;',
    'hover:text-indigo-600:hover': 'color: #4f46e5;',
    'hover:text-white:hover': 'color: #ffffff;',
    'hover:text-gray-900:hover': 'color: #111827;',
    'hover:shadow-xl:hover': 'box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);',
    'hover:shadow-lg:hover': 'box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);',
    'hover:shadow-indigo-500/50:hover': 'box-shadow: 0 0 25px 0 rgb(99 102 241 / 0.5);',
    'hover:border-slate-300:hover': 'border-color: #cbd5e1;',
    'hover:border-indigo-300:hover': 'border-color: #a5b4fc;',
    'hover:translate-x-1:hover': '--tw-translate-x: 0.25rem;',
    'group-hover:opacity-100': '--tw-opacity: 1;',
    'group-hover:scale-110': '--tw-scale-x: 1.1; --tw-scale-y: 1.1;',
    'group-hover:text-indigo-600': 'color: #4f46e5;',
    'group-hover:translate-x-1': '--tw-translate-x: 0.25rem;',
    
    // Focus states
    'focus:outline-none': 'outline: 2px solid transparent; outline-offset: 2px;',
    'focus:ring-2': '--tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color); --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color); box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);',
    'focus:ring-indigo-500': '--tw-ring-color: #6366f1;',
    'focus:border-indigo-500': 'border-color: #6366f1;',
    
    // Active states
    'active:bg-indigo-800:active': 'background-color: #3730a3;',
    'active:text-white:active': 'color: #ffffff;',
    
    // Cursor
    'cursor-pointer': 'cursor: pointer;',
    'cursor-default': 'cursor: default;',
    
    // Pointer events
    'pointer-events-none': 'pointer-events: none;',
    'pointer-events-auto': 'pointer-events: auto;',
    
    // Visibility
    'visible': 'visibility: visible;',
    'invisible': 'visibility: hidden;',
    
    // Z-index variations
    '-z-10': 'z-index: -10;',
    
    // Opacity variations
    'opacity-0': 'opacity: 0;',
    'opacity-50': 'opacity: 0.5;',
    'opacity-100': 'opacity: 1;',
    
    // Blur
    'blur-3xl': '--tw-blur: blur(64px);',
    
    // Backdrop
    'backdrop-blur': '--tw-backdrop-blur: blur(8px);',
    'backdrop-blur-12': '--tw-backdrop-blur: blur(12px);',
    'backdrop-blur-sm': '--tw-backdrop-blur: blur(4px);',
    
    // Mix blend
    'mix-blend-multiply': 'mix-blend-mode: multiply;',
    
    // Inset
    'inset-x-0': 'left: 0; right: 0;',
    
    // Width variants
    'w-1': 'width: 0.25rem;',
    'w-2': 'width: 0.5rem;',
    'w-3': 'width: 0.75rem;',
    'w-4': 'width: 1rem;',
    'w-5': 'width: 1.25rem;',
    'w-6': 'width: 1.5rem;',
    'w-7': 'width: 1.75rem;',
    'w-8': 'width: 2rem;',
    'w-9': 'width: 2.25rem;',
    'w-11': 'width: 2.75rem;',
    'w-14': 'width: 3.5rem;',
    'w-24': 'width: 6rem;',
    'w-32': 'width: 8rem;',
    'w-40': 'width: 10rem;',
    'w-48': 'width: 12rem;',
    'w-96': 'width: 24rem;',
    
    // Height variants
    'h-1': 'height: 0.25rem;',
    'h-2': 'height: 0.5rem;',
    'h-3': 'height: 0.75rem;',
    'h-4': 'height: 1rem;',
    'h-5': 'height: 1.25rem;',
    'h-6': 'height: 1.5rem;',
    'h-7': 'height: 1.75rem;',
    'h-9': 'height: 2.25rem;',
    'h-11': 'height: 2.75rem;',
    'h-14': 'height: 3.5rem;',
    'h-20': 'height: 5rem;',
    'h-24': 'height: 6rem;',
    'h-32': 'height: 8rem;',
    'h-40': 'height: 10rem;',
    'h-48': 'height: 12rem;',
    'h-64': 'height: 16rem;',
    'h-96': 'height: 24rem;',
    'h-[400px]': 'height: 400px;',
    
    // Min height
    'min-h-16': 'min-height: 4rem;',
    
    // Flex grow/shrink
    'grow': 'flex-grow: 1;',
    
    // Grid columns
    'grid-cols-1': 'grid-template-columns: repeat(1, minmax(0, 1fr));',
    
    // Order
    'order-1': 'order: 1;',
    'order-2': 'order: 2;',
    'order-3': 'order: 3;',
    'order-first': 'order: -9999;',
    'order-last': 'order: 9999;',
    
    // Self align
    'self-center': 'align-self: center;',
    'self-start': 'align-self: flex-start;',
    'self-end': 'align-self: flex-end;',
    
    // Justify self
    'justify-self-center': 'justify-self: center;',
    'justify-self-end': 'justify-self: end;',
    'justify-self-start': 'justify-self: start;',
    
    // Overflow
    'overflow-x-auto': 'overflow-x: auto;',
    'overflow-y-hidden': 'overflow-y: hidden;',
    'overflow-visible': 'overflow: visible;',
    
    // Text decoration
    'underline': 'text-decoration-line: underline;',
    'no-underline': 'text-decoration-line: none;',
    
    // Text transform
    'uppercase': 'text-transform: uppercase;',
    'lowercase': 'text-transform: lowercase;',
    'capitalize': 'text-transform: capitalize;',
    
    // Whitespace
    'whitespace-nowrap': 'white-space: nowrap;',
    
    // Word break
    'break-words': 'overflow-wrap: break-word;',
    
    // Fill
    'fill-current': 'fill: currentColor;',
    
    // Stroke
    'stroke-current': 'stroke: currentColor;',
    'stroke-2': 'stroke-width: 2;',
    'stroke-3': 'stroke-width: 3;',
    
    // Container queries
    '@container': 'container-type: inline-size;',
    
    // Aspect ratio
    'aspect-square': 'aspect-ratio: 1 / 1;',
    'aspect-video': 'aspect-ratio: 16 / 9;',
  };
  
  return utilities[className] || null;
};

// Generate CSS for found classes
let utilityCSS = '\n/* Utility Classes */\n';
let count = 0;

allClasses.forEach(cls => {
  const cssDecl = generateUtilityCSS(cls);
  if (cssDecl) {
    utilityCSS += `.${cls} { ${cssDecl} }\n`;
    count++;
  }
});

if (count > 0) {
  css += utilityCSS;
  console.log(`Generated CSS for ${count} utility classes`);
} else {
  console.log('No utility classes found to generate CSS for');
}

// Add some responsive variants
css += `\n/* Responsive Variants */\n`;
css += `@media (min-width: 640px) { .sm\\:text-5xl { font-size: 3rem; line-height: 1; } .sm\\:text-xl { font-size: 1.25rem; line-height: 1.75rem; } }\n`;
css += `@media (min-width: 768px) { .md\\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .md\\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } }\n`;
css += `@media (min-width: 1024px) { .lg\\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .lg\\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } .lg\\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); } .lg\\:text-6xl { font-size: 3.75rem; line-height: 1; } .lg\\:flex-row { flex-direction: row; } .lg\\:h-20 { height: 5rem; } .lg\\:px-8 { padding-left: 2rem; padding-right: 2rem; } }\n`;
css += `@media (min-width: 1280px) { .xl\\:block { display: block; } .xl\\:right-\\[15\\%\\] { right: 15%; } .xl\\:left-\\[10\\%\\] { left: 10%; } .xl\\:right-\\[20\\%\\] { right: 20%; } }\n`;

// Write the CSS file
const outputPath = './out/_next/static/css/complete.css';
fs.writeFileSync(outputPath, css);
console.log(`\nGenerated complete CSS file: ${outputPath}`);
console.log(`File size: ${(css.length / 1024).toFixed(2)} KB`);
console.log(`Total classes processed: ${allClasses.size}`);
console.log(`CSS classes generated: ${count}`);

// Now append the custom landing.css content
const landingCSSPath = './src/components/landing/landing.css';
if (fs.existsSync(landingCSSPath)) {
  const landingCSS = fs.readFileSync(landingCSSPath, 'utf8');
  fs.appendFileSync(outputPath, '\n\n/* Custom Landing Page Styles */\n' + landingCSS);
  console.log(`\nAppended custom landing CSS from: ${landingCSSPath}`);
  console.log(`Final file size: ${(fs.statSync(outputPath).size / 1024).toFixed(2)} KB`);
} else {
  console.log(`\nWarning: Custom landing CSS file not found at ${landingCSSPath}`);
}
