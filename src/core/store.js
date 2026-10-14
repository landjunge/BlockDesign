import { clone, initialState, validateState } from './model.js';
import { reduce } from './actions.js';
export const frame = (s) =>
  Object.fromEntries(
    [
      'version',
      'document',
      'boxes',
      'nextNumber',
      'creationCounts',
      'activeLayer',
      'selection',
      'grid',
      'myspace',
    ].map((k) => [k, clone(s[k])]),
  );
const signature = (s) => JSON.stringify([s.document, s.boxes, s.nextNumber, s.grid, s.myspace]);
export function createStore(initial = initialState()) {
  let state = validateState(clone(initial)),
    undo = [],
    redo = [],
    transaction = null,
    locked = false;
  const listeners = new Set();
  function emit() {
    for (const fn of listeners) fn(clone(state));
  }
  function fail(error) {
    state.ui = { ...state.ui, notice: error, noticeArgs: {}, error: true };
    emit();
    return { ok: false, error };
  }
  function remember(before, after, label) {
    if (signature(before) !== signature(after)) {
      undo.push({ state: frame(before), label });
      redo = [];
    }
  }
  const api = {
    getState: () => clone(state),
    subscribe(fn) {
      listeners.add(fn);
      fn(clone(state));
      return () => listeners.delete(fn);
    },
    history: () => ({
      undo: undo.length,
      redo: redo.length,
      undoLabel: undo.at(-1)?.label,
      redoLabel: redo.at(-1)?.label,
    }),
    exportHistory: () => clone({ undo, redo }),
    importHistory(h) {
      undo = clone(h?.undo || []);
      redo = clone(h?.redo || []);
      for (const item of [...undo, ...redo]) validateState({ ...initialState(), ...item.state });
      emit();
    },
    begin(label) {
      if (!transaction) transaction = { state: clone(state), label };
    },
    end() {
      if (transaction) {
        remember(transaction.state, state, transaction.label);
        transaction = null;
        emit();
      }
    },
    lock(value) {
      locked = value;
    },
    candidate(action) {
      return validateState(reduce(state, { version: 1, ...action }));
    },
    prepare(action) {
      const next = api.candidate(action),
        history = api.exportHistory();
      if (signature(state) !== signature(next)) {
        history.undo.push({
          state: frame(state),
          label: action.type === 'aiApply' ? `KI ${action.task_id}` : action.type,
        });
        history.redo = [];
      }
      return { state: next, history };
    },
    replace(next, { history = null, resetHistory = false } = {}) {
      state = validateState(clone(next));
      transaction = null;
      if (resetHistory) {
        undo = [];
        redo = [];
      }
      if (history) {
        undo = clone(history.undo);
        redo = clone(history.redo);
      }
      emit();
    },
    commitCandidate(next, action) {
      const before = clone(state);
      state = validateState({
        ...clone(next),
        ui: {
          ...state.ui,
          aiPreview: null,
          monitor: { ...state.ui.monitor, last: clone(next.ui.monitor.last) },
        },
      });
      remember(before, state, action.type === 'aiApply' ? `KI ${action.task_id}` : action.type);
      emit();
      return { ok: true, revision: state.revision };
    },
    dispatch(action) {
      if (
        locked &&
        ![
          'notice',
          'monitor',
          'language',
          'view',
          'zoom',
          'taskUpdate',
          'aiPreview',
          'aiPreviewClear',
        ].includes(action.type)
      )
        return fail('savingBusy');
      try {
        if (['undo', 'redo'].includes(action.type)) {
          if (state.ui.grabbed || state.ui.preview) throw Error('finishGesture');
          const source = action.type === 'undo' ? undo : redo,
            target = action.type === 'undo' ? redo : undo,
            item = source.at(-1);
          if (!item) return { ok: true, revision: state.revision };
          const next = validateState({
            ...clone(state),
            ...clone(item.state),
            revision: state.revision + 1,
            ui: { ...state.ui, grabbed: null, preview: null, notice: action.type, error: false },
          });
          target.push({ state: frame(state), label: item.label });
          source.pop();
          state = next;
          emit();
          return { ok: true, revision: state.revision };
        }
        if (
          transaction &&
          ['layer', 'select', 'create', 'group', 'previewStart', 'parent'].includes(action.type)
        ) {
          remember(transaction.state, state, transaction.label);
          transaction = null;
        }
        const before = state,
          next = validateState(reduce(state, { version: 1, ...action }));
        state = next;
        if (!transaction) remember(before, next, action.type);
        emit();
        return { ok: true, revision: state.revision };
      } catch (err) {
        return fail(err.message);
      }
    },
  };
  return api;
}
