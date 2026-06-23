const SVG_NS = 'http://www.w3.org/2000/svg';

/**
 * Create an SVG viewport centered around the origin.
 */
export function createSvg(width: number, height: number): SVGSVGElement {
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', `${-width / 2} ${-height / 2} ${width} ${height}`);
  svg.setAttribute('width', String(width));
  svg.setAttribute('height', String(height));
  return svg;
}

/**
 * Create a strongly typed SVG node.
 */
export function createSvgElement<T extends keyof SVGElementTagNameMap>(name: T): SVGElementTagNameMap[T] {
  return document.createElementNS(SVG_NS, name);
}
