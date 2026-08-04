/**
 * Teaching scene state (subscribe/emit, mirroring state/color-state-store.ts).
 */
export type ProjectionMode = 'hex' | 'circle';

export interface TeachState {
  /** Hue in degrees [0, 360). */
  h: number;
  /** Saturation [0, 1]. */
  s: number;
  /** Value [0, 1]. */
  v: number;
  /** Projection shape: regular hexagon (default) or circle. */
  projection: ProjectionMode;
  /** 倾斜 RGB 立方体. */
  showCube: boolean;
  /** 小立方体 [0,v]³ + 外表面. */
  showSubCube: boolean;
  /** RGB 轴 + 中性轴 + RGB 投影轴 + V 值标注. */
  showAxes: boolean;
  /** 投影面板（六边形/圆）. */
  showProjectionPlane: boolean;
  /** 切割面 r/v、g/v、b/v. */
  showCutPlanes: boolean;
  /** 投影线（3D → 平面）. */
  showProjectionLine: boolean;
  /** 等 S 六边形环轨迹. */
  showHexRing: boolean;
  /** 小立方体对应的正六边形（虚线）. */
  showCubeHex: boolean;
  /** 圆超出六边形的越界区域. */
  showOverflow: boolean;
  /** 数值标签（RGB / HSV）. */
  showLabels: boolean;
}

type Listener = (state: TeachState) => void;

export class TeachStateStore {
  private readonly listeners = new Set<Listener>();

  private state: TeachState = {
    h: 30,
    s: 1,
    v: 0.8,
    projection: 'hex',
    showCube: true,
    showSubCube: true,
    showAxes: true,
    showProjectionPlane: true,
    showCutPlanes: false,
    showProjectionLine: true,
    showHexRing: true,
    showCubeHex: true,
    showOverflow: true,
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
