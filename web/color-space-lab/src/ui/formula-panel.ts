import { hsvSpace } from '../core/spaces/hsv-space';
import type { ColorStateStore } from '../state/color-state-store';

/**
 * Build the live formula and coordinate summary panel.
 */
export function createFormulaPanel(store: ColorStateStore): HTMLElement {
  const section = document.createElement('section');
  section.className = 'panel';
  section.innerHTML = `
    <h2>Current Formula</h2>
    <div class="formula-swatch" data-role="swatch"></div>
    <pre data-role="coords"></pre>
    <ul data-role="formula-list"></ul>
  `;

  const list = section.querySelector<HTMLUListElement>('[data-role="formula-list"]');
  const swatch = section.querySelector<HTMLDivElement>('[data-role="swatch"]');
  const coords = section.querySelector<HTMLPreElement>('[data-role="coords"]');

  if (!list || !swatch || !coords) {
    throw new Error('Formula panel template is incomplete.');
  }

  hsvSpace.formulas.forEach((formula) => {
    const item = document.createElement('li');
    item.textContent = formula;
    list.append(item);
  });

  store.subscribe((state) => {
    swatch.style.backgroundColor = `rgb(${state.rgb255.r}, ${state.rgb255.g}, ${state.rgb255.b})`;
    coords.textContent =
      `RGB255: (${state.rgb255.r}, ${state.rgb255.g}, ${state.rgb255.b})\n` +
      `HSV: (${state.hsv.h.toFixed(1)}, ${state.hsv.s.toFixed(3)}, ${state.hsv.v.toFixed(3)})`;
  });

  return section;
}
