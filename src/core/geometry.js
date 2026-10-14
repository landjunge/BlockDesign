export const center = b => ({ x: b.x + b.width / 2, y: b.y + b.height / 2 });
export const clamp = (v, low, high) => Math.max(low, Math.min(high, v));
export function nearest(state, point) {
  return state.boxes.filter(b => b.layer === state.activeLayer).sort((a, b) => {
    const ca = center(a), cb = center(b);
    return (ca.x - point.x) ** 2 + (ca.y - point.y) ** 2 - (cb.x - point.x) ** 2 - (cb.y - point.y) ** 2 || a.number - b.number;
  })[0] || null;
}
export function descendants(boxes, id) {
  const result = [];
  for (const b of boxes.filter(b => b.parentId === id)) result.push(b, ...descendants(boxes, b.id));
  return result;
}
export function footprint(boxes, box) {
  const family = [box, ...descendants(boxes, box.id)];
  return { left: Math.min(...family.map(b => b.x)), top: Math.min(...family.map(b => b.y)),
    right: Math.max(...family.map(b => b.x + b.width)), bottom: Math.max(...family.map(b => b.y + b.height)) };
}
export function snap(value, grid) {
  if (!grid.enabled) return value;
  const next = Math.round(value / grid.spacing) * grid.spacing;
  return Math.abs(next - value) <= grid.magnet + 1e-9 ? next : value;
}
export function move(boxes, box, dx, dy, document, grid) {
  const bounds = footprint(boxes, box);
  dx = snap(box.x + dx, grid) - box.x; dy = snap(box.y + dy, grid) - box.y;
  dx = clamp(dx, -bounds.left, document.width - bounds.right);
  dy = clamp(dy, -bounds.top, document.height - bounds.bottom);
  for (const b of [box, ...descendants(boxes, box.id)]) { b.x += dx; b.y += dy; }
}
export function resize(box, axis, delta, document, grid) {
  if (axis === 'width') box.width = clamp(snap(box.x + box.width + delta, grid) - box.x, 4, document.width - box.x);
  if (axis === 'height') box.height = clamp(snap(box.y + box.height + delta, grid) - box.y, 4, document.height - box.y);
}
export function scale(box, factor, document) {
  const low = Math.max(4 / box.width, 4 / box.height);
  const high = Math.min((document.width - box.x) / box.width, (document.height - box.y) / box.height);
  const f = clamp(factor, low, high);
  box.width *= f; box.height *= f;
}
