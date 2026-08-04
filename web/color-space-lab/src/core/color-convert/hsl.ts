/**
 * Compute HSL lightness from normalized channel extrema.
 */
export function computeHslLightness(max: number, min: number): number {
  return (max + min) / 2;
}
