/**
 * Teaching control panel (Chinese UI): initial color point inputs (RGB or HSV),
 * ΔH/ΔS/ΔV adjustment sliders that act on the input point, projection shape
 * selection, display toggles, an input/output value block, a live RGB<->HSV
 * formula block and a short teaching note that updates with the current state.
 */
import { hsvToRgb, rgbToHsv } from '../core/color-convert/rgb-hsv';
import type { HsvColor, RgbColor } from '../state/types';
import type { HsvProjectionScene } from './hsv-projection-scene';
import { applyHsvAdjust, circleChroma, hexChroma, rgbToWorld } from './teach-math';
import type { ProjectionMode, TeachState, TeachStateStore } from './teach-state';

const fmt = (n: number, digits = 3): string => n.toFixed(digits);

interface SliderRow {
  slider: HTMLInputElement;
  number: HTMLInputElement;
}

const clamp = (v: number, lo: number, hi: number): number => Math.min(hi, Math.max(lo, v));

export function createTeachPanel(store: TeachStateStore, scene: HsvProjectionScene): HTMLElement {
  const section = document.createElement('section');
  section.className = 'panel teach-panel';
  section.innerHTML = `
    <h2>投影教学控制</h2>

    <div class="stack">
      <h3>初始颜色点（输入）</h3>
      ${valueRow('R', 'r', 0, 255, 1)}
      ${valueRow('G', 'g', 0, 255, 1)}
      ${valueRow('B', 'b', 0, 255, 1)}
      ${valueRow('H', 'h', 0, 360, 1)}
      ${valueRow('S', 's', 0, 100, 1)}
      ${valueRow('V', 'v', 0, 100, 1)}
      <div class="wheel-wrap">
        <canvas data-role="wheel" width="220" height="220"></canvas>
        <div data-role="wheel-marker" class="wheel-marker"></div>
        <div class="wheel-hint">点击 / 拖拽圆形色轮选 H/S（方案 A：圆盘化六边形 HSV，V 由上方滑条控制）</div>
      </div>
    </div>

    <div class="stack">
      <h3>调整参数（Δ 作用于输入点）</h3>
      ${valueRow('ΔH 色相', 'dh', -180, 180, 1)}
      ${valueRow('ΔS 饱和度', 'ds', -100, 100, 1)}
      ${valueRow('ΔV 明度', 'dv', -100, 100, 1)}
    </div>

    <div class="stack">
      <h3>投影形状</h3>
      <label class="check-field">
        <input data-role="proj-hex" type="radio" name="proj" value="hex" checked />
        <span>正六边形（默认）— 立方体真实投影</span>
      </label>
      <label class="check-field">
        <input data-role="proj-circle" type="radio" name="proj" value="circle" />
        <span>圆形 — 极坐标投影（FIXME）</span>
      </label>
    </div>

    <div class="stack">
      <h3>显示元素</h3>
      ${toggleRow('showCube', '倾斜 RGB 立方体')}
      ${toggleRow('showSubCube', '小立方体 [0,v]³ + 外表面')}
      ${toggleRow('showAxes', 'RGB 轴 + 中性轴')}
      ${toggleRow('showProjectionLine', '投影线（3D → 平面）')}
      ${toggleRow('showHexRing', '等S轨迹线')}
      ${toggleRow('showLabels', '数值标签（RGB / HSV）')}
      <button data-role="top-view" type="button">沿中性轴俯视</button>
    </div>

    <div class="stack">
      <h3>输入 / 输出</h3>
      <pre class="formula-box" data-role="io"></pre>
    </div>

    <div class="stack">
      <h3>RGB ↔ HSV 转换</h3>
      <pre class="formula-box" data-role="formula"></pre>
    </div>

    <div class="stack">
      <h3>投影原理（4 点理解）</h3>
      <ol class="note-list" data-role="note">
        <li>V=v：r=v / g=v / b=v 三个截面包围边长为 v 的小立方体，其外表面即 V=v。</li>
        <li>小立方体沿中性轴投影到水平面 = 正六边形；六边形上每点都对应外表面上一点。</li>
        <li>调 ΔH：输出点沿 V=v 表面的等 S 环移动（六边形轨迹；圆形模式为圆环，圆会超出六边形）。</li>
        <li>调 ΔS：输出点沿 V=v 表面向中性轴点 (v,v,v) 径向移动，V 不变。</li>
      </ol>
      <p class="note-dynamic" data-role="note-dynamic"></p>
    </div>
  `;

  // ---- Input rows ----------------------------------------------------------
  const rows: Record<string, SliderRow> = {};
  ['r', 'g', 'b', 'h', 's', 'v', 'dh', 'ds', 'dv'].forEach((key) => {
    const slider = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="slider"]`);
    const number = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="number"]`);
    if (!slider || !number) {
      throw new Error(`Missing slider for ${key}`);
    }
    rows[key] = { slider, number };
  });

  // ---- Initial color point (input) -----------------------------------------
  const readInputRgb = (): RgbColor => ({
    r: clamp(Number(rows.r.number.value) || 0, 0, 255) / 255,
    g: clamp(Number(rows.g.number.value) || 0, 0, 255) / 255,
    b: clamp(Number(rows.b.number.value) || 0, 0, 255) / 255,
  });
  const readInputHsv = (): HsvColor => ({
    h: clamp(Number(rows.h.number.value) || 0, 0, 360),
    s: clamp(Number(rows.s.number.value) || 0, 0, 100) / 100,
    v: clamp(Number(rows.v.number.value) || 0, 0, 100) / 100,
  });

  const commitInputRgb = (): void => {
    const inputRgb = readInputRgb();
    store.set({ inputRgb, inputHsv: rgbToHsv(inputRgb) });
  };
  const commitInputHsv = (): void => {
    const inputHsv = readInputHsv();
    store.set({ inputHsv, inputRgb: hsvToRgb(inputHsv) });
  };

  ['r', 'g', 'b'].forEach((key) => {
    const row = rows[key];
    const onInput = (e: Event): void => {
      const src = e.target as HTMLInputElement;
      const v = Number(src.value);
      if (Number.isNaN(v)) {
        return;
      }
      syncPair(row, clamp(v, 0, 255));
      commitInputRgb();
    };
    row.slider.addEventListener('input', onInput);
    row.number.addEventListener('input', onInput);
  });
  ['h', 's', 'v'].forEach((key) => {
    const row = rows[key];
    const onInput = (e: Event): void => {
      const src = e.target as HTMLInputElement;
      const v = Number(src.value);
      if (Number.isNaN(v)) {
        return;
      }
      const max = key === 'h' ? 360 : 100;
      syncPair(row, clamp(v, 0, max));
      commitInputHsv();
    };
    row.slider.addEventListener('input', onInput);
    row.number.addEventListener('input', onInput);
  });

  // ---- Adjustment deltas (ΔH/ΔS/ΔV) ----------------------------------------
  const commitDelta = (): void => {
    store.set({
      dh: clamp(Number(rows.dh.number.value) || 0, -180, 180),
      ds: clamp(Number(rows.ds.number.value) || 0, -100, 100) / 100,
      dv: clamp(Number(rows.dv.number.value) || 0, -100, 100) / 100,
    });
  };
  ['dh', 'ds', 'dv'].forEach((key) => {
    const row = rows[key];
    const onInput = (e: Event): void => {
      const src = e.target as HTMLInputElement;
      const v = Number(src.value);
      if (Number.isNaN(v)) {
        return;
      }
      const max = key === 'dh' ? 180 : 100;
      syncPair(row, clamp(v, -max, max));
      commitDelta();
    };
    row.slider.addEventListener('input', onInput);
    row.number.addEventListener('input', onInput);
  });

  // ---- Projection shape -----------------------------------------------------
  const hexRadio = section.querySelector<HTMLInputElement>('input[data-role="proj-hex"]');
  const circleRadio = section.querySelector<HTMLInputElement>('input[data-role="proj-circle"]');
  if (!hexRadio || !circleRadio) {
    throw new Error('Projection radios missing');
  }
  const setProjection = (mode: ProjectionMode): void => {
    hexRadio.checked = mode === 'hex';
    circleRadio.checked = mode === 'circle';
    store.set({ projection: mode });
  };
  hexRadio.addEventListener('change', () => setProjection('hex'));
  circleRadio.addEventListener('change', () => setProjection('circle'));

  // ---- Display toggles ------------------------------------------------------
  const toggleKeys: Array<{ key: 'showCube' | 'showSubCube' | 'showAxes' | 'showProjectionLine' | 'showHexRing' | 'showLabels'; input: HTMLInputElement }> = [];
  const toggleDefs = [
    'showCube', 'showSubCube', 'showAxes',
    'showProjectionLine', 'showHexRing',
    'showLabels',
  ] as const;
  toggleDefs.forEach((key) => {
    const input = section.querySelector<HTMLInputElement>(`input[data-role="${key}"]`);
    if (!input) {
      throw new Error(`Missing toggle ${key}`);
    }
    toggleKeys.push({ key, input });
    input.addEventListener('change', () => {
      store.set({ [key]: input.checked } as Partial<TeachState>);
    });
  });

  // ---- Top view button --------------------------------------------------------
  const topView = section.querySelector<HTMLButtonElement>('button[data-role="top-view"]');
  if (!topView) {
    throw new Error('Top view button missing');
  }
  topView.addEventListener('click', () => scene.lookAlongAxis());

  // ---- Interactive circle color wheel (Scheme A) ------------------------------
  // Disk filled with the hexagonal HSV painted as a circle (x=S·cosH, y=S·sinH),
  // so the click position and the shown color always agree (what-you-see-is-
  // what-you-get).  Click / drag picks the H/S of the INPUT point; V comes from
  // the V slider above.  This is the standard UI color-picker scheme (PS/GIMP).
  const wheel = section.querySelector<HTMLCanvasElement>('canvas[data-role="wheel"]');
  const wheelMarker = section.querySelector<HTMLElement>('[data-role="wheel-marker"]');
  if (!wheel || !wheelMarker) {
    throw new Error('Wheel elements missing');
  }
  const WHEEL_R = wheel.width / 2 - 8; /* 圆盘半径（px） */
  let wheelDragging = false;
  let lastWheelV = -1;

  const paintWheel = (v: number): void => {
    const ctx = wheel.getContext('2d');
    if (!ctx) {
      return;
    }
    const cx = wheel.width / 2;
    const cy = wheel.height / 2;
    const img = ctx.createImageData(wheel.width, wheel.height);
    const d = img.data;
    for (let y = 0; y < wheel.height; y++) {
      for (let x = 0; x < wheel.width; x++) {
        const dx = x - cx;
        const dy = y - cy;
        const r = Math.hypot(dx, dy);
        const i = (y * wheel.width + x) * 4;
        if (r > WHEEL_R) {
          d[i + 3] = 0;
          continue;
        }
        // Mirror canvas y (-dy) so the wheel matches the hexagon orientation
        // (red right, yellow top-right), same as the 3D scene.
        const h = (Math.atan2(-dy, dx) * 180) / Math.PI;
        const c = hsvToRgb({ h: (h + 360) % 360, s: Math.min(1, r / WHEEL_R), v });
        d[i] = Math.round(c.r * 255);
        d[i + 1] = Math.round(c.g * 255);
        d[i + 2] = Math.round(c.b * 255);
        d[i + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    lastWheelV = v;
  };

  const setWheelMarker = (h: number, s: number): void => {
    const cx = wheel.width / 2;
    const cy = wheel.height / 2;
    const rad = (h * Math.PI) / 180;
    wheelMarker.style.left = `${cx + s * WHEEL_R * Math.cos(rad)}px`;
    wheelMarker.style.top = `${cy - s * WHEEL_R * Math.sin(rad)}px`; /* mirror y */
  };

  const pickFromWheel = (e: PointerEvent): void => {
    const rect = wheel.getBoundingClientRect();
    const scale = wheel.width / rect.width;
    const cx = wheel.width / 2;
    const cy = wheel.height / 2;
    const dx = (e.clientX - rect.left) * scale - cx;
    const dy = (e.clientY - rect.top) * scale - cy;
    const r = Math.hypot(dx, dy);
    if (r > WHEEL_R) {
      return; /* 点击圆盘外不响应 */
    }
    const h = (Math.atan2(-dy, dx) * 180) / Math.PI;
    const s = r / WHEEL_R;
    const v = store.getState().inputHsv.v;
    const inputHsv = { h: (h + 360) % 360, s, v };
    store.set({ inputHsv, inputRgb: hsvToRgb(inputHsv) });
  };

  wheel.addEventListener('pointerdown', (e) => {
    wheelDragging = true;
    try {
      wheel.setPointerCapture(e.pointerId);
    } catch {
      /* 合成事件 / 无 active pointer 时忽略，选色仍继续 */
    }
    pickFromWheel(e);
  });
  wheel.addEventListener('pointermove', (e) => {
    if (wheelDragging) {
      pickFromWheel(e);
    }
  });
  wheel.addEventListener('pointerup', () => {
    wheelDragging = false;
  });
  wheel.addEventListener('pointercancel', () => {
    wheelDragging = false;
  });

  // ---- Formula + IO + dynamic note --------------------------------------------
  const formulaEl = section.querySelector<HTMLPreElement>('[data-role="formula"]');
  const ioEl = section.querySelector<HTMLPreElement>('[data-role="io"]');
  const noteDynamicEl = section.querySelector<HTMLElement>('[data-role="note-dynamic"]');
  if (!formulaEl || !ioEl || !noteDynamicEl) {
    throw new Error('Formula / IO / note elements missing');
  }

  store.subscribe((state) => {
    // Sync input point controls.
    syncPair(rows.r, Math.round(state.inputRgb.r * 255));
    syncPair(rows.g, Math.round(state.inputRgb.g * 255));
    syncPair(rows.b, Math.round(state.inputRgb.b * 255));
    syncPair(rows.h, Math.round(state.inputHsv.h));
    syncPair(rows.s, Math.round(state.inputHsv.s * 100));
    syncPair(rows.v, Math.round(state.inputHsv.v * 100));
    // Sync adjustment deltas.
    syncPair(rows.dh, Math.round(state.dh));
    syncPair(rows.ds, Math.round(state.ds * 100));
    syncPair(rows.dv, Math.round(state.dv * 100));
    hexRadio.checked = state.projection === 'hex';
    circleRadio.checked = state.projection === 'circle';
    toggleKeys.forEach(({ key, input }) => {
      input.checked = state[key];
    });

    // Input / output values.
    const inRgb = state.inputRgb;
    const inHsv = state.inputHsv;
    const outHsv = applyHsvAdjust(inHsv, state.dh, state.ds, state.dv);
    const outRgb = hsvToRgb(outHsv);
    const in255 = (c: RgbColor): string =>
      `${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}`;
    ioEl.textContent =
      `输入 RGB = (${fmt(inRgb.r)}, ${fmt(inRgb.g)}, ${fmt(inRgb.b)})  [${in255(inRgb)}]\n` +
      `输入 HSV = (${fmt(inHsv.h, 1)}°, ${fmt(inHsv.s)}, ${fmt(inHsv.v)})\n` +
      `ΔH = ${fmt(state.dh, 1)}°  ΔS = ${fmt(state.ds, 3)}  ΔV = ${fmt(state.dv, 3)}\n\n` +
      `输出 HSV = (${fmt(outHsv.h, 1)}°, ${fmt(outHsv.s)}, ${fmt(outHsv.v)})\n` +
      `输出 RGB = (${fmt(outRgb.r)}, ${fmt(outRgb.g)}, ${fmt(outRgb.b)})  [${in255(outRgb)}]`;

    // Formula block (based on the output point).
    const rgb = outRgb;
    const world = rgbToWorld(rgb);
    const alpha = (2 * rgb.r - rgb.g - rgb.b) / 2;
    const beta = (Math.sqrt(3) / 2) * (rgb.g - rgb.b);
    const c = hexChroma(rgb);
    const m = Math.min(rgb.r, rgb.g, rgb.b);
    const r255 = Math.round(rgb.r * 255);
    const g255 = Math.round(rgb.g * 255);
    const b255 = Math.round(rgb.b * 255);
    // Circle (polar) projection coordinates: (x, y) = (S·cosH, S·sinH), V-independent.
    const isCircle = state.projection === 'circle';
    const px = outHsv.s * Math.cos((outHsv.h * Math.PI) / 180);
    const py = outHsv.s * Math.sin((outHsv.h * Math.PI) / 180);

    formulaEl.textContent =
      `输出 RGB = (${fmt(rgb.r)}, ${fmt(rgb.g)}, ${fmt(rgb.b)})  [${r255}, ${g255}, ${b255}]\n` +
      `输出 HSV = (${fmt(outHsv.h, 1)}°, ${fmt(outHsv.s)}, ${fmt(outHsv.v)})\n\n` +
      `RGB → HSV\n` +
      `  M = max(R,G,B) = ${fmt(outHsv.v)}\n` +
      `  m = min(R,G,B) = ${fmt(m)}\n` +
      `  C = M − m = ${fmt(c)}   （六边形色度）\n` +
      `  S = C / M = ${fmt(c / outHsv.v)}\n` +
      `  H = 分段函数（60° 一步） = ${fmt(outHsv.h, 1)}°\n\n` +
      (isCircle
        ? `RGB → 圆形极坐标投影（方案 A）\n` +
          `  x = S·cosH = ${fmt(px)}\n` +
          `  y = S·sinH = ${fmt(py)}\n` +
          `  r = S = ${fmt(outHsv.s)}   （与 V 无关）`
        : `RGB → 色度平面投影（α/β 坐标）\n` +
          `  α = (2R−G−B)/2 = ${fmt(alpha)}\n` +
          `  β = (√3/2)(G−B) = ${fmt(beta)}\n` +
          `  C₂ = √(α²+β²) = ${fmt(circleChroma(world))}   （圆形色度）\n` +
          `  六边形 vs 圆：顶点方向 C=C₂；边中点方向圆比六边形大 ${fmt(Math.sqrt(3) / 2, 4)}×`);

    // Dynamic note.
    const shapeText = state.projection === 'hex' ? '六边形环' : '圆环';
    noteDynamicEl.textContent =
      `输入点：RGB(${in255(inRgb)}) → HSV(${fmt(inHsv.h, 1)}°, ${fmt(inHsv.s)}, ${fmt(inHsv.v)})。` +
      `应用 ΔH=${fmt(state.dh, 1)}° ΔS=${fmt(state.ds, 3)} ΔV=${fmt(state.dv, 3)} 后：` +
      `输出 V=${fmt(outHsv.v)}（小立方体边长 ${fmt(outHsv.v)}）；` +
      `S=${fmt(outHsv.s)}（等S${shapeText}，色度 C=${fmt(outHsv.s * outHsv.v)}）；` +
      `H=${fmt(outHsv.h, 1)}°。` +
      `输出点位于 V=v 外表面，` +
      (isCircle
        ? `圆形极坐标投影坐标为 (x,y)=(${fmt(px)}, ${fmt(py)})。`
        : `投影到六边形平面坐标为 (α,β)=(${fmt(alpha)}, ${fmt(beta)})。`);

    // Interactive wheel: repaint only when V changed, marker on every update.
    if (state.inputHsv.v !== lastWheelV) {
      paintWheel(state.inputHsv.v);
    }
    setWheelMarker(state.inputHsv.h, state.inputHsv.s);
  });

  return section;
}

// ---- Small builders ----------------------------------------------------------

function valueRow(label: string, key: string, min: number, max: number, step: number): string {
  return `
    <div class="value-row">
      <label class="value-label">${label}</label>
      <input data-key="${key}" data-kind="number" type="number" min="${min}" max="${max}" step="${step}" />
      <input data-key="${key}" data-kind="slider" type="range" min="${min}" max="${max}" step="${step}" />
    </div>
  `;
}

function toggleRow(key: string, label: string): string {
  return `
    <label class="check-field">
      <input data-role="${key}" type="checkbox" />
      <span>${label}</span>
    </label>
  `;
}

function syncPair(pair: SliderRow, value: number): void {
  pair.slider.value = String(value);
  pair.number.value = String(value);
}
