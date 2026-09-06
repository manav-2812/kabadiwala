import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.resolve(__dirname, '../web/public/audio');
const manifestPath = path.join(outputDir, 'manifest.json');

const LANGUAGES = ['mr', 'hi', 'pa', 'en'];

const MATERIALS = [
  'battery',
  'pcb_high',
  'pcb_low',
  'copper_wire',
  'aluminum_heat',
  'crt_glass',
  'compressor',
  'plastic_abs',
  'mixed_motor',
  'solar_cell'
];

const PROMPTS = [
  'rupees_per_kg',
  'current_rate',
  'formal_premium',
  'cpcb_authorized',
  'cash_payment_verified'
];

const NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '50', '100', '500'];

const manifest: Record<string, any> = {
  version: '1.0.0',
  description: 'Vernacular Spoken Price Board Audio Clip Manifest (SIH26229)',
  languages: LANGUAGES,
  fallback: 'speech_synthesis',
  clips: {}
};

for (const lang of LANGUAGES) {
  manifest.clips[lang] = {
    materials: {},
    prompts: {},
    numbers: {}
  };

  for (const m of MATERIALS) {
    manifest.clips[lang].materials[m] = {
      path: `/audio/${lang}/materials/${m}.mp3`,
      exists: false,
      tts_fallback: true
    };
  }

  for (const p of PROMPTS) {
    manifest.clips[lang].prompts[p] = {
      path: `/audio/${lang}/prompts/${p}.mp3`,
      exists: false,
      tts_fallback: true
    };
  }

  for (const n of NUMBERS) {
    manifest.clips[lang].numbers[n] = {
      path: `/audio/${lang}/numbers/${n}.mp3`,
      exists: false,
      tts_fallback: true
    };
  }
}

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
console.log(`✅ Audio manifest generated with 4 languages at: ${manifestPath}`);
