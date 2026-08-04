/**
 * HSV projection teaching — main 3D scene.
 *
 * Shows the tilted RGB cube, the V = v sub-cube (outer surface highlighted),
 * the three cutting planes, the horizontal chromaticity plane at z = 0 with a
 * hexagon/circle projection panel, the projection line, the 3D color marker
 * (labelled with RGB) and its 2D projected point (labelled with HSV), plus the
 * equal-S hexagon ring and the circle ring for trajectory comparison.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

import { hsvToRgb } from '../core/color-convert/rgb-hsv';
import type { Point3D } from '../state/types';
import type { TeachState, TeachStateStore } from './teach-state';
import {
  SQRT3,
  hexRing3D,
  hexVertices,
  hsvToPlane,
  hsvToWorld,
  overflowSegments,
  rgbToWorld,
} from './teach-math';

/**
 * Build the linear RGB -> world map (tilted cube) from the verified
 * rgbToWorld() math, so the cube geometry can never drift from the axes /
 * marker math. Columns are the world images of the R/G/B basis vectors.
 * NOTE: Matrix4.set() takes row-major arguments (n11 = row0 col0).
 */
function buildCubeMatrix(): THREE.Matrix4 {
  const r = rgbToWorld({ r: 1, g: 0, b: 0 });
  const g = rgbToWorld({ r: 0, g: 1, b: 0 });
  const b = rgbToWorld({ r: 0, g: 0, b: 1 });
  return new THREE.Matrix4().set(
    r.x, g.x, b.x, 0,
    r.y, g.y, b.y, 0,
    r.z, g.z, b.z, 0,
    0, 0, 0, 1,
  );
}

const CUBE_MATRIX = buildCubeMatrix();

/**
 * Vertical gap between the projection plane (z = 0) and the bottom of the
 * tilted cube, so the cube floats above the hexagon/circle panel and the
 * projection lines fall down onto it.
 */
const CUBE_Z_OFFSET = 0.6;

/** How much longer the R/G/B axes are drawn than the cube edge / hexagon radius. */
const AXIS_OVERLEN = 1.18;

const fmt = (n: number, digits = 2): string => n.toFixed(digits);

export class HsvProjectionScene {
  readonly element: HTMLDivElement;

  private readonly renderer: THREE.WebGLRenderer;
  private readonly labelRenderer: CSS2DRenderer;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly controls: OrbitControls;

  // Scene objects that need per-frame / per-state updates.
  private readonly marker3D: THREE.Mesh;
  private readonly marker2D: THREE.Mesh;
  private readonly label3D: CSS2DObject;
  private readonly label2D: CSS2DObject;
  private readonly projectionLine: THREE.Line;
  private readonly subCubeGroup: THREE.Group;
  private readonly cutPlanesGroup: THREE.Group;
  private readonly hexRing: THREE.LineLoop;
  private readonly hexFill: THREE.Mesh;
  private readonly circleFill: THREE.Mesh;
  private readonly overflowMeshes: THREE.Mesh[] = [];
  private readonly cubeWire: THREE.LineSegments;
  private readonly axisLine: THREE.Line;
  private readonly hexOutline: THREE.LineLoop;
  private readonly circleOutline: THREE.LineLoop;
  private readonly rgbAxesGroup: THREE.Group;
  private readonly rgbProjectionAxesGroup: THREE.Group;
  private readonly axisVMarker: THREE.Mesh;
  private readonly axisVLabel: CSS2DObject;
  private readonly cubeHexRing: THREE.LineSegments;
  private readonly hexTexture: THREE.CanvasTexture;

  // Cached last values so hue-only updates skip the expensive S/V work
  // (texture repaint, ring geometry rebuild, sub-cube scaling).
  private lastS = -1;
  private lastV = -1;
  private lastPaintedV = -1;

  constructor(store: TeachStateStore) {
    this.element = document.createElement('div');
    this.element.className = 'panel scene-host teach-scene';
    this.element.innerHTML = '<h2>HSV 投影教学</h2>';

    const canvas = document.createElement('canvas');
    this.element.append(canvas);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc);

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    this.camera.position.set(3.6, 2.4, 3.6);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);

    this.labelRenderer = new CSS2DRenderer();
    this.labelRenderer.domElement.style.position = 'absolute';
    this.labelRenderer.domElement.style.top = '0';
    this.labelRenderer.domElement.style.left = '0';
    this.labelRenderer.domElement.style.pointerEvents = 'none';
    this.element.append(this.labelRenderer.domElement);

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.target.set(0, 0, SQRT3 / 2 + CUBE_Z_OFFSET);

    // ---- Static helpers -------------------------------------------------
    const grid = new THREE.GridHelper(6, 24, 0x94a3b8, 0xe2e8f0);
    grid.rotation.x = Math.PI / 2;
    grid.position.z = -0.01;
    scene.add(grid);

    // Tilted RGB cube wireframe (0..1, 12 edges).
    const cubeBaseGeo = new THREE.BoxGeometry(1, 1, 1);
    cubeBaseGeo.translate(0.5, 0.5, 0.5);
    cubeBaseGeo.applyMatrix4(CUBE_MATRIX);
    this.cubeWire = new THREE.LineSegments(
      new THREE.EdgesGeometry(cubeBaseGeo),
      new THREE.LineBasicMaterial({ color: 0x475569, transparent: true, opacity: 0.6 }),
    );

    // Neutral axis (black -> white).
    this.axisLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, 0, SQRT3),
      ]),
      new THREE.LineBasicMaterial({ color: 0x1e293b }),
    );

    this.rgbAxesGroup = createRgbAxes();
    this.rgbProjectionAxesGroup = createRgbProjectionAxes();

    // V value marker on the neutral axis (moves with v).
    const axisV = createAxisVMarker();
    this.axisVMarker = axisV.marker;
    this.axisVLabel = axisV.label;

    // Projection panel at z = 0: hexagon + circle outlines, and two fills.
    this.hexOutline = makeLineLoop(hexOutlinePoints());
    this.circleOutline = makeLineLoop(circleOutlinePoints());

    // Hexagon panel filled with the full hue wheel at the current value.
    this.hexTexture = makeHexTexture();
    this.hexFill = new THREE.Mesh(
      hexGeometryWithUV(),
      new THREE.MeshBasicMaterial({
        map: this.hexTexture,
        transparent: true,
        opacity: 0.75,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );

    this.circleFill = new THREE.Mesh(
      new THREE.CircleGeometry(1, 96),
      new THREE.MeshBasicMaterial({
        color: 0xf59e0b,
        transparent: true,
        opacity: 0.1,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );

    // Overflow segments (circle outside hexagon) at z = 0.
    const overflowMaterial = new THREE.MeshBasicMaterial({
      color: 0xef4444,
      transparent: true,
      opacity: 0.28,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    for (const seg of overflowSegments()) {
      const shape = new THREE.Shape();
      shape.moveTo(seg[0].x, seg[0].y);
      for (let i = 1; i < seg.length; i++) {
        shape.lineTo(seg[i].x, seg[i].y);
      }
      const mesh = new THREE.Mesh(new THREE.ShapeGeometry(shape), overflowMaterial);
      this.overflowMeshes.push(mesh);
    }

    // ---- Sub-cube group (scaled by v) ------------------------------------
    this.subCubeGroup = new THREE.Group();
    const subCubeEdges = new THREE.LineSegments(
      new THREE.EdgesGeometry(cubeBaseGeo),
      new THREE.LineBasicMaterial({ color: 0x6366f1 }),
    );
    this.subCubeGroup.add(subCubeEdges);

    // Outer surface (r=1 / g=1 / b=1 faces of the unit cube), tinted.
    this.subCubeGroup.add(
      new THREE.Mesh(
        outerSurfaceGeometry(),
        new THREE.MeshBasicMaterial({
          color: 0xa5b4fc,
          transparent: true,
          opacity: 0.5,
          side: THREE.DoubleSide,
          depthWrite: false,
        }),
      ),
    );
    this.subCubeGroup.visible = false;

    // ---- Cutting planes (r=v / g=v / b=v), tinted per axis ---------------
    this.cutPlanesGroup = new THREE.Group();
    const planeColors = [0xf87171, 0x4ade80, 0x60a5fa]; // R / G / B
    const planeAxes: Array<'r' | 'g' | 'b'> = ['r', 'g', 'b'];
    planeAxes.forEach((axis, i) => {
      this.cutPlanesGroup.add(
        new THREE.Mesh(
          cutPlaneGeometry(axis),
          new THREE.MeshBasicMaterial({
            color: planeColors[i],
            transparent: true,
            opacity: 0.16,
            side: THREE.DoubleSide,
            depthWrite: false,
          }),
        ),
      );
    });
    this.cutPlanesGroup.visible = false;

    // ---- Projection line (dashed) ---------------------------------------
    this.projectionLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
      new THREE.LineDashedMaterial({
        color: 0x64748b,
        dashSize: 0.06,
        gapSize: 0.05,
        transparent: true,
        opacity: 0.8,
      }),
    );

    // ---- Markers + labels ------------------------------------------------
    this.marker3D = new THREE.Mesh(
      new THREE.SphereGeometry(0.06, 24, 24),
      new THREE.MeshBasicMaterial({ color: 0xdc2626 }),
    );
    this.marker2D = new THREE.Mesh(
      new THREE.SphereGeometry(0.05, 24, 24),
      new THREE.MeshBasicMaterial({ color: 0x0ea5e9 }),
    );

    this.label3D = createLabel('', 'teach-label teach-label-3d');
    this.label2D = createLabel('', 'teach-label teach-label-2d');
    this.marker3D.add(this.label3D);
    this.marker2D.add(this.label2D);
    this.label3D.position.set(0.12, 0.12, 0.08);
    this.label2D.position.set(0.12, 0.12, 0);

    // ---- Equal-S hexagon ring -------------------------------------------
    this.hexRing = makeLineLoop(
      hexRing3D(1, 1).map(toVec3),
      new THREE.LineBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.9 }),
    );

    // Dashed black hexagon on the projection plane: the projection of the
    // V=v sub-cube (radius v). Manual dash segments in solid black, rendered
    // after the (transparent) hue wheel so it is never washed out.
    this.cubeHexRing = new THREE.LineSegments(
      new THREE.BufferGeometry(),
      new THREE.LineBasicMaterial({ color: 0x000000, transparent: true }),
    );
    this.cubeHexRing.position.z = 0.002;
    this.cubeHexRing.renderOrder = 100;
    (this.cubeHexRing.material as THREE.LineBasicMaterial).depthTest = false;

    // ---- Compose scene ----------------------------------------------------
    // Everything that belongs to the cube world floats above the projection
    // plane (z = 0) inside cubeGroup; the panel, grid, 2D marker and the
    // in-plane projection helpers (RGB axis projections, cube hexagon) stay put.
    const cubeGroup = new THREE.Group();
    cubeGroup.position.z = CUBE_Z_OFFSET;
    cubeGroup.add(
      this.cubeWire,
      this.axisLine,
      this.rgbAxesGroup,
      this.axisVMarker,
      this.subCubeGroup,
      this.cutPlanesGroup,
      this.marker3D,
      this.hexRing,
    );

    scene.add(
      grid,
      cubeGroup,
      this.rgbProjectionAxesGroup,
      this.cubeHexRing,
      this.hexOutline,
      this.circleOutline,
      this.hexFill,
      this.circleFill,
      ...this.overflowMeshes,
      this.projectionLine,
      this.marker2D,
    );

    // ---- Animation loop ---------------------------------------------------
    const animate = (): void => {
      this.controls.update();
      this.renderer.render(scene, this.camera);
      this.labelRenderer.render(scene, this.camera);
      requestAnimationFrame(animate);
    };
    animate();

    // ---- Resize -----------------------------------------------------------
    const resize = (): void => {
      const width = this.element.clientWidth;
      const height = this.element.clientHeight || 480;
      this.renderer.setSize(width, height, false);
      this.labelRenderer.setSize(width, height);
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    };
    resize();
    new ResizeObserver(resize).observe(this.element);

    // ---- State subscription ----------------------------------------------
    store.subscribe((state) => this.apply(state));
  }

  /** Move the camera to look straight down the neutral axis. */
  lookAlongAxis(): void {
    this.controls.target.set(0, 0, SQRT3 / 2 + CUBE_Z_OFFSET);
    this.camera.position.set(0.001, 0.001, 9);
    this.camera.lookAt(0, 0, SQRT3 / 2 + CUBE_Z_OFFSET);
  }

  /** Apply the latest teaching state to the scene. */
  private apply(state: TeachState): void {
    const hsv = { h: state.h, s: state.s, v: state.v };
    const rgb = hsvToRgb(hsv);
    const world = hsvToWorld(hsv);
    const plane = hsvToPlane(hsv);

    // Markers (both 3D and 2D points carry the current color).
    this.marker3D.position.set(world.x, world.y, world.z);
    (this.marker3D.material as THREE.MeshBasicMaterial).color.setRGB(rgb.r, rgb.g, rgb.b);
    this.marker2D.position.set(plane.x, plane.y, 0);
    (this.marker2D.material as THREE.MeshBasicMaterial).color.setRGB(rgb.r, rgb.g, rgb.b);

    // Labels: 3D point shows RGB, 2D point shows HSV.
    const r255 = Math.round(rgb.r * 255);
    const g255 = Math.round(rgb.g * 255);
    const b255 = Math.round(rgb.b * 255);
    this.label3D.element.textContent = `RGB(${r255},${g255},${b255})`;
    this.label2D.element.textContent = `H:${Math.round(hsv.h)}° S:${fmt(hsv.s, 3)} V:${fmt(hsv.v, 3)}`;

    // Projection line (depends on the 3D marker position).
    const linePos = this.projectionLine.geometry.getAttribute('position') as THREE.BufferAttribute;
    linePos.setXYZ(0, world.x, world.y, world.z + CUBE_Z_OFFSET);
    linePos.setXYZ(1, world.x, world.y, 0);
    linePos.needsUpdate = true;
    this.projectionLine.computeLineDistances();

    // ---- S/V dependent updates (skipped when only hue changes) ----------
    if (state.s !== this.lastS || state.v !== this.lastV) {
      // V value marker on the neutral axis (gray point (v,v,v) -> z = √3·v).
      this.axisVMarker.position.set(0, 0, SQRT3 * state.v);
      this.axisVLabel.element.textContent = `V=${fmt(state.v, 2)}`;

      // Sub-cube & cutting planes scale with v.
      this.subCubeGroup.scale.setScalar(state.v);
      this.cutPlanesGroup.scale.setScalar(state.v);

      // Equal-S ring + dashed cube-projection hexagon on the plane. The dashed
      // hexagon follows the equal-S ring radius (s·v), so it shrinks/grows with S.
      setLinePoints(this.hexRing, hexRing3D(state.s, state.v).map(toVec3));
      setLinePoints(this.cubeHexRing, dashedHexagonPoints(state.s * state.v));

      this.lastS = state.s;
      this.lastV = state.v;
    }

    // Hexagon panel shows the full hue wheel; brightness follows the current v.
    if (state.v !== this.lastPaintedV) {
      paintHexTexture(this.hexTexture, state.v);
      this.lastPaintedV = state.v;
    }

    // Visibility.
    this.cubeWire.visible = state.showCube;
    this.axisLine.visible = state.showAxes;
    this.rgbAxesGroup.visible = state.showAxes;
    this.rgbProjectionAxesGroup.visible = state.showAxes;
    this.axisVMarker.visible = state.showAxes;
    this.axisVLabel.visible = state.showAxes && state.showLabels;
    this.subCubeGroup.visible = state.showSubCube;
    this.cutPlanesGroup.visible = state.showCutPlanes;
    this.projectionLine.visible = state.showProjectionLine;
    this.hexRing.visible = state.showHexRing;
    this.cubeHexRing.visible = state.showCubeHex;
    this.hexOutline.visible = state.showProjectionPlane;
    this.circleOutline.visible = state.showProjectionPlane;
    this.hexFill.visible = state.showProjectionPlane && state.projection === 'hex';
    this.circleFill.visible = state.showProjectionPlane && state.projection === 'circle';
    this.overflowMeshes.forEach((m) => {
      m.visible = state.showOverflow && state.projection === 'circle';
    });
    this.marker3D.visible = true;
    this.marker2D.visible = state.showProjectionPlane || state.showProjectionLine;
    this.label3D.visible = state.showLabels;
    this.label2D.visible = state.showLabels && this.marker2D.visible;
  }
}

// ---- Small helpers ---------------------------------------------------------

function toVec3(p: Point3D): THREE.Vector3 {
  return new THREE.Vector3(p.x, p.y, p.z);
}

function makeLineLoop(points: THREE.Vector3[], material = new THREE.LineBasicMaterial({ color: 0x94a3b8 })): THREE.LineLoop {
  const geo = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.LineLoop(geo, material);
}

function setLinePoints(line: THREE.LineLoop | THREE.LineSegments, points: THREE.Vector3[]): void {
  const geo = line.geometry;
  const pos = geo.getAttribute('position') as THREE.BufferAttribute | undefined;
  // Reuse the geometry when the vertex count is unchanged (just update the
  // buffer); rebuild only when the size actually changes.
  if (pos && pos.count === points.length && !geo.index) {
    for (let i = 0; i < points.length; i++) {
      pos.setXYZ(i, points[i].x, points[i].y, points[i].z);
    }
    pos.needsUpdate = true;
  } else {
    line.geometry.dispose();
    line.geometry = new THREE.BufferGeometry().setFromPoints(points);
  }
}

/**
 * Manual dash segments for a hexagon outline: each edge is split into several
 * short opaque segments separated by gaps, so the dashed look works even with
 * 1px lines and over textured/transparent fills.
 */
function dashedHexagonPoints(radius: number, dashesPerEdge = 6): THREE.Vector3[] {
  const verts = hexVertices(radius);
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i < 6; i++) {
    const a = verts[i];
    const b = verts[(i + 1) % 6];
    for (let j = 0; j < dashesPerEdge; j++) {
      const t0 = j / dashesPerEdge;
      const t1 = (j + 0.55) / dashesPerEdge;
      pts.push(new THREE.Vector3(a.x + (b.x - a.x) * t0, a.y + (b.y - a.y) * t0, 0));
      pts.push(new THREE.Vector3(a.x + (b.x - a.x) * t1, a.y + (b.y - a.y) * t1, 0));
    }
  }
  return pts;
}

function createLabel(text: string, className: string): CSS2DObject {
  const div = document.createElement('div');
  div.className = className;
  div.textContent = text;
  return new CSS2DObject(div);
}

/**
 * RGB cube axes: three arrows from the black origin along the red, green and
 * blue edges of the tilted cube (derived from rgbToWorld so they always match
 * the cube geometry). They are 120° apart and never overlap the neutral axis.
 */
function createRgbAxes(): THREE.Group {
  const group = new THREE.Group();
  const axesData = [
    { p: rgbToWorld({ r: 1, g: 0, b: 0 }), color: 0xef4444 }, // R
    { p: rgbToWorld({ r: 0, g: 1, b: 0 }), color: 0x22c55e }, // G
    { p: rgbToWorld({ r: 0, g: 0, b: 1 }), color: 0x3b82f6 }, // B
  ];
  for (const { p, color } of axesData) {
    const dir = new THREE.Vector3(p.x, p.y, p.z);
    // Slightly longer than the cube edge so the tip sticks out a bit.
    const length = dir.length() * AXIS_OVERLEN;
    const arrow = new THREE.ArrowHelper(
      dir.clone().normalize(),
      new THREE.Vector3(0, 0, 0),
      length,
      color,
      0.12,
      0.08,
    );
    group.add(arrow);
  }
  return group;
}

function hexOutlinePoints(): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i < 6; i++) {
    const a = (i * 60 * Math.PI) / 180;
    pts.push(new THREE.Vector3(Math.cos(a), Math.sin(a), 0));
  }
  return pts;
}

/** Projection-plane z in cubeGroup local coordinates. */
/**
 * Projections of the R/G/B cube axes onto the plane: the whole axis (from the
 * black origin to the tip) maps to a radial line segment from the plane centre
 * to the corresponding hexagon vertex. Drawn as dashed arrows 120° apart,
 * slightly longer than the hexagon so they stick out a little.
 */
function createRgbProjectionAxes(): THREE.Group {
  const group = new THREE.Group();
  const colors = [0xef4444, 0x22c55e, 0x3b82f6];
  const dirs = [
    new THREE.Vector3(1, 0, 0),
    new THREE.Vector3(-0.5, SQRT3 / 2, 0),
    new THREE.Vector3(-0.5, -SQRT3 / 2, 0),
  ];
  dirs.forEach((dir, i) => {
    const end = dir.clone().multiplyScalar(AXIS_OVERLEN);
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        end,
      ]),
      new THREE.LineDashedMaterial({
        color: colors[i],
        dashSize: 0.05,
        gapSize: 0.04,
        transparent: true,
      }),
    );
    line.computeLineDistances();
    line.renderOrder = 100;
    (line.material as THREE.LineDashedMaterial).depthTest = false;
    group.add(line);

    // Arrow head pointing along the segment, near the extended tip.
    const headMaterial = new THREE.MeshBasicMaterial({
      color: colors[i],
      transparent: true,
    });
    headMaterial.depthTest = false;
    const head = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.16, 12), headMaterial);
    head.renderOrder = 100;
    const dirN = dir.clone().normalize();
    head.position.copy(dirN.clone().multiplyScalar(0.9 * AXIS_OVERLEN));
    head.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dirN);
    group.add(head);
  });
  return group;
}

/**
 * V value marker on the neutral axis: a small sphere plus a CSS label. The
 * apply() step places it at z = √3·v, i.e. the grey point (v,v,v) mapped to
 * the tilted-cube world.
 */
function createAxisVMarker(): { marker: THREE.Mesh; label: CSS2DObject } {
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.035, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0x0f172a }),
  );
  const label = createLabel('V=0.00', 'teach-label teach-label-v');
  label.position.set(0.12, 0.12, 0);
  marker.add(label);
  return { marker, label };
}

function circleOutlinePoints(): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i <= 120; i++) {
    const a = (i / 120) * Math.PI * 2;
    pts.push(new THREE.Vector3(Math.cos(a), Math.sin(a), 0));
  }
  return pts;
}

/**
 * Hexagon geometry (center + 6 vertices) with explicit UVs so the gradient
 * texture maps center -> (0.5, 0.5) and vertices -> the canvas edge.
 */
function hexGeometryWithUV(): THREE.BufferGeometry {
  const verts: number[] = [0, 0, 0];
  const uvs: number[] = [0.5, 0.5];
  for (let i = 0; i < 6; i++) {
    const a = (i * 60 * Math.PI) / 180;
    verts.push(Math.cos(a), Math.sin(a), 0);
    uvs.push(0.5 + 0.5 * Math.cos(a), 0.5 + 0.5 * Math.sin(a));
  }
  const indices: number[] = [];
  for (let i = 0; i < 6; i++) {
    indices.push(0, i + 1, ((i + 1) % 6) + 1);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setIndex(indices);
  return geo;
}

/**
 * The hue wheel depends only on (hue, saturation), not on v: v scales the
 * whole wheel's brightness. So we paint a V=1 base wheel once, then re-use it
 * with a CSS brightness() filter when v changes (much cheaper than repainting
 * every pixel).
 */
const WHEEL_SIZE = 128;

let wheelV1Canvas: HTMLCanvasElement | null = null;

function getWheelV1Canvas(): HTMLCanvasElement {
  if (!wheelV1Canvas) {
    wheelV1Canvas = document.createElement('canvas');
    wheelV1Canvas.width = WHEEL_SIZE;
    wheelV1Canvas.height = WHEEL_SIZE;
    const ctx = wheelV1Canvas.getContext('2d');
    if (!ctx) {
      return wheelV1Canvas;
    }
    const img = ctx.createImageData(WHEEL_SIZE, WHEEL_SIZE);
    const radius = WHEEL_SIZE / 2;
    const cx = radius;
    const cy = radius;
    const data = img.data;
    for (let y = 0; y < WHEEL_SIZE; y++) {
      for (let x = 0; x < WHEEL_SIZE; x++) {
        const dx = x - cx;
        const dy = y - cy;
        const s = Math.min(1, Math.hypot(dx, dy) / radius);
        // Hue follows the angle; -dy mirrors the canvas y-axis so the wheel
        // matches the hexagon orientation (red right, yellow top-right, ...).
        const h = (Math.atan2(-dy, dx) * 180) / Math.PI;
        const hue = (h + 360) % 360;
        const c = hsvToRgb({ h: hue, s, v: 1 });
        const i = (y * WHEEL_SIZE + x) * 4;
        data[i] = Math.round(c.r * 255);
        data[i + 1] = Math.round(c.g * 255);
        data[i + 2] = Math.round(c.b * 255);
        data[i + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
  }
  return wheelV1Canvas;
}

function makeHexTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = WHEEL_SIZE;
  canvas.height = WHEEL_SIZE;
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const ctx = canvas.getContext('2d');
  ctx?.drawImage(getWheelV1Canvas(), 0, 0);
  return tex;
}

function paintHexTexture(tex: THREE.CanvasTexture, v: number): void {
  const canvas = tex.image as HTMLCanvasElement;
  const size = canvas.width;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return;
  }
  ctx.clearRect(0, 0, size, size);
  if (v < 1) {
    ctx.filter = `brightness(${(v * 100).toFixed(2)}%)`;
  }
  ctx.drawImage(getWheelV1Canvas(), 0, 0);
  ctx.filter = 'none';
  tex.needsUpdate = true;
}

/**
 * Outer surface of the unit cube: the three faces r=1, g=1, b=1 (triangles in
 * RGB space), transformed to world coordinates.
 */
function outerSurfaceGeometry(): THREE.BufferGeometry {
  const verts = [
    // face r=1
    1, 0, 0, 1, 1, 0, 1, 0, 1,
    1, 1, 0, 1, 1, 1, 1, 0, 1,
    // face g=1
    0, 1, 0, 1, 1, 0, 0, 1, 1,
    1, 1, 0, 1, 1, 1, 0, 1, 1,
    // face b=1
    0, 0, 1, 1, 0, 1, 0, 1, 1,
    1, 0, 1, 1, 1, 1, 0, 1, 1,
  ];
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.applyMatrix4(CUBE_MATRIX);
  return geo;
}

/**
 * Cutting plane at r=1 / g=1 / b=1 (unit version, spans 0..1.5 on the other
 * two axes), transformed to world coordinates; the group is scaled by v.
 */
function cutPlaneGeometry(axis: 'r' | 'g' | 'b'): THREE.BufferGeometry {
  const h = 1.5;
  let verts: number[];
  if (axis === 'r') {
    verts = [
      1, 0, 0, 1, h, 0, 1, 0, h,
      1, h, 0, 1, h, h, 1, 0, h,
    ];
  } else if (axis === 'g') {
    verts = [
      0, 1, 0, h, 1, 0, 0, 1, h,
      h, 1, 0, h, 1, h, 0, 1, h,
    ];
  } else {
    verts = [
      0, 0, 1, h, 0, 1, 0, h, 1,
      h, 0, 1, h, h, 1, 0, h, 1,
    ];
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.applyMatrix4(CUBE_MATRIX);
  return geo;
}
