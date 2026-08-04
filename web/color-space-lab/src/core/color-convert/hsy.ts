import type { RgbColor } from '../../state/types';

/**
 * Compute HSY luma using the BT.601 coefficients.
 */
export function computeHsyLuma601(rgb: RgbColor): number {
  return 0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
}
