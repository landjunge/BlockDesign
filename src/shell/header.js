import { mountLayersGrid } from '../workspace/layers-grid.js';
export function mountHeader(store, root) {
  mountLayersGrid(store, root);
  root
    .querySelectorAll('[data-language]')
    .forEach((el) =>
      el.addEventListener('click', () =>
        store.dispatch({ type: 'language', language: el.dataset.language }),
      ),
    );
  root.querySelector('#undo').addEventListener('click', () => store.dispatch({ type: 'undo' }));
  root.querySelector('#redo').addEventListener('click', () => store.dispatch({ type: 'redo' }));
  store.subscribe((s) => {
    root
      .querySelectorAll('[data-language]')
      .forEach((el) =>
        el.setAttribute('aria-pressed', String(el.dataset.language === s.ui.language)),
      );
    const h = store.history();
    root.querySelector('#undo').title = h.undoLabel || '';
    root.querySelector('#redo').title = h.redoLabel || '';
    root.querySelector('#undo').disabled = !h.undo || !!s.ui.grabbed || !!s.ui.preview;
    root.querySelector('#redo').disabled = !h.redo || !!s.ui.grabbed || !!s.ui.preview;
  });
}
