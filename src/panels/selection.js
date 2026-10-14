import { primary, TYPES } from '../core/model.js';
import { PALETTE, tint } from '../core/palette.js';
import { t } from '../i18n.js';
export function mountSelection(store, root) {
  const type = root.querySelector('#box-type'), label = root.querySelector('#box-label'), parent = root.querySelector('#box-parent');
  for (const value of TYPES) { const option = document.createElement('option'); option.value = value; root.querySelector('#types').append(option); }
  function set(changes) { const s = store.getState(); if (s.selection[0]) store.dispatch({ type: 'patch', id: s.selection[0], changes }); }
  type.addEventListener('change', () => set({ type: type.value.trim() }));
  label.addEventListener('change', () => set({ label: label.value }));
  parent.addEventListener('change', () => { const id = store.getState().selection[0]; if (id) store.dispatch({ type: 'parent', id, parentId: parent.value || null }); });
  root.querySelector('#transfer').addEventListener('click', () => store.dispatch({ type: 'transfer' }));
  root.querySelector('#group').addEventListener('click', () => store.dispatch({ type: 'group' }));
  for (const [i, color] of PALETTE.entries()) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'np-button'; button.dataset.palette = i + 1;
    const swatch = document.createElement('span'); swatch.className = 'swatch'; swatch.style.background = color;
    button.append(swatch, document.createTextNode(String(i + 1)));
    button.addEventListener('click', () => store.dispatch({ type: 'previewColor', index: i + 1 }));
    root.querySelector('#palette').append(button);
  }
  store.subscribe(s => {
    const p = primary(s), lang = s.ui.language;
    root.querySelector('#selection-info').textContent = p ? `${s.selection.map(id => s.boxes.find(b => b.id === id).number).join(', ')} · ${t(lang, 'primary')} ${p.number}` : t(lang, 'noSelection');
    for (const el of [type, label, parent]) el.disabled = !p || !!s.ui.preview || !!s.ui.grabbed;
    if (document.activeElement !== type) type.value = p?.type || '';
    if (document.activeElement !== label) label.value = p?.label || '';
    if (document.activeElement !== parent) {
      parent.replaceChildren(); const none = document.createElement('option'); none.value = ''; none.textContent = t(lang, 'none'); parent.append(none);
      for (const box of s.boxes.filter(b => b.type === 'Modul' && b.layer === s.activeLayer && b.id !== p?.id)) {
        const option = document.createElement('option'); option.value = box.id; option.textContent = `${box.number} · ${box.label || box.type}`; parent.append(option);
      }
      parent.value = p?.parentId || '';
    }
    root.querySelector('#transfer').disabled = s.selection.length < 2 || !!s.ui.preview || !!s.ui.grabbed;
    root.querySelector('#group').disabled = s.selection.length < 2 || !!s.ui.preview || !!s.ui.grabbed;
    root.querySelectorAll('[data-palette]').forEach(el => {
      el.disabled = !s.ui.preview;
      el.setAttribute('aria-label', `${t(lang, 'color')} ${el.dataset.palette}`);
      el.setAttribute('aria-pressed', String(Number(el.dataset.palette) === s.ui.preview?.paletteIndex));
    });
    const info = root.querySelector('#preview-info');
    info.textContent = s.ui.preview ? `${t(lang, 'preview')} · ${t(lang, 'brightness')} ${s.ui.preview.brightness}%` : t(lang, 'noPreview');
    info.style.borderLeft = s.ui.preview ? `16px solid ${tint(s.ui.preview.color, s.ui.preview.brightness)}` : '';
  });
}
