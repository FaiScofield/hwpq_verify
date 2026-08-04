import type { HsvColor, RgbColor } from '../../state/types';

/**
 * Clamp a scalar to the normalized RGB range.
 */
function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

/**
 * Convert a normalized RGB color to HSV.
 */
export function rgbToHsv(rgb: RgbColor): HsvColor {
  const r = clamp01(rgb.r);
  const g = clamp01(rgb.g);
  const b = clamp01(rgb.b);
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const chroma = max - min;
  let h = 0;

  if (chroma !== 0) {
    if (max === r) {
      h = 60 * (((g - b) / chroma + 6) % 6);
    } else if (max === g) {
      h = 60 * ((b - r) / chroma + 2);
    } else {
      h = 60 * ((r - g) / chroma + 4);
    }
  }

  const s = max === 0 ? 0 : chroma / max;
  return { h, s, v: max };
}

/**
 * Convert an HSV color to normalized RGB.
 */
export function hsvToRgb(hsv: HsvColor): RgbColor {
  const h = ((hsv.h % 360) + 360) % 360;
  const s = clamp01(hsv.s);
  const v = clamp01(hsv.v);
  const c = v * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = v - c;

  let r1 = 0;
  let g1 = 0;
  let b1 = 0;

  if (h < 60) {
    [r1, g1, b1] = [c, x, 0];
  } else if (h < 120) {
    [r1, g1, b1] = [x, c, 0];
  } else if (h < 180) {
    [r1, g1, b1] = [0, c, x];
  } else if (h < 240) {
    [r1, g1, b1] = [0, x, c];
  } else if (h < 300) {
    [r1, g1, b1] = [x, 0, c];
  } else {
    [r1, g1, b1] = [c, 0, x];
  }

  return {
    r: r1 + m,
    g: g1 + m,
    b: b1 + m,
  };
}
