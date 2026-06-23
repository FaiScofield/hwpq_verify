import { createSectionRow } from './layout';
import { ColorStateStore } from '../state/color-state-store';
import { createControlPanel } from '../ui/control-panel';
import { createFormulaPanel } from '../ui/formula-panel';
import { createValueInputs } from '../ui/value-inputs';
import { createHsvCircleProjection } from '../view2d/hsv-circle-projection';
import { createHsvHexProjection } from '../view2d/hsv-hex-projection';
import { HsvHexconeScene } from '../view3d/hsv-hexcone-scene';
import { RgbCubeScene } from '../view3d/rgb-cube-scene';

/**
 * Compose the full HSV visualization workspace.
 */
export function createAppShell(): HTMLElement {
  const store = new ColorStateStore();
  const page = document.createElement('main');
  page.className = 'page';

  const sceneRow = createSectionRow(new RgbCubeScene(store).element, new HsvHexconeScene(store).element);
  const controlRow = createSectionRow(createControlPanel(store), createValueInputs(store));
  const projectionRow = createSectionRow(createHsvHexProjection(store), createHsvCircleProjection(store));

  page.append(sceneRow, controlRow, projectionRow, createFormulaPanel(store));
  return page;
}
