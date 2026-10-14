import { primary } from '../core/model.js';
import { nearest } from '../core/geometry.js';
export function mountInput(store, root, workspace) {
  const held = new Set(); let pointer = { x: 0, y: 0 }, known = false, anchor = null;
  const editing = () => !!document.querySelector('dialog[open]') || document.activeElement?.matches('input,textarea,select,[contenteditable="true"]');
  const canvasScroll = root.querySelector('#canvas-scroll');
  const notify = (message, args) => store.dispatch({ type: 'notice', message, args });
  function setAnchor() {
    const s = store.getState(), box = s.boxes.find(b => b.id === s.ui.grabbed) || primary(s);
    anchor = box ? { clientX: pointer.x, clientY: pointer.y, x: box.x, y: box.y, width: box.width, height: box.height, id: box.id, zoom: s.ui.zoom } : null;
  }
  window.addEventListener('keydown', e => {
    const k = e.key.toLowerCase();
    if (editing() || e.ctrlKey || e.metaKey || e.altKey) return;
    if (!['b', '1', '2', '3', ' ', 'd', 'f', '+', '=', '-', 'a', 't', 'escape'].includes(k)) return;
    e.preventDefault();
    if (e.repeat) return;
    held.add(k);
    const s = store.getState();
    if (k === 'b') { if (!s.ui.preview) { const result = store.dispatch({ type: 'create' }); if (result.ok) notify('boxCreated', { number: store.getState().nextNumber - 1 }); } }
    else if (['1', '2', '3'].includes(k)) { store.dispatch({ type: 'layer', layer: Number(k) }); anchor = null; }
    else if (k === ' ') {
      if (s.ui.preview) return;
      if (s.ui.grabbed) { store.dispatch({ type: 'drop' }); notify('dropped'); anchor = null; }
      else {
        const point = known ? workspace.toDocument(pointer.x, pointer.y) : { x: s.document.width / 2, y: s.document.height / 2 };
        const box = nearest(s, point);
        if (box) { store.dispatch({ type: 'grab', id: box.id }); setAnchor(); notify('grabbed'); }
        else notify('needSelection');
      }
    } else if (k === 'd' || k === 'f') setAnchor();
    else if (['+', '=', '-'].includes(k)) { const box = s.boxes.find(b => b.id === s.ui.grabbed) || primary(s); if (box && !s.ui.preview) { store.dispatch({ type: 'scale', id: box.id, factor: k === '-' ? 1 / 1.1 : 1.1 }); setAnchor(); } else notify('needSelection'); }
    else if (k === 't') { if (!s.ui.preview) { const r = store.dispatch({ type: 'transfer' }); if (r.ok) notify('copied'); } }
    else if (k === 'a') { const r = store.dispatch({ type: 'previewStart' }); if (r.ok) root.querySelector('#attribute-panel').open = true; }
    else if (k === 'escape') { store.dispatch({ type: 'previewCancel' }); store.dispatch({ type: 'drop' }); held.clear(); anchor = null; }
  });
  window.addEventListener('keyup', e => {
    const k = e.key.toLowerCase(), was = held.delete(k);
    if (k === 'a' && was) store.dispatch({ type: 'previewCommit' });
    if (k === 'd' || k === 'f') setAnchor();
  });
  window.addEventListener('pointermove', e => {
    pointer = { x: e.clientX, y: e.clientY }; known = true;
    const s = store.getState();
    if (editing() || s.ui.preview || e.target.closest?.('#monitor')) return;
    if (!s.ui.grabbed && !held.has('d') && !held.has('f')) return;
    if (held.has('d') && held.has('f')) return;
    const b = s.boxes.find(b => b.id === s.ui.grabbed) || primary(s);
    if (!b) return;
    if (!anchor || anchor.id !== b.id || anchor.zoom !== s.ui.zoom) { setAnchor(); return; }
    const dx = (pointer.x - anchor.clientX) / s.ui.zoom, dy = (pointer.y - anchor.clientY) / s.ui.zoom;
    if (held.has('d')) store.dispatch({ type: 'resize', id: b.id, axis: 'height', delta: anchor.height + dy - b.height });
    else if (held.has('f')) store.dispatch({ type: 'resize', id: b.id, axis: 'width', delta: anchor.width + dx - b.width });
    else if (s.ui.grabbed) store.dispatch({ type: 'move', id: s.ui.grabbed, dx: anchor.x + dx - b.x, dy: anchor.y + dy - b.y });
  });
  window.addEventListener('wheel', e => {
    if (!store.getState().ui.preview) return;
    e.preventDefault(); store.dispatch({ type: 'previewBrightness', delta: e.deltaY > 0 ? -1 : 1 });
  }, { passive: false });
  function release() { held.clear(); anchor = null; store.dispatch({ type: 'previewCancel' }); if (store.getState().ui.grabbed) store.dispatch({ type: 'drop' }); }
  window.addEventListener('blur', release);
  document.addEventListener('visibilitychange', () => { if (document.hidden) release(); });
  document.addEventListener('focusin', () => { if (editing()) release(); });
  canvasScroll.addEventListener('pointerdown', () => { if (!store.getState().ui.preview) canvasScroll.focus({ preventScroll: true }); });
  store.subscribe(s => { if (!s.ui.grabbed && !held.has('d') && !held.has('f')) anchor = null; });
}
