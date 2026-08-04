import { describe, expect, it } from 'vitest';

import { hsvToRgb } from '../../core/color-convert/rgb-hsv';
import {
  SQRT3,
  circleChroma,
  circleRing3D,
  hexChroma,
  hexRing3D,
  hexVertices,
  overflowSegments,
  projectToPlane,
  rgbToWorld,
} from '../teach-math';

describe('rgbToWorld projection', () => {
  it('red/green/blue map to hexagon vertices with radius 1', () => {
    const red = rgbToWorld({ r: 1, g: 0, b: 0 });
    expect(red.x).toBeCloseTo(1, 5);
    expect(red.y).toBeCloseTo(0, 5);

    const green = rgbToWorld({ r: 0, g: 1, b: 0 });
    expect(green.x).toBeCloseTo(-0.5, 5);
    expect(green.y).toBeCloseTo(SQRT3 / 2, 5);

    const blue = rgbToWorld({ r: 0, g: 0, b: 1 });
    expect(blue.x).toBeCloseTo(-0.5, 5);
    expect(blue.y).toBeCloseTo(-SQRT3 / 2, 5);
  });

  it('white sits at (0, 0, sqrt(3)) and black at the origin', () => {
    const white = rgbToWorld({ r: 1, g: 1, b: 1 });
    expect(white.x).toBeCloseTo(0, 5);
    expect(white.y).toBeCloseTo(0, 5);
    expect(white.z).toBeCloseTo(SQRT3, 5);

    const black = rgbToWorld({ r: 0, g: 0, b: 0 });
    expect(black.x).toBeCloseTo(0, 5);
    expect(black.y).toBeCloseTo(0, 5);
    expect(black.z).toBeCloseTo(0, 5);
  });

  it('at 30° hue the circular chroma is sqrt(3)/2 while hexagonal chroma is 1', () => {
    // Pure color V=1, S=1, H=30 -> lies on a hexagon edge midpoint.
    const rgb = hsvToRgb({ h: 30, s: 1, v: 1 });
    const world = rgbToWorld(rgb);
    expect(circleChroma(world)).toBeCloseTo(SQRT3 / 2, 5);
    expect(hexChroma(rgb)).toBeCloseTo(1, 5);
  });

  it('yellow (secondary) also lands on the hexagon boundary with radius 1', () => {
    const yellow = rgbToWorld({ r: 1, g: 1, b: 0 });
    expect(Math.hypot(yellow.x, yellow.y)).toBeCloseTo(1, 5);
  });

  it('projectToPlane drops the z component', () => {
    const p = projectToPlane({ x: 0.3, y: -0.7, z: 1.2 });
    expect(p.x).toBeCloseTo(0.3, 5);
    expect(p.y).toBeCloseTo(-0.7, 5);
  });
});

describe('hexRing3D', () => {
  it('projects to a concentric hexagon: vertex direction s*v, edge-mid direction s*v*sqrt(3)/2', () => {
    const s = 0.5;
    const v = 0.8;
    const ring = hexRing3D(s, v, 120);

    const p0 = projectToPlane(ring[0]); // H = 0 (red vertex direction)
    expect(Math.hypot(p0.x, p0.y)).toBeCloseTo(s * v, 5);

    const p30 = projectToPlane(ring[10]); // H = 30 (edge midpoint direction)
    expect(Math.hypot(p30.x, p30.y)).toBeCloseTo((s * v * SQRT3) / 2, 5);
  });
});

describe('circleRing3D', () => {
  it('keeps the distance-to-axis (C2) and height constant', () => {
    const ref = rgbToWorld(hsvToRgb({ h: 30, s: 1, v: 1 }));
    const c2 = circleChroma(ref);
    const ring = circleRing3D(ref, 96);

    for (const p of ring) {
      expect(Math.hypot(p.x, p.y)).toBeCloseTo(c2, 5);
      expect(p.z).toBeCloseTo(ref.z, 5);
    }
  });
});

describe('hexVertices / overflowSegments', () => {
  it('produces 6 counter-clockwise vertices starting at red', () => {
    const verts = hexVertices();
    expect(verts).toHaveLength(6);
    expect(verts[0].x).toBeCloseTo(1, 5);
    expect(verts[0].y).toBeCloseTo(0, 5);
    // Counter-clockwise: vertex 1 is at 60°.
    expect(verts[1].x).toBeCloseTo(0.5, 5);
    expect(verts[1].y).toBeCloseTo(SQRT3 / 2, 5);
  });

  it('produces 6 closed overflow segments whose arc endpoints are hexagon vertices', () => {
    const segs = overflowSegments();
    expect(segs).toHaveLength(6);
    for (const seg of segs) {
      expect(seg.length).toBeGreaterThan(3);
      // Closed polygon: last point equals first.
      expect(seg[0].x).toBeCloseTo(seg[seg.length - 1].x, 5);
      expect(seg[0].y).toBeCloseTo(seg[seg.length - 1].y, 5);
    }
    // Edge-midpoint (30°) arc radius is 1 (circle), while hexagon edge distance is sqrt(3)/2.
    const mid = segs[0][Math.ceil(segs[0].length / 2)];
    expect(Math.hypot(mid.x, mid.y)).toBeCloseTo(1, 5);
    expect(Math.hypot(mid.x, mid.y)).toBeGreaterThan(SQRT3 / 2 + 0.1);
  });
});
