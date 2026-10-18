// One numbered source for all design controls. Provisional palette v1.
export const PALETTE = Object.freeze([
  '#000000', '#808080', '#c0c0c0', '#ffffff',
  '#800000', '#ff0000', '#ff8000', '#ffff00',
  '#808000', '#008000', '#00ff00', '#008080',
  '#00ffff', '#000080', '#42a5f5', '#800080',
]);
export function tint(hex, brightness = 0) {
  const amount = Math.abs(brightness) / 100;
  return '#' + [1, 3, 5].map(i => {
    const value = parseInt(hex.slice(i, i + 2), 16);
    return Math.round(value + ((brightness >= 0 ? 255 : 0) - value) * amount).toString(16).padStart(2, '0');
  }).join('');
}
export function orientation(number) {
  // Unique light hue sequence, separate from the reusable design palette.
  return `hsl(${(number * 137.508) % 360} 80% 76%)`;
}
