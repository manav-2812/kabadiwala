import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Locate i18n directory
const possibleDirs = [
  path.resolve(__dirname, '../web/src/i18n'),
  path.resolve(__dirname, '../src/i18n'),
  path.resolve(process.cwd(), 'web/src/i18n'),
  path.resolve(process.cwd(), 'src/i18n')
];

let i18nDir = possibleDirs.find(d => fs.existsSync(path.join(d, 'en.json')));
if (!i18nDir) {
  console.error('❌ Could not locate i18n directory containing en.json');
  process.exit(1);
}

console.log(`🔍 Checking i18n files in: ${i18nDir}`);

const languages = ['en', 'hi', 'mr', 'pa'];
const data: Record<string, any> = {};

for (const lang of languages) {
  const filePath = path.join(i18nDir, `${lang}.json`);
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Missing language file: ${lang}.json`);
    process.exit(1);
  }
  try {
    data[lang] = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err: any) {
    console.error(`❌ Syntax error in ${lang}.json: ${err.message}`);
    process.exit(1);
  }
}

function extractKeysAndPlaceholders(obj: any, prefix = ''): Map<string, { value: string; placeholders: string[] }> {
  const result = new Map<string, { value: string; placeholders: string[] }>();
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (typeof v === 'object' && v !== null) {
      const nested = extractKeysAndPlaceholders(v, fullKey);
      for (const [nk, nv] of nested.entries()) {
        result.set(nk, nv);
      }
    } else if (typeof v === 'string') {
      const placeholders = (v.match(/\{[a-zA-Z0-9_]+\}/g) || []).sort();
      result.set(fullKey, { value: v, placeholders });
    }
  }
  return result;
}

const baseEntries = extractKeysAndPlaceholders(data.en);
let errorCount = 0;

console.log(`📋 Found ${baseEntries.size} translation keys in en.json.\n`);

for (const lang of ['hi', 'mr', 'pa']) {
  console.log(`Checking ${lang.toUpperCase()} (${lang}.json)...`);
  const targetEntries = extractKeysAndPlaceholders(data[lang]);
  let langErrors = 0;

  // 1. Check missing keys
  for (const [key, baseInfo] of baseEntries.entries()) {
    if (!targetEntries.has(key)) {
      console.error(`  ❌ Missing key in ${lang}: "${key}"`);
      langErrors++;
      errorCount++;
    } else {
      const targetInfo = targetEntries.get(key)!;
      // 2. Check empty strings
      if (!targetInfo.value || targetInfo.value.trim() === '') {
        console.error(`  ❌ Empty string in ${lang}: "${key}"`);
        langErrors++;
        errorCount++;
      }
      // 3. Check placeholder matching
      const bp = baseInfo.placeholders.join(',');
      const tp = targetInfo.placeholders.join(',');
      if (bp !== tp) {
        console.error(`  ❌ Placeholder mismatch in ${lang} for "${key}": expected [${bp}], got [${tp}]`);
        langErrors++;
        errorCount++;
      }
    }
  }

  // 4. Check extraneous keys in target
  for (const [key] of targetEntries.entries()) {
    if (!baseEntries.has(key)) {
      console.warn(`  ⚠️ Extraneous key in ${lang} (not in en): "${key}"`);
    }
  }

  if (langErrors === 0) {
    console.log(`  ✅ ${lang.toUpperCase()} is 100% complete with no errors (${targetEntries.size} keys).`);
  }
}

console.log('\n----------------------------------------');
if (errorCount === 0) {
  console.log(`🎉 i18n Completeness Verification PASSED! All 4 languages (EN, HI, MR, PA) are in sync.`);
  process.exit(0);
} else {
  console.error(`💥 i18n Verification FAILED with ${errorCount} errors.`);
  process.exit(1);
}
