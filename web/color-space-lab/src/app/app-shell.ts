import { createSectionRow } from './layout';
import { ColorStateStore } from '../state/color-state-store';
import { createControlPanel } from '../ui/control-panel';
import { createFormulaPanel } from '../ui/formula-panel';
import { createValueInputs } from '../ui/value-inputs';
import { createHsvCircleProjection } from '../view2d/hsv-circle-projection';
import { createHsvHexProjection } from '../view2d/hsv-hex-projection';
import { HsvHexconeScene } from '../view3d/hsv-hexcone-scene';
import { RgbCubeScene } from '../view3d/rgb-cube-scene';
import { HsvProjectionScene } from '../hsv-demo/hsv-projection-scene';
import { createTeachPanel } from '../hsv-demo/teach-panel';
import { TeachStateStore } from '../hsv-demo/teach-state';

/**
 * Compose the app shell: a main "projection teaching" tab and a secondary
 * "classic views" tab that keeps the original panels.
 */
export function createAppShell(): HTMLElement {
  const page = document.createElement('main');
  page.className = 'page';

  // ---- Projection teaching tab (main) ----------------------------------
  const teachStore = new TeachStateStore();
  const teachScene = new HsvProjectionScene(teachStore);
  const teachPanel = createTeachPanel(teachStore, teachScene);

  const teachView = document.createElement('div');
  teachView.className = 'teach-view';
  teachView.append(teachScene.element, teachPanel);

  // ---- Classic views tab (original panels, unchanged logic) -------------
  const classicStore = new ColorStateStore();
  const classicView = document.createElement('div');
  classicView.className = 'classic-view';
  classicView.append(
    createSectionRow(new RgbCubeScene(classicStore).element, new HsvHexconeScene(classicStore).element),
    createSectionRow(createControlPanel(classicStore), createValueInputs(classicStore)),
    createSectionRow(createHsvHexProjection(classicStore), createHsvCircleProjection(classicStore)),
    createFormulaPanel(classicStore),
  );

  // ---- Header + tabs ------------------------------------------------------
  const header = document.createElement('header');
  header.className = 'app-header';
  header.innerHTML = '<h1>HSV 色彩投影实验室</h1>';

  const tabs = document.createElement('nav');
  tabs.className = 'tabs';
  const tabTeach = document.createElement('button');
  tabTeach.type = 'button';
  tabTeach.className = 'tab active';
  tabTeach.textContent = '投影教学';
  const tabClassic = document.createElement('button');
  tabClassic.type = 'button';
  tabClassic.className = 'tab';
  tabClassic.textContent = '经典视图';

  const switchTo = (view: HTMLElement, btn: HTMLButtonElement): void => {
    teachView.hidden = view !== teachView;
    classicView.hidden = view !== classicView;
    tabTeach.classList.toggle('active', btn === tabTeach);
    tabClassic.classList.toggle('active', btn === tabClassic);
  };
  tabTeach.addEventListener('click', () => switchTo(teachView, tabTeach));
  tabClassic.addEventListener('click', () => switchTo(classicView, tabClassic));
  tabs.append(tabTeach, tabClassic);

  classicView.hidden = true;

  page.append(header, tabs, teachView, classicView);
  return page;
}

