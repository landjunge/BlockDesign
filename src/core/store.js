import { clone, initialState, validateState } from './model.js';
import { reduce } from './actions.js';

export function createStore(initial = initialState()) {
  let state = validateState(clone(initial));
  const listeners = new Set();
  return {
    getState: () => clone(state),
    subscribe(fn) { listeners.add(fn); fn(clone(state)); return () => listeners.delete(fn); },
    dispatch(action) {
      try {
        const next = validateState(reduce(state, { version: 1, ...action }));
        state = next;
        for (const fn of listeners) fn(clone(state));
        return { ok: true, revision: state.revision };
      } catch (err) {
        // Rejected batches never partially mutate the document.
        state = { ...state, ui: { ...state.ui, notice: err.message, noticeArgs: {}, error: true } };
        for (const fn of listeners) fn(clone(state));
        return { ok: false, error: err.message };
      }
    },
  };
}
