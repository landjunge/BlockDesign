import { createWhiteboardBridge } from '../bridge/whiteboard.js';
import { proposalCard, changeSummary } from './proposal.js';
import { t } from '../i18n.js';
export function mountAI(store, root, projects = null) {
  const bridge = createWhiteboardBridge(store, fetch, projects),
    send = root.querySelector('#send'),
    order = root.querySelector('#order');
  const grow = () => {
    order.style.height = 'auto';
    order.style.height = `${Math.min(200, Math.max(40, order.scrollHeight))}px`;
  };
  order.addEventListener('input', grow);
  grow();
  let parentTaskId = null;
  let connection = { ok: false, pending: true };
  let wasPending = false;
  async function check() {
    try {
      connection = await bridge.status();
    } catch {
      connection = { ok: false };
    }
    render(store.getState());
  }
  root.querySelector('#ai-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const text = order.value;
      await bridge.submit(text, parentTaskId);
      parentTaskId = null;
      if (order.value === text) {
        order.value = '';
        grow();
      }
    } catch (err) {
      store.dispatch({ type: 'notice', message: err.message, error: true });
    }
  });
  function render(s) {
    const lang = s.ui.language;
    const parent = s.tasks.find((t) => t.task_id === parentTaskId);
    if (parentTaskId && !parent) parentTaskId = null;
    const context = root.querySelector('#reply-context');
    context.hidden = !parent;
    context.textContent = parent
      ? `${t(lang, 'answer')} · ${parent.task_id.slice(0, 8)}: ${parent.clarification?.question || parent.reply?.question || parent.instruction}`
      : '';
    const pending = s.tasks.some(
      (task) => !task.archived && ['saving', 'waiting', 'claimed', 'running'].includes(task.status),
    );
    if (wasPending && !pending) queueMicrotask(check);
    wasPending = pending;
    root.querySelector('#connection').textContent =
      t(lang, connection.pending ? 'connection' : connection.ok ? 'online' : 'offline', {
        model: connection.model,
      }) + (connection.busy && !pending ? ` · ${t(lang, 'busy')}` : '');
    send.disabled =
      !connection.ok ||
      connection.busy ||
      s.tasks.some(
        (task) =>
          !task.archived &&
          ['saving', 'waiting', 'claimed', 'running', 'disconnected'].includes(task.status),
      ) ||
      !!s.ui.preview ||
      !!s.ui.grabbed;
    const list = root.querySelector('#tasks');
    const active = document.activeElement,
      focusedTask = active?.closest('[data-task-id]')?.dataset.taskId,
      focusedAction = active?.dataset.action;
    list.replaceChildren();
    if (!s.tasks.length) {
      const p = document.createElement('p');
      p.className = 'np-meta';
      p.textContent = t(lang, 'noTasks');
      list.append(p);
    }
    for (const task of [...s.tasks].reverse()) {
      const card = document.createElement('article');
      card.className = 'task-card';
      card.dataset.taskId = task.task_id;
      card.dataset.status = task.status;
      const title = document.createElement('h3');
      title.textContent = task.instruction;
      const status = document.createElement('p');
      status.className = 'task-state';
      status.textContent = t(lang, task.status);
      const ref = document.createElement('p');
      ref.className = 'np-meta';
      ref.textContent = `${t(lang, 'task')} ${task.task_id.slice(0, 8)} · ${t(lang, 'revision')} ${task.revision}`;
      const targets = document.createElement('p');
      targets.className = 'np-meta';
      targets.textContent = `${t(lang, 'selection')}: ${task.box_ids.map((id) => s.boxes.find((b) => b.id === id)?.number || id.slice(0, 8)).join(', ') || '—'}`;
      card.append(title, status, targets, ref);
      for (const application of task.proposal_applications || []) {
        const used = document.createElement('p');
        used.className = 'np-meta';
        used.textContent = `${t(lang, 'applied')}: ${application.box_ids.map((id) => s.boxes.find((b) => b.id === id)?.number || id.slice(0, 8)).join(', ')} · r${application.revision}`;
        card.append(used);
      }
      if (task.selection_changed) {
        const changed = document.createElement('p');
        changed.textContent = t(lang, 'selectionChanged');
        card.append(changed);
      }
      if (task.error && task.status !== 'disconnected') {
        const error = document.createElement('p');
        error.textContent = t(lang, task.error);
        card.append(error);
      }
      if (task.status === 'disconnected' && !task.archived) {
        const retry = document.createElement('button');
        retry.className = 'np-button';
        retry.dataset.action = 'reconnect';
        retry.textContent = t(lang, 'reconnect');
        retry.addEventListener('click', () => {
          bridge.poll(task.task_id);
          check();
        });
        card.append(retry);
      }
      if (task.clarification?.question || task.reply?.question) {
        const q = document.createElement('p');
        const question = task.clarification?.question || task.reply.question;
        q.textContent = (task.clarification ? t(lang, 'localQuestion') + ' · ' : '') + question;
        card.append(q);
        const answer = document.createElement('button');
        answer.className = 'np-button';
        answer.dataset.action = 'answer';
        answer.textContent = t(lang, 'answer');
        answer.addEventListener('click', () => {
          parentTaskId = task.task_id;
          order.placeholder = question;
          render(store.getState());
          order.focus();
        });
        card.append(answer);
      }
      if (task.reply) {
        const summary = document.createElement('p');
        summary.textContent = task.reply.summary;
        card.append(summary);
        for (const proposal of task.reply.proposals)
          card.append(proposalCard(proposal, store, false, projects));
        if (task.status === 'aiPreview') {
          const diff = document.createElement('section');
          diff.className = 'ai-preview';
          const values = document.createElement('pre');
          values.textContent = changeSummary(task.reply.actions, s);
          diff.append(values);
          for (const action of ['commit', 'discard']) {
            const button = document.createElement('button');
            button.className = 'np-button';
            button.dataset.action = action;
            button.textContent = t(lang, action);
            button.addEventListener('click', async () => {
              try {
                if (action === 'commit') await bridge.apply(task.task_id);
                else await bridge.discard(task.task_id);
              } catch (e) {
                store.dispatch({ type: 'notice', message: e.message, error: true });
              }
            });
            diff.append(button);
          }
          card.append(diff);
        }
      }
      list.append(card);
    }
    if (focusedTask && focusedAction)
      list
        .querySelector(
          `[data-task-id="${CSS.escape(focusedTask)}"] [data-action="${CSS.escape(focusedAction)}"]`,
        )
        ?.focus({ preventScroll: true });
  }
  store.subscribe(render);
  store.subscribe((s) => {
    const preview = s.ui.aiPreview;
    if (!preview) return;
    const task = s.tasks.find((t) => t.task_id === preview.task_id);
    if (
      !task ||
      task.revision !== s.revision ||
      JSON.stringify(task.box_ids) !== JSON.stringify(s.selection)
    ) {
      store.dispatch({ type: 'aiPreviewClear' });
      if (task && !task.applied)
        store.dispatch({
          type: 'taskUpdate',
          task_id: task.task_id,
          changes: { status: 'stale', error: 'selectionChanged' },
        });
    }
  });
  const pendingPreview = store
    .getState()
    .tasks.find((t) => t.status === 'aiPreview' && !t.archived);
  if (pendingPreview) bridge.showPreview(pendingPreview.task_id);
  check();
  const interval = setInterval(check, 15000);
  window.addEventListener('pagehide', () => clearInterval(interval), { once: true });
  return bridge;
}
