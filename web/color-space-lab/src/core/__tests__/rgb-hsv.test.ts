import { describe, expect, it } from 'vitest';

import { hsvToRgb, rgbToHsv } from '../color-convert/rgb-hsv';

describe('rgbToHsv', () => {
  it('maps pure red to hue 0', () => {
    expect(rgbToHsv({ r: 1, g: 0, b: 0 })).toMatchObject({ h: 0, s: 1, v: 1 });
  });

  it('maps pure green to hue 120', () => {
    expect(rgbToHsv({ r: 0, g: 1, b: 0 })).toMatchObject({ h: 120, s: 1, v: 1 });
  });

  it('maps gray to zero saturation', () => {
    expect(rgbToHsv({ r: 0.5, g: 0.5, b: 0.5 })).toMatchObject({ s: 0, v: 0.5 });
  });
});

describe('hsvToRgb', () => {
  it('round-trips a non-trivial sample', () => {
    const hsv = rgbToHsv({ r: 0.85, g: 0.46, b: 0.13 });
    const rgb = hsvToRgb(hsv);

    expect(rgb.r).toBeCloseTo(0.85, 6);
    expect(rgb.g).toBeCloseTo(0.46, 6);
    expect(rgb.b).toBeCloseTo(0.13, 6);
  });
});
