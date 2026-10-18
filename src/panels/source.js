import { primary } from '../core/model.js';
import { bindingState, boxBinding, sourceTransform } from '../core/design.js';
import { t } from '../i18n.js';

async function base64(file, limit) {
  if (!file || !file.size || file.size > limit) throw Error('designSourceLimit');
  const bytes = new Uint8Array(await file.arrayBuffer());
  let value = '';
  for (let offset = 0; offset < bytes.length; offset += 8192) value += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
  return btoa(value);
}
export function mountSource(store, root, projects) {
  const form = root.querySelector('#source-form'), status = root.querySelector('#source-info');
  const operation = root.querySelector('#source-operation'), element = root.querySelector('#source-element');
  let busy = false;
  let viewportKey = null;
  const fail = error => store.dispatch({ type: 'notice', message: error.message, error: true });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;
    const initial = store.getState(), project_id = projects.info().project, files = root.querySelector('#source-html').files;
    busy = true;
    form.querySelector('button').disabled = true;
    try {
      const preview_base64 = await base64(root.querySelector('#source-png').files[0], 1048576);
      const html_base64 = files[0] ? await base64(files[0], 262144) : null;
      const reference_viewport = { width: Number(root.querySelector('#source-width').value), height: Number(root.querySelector('#source-height').value) };
      const response = await fetch('/api/design/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ preview_base64, html_base64, reference_viewport }), signal: AbortSignal.timeout(12000) });
      const design = await response.json();
      if (!response.ok) throw Error(design.error || 'designInvalidSource');
      await projects.apply({ type: 'designImport', expected_revision: initial.revision, design }, { kind: 'sourceImport' }, { project_id });
      store.dispatch({ type: 'notice', message: 'designImported' });
    } catch (error) { fail(error); }
    finally { busy = false; form.querySelector('button').disabled = false; }
  });
  root.querySelector('#source-bind').addEventListener('click', async () => {
    const state = store.getState(), project_id = projects.info().project, box = primary(state);
    if (!box || !state.design) return;
    try {
      await projects.apply({ type: 'designBind', id: box.id, expected_revision: state.revision, source_hash: state.design.source.artifact_sha256, operation: operation.value, element_id: element.value || null }, { kind: 'sourceBinding' }, { project_id });
      store.dispatch({ type: 'notice', message: 'designBound' });
    } catch (error) { fail(error); }
  });
  store.subscribe(state => {
    const design = state.design, lang = state.ui.language, box = primary(state);
    const nextKey = JSON.stringify([projects.info().project, design?.source.reference_viewport]);
    if (nextKey !== viewportKey) {
      const viewport = design?.source.reference_viewport || state.document;
      root.querySelector('#source-width').value = viewport.width;
      root.querySelector('#source-height').value = viewport.height;
      viewportKey = nextKey;
    }
    if (design) {
      const view = design.source.reference_viewport, transform = sourceTransform(state);
      status.textContent = `${t(lang, 'designReference')} ${view.width} × ${view.height} px · ${t(lang, 'designViewportClaim')} · ${t(lang, 'designScale')} ${transform.scale.toFixed(3)} · SHA256 ${design.source.artifact_sha256} · ${t(lang, 'designCommitUnknown')}`;
    } else status.textContent = t(lang, 'designNoSource');
    const binding = boxBinding(design, box?.id);
    operation.value = binding?.action || 'new';
    element.replaceChildren();
    const unknown = document.createElement('option'); unknown.value = ''; unknown.textContent = t(lang, 'designUnresolved'); element.append(unknown);
    for (const item of design?.catalog || []) {
      const option = document.createElement('option'); option.value = item.element_id;
      option.textContent = `${item.element_id} · ${item.tag} · ${item.count}×${item.resolution === 'unique' ? '' : ' · ?'}`;
      element.append(option);
    }
    element.value = binding?.source_element?.element_id || '';
    const blocked = busy || !design || !box || !!state.ui.preview || !!state.ui.grabbed || !!state.ui.aiPreview;
    operation.disabled = element.disabled = root.querySelector('#source-bind').disabled = blocked;
    root.querySelector('#source-binding-state').textContent = !box ? t(lang, 'needSelection') : !design ? t(lang, 'designNoSource') : t(lang, 'designStatus_' + bindingState(design, binding));
    form.querySelector('button').disabled = busy || !!state.ui.preview || !!state.ui.grabbed || !!state.ui.aiPreview;
  });
}
