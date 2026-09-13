/**
 * Photo Quality Gate
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Checks brightness and blur before photo is submitted.
 * Spoken feedback: "Photo is dark / blurry, try again" in 4 languages.
 *
 * Gate runs client-side on a downscaled canvas (lightweight).
 * User can override after one retry (the gate is advisory, not blocking).
 *
 * Thresholds:
 *   - Too dark:   mean luminance < 30  (out of 255)
 *   - Too bright: mean luminance > 230
 *   - Blurry:     Laplacian-variance proxy < 50 (on 64×64 downscale)
 */

export type QualityIssue = 'too_dark' | 'too_bright' | 'blurry' | null;

export interface QualityResult {
  ok: boolean;
  issue: QualityIssue;
  /** Spoken feedback key for i18n lookup */
  spokenKey: string | null;
  /** Mean luminance 0-255 */
  meanLuminance: number;
  /** Laplacian variance proxy (higher = sharper) */
  sharpnessScore: number;
}

const TOO_DARK_THRESHOLD = 30;
const TOO_BRIGHT_THRESHOLD = 230;
const BLUR_THRESHOLD = 50;
const QUALITY_CANVAS_SIZE = 64;

/**
 * Compute a simple Laplacian-variance proxy for blur detection.
 * Uses the sum of squared differences between adjacent pixels.
 * Higher value = sharper image.
 */
function laplacianVariance(gray: number[], width: number, height: number): number {
  let sum = 0;
  let count = 0;
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const center = gray[y * width + x];
      const laplacian =
        -center * 4 +
        gray[(y - 1) * width + x] +
        gray[(y + 1) * width + x] +
        gray[y * width + (x - 1)] +
        gray[y * width + (x + 1)];
      sum += laplacian * laplacian;
      count++;
    }
  }
  return count > 0 ? sum / count : 0;
}

/**
 * Assess photo quality from a canvas or image source.
 * Returns a QualityResult with ok=false if action is needed.
 */
export async function assessQuality(
  source: ImageBitmapSource | HTMLCanvasElement,
): Promise<QualityResult> {
  const W = QUALITY_CANVAS_SIZE;
  const H = QUALITY_CANVAS_SIZE;

  const canvas = new OffscreenCanvas(W, H);
  const ctx = canvas.getContext('2d')!;

  if (source instanceof HTMLCanvasElement) {
    ctx.drawImage(source, 0, 0, W, H);
  } else {
    const bmp = await createImageBitmap(source as ImageBitmapSource, {
      resizeWidth: W,
      resizeHeight: H,
      resizeQuality: 'low',
    });
    ctx.drawImage(bmp, 0, 0);
    bmp.close();
  }

  const { data } = ctx.getImageData(0, 0, W, H);

  // Grayscale + mean luminance
  const gray: number[] = [];
  let totalLum = 0;
  for (let i = 0; i < W * H; i++) {
    const r = data[i * 4];
    const g = data[i * 4 + 1];
    const b = data[i * 4 + 2];
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;
    gray.push(lum);
    totalLum += lum;
  }
  const meanLuminance = totalLum / (W * H);

  // Blur check
  const sharpnessScore = laplacianVariance(gray, W, H);

  // Evaluate
  if (meanLuminance < TOO_DARK_THRESHOLD) {
    return {
      ok: false,
      issue: 'too_dark',
      spokenKey: 'photo_too_dark',
      meanLuminance,
      sharpnessScore,
    };
  }
  if (meanLuminance > TOO_BRIGHT_THRESHOLD) {
    return {
      ok: false,
      issue: 'too_bright',
      spokenKey: 'photo_too_bright',
      meanLuminance,
      sharpnessScore,
    };
  }
  if (sharpnessScore < BLUR_THRESHOLD) {
    return {
      ok: false,
      issue: 'blurry',
      spokenKey: 'photo_blurry',
      meanLuminance,
      sharpnessScore,
    };
  }

  return { ok: true, issue: null, spokenKey: null, meanLuminance, sharpnessScore };
}

/** i18n spoken feedback messages (used as fallback if audio clips missing) */
export const QUALITY_SPOKEN: Record<string, Record<string, string>> = {
  photo_too_dark: {
    en: 'Photo is too dark. Please move to better light and try again.',
    hi: 'फोटो बहुत अंधेरी है। कृपया रोशनी में जाकर दोबारा लें।',
    mr: 'फोटो खूप अंधारी आहे. कृपया प्रकाशात जाऊन पुन्हा काढा.',
    pa: 'ਫੋਟੋ ਬਹੁਤ ਹਨੇਰੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਰੌਸ਼ਨੀ ਵਿੱਚ ਜਾ ਕੇ ਦੁਬਾਰਾ ਲਓ।',
  },
  photo_too_bright: {
    en: 'Photo is overexposed. Please avoid direct sunlight and try again.',
    hi: 'फोटो बहुत चमकदार है। कृपया सीधी धूप से बचाकर दोबारा लें।',
    mr: 'फोटो जास्त उजळ आहे. कृपया थेट सूर्यप्रकाश टाळून पुन्हा काढा.',
    pa: 'ਫੋਟੋ ਬਹੁਤ ਚਮਕਦਾਰ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਸਿੱਧੀ ਧੁੱਪ ਤੋਂ ਬਚ ਕੇ ਦੁਬਾਰਾ ਲਓ।',
  },
  photo_blurry: {
    en: 'Photo is blurry. Please hold steady and try again.',
    hi: 'फोटो धुंधली है। कृपया स्थिर रखकर दोबारा लें।',
    mr: 'फोटो अस्पष्ट आहे. कृपया स्थिर ठेवून पुन्हा काढा.',
    pa: 'ਫੋਟੋ ਧੁੰਦਲੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਸਥਿਰ ਰੱਖ ਕੇ ਦੁਬਾਰਾ ਲਓ।',
  },
};
