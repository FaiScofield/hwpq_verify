import { describe, expect, it } from 'vitest';

import { ColorStateStore } from '../color-state-store';

describe('ColorStateStore', () => {
  it('updates HSV when RGB changes', () => {
    const store = new ColorStateStore();

    store.setRgb255({ r: 255, g: 0, b: 0 });

    expect(store.getState().hsv).toMatchObject({ h: 0, s: 1, v: 1 });
  });

  it('updates RGB when HSV changes', () => {
    const store = new ColorStateStore();

    store.setHsv({ h: 120, s: 1, v: 1 });

    expect(store.getState().rgb255).toEqual({ r: 0, g: 255, b: 0 });
  });

  it('preserves last hue when saturation drops to zero', () => {
    const store = new ColorStateStore();

    store.setHsv({ h: 210, s: 1, v: 0.7 });
    store.setRgb255({ r: 128, g: 128, b: 128 });

    expect(store.getState().lastHue).toBe(210);
  });
});
