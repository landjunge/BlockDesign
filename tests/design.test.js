import test from 'node:test';
import assert from 'node:assert/strict';
import { createStore } from '../src/core/store.js';
import { initialState } from '../src/core/model.js';
import { hydrate, projectBody } from '../src/bridge/projects.js';
import { bindingState, describeDesign, sourceTransform } from '../src/core/design.js';

const source = hash => ({ version: 1, source: { artifact_sha256: hash, media_type: 'text/html', source_commit: null, reference_viewport: { width: 2000, height: 1280 } }, preview: { artifact_sha256: 'b'.repeat(64), media_type: 'image/png', rendering_mode: 'inert-image' }, catalog: [{ element_id: 'id:left', tag: 'button', count: 1, resolution: 'unique' }, { element_id: 'id:right', tag: 'button', count: 1, resolution: 'unique' }, { element_id: 'id:duplicate', tag: 'button', count: 2, resolution: 'unresolved' }], bindings: {} });
function importSource(store, hash = 'a'.repeat(64)) { assert.ok(store.dispatch({ type: 'designImport', design: source(hash), expected_revision: store.getState().revision }).ok); }
function bind(store, id, operation, element_id = null, extra = {}) {
  return store.dispatch({ type: 'designBind', id, operation, element_id, source_hash: store.getState().design.source.artifact_sha256, expected_revision: store.getState().revision, ...extra });
}
test('move/replace/new keep box identity and exact distinct original IDs over save/reload/zoom', () => {
  const store = createStore();
  for (let i = 0; i < 3; i++) store.dispatch({ type: 'create' });
  const boxes = store.getState().boxes;
  importSource(store);
  assert.ok(bind(store, boxes[0].id, 'move', 'id:left').ok);
  assert.ok(bind(store, boxes[1].id, 'replace', 'id:right').ok);
  assert.ok(bind(store, boxes[2].id, 'new').ok);
  store.dispatch({ type: 'zoom', zoom: 1.5 });
  const saved = projectBody(store), loaded = hydrate(JSON.parse(JSON.stringify(saved)));
  assert.deepEqual(loaded.boxes, boxes);
  assert.equal(loaded.ui.zoom, 1.5);
  assert.deepEqual(sourceTransform(loaded), { scale: .5, x: 0, y: 0 });
  const exported = describeDesign(loaded, 'project', 'snapshot', 'Move left, replace right, add third');
  assert.equal(exported.ready, true);
  assert.deepEqual(exported.descriptor.elements.map(e => e.action), ['move', 'replace', 'new']);
  assert.notDeepEqual(exported.descriptor.elements[0].source_element, exported.descriptor.elements[1].source_element);
  assert.equal(exported.execution_started, false);
  assert.equal(exported.source_commit_verified, false);
  assert.ok(bind(store, boxes[1].id, 'replace', 'id:left').ok);
  assert.equal(describeDesign(store.getState(), 'p', 's', 'Two boxes target one original').ready, false);
});
test('duplicate/missing IDs remain questions, foreign and stale references cannot be silently applied', () => {
  const store = createStore(); store.dispatch({ type: 'create' }); importSource(store);
  const id = store.getState().boxes[0].id;
  assert.ok(bind(store, id, 'move', 'id:duplicate').ok);
  assert.equal(describeDesign(store.getState(), 'p', 's', 'Move').ready, false);
  const before = store.getState().design;
  assert.equal(bind(store, id, 'move', 'id:foreign').error, 'designForeignElement');
  assert.equal(bind(store, id, 'move', 'id:left', { source_hash: 'f'.repeat(64) }).error, 'designStale');
  assert.equal(bind(store, id, 'move', 'id:left', { expected_revision: 0 }).error, 'designStale');
  assert.deepEqual(store.getState().design, before);
  assert.ok(bind(store, id, 'move', 'id:left').ok);
  importSource(store, 'c'.repeat(64));
  assert.equal(bindingState(store.getState().design, store.getState().design.bindings[id]), 'stale');
  assert.equal(describeDesign(store.getState(), 'p', 's', 'Move').ready, false);
  assert.equal(describeDesign(hydrate(projectBody(store)), 'p', 's', 'Move').ready, false);
  assert.ok(bind(store, id, 'move', 'id:left').ok);
  const differentView = source('c'.repeat(64)); differentView.source.reference_viewport = {width:1000,height:640};
  assert.ok(store.dispatch({type:'designImport',design:differentView,expected_revision:store.getState().revision}).ok);
  assert.equal(bindingState(store.getState().design, store.getState().design.bindings[id]), 'unresolved');
});
test('import and binding are existing undo steps; old inline frames never inherit a new background', () => {
  const store = createStore(); store.dispatch({ type: 'create' });
  const old = projectBody(store); delete old.state.design;
  for (const frame of old.history.undo) delete frame.state.design;
  const reopened = createStore(hydrate(old)); reopened.importHistory(old.history);
  importSource(reopened);
  assert.ok(reopened.getState().design);
  reopened.dispatch({ type: 'undo' }); assert.equal(reopened.getState().design, null);
  reopened.dispatch({ type: 'redo' }); assert.ok(reopened.getState().design);
  reopened.dispatch({ type: 'undo' }); reopened.dispatch({ type: 'undo' });
  assert.equal(reopened.getState().design, null);
  assert.equal(reopened.getState().boxes.length, 0);
});
test('locked layers and malformed design metadata cannot mutate state', () => {
  const store = createStore(); store.dispatch({ type: 'create' }); importSource(store);
  const id = store.getState().boxes[0].id;
  store.dispatch({ type: 'layer', layer: 2 });
  assert.equal(bind(store, id, 'replace', 'id:left').error, 'layerLocked');
  const forged = source('a'.repeat(64)); forged.preview.artifact_sha256 = '../../state';
  assert.equal(store.dispatch({ type: 'designImport', design: forged, expected_revision: store.getState().revision }).ok, false);
  assert.equal(store.getState().design.preview.artifact_sha256, 'b'.repeat(64));
  const future = source('a'.repeat(64)); future.version = 2;
  assert.equal(store.dispatch({ type:'designImport', design:future, expected_revision:store.getState().revision }).error, 'storageFormat');
  const old = initialState(); delete old.design; assert.equal(createStore(old).getState().design, undefined);
});
test('valid legacy box IDs cannot become prototype lookups; export bounds stay explicit', () => {
  const state = initialState();
  const seed = createStore(); seed.dispatch({type:'create'});
  state.boxes = seed.getState().boxes; state.boxes[0].id = '__proto__'; state.selection = ['__proto__']; state.nextNumber = 2;
  const store = createStore(state); importSource(store);
  assert.equal(describeDesign(store.getState(),'p','s','Add').descriptor.elements[0].action, 'new');
  assert.ok(bind(store, '__proto__', 'move', 'id:left').ok);
  assert.equal(describeDesign(store.getState(),'p','s','Move').descriptor.elements[0].source_element.element_id, 'id:left');
  store.dispatch({type:'patch',id:'__proto__',changes:{label:'x'.repeat(4000)}});
  assert.throws(()=>describeDesign(store.getState(),'p','s','Move'), /designElementLimit/);
});
