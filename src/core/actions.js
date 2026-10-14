import { clone, editable, primary, newBox, validatePatch } from './model.js';
import { PALETTE } from './palette.js';
import { descendants, move, resize, scale } from './geometry.js';

const touch = s => { s.revision++; };
function patch(s, id, changes) {
  validatePatch(changes);
  const b = editable(s, id);
  if (changes.type && changes.type !== 'Modul' && descendants(s.boxes, id).length) throw new Error('parentHasChildren');
  // A module's position is a family translation, including nested children.
  if ('x' in changes || 'y' in changes) {
    const dx = (changes.x ?? b.x) - b.x, dy = (changes.y ?? b.y) - b.y;
    for (const child of descendants(s.boxes, id)) { child.x += dx; child.y += dy; }
  }
  const font = changes.font ? { ...b.font, ...changes.font } : b.font;
  Object.assign(b, clone(changes)); b.font = font;
  if ('paletteIndex' in changes && changes.paletteIndex !== null) b.color = PALETTE[changes.paletteIndex - 1];
  else if ('color' in changes) { b.color = changes.color.toLowerCase(); b.paletteIndex = PALETTE.indexOf(b.color) + 1 || null; }
  // Module background decisions apply to contained presentation elements.
  // Identity, text and geometry are never inherited by this rule.
  if (b.type === 'Modul') for (const child of descendants(s.boxes, id)) {
    if ('color' in changes || 'paletteIndex' in changes) { child.color = b.color; child.paletteIndex = b.paletteIndex; }
    if ('brightness' in changes) child.brightness = b.brightness;
  }
}
export function applyOperation(s, a) {
  if (a.type === 'patch') { patch(s, a.box_id, a.changes); }
  else if (a.type === 'scale') {
    if (typeof a.factor !== 'number' || !Number.isFinite(a.factor) || a.factor <= 0 || a.factor > 10) throw new Error('invalidValues');
    scale(editable(s, a.box_id), a.factor, s.document);
  } else if (a.type === 'grid') {
    if (Object.keys(a).some(k => !['type', 'spacing', 'magnet'].includes(k))) throw new Error('invalidAttributes');
    if (typeof a.spacing !== 'number' || !Number.isFinite(a.spacing) || a.spacing <= 0) throw new Error('invalidGrid');
    s.grid.spacing = a.spacing; s.grid.magnet = a.magnet ?? a.spacing / 10;
  } else throw new Error('invalidAction');
}
export function reduce(state, action) {
  if (!action || action.version !== 1) throw new Error('invalidAction');
  const s = clone(state), a = action;
  switch (a.type) {
    case 'create': {
      const i = s.activeLayer - 1, offset = s.creationCounts[i] * 5;
      const x = (s.document.width - 50) / 2 + offset, y = (s.document.height - 50) / 2 + offset;
      if (x + 50 > s.document.width || y + 50 > s.document.height) throw new Error('creationFull');
      const b = newBox(s.nextNumber++, s.activeLayer, x, y);
      s.boxes.push(b); s.creationCounts[i]++; s.selection = [b.id]; s.ui.grabbed = null; touch(s); break;
    }
    case 'layer':
      if (![1, 2, 3].includes(a.layer)) throw new Error('invalidAction');
      s.activeLayer = a.layer; s.selection = []; s.ui.grabbed = null; s.ui.preview = null; touch(s); break;
    case 'select':
      if (a.id === null) s.selection = [];
      else {
        editable(s, a.id);
        if (a.extend) s.selection = s.selection.includes(a.id) ? s.selection.filter(id => id !== a.id) : [...s.selection, a.id];
        else s.selection = [a.id];
      }
      s.ui.grabbed = null; s.ui.preview = null; touch(s); break;
    case 'grab':
      editable(s, a.id);
      if (!s.selection.includes(a.id)) s.selection = [a.id];
      s.ui.grabbed = a.id; touch(s); break;
    case 'drop': s.ui.grabbed = null; touch(s); break;
    case 'move':
      if (![a.dx, a.dy].every(v => typeof v === 'number' && Number.isFinite(v))) throw new Error('invalidValues');
      move(s.boxes, editable(s, a.id), a.dx, a.dy, s.document, s.grid); touch(s); break;
    case 'resize':
      if (!['width', 'height'].includes(a.axis) || typeof a.delta !== 'number' || !Number.isFinite(a.delta)) throw new Error('invalidValues');
      resize(editable(s, a.id), a.axis, a.delta, s.document, s.grid); touch(s); break;
    case 'scale': applyOperation(s, { type: 'scale', box_id: a.id, factor: a.factor }); touch(s); break;
    case 'patch': patch(s, a.id, a.changes); touch(s); break;
    case 'transfer': {
      const p = primary(s); if (!p || s.selection.length < 2) throw new Error('needMultiple');
      for (const id of s.selection.slice(1)) {
        const b = editable(s, id);
        const changes = Object.fromEntries(['width', 'height', 'radius', 'color', 'paletteIndex', 'brightness', 'borderColor', 'borderWidth'].map(k => [k, p[k]]));
        if (b.type !== 'Checkbox' && p.type !== 'Checkbox') { changes.font = p.font; changes.label = p.label; }
        patch(s, id, changes);
      }
      touch(s); break;
    }
    case 'parent': {
      const b = editable(s, a.id);
      if (a.parentId !== null) {
        const p = editable(s, a.parentId);
        if (p.type !== 'Modul' || p.id === b.id || descendants(s.boxes, b.id).some(c => c.id === p.id)) throw new Error('invalidParent');
        if (b.x < p.x || b.y < p.y || b.x + b.width > p.x + p.width || b.y + b.height > p.y + p.height) throw new Error('childOutside');
      }
      b.parentId = a.parentId; touch(s); break;
    }
    case 'group': {
      if (s.selection.length < 2) throw new Error('needMultiple');
      const selected = s.selection.map(id => editable(s, id));
      const roots = selected.filter(b => !selected.some(p => descendants(s.boxes, p.id).some(c => c.id === b.id)));
      const family = roots.flatMap(b => [b, ...descendants(s.boxes, b.id)]);
      const x = Math.min(...family.map(b => b.x)), y = Math.min(...family.map(b => b.y));
      const w = Math.max(...family.map(b => b.x + b.width)) - x, h = Math.max(...family.map(b => b.y + b.height)) - y;
      const parent = newBox(s.nextNumber++, s.activeLayer, x, y, w, h); parent.type = 'Modul';
      s.boxes.push(parent); for (const b of roots) b.parentId = parent.id;
      s.selection = [parent.id]; s.ui.grabbed = null; touch(s); break;
    }
    case 'grid': applyOperation(s, { type: 'grid', spacing: a.spacing, magnet: a.magnet }); touch(s); break;
    case 'gridToggle': s.grid.enabled = !s.grid.enabled; touch(s); break;
    case 'view':
      if (!['structure', 'design'].includes(a.view)) throw new Error('invalidAction');
      s.ui.view = a.view; break;
    case 'zoom':
      if (typeof a.zoom !== 'number' || !Number.isFinite(a.zoom) || a.zoom < .25 || a.zoom > 2) throw new Error('invalidValues');
      s.ui.zoom = a.zoom; break;
    case 'language': if (!['de', 'en'].includes(a.language)) throw new Error('invalidValues'); s.ui.language = a.language; break;
    case 'monitor':
      if (![a.x, a.y].every(v => typeof v === 'number' && Number.isFinite(v) && v >= 0)) throw new Error('invalidValues');
      s.ui.monitor.x = a.x; s.ui.monitor.y = a.y; break;
    case 'previewStart': {
      const p = primary(s); if (!p) throw new Error('needSelection');
      s.ui.grabbed = null; s.ui.preview = { id: p.id, color: p.color, paletteIndex: p.paletteIndex, brightness: p.brightness, dirty: false, colorChanged: false, brightnessChanged: false }; break;
    }
    case 'previewColor':
      if (!s.ui.preview) throw new Error('needPreview');
      if (!Number.isInteger(a.index) || a.index < 1 || a.index > 16) throw new Error('invalidColor');
      Object.assign(s.ui.preview, { paletteIndex: a.index, color: PALETTE[a.index - 1], brightness: 0, dirty: true, colorChanged: true, brightnessChanged: true }); break;
    case 'previewBrightness':
      if (!s.ui.preview || !Number.isFinite(a.delta)) throw new Error('needPreview');
      s.ui.preview.brightness = Math.max(-100, Math.min(100, s.ui.preview.brightness + a.delta));
      s.ui.preview.dirty = true; s.ui.preview.brightnessChanged = true; break;
    case 'previewCommit':
      if (s.ui.preview?.dirty) {
        const p = s.ui.preview;
        patch(s, p.id, { ...(p.colorChanged ? { color: p.color, paletteIndex: p.paletteIndex } : {}), ...(p.brightnessChanged ? { brightness: p.brightness } : {}) }); touch(s);
      }
      s.ui.preview = null; break;
    case 'previewCancel': s.ui.preview = null; break;
    case 'notice': s.ui.notice = a.message; s.ui.noticeArgs = a.args || {}; s.ui.error = !!a.error; break;
    case 'taskAdd': s.tasks.push(clone(a.task)); break;
    case 'taskUpdate': {
      const t = s.tasks.find(t => t.task_id === a.task_id); if (!t) throw new Error('unknownTask');
      Object.assign(t, clone(a.changes)); break;
    }
    case 'aiApply': {
      const t = s.tasks.find(t => t.task_id === a.task_id);
      if (!t || t.applied) throw new Error(t?.applied ? 'duplicateReply' : 'unknownTask');
      if (t.revision !== s.revision) throw new Error('staleReply');
      if (s.ui.grabbed || s.ui.preview) throw new Error('finishGesture');
      if (!Array.isArray(a.actions) || a.actions.length > 100) throw new Error('invalidReply');
      for (const op of a.actions) {
        if (op.box_id && !t.box_ids.includes(op.box_id)) throw new Error('invalidTargets');
        applyOperation(s, op);
      }
      t.applied = true; t.status = 'applied'; touch(s); break;
    }
    case 'retain':
      if (!s.myspace.some(p => p.id === a.proposal.id)) s.myspace.push(clone(a.proposal)); break;
    case 'proposalApply':
      if (!s.selection.length) throw new Error('needSelection');
      for (const id of s.selection) patch(s, id, a.changes);
      touch(s); break;
    default: throw new Error('invalidAction');
  }
  const chosen = a.type === 'create' || a.type === 'group' ? primary(s)
    : ['select', 'grab'].includes(a.type) && a.id ? s.boxes.find(b => b.id === a.id) : null;
  if (chosen) s.ui.monitor.last = clone(chosen);
  else if (s.ui.monitor.last) {
    const live = s.boxes.find(b => b.id === s.ui.monitor.last.id);
    if (live) s.ui.monitor.last = clone(live);
  }
  return s;
}
