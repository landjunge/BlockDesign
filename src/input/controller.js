import { primary } from '../core/model.js';
import { matchShortcut } from './shortcuts.js';
import { nearest } from '../core/geometry.js';
export function mountInput(store, root, workspace, help) {
  const held = new Set();
  let pointer = { x: 0, y: 0 },
    known = false,
    anchor = null;
  const editing = () =>
    !!document.querySelector('dialog[open]') ||
    document.activeElement?.matches('input,textarea,select,[contenteditable="true"]');
  const canvasScroll = root.querySelector('#canvas-scroll');
  const notify = (message, args) => store.dispatch({ type: 'notice', message, args });
  function setAnchor() {
    const s = store.getState(),
      box = s.boxes.find((b) => b.id === s.ui.grabbed) || primary(s);
    anchor = box
      ? {
          clientX: pointer.x,
          clientY: pointer.y,
          x: box.x,
          y: box.y,
          width: box.width,
          height: box.height,
          id: box.id,
          zoom: s.ui.zoom,
        }
      : null;
  }
  window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (editing()) return;
    const shortcut = matchShortcut(e);
    if (!shortcut) return;
    if (shortcut === 'help') {
      e.preventDefault();
      help.open();
      return;
    }
    if (['undo', 'redo'].includes(shortcut)) {
      e.preventDefault();
      store.dispatch({ type: shortcut });
      return;
    }
    e.preventDefault();
    if (e.repeat) return;
    held.add(shortcut);
    const s = store.getState();
    if (shortcut === 'create') {
      if (!s.ui.preview) {
        const result = store.dispatch({ type: 'create' });
        if (result.ok) notify('boxCreated', { number: store.getState().nextNumber - 1 });
      }
    } else if (shortcut === 'layer') {
      store.dispatch({ type: 'layer', layer: Number(k) });
      anchor = null;
    } else if (shortcut === 'grab') {
      if (s.ui.preview) return;
      if (s.ui.grabbed) {
        store.dispatch({ type: 'drop' });
        notify('dropped');
        store.end();
        anchor = null;
      } else {
        const point = known
          ? workspace.toDocument(pointer.x, pointer.y)
          : { x: s.document.width / 2, y: s.document.height / 2 };
        const box = s.selection.length > 1 ? primary(s) : nearest(s, point);
        if (box) {
          store.begin('move');
          store.dispatch({ type: 'grab', id: box.id });
          setAnchor();
          notify('grabbed');
        } else notify('needSelection');
      }
    } else if (shortcut === 'height' || shortcut === 'width') {
      store.begin('resize');
      setAnchor();
    } else if (shortcut === 'scale') {
      const box = s.boxes.find((b) => b.id === s.ui.grabbed) || primary(s);
      if (box && !s.ui.preview) {
        store.dispatch({ type: 'scale', id: box.id, factor: k === '-' ? 1 / 1.1 : 1.1 });
        setAnchor();
      } else notify('needSelection');
    } else if (shortcut === 'transfer') {
      if (!s.ui.preview) {
        const r = store.dispatch({ type: 'transfer' });
        if (r.ok) notify('copied');
      }
    } else if (shortcut === 'attribute') {
      const r = store.dispatch({ type: 'previewStart' });
      if (r.ok) root.querySelector('#attribute-panel').open = true;
    } else if (shortcut === 'cancel') {
      store.dispatch({ type: 'previewCancel' });
      store.dispatch({ type: 'drop' });
      held.clear();
      store.end();
      anchor = null;
    }
  });
  window.addEventListener('keyup', (e) => {
    const shortcut = matchShortcut(e),
      was = held.delete(shortcut);
    if (shortcut === 'attribute' && was) store.dispatch({ type: 'previewCommit' });
    if (shortcut === 'height' || shortcut === 'width') {
      if (!held.has('height') && !held.has('width') && !store.getState().ui.grabbed) store.end();
      setAnchor();
    }
  });
  window.addEventListener('pointermove', (e) => {
    pointer = { x: e.clientX, y: e.clientY };
    known = true;
    const s = store.getState();
    if (editing() || s.ui.preview || e.target.closest?.('#monitor')) return;
    if (!s.ui.grabbed && !held.has('height') && !held.has('width')) return;
    if (held.has('height') && held.has('width')) return;
    const b = s.boxes.find((b) => b.id === s.ui.grabbed) || primary(s);
    if (!b) return;
    if (!anchor || anchor.id !== b.id || anchor.zoom !== s.ui.zoom) {
      setAnchor();
      return;
    }
    const dx = (pointer.x - anchor.clientX) / s.ui.zoom,
      dy = (pointer.y - anchor.clientY) / s.ui.zoom;
    if (held.has('height'))
      store.dispatch({
        type: 'resize',
        id: b.id,
        axis: 'height',
        delta: anchor.height + dy - b.height,
      });
    else if (held.has('width'))
      store.dispatch({
        type: 'resize',
        id: b.id,
        axis: 'width',
        delta: anchor.width + dx - b.width,
      });
    else if (s.ui.grabbed)
      store.dispatch({
        type: 'moveSelection',
        id: s.ui.grabbed,
        dx: anchor.x + dx - b.x,
        dy: anchor.y + dy - b.y,
      });
  });
  window.addEventListener(
    'wheel',
    (e) => {
      if (!store.getState().ui.preview) return;
      e.preventDefault();
      store.dispatch({ type: 'previewBrightness', delta: e.deltaY > 0 ? -1 : 1 });
    },
    { passive: false },
  );
  function release() {
    held.clear();
    anchor = null;
    store.dispatch({ type: 'previewCancel' });
    if (store.getState().ui.grabbed) store.dispatch({ type: 'drop' });
    store.end();
  }
  window.addEventListener('blur', release);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) release();
  });
  document.addEventListener('focusin', () => {
    if (editing()) release();
  });
  canvasScroll.addEventListener('pointerdown', () => {
    if (!store.getState().ui.preview) canvasScroll.focus({ preventScroll: true });
  });
  store.subscribe((s) => {
    if (!s.ui.grabbed && !held.has('height') && !held.has('width')) anchor = null;
  });
}
