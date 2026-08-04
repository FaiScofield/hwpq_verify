export const hsvSpace = {
  key: 'HSV',
  label: 'HSV',
  projectionLabels: {
    hex: 'Cube-Derived HSV',
    circle: 'Normalized Polar HSV',
  },
  formulas: [
    'V = max(r, g, b)',
    'S = 0 if V = 0 else (max - min) / V',
    'Hex projection uses sector interpolation between six hexagon vertices',
    'Circle projection uses x = S cos(H), y = S sin(H)',
  ],
} as const;
