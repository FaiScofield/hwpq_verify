import type { HsvColor, Point2D } from '../../state/types';

const HEX_VERTICES: Point2D[] = [
  { x: 1, y: 0 },
  { x: 0.5, y: Math.sqrt(3) / 2 },
  { x: -0.5, y: Math.sqrt(3) / 2 },
  { x: -1, y: 0 },
  { x: -0.5, y: -Math.sqrt(3) / 2 },
  { x: 0.5, y: -Math.sqrt(3) / 2 },
];

/**
 * Project HSV onto the cube-derived hexagonal boundary.
 */
export function projectHsvToHex(hsv: HsvColor): Point2D {
  if (hsv.s <= 0) {
    return { x: 0, y: 0 };
  }

  const hue = ((hsv.h % 360) + 360) % 360;
  const sector = hue / 60;
  const index = Math.floor(sector) % 6;
  const t = sector - Math.floor(sector);
  const a = HEX_VERTICES[index];
  const b = HEX_VERTICES[(index + 1) % 6];

  return {
    x: hsv.s * ((1 - t) * a.x + t * b.x),
    y: hsv.s * ((1 - t) * a.y + t * b.y),
  };
}
