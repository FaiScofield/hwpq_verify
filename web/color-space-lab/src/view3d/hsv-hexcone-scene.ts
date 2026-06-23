import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

import type { ColorStateStore } from '../state/color-state-store';
import { createAxes, createMarker, hexconePointFromHsv } from './helpers';

/**
 * Render the standard HSV hexcone and its active marker.
 */
export class HsvHexconeScene {
  readonly element: HTMLDivElement;

  constructor(store: ColorStateStore) {
    this.element = document.createElement('div');
    this.element.className = 'panel scene-host';
    this.element.innerHTML = '<h2>HSV Hexcone</h2>';

    const canvas = document.createElement('canvas');
    this.element.append(canvas);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(2.2, 1.6, 2.2);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(320, 320);

    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;

    const marker = createMarker('#dc2626');
    const axes = createAxes(1.2);
    const geometry = new THREE.CylinderGeometry(0, 1, 1, 6, 1, true);
    geometry.rotateX(Math.PI / 2);
    geometry.translate(0, 0, 0.5);

    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshBasicMaterial({
        color: 0xa78bfa,
        wireframe: true,
        transparent: true,
        opacity: 0.45,
      }),
    );

    scene.add(mesh, marker, axes);

    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();

    store.subscribe((state) => {
      const p = hexconePointFromHsv(state.hsv);
      marker.position.set(p.x, p.y, p.z);
      axes.visible = state.showAxes;
    });
  }
}
