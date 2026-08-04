import { colorSpaces } from '../core/spaces/registry';
import type { ColorStateStore } from '../state/color-state-store';

/**
 * Build the global control panel for space selection and view toggles.
 */
export function createControlPanel(store: ColorStateStore): HTMLElement {
  const section = document.createElement('section');
  section.className = 'panel';
  const spaceOptions = colorSpaces
    .map(
      (space) =>
        `<option value="${space.key}"${'disabled' in space && space.disabled ? ' disabled' : ''}>${space.label}${'disabled' in space && space.disabled ? ' (coming soon)' : ''}</option>`,
    )
    .join('');

  section.innerHTML = `
    <h2>Controls</h2>
    <div class="stack">
      <label class="field">
        <span>Color Space</span>
        <select data-role="space">
          ${spaceOptions}
        </select>
      </label>
      <label class="field">
        <span>Cube Opacity</span>
        <input data-role="opacity" type="range" min="5" max="100" value="20" />
      </label>
      <label class="check-field">
        <input data-role="axes" type="checkbox" checked />
        <span>Show Axes</span>
      </label>
      <label class="check-field">
        <input data-role="guides" type="checkbox" checked />
        <span>Show Guides</span>
      </label>
    </div>
  `;

  const spaceSelect = section.querySelector<HTMLSelectElement>('select[data-role="space"]');
  const opacityInput = section.querySelector<HTMLInputElement>('input[data-role="opacity"]');
  const axesInput = section.querySelector<HTMLInputElement>('input[data-role="axes"]');
  const guidesInput = section.querySelector<HTMLInputElement>('input[data-role="guides"]');

  if (!spaceSelect || !opacityInput || !axesInput || !guidesInput) {
    throw new Error('Control panel template is incomplete.');
  }

  spaceSelect.addEventListener('change', () => {
    store.setCurrentSpace(spaceSelect.value as 'HSV' | 'HSL' | 'HSI' | 'HSY');
  });

  opacityInput.addEventListener('input', () => {
    store.setCubeOpacity(Number(opacityInput.value) / 100);
  });

  axesInput.addEventListener('change', () => {
    store.setFlags({ showAxes: axesInput.checked });
  });

  guidesInput.addEventListener('change', () => {
    store.setFlags({ showGuides: guidesInput.checked });
  });

  return section;
}
