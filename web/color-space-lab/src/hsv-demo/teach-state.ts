/**
 * Teaching scene state (subscribe/emit, mirroring state/color-state-store.ts).
 */
import type { HsvColor, RgbColor } from '../state/types';

export type ProjectionMode = 'hex' | 'circle';

export interface TeachState {
  /** 初始输入点（RGB，归一化 0..1）。 */
  inputRgb: RgbColor;
  /** 初始输入点（HSV：h 度 [0,360)，s/v 归一化 [0,1]）。 */
  inputHsv: HsvColor;
  /** 色相偏移 ΔH（度，[-180, 180]，作用于输入点）。 */
  dh: number;
  /** 饱和度偏移 ΔS（[-1, 1]，作用于输入点）。 */
  ds: number;
  /** 明度偏移 ΔV（[-1, 1]，作用于输入点）。 */
  dv: number;
  /** Projection shape: regular hexagon (default) or circle. */
  projection: ProjectionMode;
  /** 倾斜 RGB 立方体. */
  showCube: boolean;
  /** 小立方体 [0,v]³ + 外表面. */
  showSubCube: boolean;
  /** RGB 轴 + 中性轴 + RGB 投影轴 + V 值标注. */
  showAxes: boolean;
  /** 投影线（3D → 平面）. */
  showProjectionLine: boolean;
  /** 等S轨迹线（3D 等S环 + 平面虚线六边形）. */
  showHexRing: boolean;
  /** 数值标签（RGB / HSV）. */
  showLabels: boolean;
}

type Listener = (state: TeachState) => void;

export class TeachStateStore {
  private readonly listeners = new Set<Listener>();

  private state: TeachState = {
    inputRgb: { r: 0.8, g: 0.4, b: 0 },
    inputHsv: { h: 30, s: 1, v: 0.8 },
    dh: 0,
    ds: 0,
    dv: 0,
    projection: 'hex',
    showCube: true,
    showSubCube: true,
    showAxes: true,
    showProjectionLine: true,
    showHexRing: true,
    showLabels: true,
  };

  getState(): TeachState {
    return this.state;
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  set(partial: Partial<TeachState>): void {
    this.state = { ...this.state, ...partial };
    this.emit();
  }

  private emit(): void {
    this.listeners.forEach((listener) => listener(this.state));
  }
}
