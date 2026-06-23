import { describe, expect, it } from 'vitest';

import { cubePointFromRgb255, hexconePointFromHsv } from '../helpers';

describe('cubePointFromRgb255', () => {
  it('maps red to the positive x corner', () => {
    expect(cubePointFromRgb255({ r: 255, g: 0, b: 0 })).toEqual({
      x: 0.5,
      y: -0.5,
      z: -0.5,
    });
  });
});

describe('hexconePointFromHsv', () => {
  it('maps a saturated red to the right side of the hexcone base', () => {
    const point = hexconePointFromHsv({ h: 0, s: 1, v: 1 });

    expect(point.x).toBeCloseTo(1, 6);
    expect(point.y).toBeCloseTo(0, 6);
    expect(point.z).toBeCloseTo(1, 6);
  });
});
