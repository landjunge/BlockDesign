import { PALETTE, orientation } from './palette.js';

export const VERSION = 1;
export const TYPES = ['Box', 'Button', 'Textfeld', 'Checkbox', 'Dropdown', 'Modul', 'Karte', 'Leiste', 'Header', 'Footer', 'Sidebar'];
export const PATCH_KEYS = ['x', 'y', 'width', 'height', 'radius', 'color', 'paletteIndex', 'brightness', 'borderColor', 'borderWidth', 'font', 'label', 'type'];
export const FONT_FAMILIES = ['system-ui', 'sans-serif', 'serif', 'monospace'];
export const clone = value => structuredClone(value);
export const finite = value => typeof value === 'number' && Number.isFinite(value);
export const hex = value => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);
export function initialState() {
  return {
    version: VERSION, revision: 0, document: { width: 1000, height: 640 },
    boxes: [], nextNumber: 1, creationCounts: [0, 0, 0], activeLayer: 1, selection: [],
    grid: { spacing: 20, magnet: 2, enabled: true },
    myspace: [], tasks: [],
    ui: { language: 'de', view: 'structure', zoom: .75, grabbed: null, preview: null,
      monitor: { x: 16, y: 16, last: null }, notice: '', noticeArgs: {}, error: false },
  };
}
export function newBox(number, layer, x, y, width = 50, height = 50) {
  return { id: crypto.randomUUID(), number, orientation: orientation(number), layer, type: 'Box',
    x, y, width, height, radius: 0, color: PALETTE[3], paletteIndex: 4, brightness: 0,
    borderColor: '#808080', borderWidth: 1, font: { family: 'system-ui', size: 14, color: '#000000' },
    label: '', parentId: null };
}
export function primary(state) { return state.boxes.find(b => b.id === state.selection[0]) || null; }
export function editable(state, id) {
  const box = state.boxes.find(b => b.id === id);
  if (!box || box.layer !== state.activeLayer) throw new Error('layerLocked');
  return box;
}
export function validatePatch(changes) {
  if (!changes || typeof changes !== 'object' || Array.isArray(changes) || !Object.keys(changes).length ||
    Object.keys(changes).some(k => !PATCH_KEYS.includes(k))) throw new Error('invalidAttributes');
  for (const [k, v] of Object.entries(changes)) {
    if (['x', 'y', 'width', 'height', 'radius', 'brightness', 'borderWidth'].includes(k) && !finite(v)) throw new Error('invalidValues');
    if (['color', 'borderColor'].includes(k) && !hex(v)) throw new Error('invalidColor');
    if (k === 'paletteIndex' && v !== null && (!Number.isInteger(v) || v < 1 || v > 16)) throw new Error('invalidColor');
    if (k === 'type' && (typeof v !== 'string' || !v.trim() || v.length > 80)) throw new Error('invalidType');
    if (k === 'label' && (typeof v !== 'string' || v.length > 4000)) throw new Error('invalidValues');
    if (k === 'font' && (!v || typeof v !== 'object' || Array.isArray(v) || !Object.keys(v).length ||
      Object.keys(v).some(k => !['family', 'size', 'color'].includes(k)) ||
      ('family' in v && !FONT_FAMILIES.includes(v.family)) || ('color' in v && !hex(v.color)) ||
      ('size' in v && (!finite(v.size) || v.size < 4 || v.size > 200)))) throw new Error('invalidValues');
  }
}
export function validateState(state) {
  if (state.version !== VERSION || !Number.isInteger(state.revision) || state.revision < 0 ||
    ![1, 2, 3].includes(state.activeLayer) || !finite(state.document.width) || !finite(state.document.height) ||
    state.document.width < 50 || state.document.height < 50) throw new Error('invalidDocument');
  const ids = new Set(), numbers = new Set();
  for (const b of state.boxes) {
    if (typeof b.id !== 'string' || !b.id || ids.has(b.id) || !Number.isInteger(b.number) || b.number < 1 || numbers.has(b.number) ||
      ![1, 2, 3].includes(b.layer) || b.orientation !== orientation(b.number)) throw new Error('invalidIdentity');
    ids.add(b.id); numbers.add(b.number);
    validatePatch(Object.fromEntries(PATCH_KEYS.map(k => [k, b[k]])));
    if (Object.keys(b.font).sort().join(',') !== 'color,family,size') throw new Error('invalidValues');
    if (b.x < 0 || b.y < 0 || b.width < 4 || b.height < 4 || b.x + b.width > state.document.width + 1e-8 ||
      b.y + b.height > state.document.height + 1e-8 || b.radius < 0 || b.radius > 1000 || b.brightness < -100 ||
      b.brightness > 100 || b.borderWidth < 0 || b.borderWidth > 20 ||
      (b.paletteIndex !== null && b.color.toLowerCase() !== PALETTE[b.paletteIndex - 1])) throw new Error('documentBounds');
    const visited = new Set([b.id]); let current = b;
    while (current.parentId !== null) {
      const parent = state.boxes.find(item => item.id === current.parentId);
      if (!parent || parent.type !== 'Modul' || parent.layer !== b.layer || visited.has(parent.id)) throw new Error('invalidParent');
      visited.add(parent.id); current = parent;
    }
  }
  if (!Number.isInteger(state.nextNumber) || state.nextNumber <= Math.max(0, ...numbers) ||
    new Set(state.selection).size !== state.selection.length || state.selection.some(id => !ids.has(id) || editable(state, id).layer !== state.activeLayer)) throw new Error('invalidSelection');
  if (!finite(state.grid.spacing) || state.grid.spacing < .25 || state.grid.spacing > 1000 || !finite(state.grid.magnet) ||
    state.grid.magnet < 0 || state.grid.magnet > state.grid.spacing / 2 || typeof state.grid.enabled !== 'boolean') throw new Error('invalidGrid');
  return state;
}
