// Layout preferences are deliberately separate from durable project contents.
const KEY = 'blockdesigner.layout.v1';
export function mountSidebars(store, root) {
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(KEY) || '{}');
  } catch {}
  const prefs = {
    version: 1,
    left: { visible: true, width: 216 },
    right: { visible: true, width: 332 },
  };
  if (saved.version === 1)
    for (const side of ['left', 'right'])
      if (
        saved[side] &&
        typeof saved[side].visible === 'boolean' &&
        Number.isFinite(saved[side].width)
      )
        prefs[side] = {
          visible: saved[side].visible,
          width: Math.max(180, Math.min(600, saved[side].width)),
        };
  const spaces = root.querySelector('.spaces');
  function persist() {
    try {
      localStorage.setItem(
        KEY,
        JSON.stringify({
          ...prefs,
          monitor: { x: store.getState().ui.monitor.x, y: store.getState().ui.monitor.y },
        }),
      );
    } catch {
      store.dispatch({ type: 'notice', message: 'preferencesFailed', error: true });
    }
  }
  function render() {
    spaces.style.gridTemplateColumns = `${prefs.left.visible ? prefs.left.width : 0}px minmax(240px,1fr) ${prefs.right.visible ? prefs.right.width : 0}px`;
    for (const [side, id] of [
      ['left', 'myspace'],
      ['right', 'ai-space'],
    ]) {
      root.querySelector('#' + id).hidden = !prefs[side].visible;
      root
        .querySelector('#toggle-' + id)
        .setAttribute('aria-expanded', String(prefs[side].visible));
    }
  }
  for (const [side, id] of [
    ['left', 'myspace'],
    ['right', 'ai-space'],
  ]) {
    const panel = root.querySelector('#' + id),
      toggle = root.querySelector('#toggle-' + id);
    toggle.addEventListener('click', () => {
      prefs[side].visible = !prefs[side].visible;
      render();
      persist();
    });
    panel.classList.remove('np-scroll');
    const inner = document.createElement('div');
    inner.className = 'sidebar-content np-scroll';
    inner.tabIndex = 0;
    inner.setAttribute('aria-label', panel.getAttribute('aria-label') + ' · Inhalt / content');
    while (panel.firstChild) inner.append(panel.firstChild);
    panel.append(inner);
    const edge = document.createElement('div');
    edge.className = 'resize-edge ' + side;
    edge.tabIndex = 0;
    edge.setAttribute('role', 'separator');
    edge.setAttribute('aria-orientation', 'vertical');
    panel.append(edge);
    let drag = null;
    edge.addEventListener('pointerdown', (e) => {
      drag = { x: e.clientX, width: prefs[side].width };
      edge.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    edge.addEventListener('pointermove', (e) => {
      if (!drag) return;
      prefs[side].width = Math.max(
        180,
        Math.min(600, drag.width + (e.clientX - drag.x) * (side === 'left' ? 1 : -1)),
      );
      render();
    });
    edge.addEventListener('pointerup', () => {
      drag = null;
      persist();
    });
    edge.addEventListener('pointercancel', () => {
      drag = null;
      persist();
    });
    edge.addEventListener('keydown', (e) => {
      if (!['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      e.preventDefault();
      prefs[side].width = Math.max(
        180,
        Math.min(
          600,
          prefs[side].width + (e.key === 'ArrowRight' ? 16 : -16) * (side === 'left' ? 1 : -1),
        ),
      );
      render();
      persist();
    });
  }
  if (saved.version === 1 && Number.isFinite(saved.monitor?.x) && Number.isFinite(saved.monitor?.y))
    store.dispatch({
      type: 'monitor',
      x: Math.max(0, saved.monitor.x),
      y: Math.max(0, saved.monitor.y),
    });
  let monitor = '';
  store.subscribe((s) => {
    const next = JSON.stringify({ x: s.ui.monitor.x, y: s.ui.monitor.y });
    if (next !== monitor) {
      monitor = next;
      persist();
    }
  });
  render();
}
