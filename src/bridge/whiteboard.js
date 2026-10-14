import { validatePatch } from '../core/model.js';
function exact(value, keys) { if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join(',') !== [...keys].sort().join(',')) throw new Error('invalidReply'); }
export function snapshot(state) {
  return { version: 1, revision: state.revision, document: state.document, boxes: state.boxes, selection: state.selection,
    activeLayer: state.activeLayer, grid: state.grid, coordinates: { origin: [0, 0], x: 'right', y: 'down', unit: 'px', pixel_scale: 1 },
    zoom: state.ui.zoom, language: state.ui.language };
}
export function validateReply(reply, task) {
  exact(reply, ['version', 'task_id', 'revision', 'box_ids', 'summary', 'actions', 'proposals']);
  if (reply.version !== 1 || reply.task_id !== task.task_id || reply.revision !== task.revision ||
    JSON.stringify(reply.box_ids) !== JSON.stringify(task.box_ids) || typeof reply.summary !== 'string' || reply.summary.length > 1500 ||
    !Array.isArray(reply.actions) || reply.actions.length > 100 || !Array.isArray(reply.proposals) || reply.proposals.length > 100) throw new Error('invalidReply');
  for (const op of reply.actions) {
    if (op.type === 'patch') { exact(op, ['type', 'box_id', 'changes']); validatePatch(op.changes); }
    else if (op.type === 'scale') { exact(op, ['type', 'box_id', 'factor']); if (typeof op.factor !== 'number' || !Number.isFinite(op.factor) || op.factor <= 0 || op.factor > 10) throw new Error('invalidReply'); }
    else if (op.type === 'grid') {
      exact(op, ['type', 'spacing', 'magnet']);
      if (typeof op.spacing !== 'number' || !Number.isFinite(op.spacing) || op.spacing < .25 || op.spacing > 1000 ||
        typeof op.magnet !== 'number' || !Number.isFinite(op.magnet) || op.magnet < 0 || op.magnet > op.spacing / 2) throw new Error('invalidGrid');
    } else throw new Error('invalidReply');
    if (op.box_id && !task.box_ids.includes(op.box_id)) throw new Error('invalidTargets');
  }
  const ids = new Set();
  for (const p of reply.proposals) {
    exact(p, ['id', 'source_task', 'title', 'description', 'changes']);
    if (typeof p.id !== 'string' || !p.id || ids.has(p.id) || p.source_task !== task.task_id || typeof p.title !== 'string' || !p.title || p.title.length > 100 ||
      typeof p.description !== 'string' || p.description.length > 500 || 'x' in p.changes || 'y' in p.changes) throw new Error('invalidReply');
    ids.add(p.id); validatePatch(p.changes);
  }
  return reply;
}
export function createWhiteboardBridge(store, request = fetch) {
  const timers = new Map();
  async function api(url, options) {
    const response = await request(url, { ...options, signal: AbortSignal.timeout(12000) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'disconnected');
    return payload;
  }
  function update(id, changes) { store.dispatch({ type: 'taskUpdate', task_id: id, changes }); }
  function accept(payload) {
    const task = store.getState().tasks.find(t => t.task_id === payload.task_id);
    if (!task) throw new Error('unknownTask');
    if (task.applied || task.received) return;
    const reply = validateReply(payload.reply, task);
    const state = store.getState();
    if (state.revision !== task.revision || state.activeLayer !== task.activeLayer) {
      update(task.task_id, { status: 'stale', reply, received: true, evidence: payload.evidence }); return;
    }
    if (state.ui.grabbed || state.ui.preview) {
      update(task.task_id, { status: 'stale', reply, received: true, error: 'finishGesture' }); return;
    }
    if (reply.actions.length) {
      const result = store.dispatch({ type: 'aiApply', task_id: task.task_id, actions: reply.actions });
      if (!result.ok) throw new Error(result.error);
      store.dispatch({ type: 'notice', message: 'changed' });
    }
    update(task.task_id, { status: reply.actions.length ? 'applied' : reply.proposals.length ? 'ready' : 'noChange', reply, received: true, evidence: payload.evidence });
  }
  async function poll(taskId) {
    clearTimeout(timers.get(taskId));
    try {
      const payload = await api(`/api/tasks/${encodeURIComponent(taskId)}`);
      if (payload.status === 'ready') accept(payload);
      else if (payload.status === 'failed') update(taskId, { status: 'failed', error: payload.error });
      else {
        if (!['waiting', 'claimed', 'running'].includes(payload.status)) throw new Error('invalidReply');
        update(taskId, { status: payload.status });
        timers.set(taskId, setTimeout(() => poll(taskId), 800));
      }
    } catch (e) { update(taskId, { status: e.message === 'disconnected' || e.name === 'TimeoutError' || e.name === 'TypeError' ? 'disconnected' : 'failed', error: e.message }); }
  }
  return {
    status: () => api('/api/status'), poll, accept,
    async submit(instruction) {
      const s = store.getState();
      if (s.ui.grabbed || s.ui.preview) throw new Error('finishGesture');
      if (!instruction.trim() || instruction.length > 1000) throw new Error('emptyOrder');
      const task = { task_id: crypto.randomUUID(), box_ids: s.selection, revision: s.revision, activeLayer: s.activeLayer, instruction,
        status: 'waiting', applied: false, received: false };
      store.dispatch({ type: 'taskAdd', task });
      try {
        await api('/api/tasks', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task_id: task.task_id, instruction, box_ids: task.box_ids, revision: task.revision, snapshot: snapshot(s) }) });
        await poll(task.task_id);
      } catch (e) { update(task.task_id, { status: e.name === 'TypeError' || e.name === 'TimeoutError' ? 'disconnected' : 'failed', error: e.message }); }
      return task.task_id;
    },
  };
}
