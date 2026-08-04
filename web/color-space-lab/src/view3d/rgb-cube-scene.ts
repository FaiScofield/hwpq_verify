import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

import type { ColorStateStore } from '../state/color-state-store';
import { createAxes, createMarker, cubePointFromRgb255 } from './helpers';

/**
 * Render the RGB cube and the active RGB marker.
 */
export class RgbCubeScene {
  readonly element: HTMLDivElement;

  private readonly renderer: THREE.WebGLRenderer;
  private readonly cubeMaterial = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.2,
  });
  private readonly marker = createMarker('#111827');
  private readonly axes = createAxes(0.8);

  constructor(store: ColorStateStore) {
    this.element = document.createElement('div');
    this.element.className = 'panel scene-host';
    this.element.innerHTML = '<h2>RGB Cube</h2>';

    const canvas = document.createElement('canvas');
    this.element.append(canvas);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(1.8, 1.8, 1.8);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(320, 320);

    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;

    const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), this.cubeMaterial);
    scene.add(cube, this.marker, this.axes);

    const animate = () => {
      controls.update();
      this.renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();

    store.subscribe((state) => {
      const p = cubePointFromRgb255(state.rgb255);
      this.marker.position.set(p.x, p.y, p.z);
      this.cubeMaterial.opacity = state.cubeOpacity;
      this.axes.visible = state.showAxes;
    });
  }
}
