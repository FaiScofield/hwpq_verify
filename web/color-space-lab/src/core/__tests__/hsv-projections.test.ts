import { describe, expect, it } from 'vitest';

import { projectHsvToCircle } from '../projections/hsv-circle';
import { projectHsvToHex } from '../projections/hsv-hex';

describe('projectHsvToHex', () => {
  it('places red on the positive x vertex', () => {
    expect(projectHsvToHex({ h: 0, s: 1, v: 1 })).toEqual({ x: 1, y: 0 });
  });

  it('places yellow on the upper-right vertex', () => {
    const point = projectHsvToHex({ h: 60, s: 1, v: 1 });

    expect(point.x).toBeCloseTo(0.5, 6);
    expect(point.y).toBeCloseTo(Math.sqrt(3) / 2, 6);
  });

  it('keeps gray at the center', () => {
    expect(projectHsvToHex({ h: 45, s: 0, v: 0.3 })).toEqual({ x: 0, y: 0 });
  });
});

describe('projectHsvToCircle', () => {
  it('maps hue 90 to the positive y axis', () => {
    const point = projectHsvToCircle({ h: 90, s: 1, v: 1 });

    expect(point.x).toBeCloseTo(0, 6);
    expect(point.y).toBeCloseTo(1, 6);
  });
});
