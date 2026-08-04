/**
 * Teaching control panel (Chinese UI): H/S/V sliders, projection shape
 * selection, display toggles, a live RGB<->HSV formula block and a short
 * teaching note that updates with the current state.
 */
import { hsvToRgb } from '../core/color-convert/rgb-hsv';
import type { HsvProjectionScene } from './hsv-projection-scene';
import { circleChroma, hexChroma, rgbToWorld } from './teach-math';
import type { ProjectionMode, TeachStateStore } from './teach-state';

const fmt = (n: number, digits = 3): string => n.toFixed(digits);

interface SliderRow {
  slider: HTMLInputElement;
  number: HTMLInputElement;
}

export function createTeachPanel(store: TeachStateStore, scene: HsvProjectionScene): HTMLElement {
  const section = document.createElement('section');
  section.className = 'panel teach-panel';
  section.innerHTML = `
    <h2>投影教学控制</h2>

    <div class="stack">
      <h3>颜色参数</h3>
      ${valueRow('色相 H', 'h', 0, 360, 1)}
      ${valueRow('饱和度 S', 's', 0, 100, 1)}
      ${valueRow('明度 V', 'v', 0, 100, 1)}
    </div>

    <div class="stack">
      <h3>投影形状</h3>
      <label class="check-field">
        <input data-role="proj-hex" type="radio" name="proj" value="hex" checked />
        <span>正六边形（默认）— 立方体真实投影</span>
      </label>
      <label class="check-field">
        <input data-role="proj-circle" type="radio" name="proj" value="circle" />
        <span>圆形 — 极坐标投影</span>
      </label>
    </div>

    <div class="stack">
      <h3>显示元素</h3>
      ${toggleRow('showCube', '倾斜 RGB 立方体')}
      ${toggleRow('showSubCube', '小立方体 [0,v]³ + 外表面')}
      ${toggleRow('showAxes', 'RGB 轴 + 中性轴')}
      ${toggleRow('showProjectionPlane', '投影面板（六边形/圆）')}
      ${toggleRow('showCutPlanes', '切割面 r/v、g/v、b/v')}
      ${toggleRow('showProjectionLine', '投影线（3D → 平面）')}
      ${toggleRow('showHexRing', '等 S 六边形环轨迹')}
      ${toggleRow('showCubeHex', '小立方体对应正六边形（虚线）')}
      ${toggleRow('showOverflow', '圆超出六边形的越界区域')}
      ${toggleRow('showLabels', '数值标签（RGB / HSV）')}
      <button data-role="top-view" type="button">沿中性轴俯视</button>
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
        <li>调 H：点沿 V=v 表面的等 S 环移动（六边形轨迹；圆形模式为圆环，圆会超出六边形）。</li>
        <li>调 S：点沿 V=v 表面向中性轴点 (v,v,v) 径向移动，V 不变。</li>
      </ol>
      <p class="note-dynamic" data-role="note-dynamic"></p>
    </div>
  `;

  // ---- Wire up sliders -----------------------------------------------------
  const rows: Record<string, SliderRow> = {};
  ['h', 's', 'v'].forEach((key) => {
    const slider = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="slider"]`);
    const number = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="number"]`);
    if (!slider || !number) {
      throw new Error(`Missing slider for ${key}`);
    }
    rows[key] = { slider, number };

    const onInput = (): void => {
      const v = Number(slider.value);
      syncPair(rows[key], v);
      if (key === 'h') {
        store.set({ h: v });
      } else if (key === 's') {
        store.set({ s: v / 100 });
      } else {
        store.set({ v: v / 100 });
      }
    };
    slider.addEventListener('input', onInput);
    number.addEventListener('input', () => {
      const v = Number(number.value);
      if (Number.isNaN(v)) {
        return;
      }
      syncPair(rows[key], v);
      if (key === 'h') {
        store.set({ h: v });
      } else if (key === 's') {
        store.set({ s: v / 100 });
      } else {
        store.set({ v: v / 100 });
      }
    });
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
  const toggleKeys: Array<{ key: 'showCube' | 'showSubCube' | 'showAxes' | 'showProjectionPlane' | 'showCutPlanes' | 'showProjectionLine' | 'showHexRing' | 'showCubeHex' | 'showOverflow' | 'showLabels'; input: HTMLInputElement }> = [];
  const toggleDefs = [
    'showCube', 'showSubCube', 'showAxes', 'showProjectionPlane', 'showCutPlanes',
    'showProjectionLine', 'showHexRing', 'showCubeHex',
    'showOverflow', 'showLabels',
  ] as const;
  toggleDefs.forEach((key) => {
    const input = section.querySelector<HTMLInputElement>(`input[data-role="${key}"]`);
    if (!input) {
      throw new Error(`Missing toggle ${key}`);
    }
    toggleKeys.push({ key, input });
    input.addEventListener('change', () => {
      store.set({ [key]: input.checked } as Partial<ReturnType<TeachStateStore['getState']>>);
    });
  });

  // ---- Top view button --------------------------------------------------------
  const topView = section.querySelector<HTMLButtonElement>('button[data-role="top-view"]');
  if (!topView) {
    throw new Error('Top view button missing');
  }
  topView.addEventListener('click', () => scene.lookAlongAxis());

  // ---- Formula + dynamic note --------------------------------------------------
  const formulaEl = section.querySelector<HTMLPreElement>('[data-role="formula"]');
  const noteDynamicEl = section.querySelector<HTMLElement>('[data-role="note-dynamic"]');
  if (!formulaEl || !noteDynamicEl) {
    throw new Error('Formula / note elements missing');
  }

  store.subscribe((state) => {
    // Sync sliders.
    syncPair(rows.h, Math.round(state.h));
    syncPair(rows.s, Math.round(state.s * 100));
    syncPair(rows.v, Math.round(state.v * 100));
    hexRadio.checked = state.projection === 'hex';
    circleRadio.checked = state.projection === 'circle';
    toggleKeys.forEach(({ key, input }) => {
      input.checked = state[key];
    });

    // Formula block.
    const rgb = hsvToRgb({ h: state.h, s: state.s, v: state.v });
    const world = rgbToWorld(rgb);
    const alpha = (2 * rgb.r - rgb.g - rgb.b) / 2;
    const beta = (Math.sqrt(3) / 2) * (rgb.g - rgb.b);
    const c = hexChroma(rgb);
    const m = Math.min(rgb.r, rgb.g, rgb.b);
    const r255 = Math.round(rgb.r * 255);
    const g255 = Math.round(rgb.g * 255);
    const b255 = Math.round(rgb.b * 255);

    formulaEl.textContent =
      `RGB = (${fmt(rgb.r)}, ${fmt(rgb.g)}, ${fmt(rgb.b)})  [${r255}, ${g255}, ${b255}]\n` +
      `HSV = (${fmt(state.h, 1)}°, ${fmt(state.s)}, ${fmt(state.v)})\n\n` +
      `RGB → HSV\n` +
      `  M = max(R,G,B) = ${fmt(state.v)}\n` +
      `  m = min(R,G,B) = ${fmt(m)}\n` +
      `  C = M − m = ${fmt(c)}   （六边形色度）\n` +
      `  S = C / M = ${fmt(c / state.v)}\n` +
      `  H = 分段函数（60° 一步） = ${fmt(state.h, 1)}°\n\n` +
      `RGB → 色度平面投影（α/β 坐标）\n` +
      `  α = (2R−G−B)/2 = ${fmt(alpha)}\n` +
      `  β = (√3/2)(G−B) = ${fmt(beta)}\n` +
      `  C₂ = √(α²+β²) = ${fmt(circleChroma(world))}   （圆形色度）\n` +
      `  六边形 vs 圆：顶点方向 C=C₂；边中点方向圆比六边形大 ${fmt(Math.sqrt(3) / 2, 4)}×`;

    // Dynamic note.
    const shapeText = state.projection === 'hex' ? '六边形环' : '圆环';
    noteDynamicEl.textContent =
      `当前：V=${fmt(state.v)}（小立方体边长 ${fmt(state.v)}）；` +
      `S=${fmt(state.s)}（等S${shapeText}，色度 C=${fmt(state.s * state.v)}）；` +
      `H=${fmt(state.h, 1)}°。` +
      `点位于 V=v 外表面，投影到六边形${state.projection === 'hex' ? '' : '/圆'}平面坐标为 ` +
      `(α,β)=(${fmt(alpha)}, ${fmt(beta)})。`;
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
