/**
 * Build a shared two-column section row.
 */
export function createSectionRow(...children: HTMLElement[]): HTMLDivElement {
  const row = document.createElement('div');
  row.className = 'two-up';
  row.append(...children);
  return row;
}
