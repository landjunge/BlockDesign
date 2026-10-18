import { t } from '../i18n.js';
import { validatePatch } from '../core/model.js';
function exact(value, keys) {
  if (
    !value ||
    typeof value !== 'object' ||
    Array.isArray(value) ||
    Object.keys(value).sort().join(',') !== [...keys].sort().join(',')
  )
    throw new Error('invalidReply');
}
export function snapshot(state) {
  return {
    version: 1,
    revision: state.revision,
    document: state.document,
    boxes: state.boxes,
    selection: state.selection,
    activeLayer: state.activeLayer,
    grid: state.grid,
    coordinates: { origin: [0, 0], x: 'right', y: 'down', unit: 'px', pixel_scale: 1 },
    zoom: state.ui.zoom,
    language: state.ui.language,
  };
}
export function validateReply(reply, task) {
  exact(reply, [
    'version',
    'task_id',
    'revision',
    'box_ids',
    'summary',
    'actions',
    'proposals',
    ...('question' in reply ? ['question'] : []),
  ]);
  if (
    'question' in reply &&
    (typeof reply.question !== 'string' ||
      reply.question.length > 500 ||
      (reply.question &&
        (!Array.isArray(reply.actions) ||
          !Array.isArray(reply.proposals) ||
          reply.actions.length ||
          reply.proposals.length)))
  )
    throw Error('invalidReply');
  if (
    reply.version !== 1 ||
    reply.task_id !== task.task_id ||
    reply.revision !== task.revision ||
    JSON.stringify(reply.box_ids) !== JSON.stringify(task.box_ids) ||
    typeof reply.summary !== 'string' ||
    reply.summary.length > 1500 ||
    !Array.isArray(reply.actions) ||
    reply.actions.length > 100 ||
    !Array.isArray(reply.proposals) ||
    reply.proposals.length > 100
  )
    throw new Error('invalidReply');
  for (const op of reply.actions) {
    if (op.type === 'patch') {
      exact(op, ['type', 'box_id', 'changes']);
      validatePatch(op.changes);
    } else if (op.type === 'scale') {
      exact(op, ['type', 'box_id', 'factor']);
      if (
        typeof op.factor !== 'number' ||
        !Number.isFinite(op.factor) ||
        op.factor <= 0 ||
        op.factor > 10
      )
        throw new Error('invalidReply');
    } else if (op.type === 'grid') {
      exact(op, ['type', 'spacing', 'magnet']);
      if (
        typeof op.spacing !== 'number' ||
        !Number.isFinite(op.spacing) ||
        op.spacing < 0.25 ||
        op.spacing > 1000 ||
        typeof op.magnet !== 'number' ||
        !Number.isFinite(op.magnet) ||
        op.magnet < 0 ||
        op.magnet > op.spacing / 2
      )
        throw new Error('invalidGrid');
    } else throw new Error('invalidReply');
    if (op.box_id && !task.box_ids.includes(op.box_id)) throw new Error('invalidTargets');
  }
  const ids = new Set();
  for (const p of reply.proposals) {
    exact(p, ['id', 'source_task', 'title', 'description', 'changes']);
    if (
      typeof p.id !== 'string' ||
      !p.id ||
      ids.has(p.id) ||
      p.source_task !== task.task_id ||
      typeof p.title !== 'string' ||
      !p.title ||
      p.title.length > 100 ||
      typeof p.description !== 'string' ||
      p.description.length > 500 ||
      'x' in p.changes ||
      'y' in p.changes
    )
      throw new Error('invalidReply');
    ids.add(p.id);
    validatePatch(p.changes);
  }
  return reply;
}
// Deliberately conservative automatic-change policy. Larger/compound edits are
// genuine document previews, validated before display and again before apply.
export function isSmallChange(reply, state) {
  if (reply.proposals.length || reply.actions.length !== 1) return false;
  const op = reply.actions[0],
    b = state.boxes.find((b) => b.id === op.box_id);
  if (
    op.type !== 'patch' ||
    !b ||
    state.selection.length !== 1 ||
    state.boxes.some((c) => c.parentId === b.id)
  )
    return false;
  const keys = Object.keys(op.changes);
  if (keys.length === 1 && keys[0] === 'label') return op.changes.label.length <= 80;
  if (keys.length === 1 && ['width', 'height'].includes(keys[0])) {
    const k = keys[0];
    return Math.abs(op.changes[k] - b[k]) <= b[k] * 0.1 + 1e-9;
  }
  return false;
}
export function createWhiteboardBridge(store, request = fetch, projects = null) {
  const timers = new Map(),
    accepting = new Set();
  async function api(url, options) {
    const response = await request(url, { ...options, signal: AbortSignal.timeout(12000) });
    const payload = await response.json();
    if (!response.ok) throw Error(payload.error || 'disconnected');
    return payload;
  }
  function update(id, changes) {
    store.dispatch({ type: 'taskUpdate', task_id: id, changes });
  }
  const taskFor = (id) => store.getState().tasks.find((t) => t.task_id === id);
  async function checkpoint(task, kind) {
    if (projects)
      await projects.snapshot({
        kind,
        task_id: task.task_id,
        pre_snapshot: task.pre_snapshot,
        instruction: task.instruction,
        parent_task_id: task.parent_task_id || null,
      });
  }
  function current(task) {
    const s = store.getState();
    return (
      s.revision === task.revision &&
      s.activeLayer === task.activeLayer &&
      JSON.stringify(s.selection) === JSON.stringify(task.box_ids) &&
      !s.ui.grabbed &&
      !s.ui.preview
    );
  }
  function preview(task, reply) {
    const candidate = store.candidate({
      type: 'aiApply',
      task_id: task.task_id,
      actions: reply.actions,
    });
    store.dispatch({
      type: 'aiPreview',
      preview: { task_id: task.task_id, boxes: candidate.boxes, grid: candidate.grid },
    });
  }
  async function apply(taskId) {
    const task = taskFor(taskId);
    if (!task || task.applied) return;
    if (!current(task)) {
      update(taskId, { status: 'stale', error: 'staleReply' });
      store.dispatch({ type: 'aiPreviewClear' });
      await checkpoint(task, 'stale');
      return;
    }
    const action = { type: 'aiApply', task_id: taskId, actions: task.reply.actions };
    try {
      if (projects)
        await projects.apply(action, {
          task_id: taskId,
          pre_snapshot: task.pre_snapshot,
          instruction: task.instruction,
        });
      else {
        const result = store.dispatch(action);
        if (!result.ok) throw Error(result.error);
      }
      store.dispatch({ type: 'aiPreviewClear' });
      store.dispatch({ type: 'notice', message: 'changed' });
    } catch (e) {
      update(taskId, {
        status: e.message === 'staleReply' ? 'stale' : 'aiPreview',
        error: e.message,
      });
      store.dispatch({ type: 'aiPreviewClear' });
      throw e;
    }
  }
  async function accept(payload) {
    const task = taskFor(payload.task_id);
    if (!task) throw Error('unknownTask');
    if (task.archived || task.applied || task.received || accepting.has(task.task_id)) return;
    accepting.add(task.task_id);
    try {
      const reply = validateReply(payload.reply, task);
      if (!current(task)) {
        update(task.task_id, {
          status: 'stale',
          reply,
          received: true,
          evidence: payload.evidence,
        });
        await checkpoint(task, 'stale');
        return;
      }
      update(task.task_id, { reply, received: true, evidence: payload.evidence });
      if (reply.question) {
        update(task.task_id, { status: 'question' });
        await checkpoint(task, 'clarificationSnapshot');
      } else if (reply.actions.length) {
        // candidate validates the entire batch, including geometry, atomically.
        const candidate = store.candidate({
          type: 'aiApply',
          task_id: task.task_id,
          actions: reply.actions,
        });
        const actual = store.getState();
        if (
          JSON.stringify([candidate.boxes, candidate.grid]) ===
          JSON.stringify([actual.boxes, actual.grid])
        ) {
          update(task.task_id, { status: 'noChange' });
          await checkpoint(task, 'noChange');
          return;
        }
        if (!projects || isSmallChange(reply, store.getState())) await apply(task.task_id);
        else {
          update(task.task_id, { status: 'aiPreview' });
          preview(task, reply);
          await checkpoint(task, 'previewSnapshot');
        }
      } else {
        update(task.task_id, { status: reply.proposals.length ? 'ready' : 'noChange' });
        await checkpoint(task, reply.proposals.length ? 'ready' : 'noChange');
      }
    } finally {
      accepting.delete(task.task_id);
    }
  }
  async function poll(taskId) {
    clearTimeout(timers.get(taskId));
    if (!taskFor(taskId) || taskFor(taskId).archived) return;
    try {
      const payload = await api(`/api/tasks/${encodeURIComponent(taskId)}`);
      if (!taskFor(taskId)) return;
      if (payload.status === 'ready') await accept(payload);
      else if (payload.status === 'failed') {
        update(taskId, { status: 'failed', error: payload.error });
        await checkpoint(taskFor(taskId), 'failedSnapshot');
      } else {
        if (!['waiting', 'claimed', 'running'].includes(payload.status))
          throw Error('invalidReply');
        update(taskId, { status: payload.status });
        timers.set(
          taskId,
          setTimeout(() => poll(taskId), 800),
        );
      }
    } catch (e) {
      const task = taskFor(taskId);
      if (task?.status === 'aiPreview' && e.message === 'saveFailed') return;
      update(taskId, {
        status:
          ['disconnected', 'TimeoutError', 'TypeError'].includes(e.message) ||
          ['TimeoutError', 'TypeError'].includes(e.name)
            ? 'disconnected'
            : 'failed',
        error: e.message,
      });
      try {
        await checkpoint(taskFor(taskId), 'failedSnapshot');
      } catch {}
    }
  }
  return {
    status: () => api('/api/status'),
    poll,
    accept,
    apply,
    async discard(taskId) {
      const task = taskFor(taskId);
      if (!task || task.applied) return;
      update(taskId, { status: 'discarded', received: true });
      store.dispatch({ type: 'aiPreviewClear' });
      await checkpoint(task, 'discarded');
    },
    showPreview(taskId) {
      const task = taskFor(taskId);
      if (task && current(task)) preview(task, task.reply);
    },
    async submit(instruction, parentTaskId = null) {
      const s = store.getState();
      if (s.ui.grabbed || s.ui.preview) throw Error('finishGesture');
      if (!instruction.trim() || instruction.length > 1000) throw Error('emptyOrder');
      const previous = parentTaskId
        ? s.tasks.find((t) => t.task_id === parentTaskId)
        : s.tasks.at(-1);
      const task = {
        task_id: crypto.randomUUID(),
        box_ids: s.selection,
        revision: s.revision,
        activeLayer: s.activeLayer,
        instruction,
        status: 'saving',
        applied: false,
        received: false,
        parent_task_id: previous?.task_id || null,
        selection_changed:
          !!previous && JSON.stringify(previous.box_ids) !== JSON.stringify(s.selection),
        created_at: new Date().toISOString(),
      };
      store.dispatch({ type: 'aiPreviewClear' });
      store.dispatch({ type: 'taskAdd', task });
      try {
        let conversation;
        if (projects) {
          const before = await projects.snapshot(
            {
              kind: 'preRequest',
              task_id: task.task_id,
              instruction,
              parent_task_id: task.parent_task_id,
              revision: task.revision,
              box_ids: task.box_ids,
            },
            store.getState(),
          );
          task.pre_snapshot = before.head;
          update(task.task_id, { pre_snapshot: before.head });
          conversation = {
            version: 1,
            project_id: projects.info().project,
            snapshot_id: before.head,
            parent_task_id: task.parent_task_id,
            selection_changed: task.selection_changed,
            turns: (previous
              ? [...s.tasks.filter((t) => t.task_id !== previous.task_id).slice(-1), previous]
              : s.tasks.slice(-2)
            ).map((t) => ({
              task_id: t.task_id,
              instruction: t.instruction,
              summary: t.reply?.summary || '',
              question: t.clarification?.question || t.reply?.question || '',
              box_ids: t.box_ids,
              status: t.status,
              actions: t.reply?.actions || [],
              proposals: t.reply?.proposals || [],
            })),
          };
        }
        if (!current(task)) {
          update(task.task_id, { status: 'stale', error: 'selectionChanged' });
          await checkpoint(task, 'stale');
          return task.task_id;
        }
        if (projects && !s.selection.length && !previous?.clarification) {
          // A product precondition, explicitly not a simulated model answer.
          update(task.task_id, {
            status: 'question',
            received: true,
            clarification: {
              origin: 'selection-guard',
              question: t(s.ui.language, 'targetQuestion'),
            },
          });
          await checkpoint(task, 'clarificationSnapshot');
          return task.task_id;
        }
        await api('/api/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task_id: task.task_id,
            instruction,
            box_ids: task.box_ids,
            revision: task.revision,
            snapshot: snapshot(s),
            ...(conversation ? { conversation } : {}),
          }),
        });
        update(task.task_id, { status: 'waiting' });
        await poll(task.task_id);
      } catch (e) {
        update(task.task_id, {
          status: ['TypeError', 'TimeoutError'].includes(e.name) ? 'disconnected' : 'failed',
          error: e.message,
        });
        try {
          await checkpoint(task, 'failedSnapshot');
        } catch {}
        throw e;
      }
      return task.task_id;
    },
  };
}
