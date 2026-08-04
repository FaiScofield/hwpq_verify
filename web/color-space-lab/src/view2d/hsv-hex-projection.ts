import { projectHsvToHex } from '../core/projections/hsv-hex';
import type { ColorStateStore } from '../state/color-state-store';
import { createSvg, createSvgElement } from './svg-helpers';

/**
 * Build the cube-derived HSV hexagon projection panel.
 */
export function createHsvHexProjection(store: ColorStateStore): HTMLElement {
  const panel = document.createElement('section');
  panel.className = 'panel';
  panel.innerHTML = '<h2>Cube-Derived HSV</h2>';

  const svg = createSvg(280, 280);
  const border = createSvgElement('polygon');
  border.setAttribute('points', '90,0 45,77.94 -45,77.94 -90,0 -45,-77.94 45,-77.94');
  border.setAttribute('fill', 'rgba(99, 102, 241, 0.08)');
  border.setAttribute('stroke', '#4f46e5');
  border.setAttribute('stroke-width', '2');

  const point = createSvgElement('circle');
  point.setAttribute('r', '5');
  point.setAttribute('fill', '#111827');

  svg.append(border, point);
  panel.append(svg);

  store.subscribe((state) => {
    const p = projectHsvToHex(state.hsv);
    point.setAttribute('cx', String(p.x * 90));
    point.setAttribute('cy', String(-p.y * 90));
  });

  return panel;
}
