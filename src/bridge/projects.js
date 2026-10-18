import { clone, initialState, validateState } from '../core/model.js';
import { frame } from '../core/store.js';
import { renderSnapshotPreview } from '../workspace/render.js';
import { t } from '../i18n.js';
const FORMAT = 1;
export function projectBody(store, state = store.getState(), history = store.exportHistory()) {
  const ui = state.ui;
  return {
    format: FORMAT,
    state: {
      ...frame(state),
      revision: state.revision,
      tasks: clone(state.tasks),
      ui: {
        language: ui.language,
        view: ui.view,
        zoom: ui.zoom,
        monitorLastId: ui.monitor.last?.id || null,
      },
    },
    history: clone(history),
  };
}
export function hydrate(body, current = initialState(), restored = false) {
  if (body?.format !== FORMAT) throw Error('storageFormat');
  const s = {
    ...initialState(),
    ...clone(body.state),
    ui: {
      ...initialState().ui,
      ...clone(body.state.ui),
      monitor: clone(current.ui.monitor),
      grabbed: null,
      preview: null,
    },
  };
  s.ui.monitor.last = clone(
    s.boxes.find((b) => b.id === body.state.ui.monitorLastId) ||
      s.boxes.find((b) => b.id === s.selection[0]) ||
      null,
  );
  s.tasks = s.tasks.map((task) =>
    ['saving', 'waiting', 'claimed', 'running'].includes(task.status)
      ? { ...task, status: 'disconnected', archived: restored }
      : restored
        ? { ...task, archived: true }
        : task,
  );
  return validateState(s);
}
export function createProjects(store, request = fetch) {
  let project = null,
    head = null,
    name = '',
    saved = '',
    timer = null,
    tail = Promise.resolve(),
    paused = true,
    problem = null;
  const listeners = new Set();
  const info = () => ({ project, head, name, problem });
  function emit(status) {
    for (const fn of listeners) fn({ ...info(), status });
  }
  async function api(url, options) {
    const r = await request(url, { ...options, signal: AbortSignal.timeout(12000) });
    const data = await r.json();
    if (!r.ok) throw Error(data.error || 'saveFailed');
    return data;
  }
  function queue(fn) {
    const next = tail.then(fn, fn);
    tail = next.catch(() => {});
    return next;
  }
  function report(e) {
    clearTimeout(timer);
    problem =
      e.message === 'storageConflict'
        ? 'storageConflict'
        : e.message === 'storageFormat'
          ? 'storageFormat'
          : 'saveFailed';
    emit('failed');
    store.dispatch({ type: 'notice', message: problem, error: true });
  }
  async function write(body, meta) {
    if (!project) throw Error('saveFailed');
    emit('saving');
    try {
      const result = await api(`/api/projects/${project}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base: head, body, meta: { name, ...meta } }),
      });
      head = result.head;
      saved = JSON.stringify(body);
      problem = null;
      emit('saved');
      return result;
    } catch (e) {
      report(e);
      throw e;
    }
  }
  store.subscribe(() => {
    if (paused || !project || problem) return;
    clearTimeout(timer);
    if (JSON.stringify(projectBody(store)) !== saved) emit('pendingSave');
    timer = setTimeout(() => {
      if (JSON.stringify(projectBody(store)) !== saved)
        queue(() => write(projectBody(store), { kind: 'automatic' })).catch(() => {});
    }, 500);
  });
  window.addEventListener('beforeunload', (e) => {
    if (!paused && project && JSON.stringify(projectBody(store)) !== saved) {
      e.preventDefault();
      e.returnValue = '';
    }
  });
  const apiObject = {
    info,
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    async init() {
      try {
        const data = await api('/api/projects');
        if (data.format !== FORMAT) throw Error('storageFormat');
        const remembered = localStorage.getItem('blockdesigner.project.v1');
        const chosen =
          data.projects.find((p) => p.id === remembered && !p.error) ||
          data.projects.find((p) => !p.error);
        if (data.projects.length && !chosen)
          throw Error(
            data.projects.some((p) => p.error === 'storageFormat')
              ? 'storageFormat'
              : 'storageCorrupt',
          );
        if (chosen) await apiObject.open(chosen.id);
        else await apiObject.create('Projekt 1');
      } catch (e) {
        paused = false;
        report(e);
      }
    },
    list: () => api('/api/projects'),
    dirty: () => JSON.stringify(projectBody(store)) !== saved,
    async open(id) {
      return queue(async () => {
        clearTimeout(timer);
        const wasPaused = paused;
        store.end();
        paused = true;
        store.lock(true);
        try {
          if (!wasPaused && project && JSON.stringify(projectBody(store)) !== saved)
            await write(projectBody(store), { kind: 'automatic' });
          const data = await api(`/api/projects/${id}`);
          project = id;
          head = data.head;
          name = data.snapshot.name;
          store.replace(hydrate(data.body, store.getState()), { history: data.body.history });
          saved = JSON.stringify(projectBody(store));
          localStorage.setItem('blockdesigner.project.v1', project);
          problem = null;
          emit('saved');
          if (data.warning) store.dispatch({ type: 'notice', message: data.warning, error: true });
        } catch (e) {
          report(e);
          throw e;
        } finally {
          store.lock(false);
          paused = false;
        }
      });
    },
    async create(projectName) {
      return queue(async () => {
        clearTimeout(timer);
        const wasPaused = paused;
        store.end();
        paused = true;
        store.lock(true);
        try {
          if (!wasPaused && project && JSON.stringify(projectBody(store)) !== saved)
            await write(projectBody(store), { kind: 'automatic' });
          const next = initialState();
          next.ui.monitor = store.getState().ui.monitor;
          const candidateId = crypto.randomUUID(),
            old = { project, head, name };
          project = candidateId;
          head = null;
          name = projectName.trim().slice(0, 120) || 'Projekt';
          try {
            await write(projectBody(store, next, { undo: [], redo: [] }), { kind: 'created' });
          } catch (e) {
            ({ project, head, name } = old);
            throw e;
          }
          store.replace(next, { resetHistory: true });
          localStorage.setItem('blockdesigner.project.v1', project);
        } catch (e) {
          report(e);
          throw e;
        } finally {
          store.lock(false);
          paused = false;
        }
      });
    },
    async rename(value) {
      return queue(() => {
        name = value.trim().slice(0, 120) || name;
        return write(projectBody(store), { kind: 'renamed' });
      });
    },
    flush(meta = { kind: 'automatic' }) {
      clearTimeout(timer);
      return queue(() => write(projectBody(store), meta));
    },
    snapshot(meta, state = null) {
      clearTimeout(timer);
      return queue(() => write(projectBody(store, state || store.getState()), meta));
    },
    history: () => api(`/api/projects/${project}/history`),
    inspect: (id) => api(`/api/projects/${project}/snapshots/${id}`),
    async restore(id) {
      return queue(async () => {
        clearTimeout(timer);
        paused = true;
        store.lock(true);
        try {
          await write(projectBody(store), { kind: 'beforeRestore', restore_of: id });
          const chosen = await apiObject.inspect(id);
          const candidate = hydrate(chosen.body, store.getState(), true);
          candidate.revision = store.getState().revision + 1;
          const result = await write(projectBody(store, candidate, chosen.body.history), {
            kind: 'restoredSnapshot',
            restore_of: id,
          });
          store.replace(candidate, { history: chosen.body.history });
          store.dispatch({ type: 'notice', message: 'restored' });
          return result;
        } catch (e) {
          report(e);
          throw e;
        } finally {
          store.lock(false);
          paused = false;
        }
      });
    },
    // Save a validated resulting document before exposing the change. This is
    // also the gateway for explicit design-proposal application.
    async apply(action, meta = {}) {
      return queue(async () => {
        clearTimeout(timer);
        paused = true;
        store.lock(true);
        try {
          const { state: candidate, history } = store.prepare(action);
          const result = await write(projectBody(store, candidate, history), {
            kind: 'resultSnapshot',
            ...meta,
          });
          store.commitCandidate(candidate, action);
          return result;
        } catch (e) {
          report(e);
          throw e;
        } finally {
          store.lock(false);
          paused = false;
        }
      });
    },
  };
  return apiObject;
}
export function mountProjects(projects, store, root) {
  const panel = root.querySelector('#projects-panel'),
    select = document.createElement('select'),
    name = document.createElement('input'),
    create = document.createElement('button');
  const projectField = document.createElement('label');
  projectField.className = 'np-field';
  const title = document.createElement('span');
  title.dataset.i18n = 'project';
  projectField.append(title, select);
  panel.append(projectField);
  const nameField = document.createElement('label');
  nameField.className = 'np-field';
  const label = document.createElement('span');
  label.dataset.i18n = 'projectName';
  nameField.append(label, name);
  name.maxLength = 120;
  panel.append(nameField);
  create.className = 'np-button';
  create.dataset.i18n = 'newProject';
  panel.append(create);
  async function refresh() {
    try {
      const data = await projects.list();
      select.replaceChildren();
      for (const p of data.projects) {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent =
          p.name + (p.error ? ` · ${t(store.getState().ui.language, p.error)}` : '');
        option.disabled = !!p.error;
        select.append(option);
      }
      select.value = projects.info().project;
      if (document.activeElement !== name) name.value = projects.info().name;
    } catch {}
  }
  name.addEventListener('change', () =>
    projects
      .rename(name.value)
      .then(refresh)
      .catch(() => {}),
  );
  select.addEventListener('change', () =>
    projects
      .open(select.value)
      .then(refresh)
      .catch((e) => store.dispatch({ type: 'notice', message: e.message, error: true })),
  );
  create.addEventListener('click', () =>
    projects
      .create(`Projekt ${new Date().toLocaleString()}`)
      .then(refresh)
      .catch(() => {}),
  );
  root
    .querySelector('#retry-save')
    .addEventListener('click', () => projects.flush().catch(() => {}));
  let status = 'saved';
  const render = () => {
    const info = projects.info(),
      el = root.querySelector('#storage-status');
    el.textContent = `${info.name} · ${t(store.getState().ui.language, info.problem || status)}`;
    el.dataset.error = String(!!info.problem);
    const indicator = root.querySelector('#save-indicator');
    indicator.textContent = t(store.getState().ui.language, info.problem || status);
    indicator.title = info.name;
    indicator.dataset.error = String(!!info.problem);
    root.querySelector('#retry-save').hidden = !info.problem;
  };
  projects.subscribe((info) => {
    status = info.status === 'failed' ? 'saveFailed' : info.status;
    render();
  });
  store.subscribe(render);
  refresh();
  const dialog = root.querySelector('#history-dialog');
  let previous = null;
  async function show() {
    const list = root.querySelector('#history-list');
    list.replaceChildren();
    try {
      const data = await projects.history();
      for (const item of data.items) {
        const card = document.createElement('article'),
          p = document.createElement('p');
        p.textContent = `${new Date(item.at).toLocaleString()} · ${t(store.getState().ui.language, item.kind)} · r${item.revision} · ${item.id.slice(0, 8)}`;
        card.append(p);
        if (item.meta.instruction) {
          const task = document.createElement('p');
          task.textContent = item.meta.instruction;
          card.append(task);
        }
        for (const action of ['inspect', 'restore']) {
          const button = document.createElement('button');
          button.className = 'np-button';
          button.textContent = t(store.getState().ui.language, action);
          button.dataset.snapshot = item.id;
          button.dataset.action = action;
          button.addEventListener('click', async () => {
            try {
              if (action === 'inspect') {
                const viewed = await projects.inspect(item.id);
                renderSnapshotPreview(root.querySelector('#history-inspect'), viewed.body.state);
              } else {
                await projects.restore(item.id);
                root.querySelector('#history-inspect').textContent = '';
                await show();
              }
            } catch (e) {
              store.dispatch({ type: 'notice', message: e.message, error: true });
              root.querySelector('#history-inspect').textContent = t(
                store.getState().ui.language,
                e.message,
              );
            }
          });
          card.append(button);
        }
        list.append(card);
      }
    } catch (e) {
      list.textContent = t(store.getState().ui.language, e.message);
    }
  }
  root.querySelector('#history').addEventListener('click', async () => {
    previous = document.activeElement;
    try {
      await projects.flush();
    } catch {}
    dialog.showModal();
    await show();
    root.querySelector('#close-history').focus();
  });
  root.querySelector('#close-history').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => previous?.focus());
}
