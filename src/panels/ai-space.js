import { createWhiteboardBridge } from '../bridge/whiteboard.js';
import { proposalCard } from './proposal.js';
import { t } from '../i18n.js';
export function mountAI(store, root) {
  const bridge = createWhiteboardBridge(store), send = root.querySelector('#send'), order = root.querySelector('#order');
  let connection = { ok: false, pending: true };
  let wasPending = false;
  async function check() {
    try { connection = await bridge.status(); } catch { connection = { ok: false }; }
    render(store.getState());
  }
  root.querySelector('#ai-form').addEventListener('submit', async e => {
    e.preventDefault();
    try { await bridge.submit(order.value); }
    catch (err) { store.dispatch({ type: 'notice', message: err.message, error: true }); }
  });
  function render(s) {
    const lang = s.ui.language;
    const pending = s.tasks.some(task => ['waiting', 'claimed', 'running'].includes(task.status));
    if (wasPending && !pending) queueMicrotask(check);
    wasPending = pending;
    root.querySelector('#connection').textContent = t(lang, connection.pending ? 'connection' : connection.ok ? 'online' : 'offline', { model: connection.model })
      + (connection.busy && !pending ? ` · ${t(lang, 'busy')}` : '');
    send.disabled = !connection.ok || connection.busy || s.tasks.some(task => ['waiting', 'claimed', 'running', 'disconnected'].includes(task.status)) || !!s.ui.preview || !!s.ui.grabbed;
    const list = root.querySelector('#tasks');
    const active = document.activeElement, focusedTask = active?.closest('[data-task-id]')?.dataset.taskId, focusedAction = active?.dataset.action;
    list.replaceChildren();
    if (!s.tasks.length) { const p = document.createElement('p'); p.className = 'np-meta'; p.textContent = t(lang, 'noTasks'); list.append(p); }
    for (const task of [...s.tasks].reverse()) {
      const card = document.createElement('article'); card.className = 'task-card'; card.dataset.taskId = task.task_id; card.dataset.status = task.status;
      const title = document.createElement('h3'); title.textContent = task.instruction;
      const status = document.createElement('p'); status.className = 'task-state'; status.textContent = t(lang, task.status);
      const ref = document.createElement('p'); ref.className = 'np-meta'; ref.textContent = `${t(lang, 'task')} ${task.task_id.slice(0, 8)} · ${t(lang, 'revision')} ${task.revision}`;
      card.append(title, status, ref);
      if (task.error && task.status !== 'disconnected') { const error = document.createElement('p'); error.textContent = t(lang, task.error); card.append(error); }
      if (task.status === 'disconnected') {
        const retry = document.createElement('button'); retry.className = 'np-button'; retry.dataset.action = 'reconnect'; retry.textContent = t(lang, 'reconnect');
        retry.addEventListener('click', () => { bridge.poll(task.task_id); check(); }); card.append(retry);
      }
      if (task.reply) {
        const summary = document.createElement('p'); summary.textContent = task.reply.summary; card.append(summary);
        for (const proposal of task.reply.proposals) card.append(proposalCard(proposal, store));
      }
      list.append(card);
    }
    if (focusedTask && focusedAction) list.querySelector(`[data-task-id="${CSS.escape(focusedTask)}"] [data-action="${CSS.escape(focusedAction)}"]`)?.focus({ preventScroll: true });
  }
  store.subscribe(render); check();
  const interval = setInterval(check, 15000);
  window.addEventListener('pagehide', () => clearInterval(interval), { once: true });
  return bridge;
}
