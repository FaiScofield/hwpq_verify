/**
 * HSV projection teaching — core math.
 *
 * World coordinate convention:
 *   - Z axis = neutral axis (black -> white diagonal). Black (0,0,0) at z = 0,
 *     white (1,1,1) at world (0, 0, sqrt(3)).
 *   - Chromaticity plane = z = 0 horizontal plane. Orthogonal projection along
 *     the neutral axis (+Z) simply drops the z component.
 *   - The hexagonal projection vertices (red/yellow/green/cyan/blue/magenta)
 *     lie on a circle of radius 1.
 *
 * Projection formulas (RGB -> chromaticity plane alpha/beta coordinates):
 *   alpha = (2R - G - B) / 2,   beta = (sqrt(3)/2) * (G - B)
 * Height along the neutral axis:
 *   z = (R + G + B) / sqrt(3)
 */
import { hsvToRgb } from '../core/color-convert/rgb-hsv';
import type { HsvColor, Point2D, Point3D, RgbColor } from '../state/types';

export const SQRT3 = Math.sqrt(3);

/** Map normalized RGB to world coordinates (tilted cube). */
export function rgbToWorld(rgb: RgbColor): Point3D {
  const { r, g, b } = rgb;
  return {
    x: (2 * r - g - b) / 2,
    y: (SQRT3 / 2) * (g - b),
    z: (r + g + b) / SQRT3,
  };
}

/** Orthogonal projection of a world point onto the z = 0 chromaticity plane. */
export function projectToPlane(world: Point3D): Point2D {
  return { x: world.x, y: world.y };
}

/** HSV -> 3D world point (the marker sits on the V = v outer surface). */
export function hsvToWorld(hsv: HsvColor): Point3D {
  return rgbToWorld(hsvToRgb(hsv));
}

/** HSV -> 2D projected point on the chromaticity plane. */
export function hsvToPlane(hsv: HsvColor): Point2D {
  return projectToPlane(hsvToWorld(hsv));
}

/** Hexagonal chroma C = M - m (the range of the RGB components). */
export function hexChroma(rgb: RgbColor): number {
  const { r, g, b } = rgb;
  return Math.max(r, g, b) - Math.min(r, g, b);
}

/** Circular chroma C2 = Euclidean distance from the neutral axis. */
export function circleChroma(world: Point3D): number {
  return Math.hypot(world.x, world.y);
}

/** Regular hexagon vertices (counter-clockwise, starting at 0° red). */
export function hexVertices(radius = 1): Point2D[] {
  const verts: Point2D[] = [];
  for (let i = 0; i < 6; i++) {
    const angle = (i * 60 * Math.PI) / 180;
    verts.push({ x: radius * Math.cos(angle), y: radius * Math.sin(angle) });
  }
  return verts;
}

/**
 * Equal-S hexagon ring in 3D: points on the V = v outer surface with
 * constant saturation S, sampled around H in [0, 360).
 */
export function hexRing3D(s: number, v: number, segments = 120): Point3D[] {
  const pts: Point3D[] = [];
  for (let i = 0; i < segments; i++) {
    pts.push(hsvToWorld({ h: (i / segments) * 360, s, v }));
  }
  return pts;
}

/**
 * Circle ring in 3D: keeps the distance-to-axis (C2) and the height (z) of
 * the reference point fixed while rotating around the neutral axis. Used to
 * contrast the circle trajectory against the hexagon trajectory.
 */
export function circleRing3D(ref: Point3D, segments = 120): Point3D[] {
  const radius = Math.hypot(ref.x, ref.y);
  const pts: Point3D[] = [];
  for (let i = 0; i < segments; i++) {
    const t = (i / segments) * Math.PI * 2;
    pts.push({ x: radius * Math.cos(t), y: radius * Math.sin(t), z: ref.z });
  }
  return pts;
}

/**
 * The 6 circular segments (one per hexagon edge) where the circle of the
 * given radius sticks out beyond the inscribed hexagon. Each segment is a
 * closed polygon: circular arc from vertex A to B, then the chord back to A.
 * Used to highlight the region that lies outside the RGB cube's real gamut.
 */
export function overflowSegments(radius = 1, arcSteps = 10): Point2D[][] {
  const verts = hexVertices(radius);
  const segs: Point2D[][] = [];
  for (let i = 0; i < 6; i++) {
    const a = verts[i];
    const seg: Point2D[] = [];
    for (let j = 0; j <= arcSteps; j++) {
      const angle = ((i * 60 + (j / arcSteps) * 60) * Math.PI) / 180;
      seg.push({ x: radius * Math.cos(angle), y: radius * Math.sin(angle) });
    }
    seg.push(a);
    segs.push(seg);
  }
  return segs;
}
