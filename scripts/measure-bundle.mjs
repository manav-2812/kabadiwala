#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import zlib from 'zlib';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, '../web/dist');

if (!fs.existsSync(distDir)) {
  console.error('❌ web/dist does not exist. Run `npm run build` in web/ first.');
  process.exit(1);
}

const COLLECTOR_CHUNK_LIMIT_KB = 250; // max 250KB gzipped JS for primary collector bundle
const TOTAL_PRECACHE_LIMIT_MB = 3.5; // max 3.5MB uncompressed precache (includes high-res PWA icon suite)

console.log('='.repeat(60));
console.log('📊 KABADIWALA CONNECT — BUNDLE BUDGET CHECKER (SIH26229)');
console.log('='.repeat(60));

// Find all files in dist
function getAllFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      getAllFiles(fullPath, fileList);
    } else {
      fileList.push(fullPath);
    }
  }
  return fileList;
}

const allFiles = getAllFiles(distDir);
let totalBytes = 0;
let collectorChunk = null;

for (const file of allFiles) {
  const rel = path.relative(distDir, file).replace(/\\/g, '/');
  const size = fs.statSync(file).size;
  totalBytes += size;

  if (rel.startsWith('assets/index-') && rel.endsWith('.js')) {
    const content = fs.readFileSync(file);
    const gzipped = zlib.gzipSync(content);
    collectorChunk = {
      file: rel,
      rawSizeKB: (size / 1024).toFixed(2),
      gzipSizeKB: (gzipped.length / 1024).toFixed(2),
      gzipBytes: gzipped.length
    };
  }
}

const totalMB = (totalBytes / (1024 * 1024)).toFixed(2);

console.log(`\n📁 Total Precache Size: ${totalMB} MB (Budget: <= ${TOTAL_PRECACHE_LIMIT_MB} MB)`);
if (!collectorChunk) {
  console.error('❌ Could not locate collector entry chunk (assets/index-*.js)');
  process.exit(1);
}

console.log(`📦 Collector JS Chunk:  ${collectorChunk.file}`);
console.log(`   - Raw Size:          ${collectorChunk.rawSizeKB} KB`);
console.log(`   - Gzipped Size:      ${collectorChunk.gzipSizeKB} KB (Budget: <= ${COLLECTOR_CHUNK_LIMIT_KB} KB)\n`);

let passed = true;

if (parseFloat(collectorChunk.gzipSizeKB) > COLLECTOR_CHUNK_LIMIT_KB) {
  console.error(`❌ Collector chunk EXCEEDS budget! ${collectorChunk.gzipSizeKB} KB > ${COLLECTOR_CHUNK_LIMIT_KB} KB`);
  passed = false;
} else {
  console.log(`✅ Collector chunk is within budget (${collectorChunk.gzipSizeKB} KB <= ${COLLECTOR_CHUNK_LIMIT_KB} KB)`);
}

if (parseFloat(totalMB) > TOTAL_PRECACHE_LIMIT_MB) {
  console.error(`❌ Total precache EXCEEDS budget! ${totalMB} MB > ${TOTAL_PRECACHE_LIMIT_MB} MB`);
  passed = false;
} else {
  console.log(`✅ Total precache is within budget (${totalMB} MB <= ${TOTAL_PRECACHE_LIMIT_MB} MB)`);
}

console.log('='.repeat(60));
if (!passed) {
  process.exit(1);
}
console.log('🎉 ALL BUNDLE BUDGETS PASSED!\n');
process.exit(0);
