/**
 * Perceptual Hash (dHash) — 64-bit implementation
 * Kabadiwala Connect — SIH 2026 (PS SIH26229)
 *
 * Computes a 9×8 grayscale difference hash of an image.
 * Output: 16-character hex string (64 bits).
 *
 * Used for:
 *   - Duplicate photo detection (Section 7.1 R5)
 *   - Sent with every photo upload to the server
 *
 * Server stores the hex string and compares Hamming distance
 * against existing photos: distance <= 6 on different lots = DUPLICATE_PHOTO flag.
 */

/**
 * Compute dHash of an ImageBitmap (or HTMLImageElement, HTMLCanvasElement, etc.)
 * using an offscreen canvas. Pure TypeScript, no dependencies.
 */
export async function computeDHash(
  source: ImageBitmapSource | HTMLCanvasElement,
): Promise<string> {
  const WIDTH = 9;   // 9 columns for differences
  const HEIGHT = 8;  // 8 rows

  // Create offscreen canvas 9x8
  const canvas = new OffscreenCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d')!;

  if (source instanceof HTMLCanvasElement) {
    ctx.drawImage(source, 0, 0, WIDTH, HEIGHT);
  } else {
    const bmp = await createImageBitmap(source as ImageBitmapSource, {
      resizeWidth: WIDTH,
      resizeHeight: HEIGHT,
      resizeQuality: 'low',
    });
    ctx.drawImage(bmp, 0, 0);
    bmp.close();
  }

  const imageData = ctx.getImageData(0, 0, WIDTH, HEIGHT);
  const data = imageData.data; // RGBA

  // Convert to grayscale (luminance) 9x8
  const gray: number[] = [];
  for (let i = 0; i < WIDTH * HEIGHT; i++) {
    const r = data[i * 4];
    const g = data[i * 4 + 1];
    const b = data[i * 4 + 2];
    // BT.601 luminance
    gray.push(0.299 * r + 0.587 * g + 0.114 * b);
  }

  // Compute dHash: for each row, compare adjacent pixels (8 diffs per row = 64 bits)
  const bits: number[] = [];
  for (let row = 0; row < HEIGHT; row++) {
    for (let col = 0; col < WIDTH - 1; col++) {
      const left = gray[row * WIDTH + col];
      const right = gray[row * WIDTH + col + 1];
      bits.push(left > right ? 1 : 0);
    }
  }

  // Pack 64 bits into 16 hex characters
  let hex = '';
  for (let i = 0; i < 64; i += 4) {
    const nibble = (bits[i] << 3) | (bits[i + 1] << 2) | (bits[i + 2] << 1) | bits[i + 3];
    hex += nibble.toString(16);
  }

  return hex;
}

/**
 * Hamming distance between two hex pHash strings.
 * Returns 64 if strings have different lengths (treat as maximum distance).
 */
export function hammingDistance(a: string, b: string): number {
  if (a.length !== b.length) return 64;
  const aInt = BigInt(`0x${a}`);
  const bInt = BigInt(`0x${b}`);
  let xor = aInt ^ bInt;
  let dist = 0;
  while (xor > 0n) {
    dist += Number(xor & 1n);
    xor >>= 1n;
  }
  return dist;
}

/**
 * Quick duplicate check against a list of known hashes.
 * Returns the first match within the Hamming distance threshold.
 */
export function findDuplicate(
  hash: string,
  knownHashes: string[],
  threshold = 6,
): { found: boolean; distance: number; matchIndex: number } {
  for (let i = 0; i < knownHashes.length; i++) {
    const dist = hammingDistance(hash, knownHashes[i]);
    if (dist <= threshold) {
      return { found: true, distance: dist, matchIndex: i };
    }
  }
  return { found: false, distance: 64, matchIndex: -1 };
}

export const computePHash = computeDHash;

