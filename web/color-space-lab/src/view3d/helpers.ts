import * as THREE from 'three';

import { projectHsvToHex } from '../core/projections/hsv-hex';
import type { HsvColor, Point3D } from '../state/types';

/**
 * Create a reusable marker sphere.
 */
export function createMarker(color = '#111827'): THREE.Mesh {
  const geometry = new THREE.SphereGeometry(0.035, 24, 24);
  const material = new THREE.MeshBasicMaterial({ color });
  return new THREE.Mesh(geometry, material);
}

/**
 * Convert 8-bit RGB to centered cube coordinates.
 */
export function cubePointFromRgb255(rgb: { r: number; g: number; b: number }): Point3D {
  return {
    x: rgb.r / 255 - 0.5,
    y: rgb.g / 255 - 0.5,
    z: rgb.b / 255 - 0.5,
  };
}

/**
 * Convert HSV to a hexcone point with value on the vertical axis.
 */
export function hexconePointFromHsv(hsv: HsvColor): Point3D {
  const point = projectHsvToHex(hsv);
  return {
    x: point.x,
    y: point.y,
    z: hsv.v,
  };
}

/**
 * Create a basic axes helper.
 */
export function createAxes(size: number): THREE.AxesHelper {
  return new THREE.AxesHelper(size);
}
