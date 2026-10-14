import { createStore } from './core/store.js';
import { translate } from './i18n.js';
import { mountWorkspace } from './workspace/render.js';
import { mountLayersGrid } from './workspace/layers-grid.js';
import { mountMonitor } from './workspace/monitor.js';
import { mountInput } from './input/controller.js';
import { mountSelection } from './panels/selection.js';
import { mountMyspace } from './panels/myspace.js';
import { mountAI } from './panels/ai-space.js';

export function mount(root = document) {
  const store = createStore();
  store.subscribe(s => { translate(root, s.ui.language); root.querySelector('#language').value = s.ui.language; });
  const workspace = mountWorkspace(store, root);
  mountLayersGrid(store, root); mountMonitor(store, root); mountSelection(store, root); mountMyspace(store, root); mountInput(store, root, workspace);
  mountAI(store, root);
  root.querySelector('#language').addEventListener('change', e => store.dispatch({ type: 'language', language: e.target.value }));
  const dialog = root.querySelector('#help-dialog'), help = root.querySelector('#help');
  help.addEventListener('click', () => dialog.showModal());
  root.querySelector('#close-help').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => help.focus());
  // Read-only inspection for acceptance, no alternative mutable document path.
  window.blockDesigner = Object.freeze({ getState: store.getState });
  return store;
}
mount();
