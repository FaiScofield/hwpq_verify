import type { HsvColor, Point2D } from '../../state/types';

/**
 * Project HSV onto a normalized polar circle.
 */
export function projectHsvToCircle(hsv: HsvColor): Point2D {
  const radians = (hsv.h * Math.PI) / 180;

  return {
    x: hsv.s * Math.cos(radians),
    y: hsv.s * Math.sin(radians),
  };
}
