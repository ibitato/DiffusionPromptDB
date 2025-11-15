import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const localesDir = join(__dirname, '../src/i18n/locales');

function loadJson(file) {
  const content = readFileSync(join(localesDir, file), 'utf-8');
  return JSON.parse(content);
}

function flatten(obj, prefix = '') {
  const entries = [];
  if (Array.isArray(obj)) {
    obj.forEach((value, index) => {
      entries.push(...flatten(value, prefix ? `${prefix}[${index}]` : `[${index}]`));
    });
    return entries;
  }

  if (obj && typeof obj === 'object') {
    Object.keys(obj).forEach((key) => {
      const next = prefix ? `${prefix}.${key}` : key;
      entries.push(...flatten(obj[key], next));
    });
    return entries;
  }

  return [prefix];
}

const locales = readdirSync(localesDir).filter((file) => file.endsWith('.json'));
if (!locales.includes('en.json')) {
  console.error('Missing base en.json locale');
  process.exit(1);
}

const base = loadJson('en.json');
const baseKeys = new Set(flatten(base));
let hasDiff = false;

for (const file of locales) {
  if (file === 'en.json') continue;
  const data = loadJson(file);
  const keys = new Set(flatten(data));

  const missing = [...baseKeys].filter((key) => !keys.has(key));
  const extra = [...keys].filter((key) => !baseKeys.has(key));

  if (missing.length || extra.length) {
    hasDiff = true;
    console.error(`\nLocale ${file} has discrepancies:`);
    if (missing.length) {
      console.error('  Missing keys:');
      missing.forEach((key) => console.error(`    - ${key}`));
    }
    if (extra.length) {
      console.error('  Extra keys:');
      extra.forEach((key) => console.error(`    - ${key}`));
    }
  }
}

if (hasDiff) {
  process.exit(1);
}

console.log('✅ All locale files are in sync with en.json');
