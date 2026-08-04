import type { ColorStateStore, ColorSpaceState } from '../state/color-state-store';

interface InputBindings {
  slider: HTMLInputElement;
  number: HTMLInputElement;
}

/**
 * Keep paired number and range inputs synchronized.
 */
function syncPair(bindings: InputBindings, value: number): void {
  bindings.slider.value = String(value);
  bindings.number.value = String(value);
}

/**
 * Read the current RGB 8-bit controls and update the store.
 */
function commitRgb(section: HTMLElement, store: ColorStateStore): void {
  const r = Number(section.querySelector<HTMLInputElement>('input[data-key="r"][data-kind="number"]')?.value ?? 0);
  const g = Number(section.querySelector<HTMLInputElement>('input[data-key="g"][data-kind="number"]')?.value ?? 0);
  const b = Number(section.querySelector<HTMLInputElement>('input[data-key="b"][data-kind="number"]')?.value ?? 0);

  store.setRgb255({ r, g, b });
}

/**
 * Read the current HSV controls and update the store.
 */
function commitHsv(section: HTMLElement, store: ColorStateStore): void {
  const h = Number(section.querySelector<HTMLInputElement>('input[data-key="h"][data-kind="number"]')?.value ?? 0);
  const s = Number(section.querySelector<HTMLInputElement>('input[data-key="s"][data-kind="number"]')?.value ?? 0) / 100;
  const v = Number(section.querySelector<HTMLInputElement>('input[data-key="v"][data-kind="number"]')?.value ?? 0) / 100;

  store.setHsv({ h, s, v });
}

/**
 * Build a single row with a number input and slider.
 */
function createValueRow(label: string, key: string, min: number, max: number, step: number): string {
  return `
    <div class="value-row">
      <label class="value-label" for="${key}-number">${label}</label>
      <input id="${key}-number" data-key="${key}" data-kind="number" type="number" min="${min}" max="${max}" step="${step}" />
      <input data-key="${key}" data-kind="slider" type="range" min="${min}" max="${max}" step="${step}" />
    </div>
  `;
}

/**
 * Update the visible inputs from the latest state snapshot.
 */
function applyState(section: HTMLElement, state: ColorSpaceState): void {
  const pairs: Record<string, number> = {
    r: state.rgb255.r,
    g: state.rgb255.g,
    b: state.rgb255.b,
    h: Math.round(state.hsv.h),
    s: Math.round(state.hsv.s * 100),
    v: Math.round(state.hsv.v * 100),
  };

  Object.entries(pairs).forEach(([key, value]) => {
    const slider = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="slider"]`);
    const number = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="number"]`);

    if (slider && number) {
      syncPair({ slider, number }, value);
    }
  });
}

/**
 * Build synchronized RGB and HSV numeric controls.
 */
export function createValueInputs(store: ColorStateStore): HTMLElement {
  const section = document.createElement('section');
  section.className = 'panel';
  section.innerHTML = `
    <h2>Color Inputs</h2>
    <div class="stack">
      ${createValueRow('R', 'r', 0, 255, 1)}
      ${createValueRow('G', 'g', 0, 255, 1)}
      ${createValueRow('B', 'b', 0, 255, 1)}
      ${createValueRow('H', 'h', 0, 360, 1)}
      ${createValueRow('S', 's', 0, 100, 1)}
      ${createValueRow('V', 'v', 0, 100, 1)}
    </div>
  `;

  section.querySelectorAll<HTMLInputElement>('input[data-key="r"], input[data-key="g"], input[data-key="b"]').forEach((input) => {
    input.addEventListener('input', () => {
      const key = input.dataset.key;
      if (!key) {
        return;
      }

      const slider = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="slider"]`);
      const number = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="number"]`);
      if (!slider || !number) {
        return;
      }

      syncPair({ slider, number }, Number(input.value));
      commitRgb(section, store);
    });
  });

  section.querySelectorAll<HTMLInputElement>('input[data-key="h"], input[data-key="s"], input[data-key="v"]').forEach((input) => {
    input.addEventListener('input', () => {
      const key = input.dataset.key;
      if (!key) {
        return;
      }

      const slider = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="slider"]`);
      const number = section.querySelector<HTMLInputElement>(`input[data-key="${key}"][data-kind="number"]`);
      if (!slider || !number) {
        return;
      }

      syncPair({ slider, number }, Number(input.value));
      commitHsv(section, store);
    });
  });

  store.subscribe((state) => {
    applyState(section, state);
  });

  return section;
}
