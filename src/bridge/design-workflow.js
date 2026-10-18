import { t } from '../i18n.js';

// A thin view over the fixed host adapter. No peer, secret, path or task authority here.
export function mountDesignWorkflow(store, root, projects) {
  let value = null, busy = false, currentProject = null, notice = null;
  const get = id => root.querySelector('#code-' + id);
  const fail = error => { notice = error.message; render(); };
  const stale = () => value && (value.stale || value.project_id !== projects.info().project || value.snapshot_id !== projects.info().head || value.document_revision !== store.getState().revision || projects.dirty());
  async function api(packet) {
    const response = await fetch('/api/design/workflows', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(packet), signal: AbortSignal.timeout(35000) });
    const result = await response.json();
    if (!response.ok) throw Error(result.error || 'designBridgeUnknown');
    return result;
  }
  function render() {
    const lang = store.getState().ui.language, changed = stale();
    get('prepare').disabled = busy || !store.getState().design || !!store.getState().ui.preview || !!store.getState().ui.grabbed;
    const unavailable = !value?.client_available;
    get('status').textContent = notice ? t(lang, notice) : !value ? t(lang, 'codeNotPrepared') : `${t(lang, changed ? 'designStale' : unavailable ? 'designProfileUnavailable' : value.last_error ? value.last_error : value.returned && value.state === 'accepted' ? 'codeDecisionAccepted' : 'codeState_' + value.state)} · ${value.id} · SHA256 ${value.descriptor_sha256} · ${t(lang, 'designCommitUnknown')}`;
    get('issue').disabled = busy || changed || unavailable || value?.state !== 'prepared';
    get('start').disabled = busy || changed || unavailable || value?.state !== 'issued_no_execution';
    get('refresh').disabled = busy || changed || unavailable || !value?.bridge_task_id;
    get('answer-field').hidden = value?.state !== 'awaiting_answer';
    get('answer-field').querySelector('span').textContent = value?.question || t(lang, 'answer');
    get('answer-send').disabled = busy || changed || unavailable;
    get('result').hidden = !value?.returned;
    get('summary').textContent = value?.summary || '';
    if (value?.returned) get('preview').src = '/api/design/preview/' + value.returned.preview_sha256;
    get('preview').alt = t(lang, 'codeReturnedPreview');
    for (const id of ['accept', 'rework', 'reject']) get(id).disabled = busy || changed || unavailable || value?.state !== 'delivered_unverified';
  }
  async function act(action, data = {}) {
    if (!value || busy || stale()) return;
    const request = value;
    busy = true; notice = null; render();
    try {
      const result = await api({ project_id: request.project_id, id: request.id, action, data });
      if (projects.info().project === request.project_id && value?.id === request.id) value = result;
    } catch (error) { fail(error); }
    finally { busy = false; render(); }
  }
  get('prepare').addEventListener('click', async () => {
    if (busy) return;
    const project = projects.info().project, revision = store.getState().revision;
    busy = true; notice = null; render();
    try {
      if (projects.dirty()) await projects.flush({ kind: 'preRequest' });
      if (projects.info().project !== project || store.getState().revision !== revision) throw Error('designStale');
      const result = await api({ project_id: project, snapshot_id: projects.info().head, instruction: get('order').value });
      if (projects.info().project !== project || store.getState().revision !== revision) throw Error('designStale');
      value = result;
      localStorage.setItem('blockdesigner.code-workflow.' + project, result.id);
    } catch (error) { fail(error); }
    finally { busy = false; render(); }
  });
  for (const action of ['issue', 'start', 'refresh']) get(action).addEventListener('click', () => act(action));
  get('answer-send').addEventListener('click', () => act('answer', { text: get('answer').value }));
  for (const [id, choice] of [['accept', 'accepted'], ['rework', 'rework'], ['reject', 'rejected']]) get(id).addEventListener('click', () => act('decision', { choice, note: get('note').value }));
  async function restore() {
    const project = projects.info().project;
    if (currentProject === project) return render();
    currentProject = project; value = null; notice = null; render();
    const identity = localStorage.getItem('blockdesigner.code-workflow.' + project);
    if (!identity) return;
    try {
      const response = await fetch(`/api/design/workflows/${project}/${identity}`, { signal: AbortSignal.timeout(12000) });
      const result = await response.json();
      if (!response.ok) throw Error(result.error || 'designBridgeUnknown');
      if (projects.info().project === project) value = result;
    } catch (error) { if (projects.info().project === project) fail(error); }
    render();
  }
  store.subscribe(render); projects.subscribe(restore); restore();
}
