import { createStore } from './core/store.js';
import { translate } from './i18n.js';
import { mountWorkspace } from './workspace/render.js';
import { mountHeader } from './shell/header.js';
import { mountHelp } from './shell/help.js';
import { mountSidebars } from './shell/sidebars.js';
import { mountMonitor } from './workspace/monitor.js';
import { mountInput } from './input/controller.js';
import { mountSelection } from './panels/selection.js';
import { mountMyspace } from './panels/myspace.js';
import { createProjects, mountProjects } from './bridge/projects.js';
import { mountAI } from './panels/ai-space.js';
import { mountSource } from './panels/source.js';
import { mountDesignWorkflow } from './bridge/design-workflow.js';

export async function mount(root = document) {
  const store = createStore();
  const projects=createProjects(store);await projects.init();
  store.subscribe(s => { translate(root, s.ui.language); });
  const workspace = mountWorkspace(store, root);
  const help=mountHelp(store,root);
  mountHeader(store,root);mountSidebars(store,root);mountMonitor(store,root);mountSelection(store,root);mountMyspace(store,root,projects);mountInput(store,root,workspace,help);
  mountProjects(projects,store,root);mountAI(store,root,projects);
  mountSource(store,root,projects);
  mountDesignWorkflow(store,root,projects);
  translate(root,store.getState().ui.language);
  // Read-only inspection for acceptance, no alternative mutable document path.
  window.blockDesigner = Object.freeze({ getState: store.getState });
  return store;
}
mount();
