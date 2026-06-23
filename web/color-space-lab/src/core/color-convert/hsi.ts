import type { RgbColor } from '../../state/types';

/**
 * Compute HSI intensity from normalized RGB.
 */
export function computeHsiIntensity(rgb: RgbColor): number {
  return (rgb.r + rgb.g + rgb.b) / 3;
}
