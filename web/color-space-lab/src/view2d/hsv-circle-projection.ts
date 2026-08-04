import { projectHsvToCircle } from '../core/projections/hsv-circle';
import type { ColorStateStore } from '../state/color-state-store';
import { createSvg, createSvgElement } from './svg-helpers';

/**
 * Build the normalized circular HSV projection panel.
 */
export function createHsvCircleProjection(store: ColorStateStore): HTMLElement {
  const panel = document.createElement('section');
  panel.className = 'panel';
  panel.innerHTML = '<h2>Normalized Polar HSV</h2>';

  const svg = createSvg(280, 280);
  const border = createSvgElement('circle');
  border.setAttribute('cx', '0');
  border.setAttribute('cy', '0');
  border.setAttribute('r', '90');
  border.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
  border.setAttribute('stroke', '#059669');
  border.setAttribute('stroke-width', '2');

  const point = createSvgElement('circle');
  point.setAttribute('r', '5');
  point.setAttribute('fill', '#111827');

  svg.append(border, point);
  panel.append(svg);

  store.subscribe((state) => {
    const p = projectHsvToCircle(state.hsv);
    point.setAttribute('cx', String(p.x * 90));
    point.setAttribute('cy', String(-p.y * 90));
  });

  return panel;
}
