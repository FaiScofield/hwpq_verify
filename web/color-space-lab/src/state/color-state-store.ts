import { hsvToRgb, rgbToHsv } from '../core/color-convert/rgb-hsv';
import type { HsvColor, RgbColor } from './types';

export interface Rgb255Color {
  r: number;
  g: number;
  b: number;
}

export interface ColorSpaceState {
  rgb: RgbColor;
  rgb255: Rgb255Color;
  hsv: HsvColor;
  lastHue: number;
  cubeOpacity: number;
  currentSpace: 'HSV' | 'HSL' | 'HSI' | 'HSY';
  showAxes: boolean;
  showGuides: boolean;
}

type Listener = (state: ColorSpaceState) => void;

/**
 * Convert normalized RGB to 8-bit RGB.
 */
function toRgb255(rgb: RgbColor): Rgb255Color {
  return {
    r: Math.round(rgb.r * 255),
    g: Math.round(rgb.g * 255),
    b: Math.round(rgb.b * 255),
  };
}

/**
 * Convert 8-bit RGB to normalized RGB.
 */
function toRgbUnit(rgb255: Rgb255Color): RgbColor {
  return {
    r: rgb255.r / 255,
    g: rgb255.g / 255,
    b: rgb255.b / 255,
  };
}

/**
 * Hold the single source of truth for color-space state.
 */
export class ColorStateStore {
  private readonly listeners = new Set<Listener>();

  private state: ColorSpaceState = {
    rgb: { r: 1, g: 0, b: 0 },
    rgb255: { r: 255, g: 0, b: 0 },
    hsv: { h: 0, s: 1, v: 1 },
    lastHue: 0,
    cubeOpacity: 0.2,
    currentSpace: 'HSV',
    showAxes: true,
    showGuides: true,
  };

  /**
   * Get the current immutable-looking state snapshot.
   */
  getState(): ColorSpaceState {
    return this.state;
  }

  /**
   * Subscribe to future state updates.
   */
  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  /**
   * Update state from 8-bit RGB controls.
   */
  setRgb255(rgb255: Rgb255Color): void {
    const rgb = toRgbUnit(rgb255);
    const hsv = rgbToHsv(rgb);
    const hue = hsv.s === 0 ? this.state.lastHue : hsv.h;

    this.state = {
      ...this.state,
      rgb,
      rgb255,
      hsv: { ...hsv, h: hue },
      lastHue: hue,
    };
    this.emit();
  }

  /**
   * Update state from HSV controls.
   */
  setHsv(hsv: HsvColor): void {
    const normalizedH = ((hsv.h % 360) + 360) % 360;
    const normalized: HsvColor = {
      h: normalizedH,
      s: Math.min(1, Math.max(0, hsv.s)),
      v: Math.min(1, Math.max(0, hsv.v)),
    };
    const rgb = hsvToRgb(normalized);

    this.state = {
      ...this.state,
      hsv: normalized,
      rgb,
      rgb255: toRgb255(rgb),
      lastHue: normalized.s === 0 ? this.state.lastHue : normalized.h,
    };
    this.emit();
  }

  /**
   * Update RGB cube opacity.
   */
  setCubeOpacity(cubeOpacity: number): void {
    this.state = {
      ...this.state,
      cubeOpacity: Math.min(1, Math.max(0.05, cubeOpacity)),
    };
    this.emit();
  }

  /**
   * Update simple display flags.
   */
  setFlags(flags: Partial<Pick<ColorSpaceState, 'showAxes' | 'showGuides'>>): void {
    this.state = { ...this.state, ...flags };
    this.emit();
  }

  /**
   * Switch the selected color-space tab.
   */
  setCurrentSpace(space: ColorSpaceState['currentSpace']): void {
    this.state = { ...this.state, currentSpace: space };
    this.emit();
  }

  /**
   * Notify all live subscribers.
   */
  private emit(): void {
    this.listeners.forEach((listener) => listener(this.state));
  }
}
