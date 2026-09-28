import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const i18nDir = path.resolve(__dirname, '../src/i18n');

console.log(`🔍 Checking i18n files in: ${i18nDir}`);

const languages = ['en', 'hi', 'mr', 'pa'];
const data = {};

for (const lang of languages) {
  const filePath = path.join(i18nDir, `${lang}.json`);
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Missing language file: ${lang}.json`);
    process.exit(1);
  }
  try {
    data[lang] = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err) {
    console.error(`❌ Syntax error in ${lang}.json: ${err.message}`);
    process.exit(1);
  }
}

function extractKeysAndPlaceholders(obj, prefix = '') {
  const result = new Map();
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

  for (const [key, baseInfo] of baseEntries.entries()) {
    if (!targetEntries.has(key)) {
      console.error(`  ❌ Missing key in ${lang}: "${key}"`);
      langErrors++;
      errorCount++;
    } else {
      const targetInfo = targetEntries.get(key);
      if (baseInfo.placeholders.join(',') !== targetInfo.placeholders.join(',')) {
        console.error(`  ⚠️ Placeholder mismatch in ${lang} for key "${key}":`);
        console.error(`     Base (en):   [${baseInfo.placeholders.join(', ')}]`);
        console.error(`     Target:      [${targetInfo.placeholders.join(', ')}]`);
        langErrors++;
        errorCount++;
      }
    }
  }

  for (const [key] of targetEntries.entries()) {
    if (!baseEntries.has(key)) {
      console.warn(`  ⚠️ Extra key in ${lang} (not in en.json): "${key}"`);
    }
  }

  if (langErrors === 0) {
    console.log(`  ✅ ${lang.toUpperCase()} is 100% complete with no errors (${targetEntries.size} keys).`);
  }
}

console.log('\n----------------------------------------');
if (errorCount === 0) {
  console.log('🎉 i18n Completeness Verification PASSED! All 4 languages (EN, HI, MR, PA) are in sync.');
  process.exit(0);
} else {
  console.error(`❌ i18n Verification FAILED with ${errorCount} error(s). Please fix missing keys.`);
  process.exit(1);
}
