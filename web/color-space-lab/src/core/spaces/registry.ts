import { hsvSpace } from './hsv-space';

export const colorSpaces = [
  hsvSpace,
  { key: 'HSL', label: 'HSL', disabled: true },
  { key: 'HSI', label: 'HSI', disabled: true },
  { key: 'HSY', label: 'HSY', disabled: true },
] as const;
