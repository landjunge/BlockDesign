import { clamp } from '../core/geometry.js';
import { t } from '../i18n.js';
const format = (n, lang) => new Intl.NumberFormat(lang, { maximumFractionDigits: 2 }).format(n);
export function mountMonitor(store, root) {
  const panel = root.querySelector('#monitor'), handle = root.querySelector('#monitor-handle'), viewport = root.querySelector('#viewport');
  let drag = null;
  function place(x, y) { store.dispatch({ type: 'monitor', x: clamp(x, 0, Math.max(0, viewport.clientWidth - panel.offsetWidth)), y: clamp(y, 0, Math.max(0, viewport.clientHeight - panel.offsetHeight)) }); }
  handle.addEventListener('pointerdown', e => { const s = store.getState(); drag = { x: e.clientX, y: e.clientY, start: s.ui.monitor }; handle.setPointerCapture(e.pointerId); e.stopPropagation(); });
  handle.addEventListener('pointermove', e => { if (drag) { place(drag.start.x + e.clientX - drag.x, drag.start.y + e.clientY - drag.y); e.stopPropagation(); } });
  handle.addEventListener('pointerup', () => { drag = null; });
  handle.addEventListener('pointercancel', () => { drag = null; });
  handle.addEventListener('keydown', e => {
    const delta = { ArrowLeft: [-8, 0], ArrowRight: [8, 0], ArrowUp: [0, -8], ArrowDown: [0, 8] }[e.key];
    if (delta) { e.preventDefault(); e.stopPropagation(); const m = store.getState().ui.monitor; place(m.x + delta[0], m.y + delta[1]); }
  });
  store.subscribe(s => {
    panel.style.left = `${s.ui.monitor.x}px`; panel.style.top = `${s.ui.monitor.y}px`;
    const values = root.querySelector('#monitor-values'); values.replaceChildren();
    const b = s.ui.monitor.last;
    if (!b) { values.textContent = t(s.ui.language, 'noSelection'); return; }
    const dl = document.createElement('dl');
    for (const [name, value] of [['number', b.number], ['X', b.x], ['Y', b.y], ['width', b.width], ['height', b.height], ['orientation', b.orientation]]) {
      const dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = t(s.ui.language, name); dd.textContent = typeof value === 'number' ? format(value, s.ui.language) + (name === 'number' ? '' : ' px') : '■';
      if (name === 'orientation') { dd.style.color = value; dd.title = value; }
      dd.dataset.value = typeof value === 'number' ? String(value) : value;
      dl.append(dt, dd);
    }
    values.append(dl);
  });
  new ResizeObserver(() => { const m = store.getState().ui.monitor; place(m.x, m.y); }).observe(viewport);
}
