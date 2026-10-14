import { center, descendants } from '../core/geometry.js';
import { tint } from '../core/palette.js';
import { t } from '../i18n.js';

export function mountWorkspace(store, root) {
  const canvas = root.querySelector('#canvas'), sizer = root.querySelector('#canvas-sizer');
  const elements = new Map();
  const gripper = document.createElement('div'); gripper.className = 'gripper'; gripper.hidden = true; canvas.append(gripper);
  canvas.addEventListener('click', e => {
    if (store.getState().ui.preview || store.getState().ui.grabbed) return;
    const hit = e.target.closest('[data-box-id]');
    store.dispatch({ type: 'select', id: hit?.dataset.boxId || null, extend: e.shiftKey });
    root.querySelector('#canvas-scroll').focus({ preventScroll: true });
  });
  canvas.addEventListener('keydown', e => {
    const hit = e.target.closest('[data-box-id]');
    if (hit && e.key === 'Enter') { e.preventDefault(); store.dispatch({ type: 'select', id: hit.dataset.boxId, extend: e.shiftKey }); }
  });
  store.subscribe(s => {
    canvas.style.width = `${s.document.width}px`; canvas.style.height = `${s.document.height}px`; canvas.style.transform = `scale(${s.ui.zoom})`;
    sizer.style.width = `${s.document.width * s.ui.zoom}px`; sizer.style.height = `${s.document.height * s.ui.zoom}px`;
    canvas.className = `${s.ui.view}${s.ui.grabbed ? ' grabbed' : ''}`;
    canvas.style.backgroundSize = `${s.grid.spacing}px ${s.grid.spacing}px`;
    canvas.style.setProperty('--hit', `${28 / s.ui.zoom}px`);
    canvas.style.backgroundImage = s.grid.enabled && s.ui.view === 'structure' ? '' : 'none';
    for (const [id, el] of elements) if (!s.boxes.some(b => b.id === id)) { el.remove(); elements.delete(id); }
    function depth(box) {
      let value = 0, current = box;
      while (current.parentId) { value++; current = s.boxes.find(b => b.id === current.parentId); }
      return value;
    }
    // Parent backgrounds must paint behind their children in both views.
    const ordered = [...s.boxes].sort((a, b) => (a.layer === s.activeLayer) - (b.layer === s.activeLayer) || a.layer - b.layer || depth(a) - depth(b) || a.number - b.number);
    for (const [i, box] of ordered.entries()) {
      let el = elements.get(box.id);
      if (!el) {
        el = document.createElement('div'); el.dataset.boxId = box.id; el.setAttribute('role', 'button');
        for (const name of ['box-visual', 'box-content', 'box-number', 'box-center']) { const child = document.createElement('span'); child.className = name; el.append(child); }
        elements.set(box.id, el); canvas.append(el);
      }
      const previewChild = s.ui.preview?.dirty && descendants(s.boxes, s.ui.preview.id).some(child => child.id === box.id);
      const b = s.ui.preview?.id === box.id ? { ...box, ...s.ui.preview } : previewChild ? { ...box,
        ...(s.ui.preview.colorChanged ? { color: s.ui.preview.color, paletteIndex: s.ui.preview.paletteIndex } : {}),
        ...(s.ui.preview.brightnessChanged ? { brightness: s.ui.preview.brightness } : {}) } : box;
      el.className = `box${s.selection.includes(b.id) ? ' selected' : ''}${s.selection[0] === b.id ? ' primary' : ''}${b.layer !== s.activeLayer ? ' locked' : ''}`;
      el.tabIndex = b.layer === s.activeLayer ? 0 : -1; el.setAttribute('aria-disabled', String(b.layer !== s.activeLayer));
      el.setAttribute('aria-label', `${t(s.ui.language, 'number')} ${b.number} · ${b.type} · ${b.label}`);
      el.setAttribute('aria-pressed', String(s.selection.includes(b.id)));
      Object.assign(el.style, { left: `${b.x}px`, top: `${b.y}px`, width: `${b.width}px`, height: `${b.height}px`, zIndex: i + 1 });
      el.style.setProperty('--orientation', b.orientation);
      const visual = el.querySelector('.box-visual'), content = el.querySelector('.box-content');
      const designing = s.ui.view === 'design' || s.ui.preview?.id === b.id || previewChild;
      Object.assign(visual.style, { background: designing ? tint(b.color, b.brightness) : 'transparent',
        borderColor: designing ? b.borderColor : b.orientation, borderWidth: designing ? `${b.borderWidth}px` : '1px', borderRadius: designing ? `${b.radius}px` : '0' });
      content.hidden = s.ui.view !== 'design'; content.textContent = b.type === 'Checkbox' ? `☐ ${b.label}` : b.type === 'Dropdown' ? `${b.label} ▾` : b.label;
      content.dataset.type = b.type;
      Object.assign(content.style, { fontFamily: b.font.family, fontSize: `${b.font.size}px`, color: b.font.color, borderRadius: `${b.radius}px` });
      el.querySelector('.box-number').textContent = String(b.number);
      const c = center(b); el.dataset.centerX = c.x; el.dataset.centerY = c.y;
    }
    const grabbed = s.boxes.find(b => b.id === s.ui.grabbed);
    gripper.hidden = !grabbed;
    if (grabbed) { const c = center(grabbed); gripper.style.left = `${c.x}px`; gripper.style.top = `${c.y}px`; }
    const status = root.querySelector('#status'); status.textContent = t(s.ui.language, s.ui.notice || 'idle', s.ui.noticeArgs); status.dataset.error = String(s.ui.error);
  });
  return { toDocument(clientX, clientY) { const r = canvas.getBoundingClientRect(); const zoom = store.getState().ui.zoom; return { x: (clientX - r.left) / zoom, y: (clientY - r.top) / zoom }; } };
}
