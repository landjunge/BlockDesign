import { SHORTCUTS } from '../input/shortcuts.js';
export function mountHelp(store, root) {
  const dialog = root.querySelector('#help-dialog');
  let previous = null;
  function open() {
    if (dialog.open) return;
    previous = document.activeElement;
    dialog.showModal();
    root.querySelector('#close-help').focus();
  }
  root.querySelector('#help').addEventListener('click', open);
  root.querySelector('#close-help').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    if (previous?.isConnected) previous.focus({ preventScroll: true });
    else root.querySelector('#canvas-scroll').focus();
  });
  store.subscribe((s) => {
    const list = root.querySelector('#shortcut-list');
    list.replaceChildren();
    const dl = document.createElement('dl');
    for (const item of SHORTCUTS) {
      const dt = document.createElement('dt'),
        dd = document.createElement('dd');
      dt.textContent = item.key;
      dd.textContent = item[s.ui.language];
      dl.append(dt, dd);
    }
    list.append(dl);
  });
  return { open };
}
